import asyncio
from typing import Dict, List, Optional
import httpx
import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = structlog.get_logger()

class Phase4APIGateway:
    def __init__(self):
        self.service_registry = {
            'quantum': {'url': 'http://quantum-service:8200', 'health': True},
            'agi': {'url': 'http://agi-service:8201', 'health': True},
            'universal-defi': {'url': 'http://universal-defi-service:8202', 'health': True},
            'metaverse': {'url': 'http://metaverse-service:8203', 'health': True},
            'climate': {'url': 'http://climate-intelligence-service:8204', 'health': True},
            'neural': {'url': 'http://neural-interface-service:8205', 'health': True},
            'quantum-ml': {'url': 'http://quantum-ml-service:8206', 'health': True},
            'orchestration': {'url': 'http://quantum-orchestration-service:8207', 'health': True},
            'coordination': {'url': 'http://agi-coordination-service:8208', 'health': True},
            'protocol': {'url': 'http://protocol-integration-service:8209', 'health': True},
            'analytics': {'url': 'http://multi-dimensional-analytics-service:8210', 'health': True},
            'consciousness': {'url': 'http://consciousness-gateway-service:8211', 'health': True},
            'planetary': {'url': 'http://planetary-impact-service:8212', 'health': True}
        }
        self.client = httpx.AsyncClient()
        
    async def initialize(self):
        """Initialize API Gateway"""
        logger.info("Initializing Phase 4 API Gateway")
        
        # Start health monitoring
        asyncio.create_task(self.monitor_service_health())
        
        logger.info("Phase 4 API Gateway initialized successfully")
    
    async def monitor_service_health(self):
        """Monitor health of all microservices"""
        while True:
            try:
                for service_name, service_info in self.service_registry.items():
                    try:
                        response = await self.client.get(f"{service_info['url']}/health", timeout=5.0)
                        service_info['health'] = response.status_code == 200
                    except:
                        service_info['health'] = False
                        logger.warning(f"Service {service_name} health check failed")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("Service health monitoring error", error=str(e))
                await asyncio.sleep(60)

gateway = Phase4APIGateway()

app = FastAPI(
    title="VedhaVriddhi Phase 4 API Gateway",
    description="Unified API Gateway for Universal Financial Intelligence System",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await gateway.initialize()

@app.get("/health")
async def health_check():
    """Gateway health check"""
    healthy_services = sum(1 for service in gateway.service_registry.values() if service['health'])
    total_services = len(gateway.service_registry)
    
    return {
        "status": "healthy" if healthy_services == total_services else "degraded",
        "gateway_version": "4.0.0",
        "services_healthy": healthy_services,
        "total_services": total_services,
        "service_status": gateway.service_registry,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.api_route("/quantum/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def quantum_proxy(request: Request, path: str):
    """Proxy requests to Quantum Computing Service"""
    return await proxy_request(request, "quantum", path)

@app.api_route("/agi/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def agi_proxy(request: Request, path: str):
    """Proxy requests to AGI Service"""
    return await proxy_request(request, "agi", path)

@app.api_route("/consciousness/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def consciousness_proxy(request: Request, path: str):
    """Proxy requests to Consciousness Gateway Service"""
    return await proxy_request(request, "consciousness", path)

async def proxy_request(request: Request, service_name: str, path: str):
    """Generic request proxy function"""
    service_info = gateway.service_registry.get(service_name)
    
    if not service_info or not service_info['health']:
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
    
    try:
        url = f"{service_info['url']}/{path}"
        body = await request.body()
        
        response = await gateway.client.request(
            method=request.method,
            url=url,
            params=request.query_params,
            headers=dict(request.headers),
            content=body
        )
        
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
            headers=dict(response.headers)
        )
        
    except Exception as e:
        logger.error(f"Proxy request failed for {service_name}/{path}", error=str(e))
        raise HTTPException(status_code=500, detail="Proxy request failed")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8300, reload=False)
