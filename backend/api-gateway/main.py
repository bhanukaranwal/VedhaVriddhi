import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import redis.asyncio as redis
import json
from datetime import datetime, timedelta

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import httpx
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL

from auth import authenticate_user, get_current_user
from models import *
from config import Settings
from websocket_manager import WebSocketManager

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class APIGateway:
    def __init__(self):
        self.settings = Settings()
        self.redis_client = None
        self.http_client = None
        self.websocket_manager = WebSocketManager()
        
    async def initialize(self):
        """Initialize the API Gateway"""
        logger.info("Initializing VedhaVriddhi API Gateway")
        
        # Initialize Redis
        self.redis_client = redis.Redis(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            password=self.settings.redis_password,
            decode_responses=True
        )
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(
                max_keepalive_connections=100,
                max_connections=1000
            )
        )
        
        logger.info("API Gateway initialized successfully")
        
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up API Gateway")
        
        if self.redis_client:
            await self.redis_client.close()
            
        if self.http_client:
            await self.http_client.aclose()
            
        logger.info("API Gateway cleanup completed")

# Global gateway instance
api_gateway = APIGateway()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await api_gateway.initialize()
    yield
    # Shutdown
    await api_gateway.cleanup()

# FastAPI application
app = FastAPI(
    title="VedhaVriddhi API Gateway",
    description="Unified API gateway for VedhaVriddhi trading platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# GraphQL Schema
@strawberry.type
class Query:
    @strawberry.field
    async def orders(self, info) -> List[OrderResponse]:
        """Get all orders for the authenticated user"""
        try:
            user = info.context["user"]
            response = await api_gateway.http_client.get(
                f"{api_gateway.settings.trading_engine_url}/orders",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            response.raise_for_status()
            
            orders_data = response.json()
            return [OrderResponse(**order) for order in orders_data]
            
        except Exception as e:
            logger.error("Error fetching orders", error=str(e))
            raise Exception("Failed to fetch orders")
    
    @strawberry.field
    async def order(self, info, order_id: str) -> Optional[OrderResponse]:
        """Get specific order by ID"""
        try:
            user = info.context["user"]
            response = await api_gateway.http_client.get(
                f"{api_gateway.settings.trading_engine_url}/orders/{order_id}",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            order_data = response.json()
            return OrderResponse(**order_data)
            
        except Exception as e:
            logger.error(f"Error fetching order {order_id}", error=str(e))
            raise Exception("Failed to fetch order")
    
    @strawberry.field
    async def market_data(self, info, symbol: str) -> Optional[MarketDataResponse]:
        """Get market data for a symbol"""
        try:
            response = await api_gateway.http_client.get(
                f"{api_gateway.settings.market_data_url}/market-data/{symbol}"
            )
            
            if response.status_code == 404:
                return None
                
            response.raise_for_status()
            data = response.json()
            return MarketDataResponse(**data)
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}", error=str(e))
            raise Exception("Failed to fetch market data")

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def submit_order(self, info, order_input: OrderInput) -> OrderResponse:
        """Submit a new trading order"""
        try:
            user = info.context["user"]
            
            # Prepare order data
            order_data = {
                "client_order_id": order_input.client_order_id,
                "symbol": order_input.symbol,
                "side": order_input.side.value,
                "order_type": order_input.order_type.value,
                "quantity": str(order_input.quantity),
                "price": str(order_input.price) if order_input.price else None,
                "time_in_force": order_input.time_in_force.value if order_input.time_in_force else "GTC",
                "user_id": user["user_id"],
                "account_id": user["account_id"]
            }
            
            response = await api_gateway.http_client.post(
                f"{api_gateway.settings.trading_engine_url}/orders",
                json=order_data,
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            response.raise_for_status()
            
            order_response = response.json()
            logger.info(f"Order submitted successfully: {order_response['id']}")
            
            return OrderResponse(**order_response)
            
        except Exception as e:
            logger.error("Error submitting order", error=str(e))
            raise Exception("Failed to submit order")
    
    @strawberry.mutation
    async def cancel_order(self, info, order_id: str) -> bool:
        """Cancel an existing order"""
        try:
            user = info.context["user"]
            
            response = await api_gateway.http_client.delete(
                f"{api_gateway.settings.trading_engine_url}/orders/{order_id}",
                headers={"Authorization": f"Bearer {user['token']}"}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Order cancelled: {order_id}")
            
            return result.get("cancelled", False)
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}", error=str(e))
            raise Exception("Failed to cancel order")

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def order_updates(self, info) -> OrderResponse:
        """Subscribe to order updates"""
        # Implementation for order updates subscription
        pass
    
    @strawberry.subscription
    async def market_data_updates(self, info, symbol: str) -> MarketDataResponse:
        """Subscribe to market data updates for a symbol"""
        # Implementation for market data subscription
        pass

# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

# GraphQL router
graphql_app = GraphQLRouter(
    schema,
    subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL]
)

app.include_router(graphql_app, prefix="/graphql")

# REST API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    """User authentication endpoint"""
    try:
        # Validate credentials
        user_data = await authenticate_user(credentials.username, credentials.password)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Store session in Redis
        session_id = f"session:{user_data['user_id']}"
        await api_gateway.redis_client.setex(
            session_id,
            timedelta(hours=8),
            json.dumps(user_data)
        )
        
        return {
            "access_token": user_data["token"],
            "token_type": "bearer",
            "expires_in": 28800,  # 8 hours
            "user": {
                "id": user_data["user_id"],
                "username": user_data["username"],
                "role": user_data["role"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(current_user: dict = Depends(get_current_user)):
    """Get orders for the authenticated user"""
    try:
        response = await api_gateway.http_client.get(
            f"{api_gateway.settings.trading_engine_url}/orders",
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        response.raise_for_status()
        
        orders_data = response.json()
        return [OrderResponse(**order) for order in orders_data]
        
    except Exception as e:
        logger.error("Error fetching orders", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders"
        )

@app.post("/orders", response_model=OrderResponse)
async def submit_order(
    order_request: OrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Submit a new trading order"""
    try:
        # Prepare order data
        order_data = {
            **order_request.dict(),
            "user_id": current_user["user_id"],
            "account_id": current_user["account_id"]
        }
        
        response = await api_gateway.http_client.post(
            f"{api_gateway.settings.trading_engine_url}/orders",
            json=order_data,
            headers={"Authorization": f"Bearer {current_user['token']}"}
        )
        response.raise_for_status()
        
        order_response = response.json()
        logger.info(f"Order submitted: {order_response['id']}")
        
        return OrderResponse(**order_response)
        
    except Exception as e:
        logger.error("Error submitting order", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit order"
        )

@app.get("/market-data/{symbol}", response_model=MarketDataResponse)
async def get_market_data(symbol: str):
    """Get market data for a symbol"""
    try:
        # Check cache first
        cached_data = await api_gateway.redis_client.get(f"market_data:{symbol}")
        if cached_data:
            return MarketDataResponse(**json.loads(cached_data))
        
        # Fetch from market data service
        response = await api_gateway.http_client.get(
            f"{api_gateway.settings.market_data_url}/market-data/{symbol}"
        )
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for symbol {symbol}"
            )
            
        response.raise_for_status()
        data = response.json()
        
        # Cache the data
        await api_gateway.redis_client.setex(
            f"market_data:{symbol}",
            60,  # Cache for 1 minute
            json.dumps(data)
        )
        
        return MarketDataResponse(**data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch market data"
        )

@app.websocket("/ws/orders")
async def orders_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time order updates"""
    await websocket.accept()
    await api_gateway.websocket_manager.connect(websocket, "orders")
    
    try:
        while True:
            # Keep connection alive
            message = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {message}")
            
    except WebSocketDisconnect:
        api_gateway.websocket_manager.disconnect(websocket, "orders")
        logger.info("Orders WebSocket disconnected")

@app.websocket("/ws/market-data/{symbol}")
async def market_data_websocket(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time market data"""
    await websocket.accept()
    await api_gateway.websocket_manager.connect(websocket, f"market_data:{symbol}")
    
    try:
        while True:
            # Keep connection alive
            message = await websocket.receive_text()
            logger.debug(f"Received market data WebSocket message for {symbol}: {message}")
            
    except WebSocketDisconnect:
        api_gateway.websocket_manager.disconnect(websocket, f"market_data:{symbol}")
        logger.info(f"Market data WebSocket disconnected for {symbol}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        log_config=None,
        access_log=False,
        reload=False
    )
