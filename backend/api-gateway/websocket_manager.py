import json
import asyncio
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import structlog
from datetime import datetime

logger = structlog.get_logger()

class WebSocketConnection:
    def __init__(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user_id = user_id
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        
    async def send_message(self, message: Dict[str, Any]):
        """Send message to WebSocket client"""
        try:
            await self.websocket.send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.error("Failed to send WebSocket message", 
                        connection_id=self.connection_id, error=str(e))
            return False
            
    async def ping(self):
        """Send ping to client"""
        try:
            await self.websocket.send_text(json.dumps({"type": "ping", "timestamp": datetime.utcnow().isoformat()}))
            self.last_ping = datetime.utcnow()
            return True
        except:
            return False

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.topic_subscribers: Dict[str, Set[str]] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self._connection_counter = 0
        
    async def connect(self, websocket: WebSocket, topic: str, user_id: Optional[str] = None) -> str:
        """Accept WebSocket connection and register for topic"""
        await websocket.accept()
        
        # Generate connection ID
        self._connection_counter += 1
        connection_id = f"conn_{self._connection_counter}_{datetime.utcnow().timestamp()}"
        
        # Create connection object
        connection = WebSocketConnection(websocket, connection_id, user_id)
        self.connections[connection_id] = connection
        
        # Subscribe to topic
        await self.subscribe(connection_id, topic)
        
        # Track user connections
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
        logger.info("WebSocket connected", 
                   connection_id=connection_id, topic=topic, user_id=user_id)
        
        return connection_id
        
    def disconnect(self, websocket: WebSocket, topic: str):
        """Disconnect WebSocket and cleanup"""
        connection_id = None
        
        # Find connection by websocket
        for conn_id, conn in self.connections.items():
            if conn.websocket == websocket:
                connection_id = conn_id
                break
                
        if connection_id:
            connection = self.connections.get(connection_id)
            
            # Remove from topic subscriptions
            for sub_topic in connection.subscriptions.copy():
                self.unsubscribe(connection_id, sub_topic)
                
            # Remove from user connections
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
                    
            # Remove connection
            del self.connections[connection_id]
            
            logger.info("WebSocket disconnected", 
                       connection_id=connection_id, topic=topic, user_id=connection.user_id)
            
    async def subscribe(self, connection_id: str, topic: str):
        """Subscribe connection to topic"""
        if connection_id not in self.connections:
            return False
            
        connection = self.connections[connection_id]
        connection.subscriptions.add(topic)
        
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = set()
        self.topic_subscribers[topic].add(connection_id)
        
        logger.debug("WebSocket subscribed to topic", 
                    connection_id=connection_id, topic=topic)
        return True
        
    def unsubscribe(self, connection_id: str, topic: str):
        """Unsubscribe connection from topic"""
        if connection_id in self.connections:
            self.connections[connection_id].subscriptions.discard(topic)
            
        if topic in self.topic_subscribers:
            self.topic_subscribers[topic].discard(connection_id)
            if not self.topic_subscribers[topic]:
                del self.topic_subscribers[topic]
                
        logger.debug("WebSocket unsubscribed from topic", 
                    connection_id=connection_id, topic=topic)
                    
    async def broadcast_to_topic(self, topic: str, message: Dict[str, Any]):
        """Broadcast message to all subscribers of a topic"""
        if topic not in self.topic_subscribers:
            return
            
        disconnected_connections = []
        message_with_topic = {**message, "topic": topic}
        
        for connection_id in self.topic_subscribers[topic].copy():
            connection = self.connections.get(connection_id)
            if not connection:
                disconnected_connections.append(connection_id)
                continue
                
            success = await connection.send_message(message_with_topic)
            if not success:
                disconnected_connections.append(connection_id)
                
        # Clean up disconnected connections
        for conn_id in disconnected_connections:
            if conn_id in self.connections:
                self.disconnect(self.connections[conn_id].websocket, topic)
                
        logger.debug(f"Broadcasted to topic {topic}", 
                    subscribers=len(self.topic_subscribers.get(topic, [])),
                    disconnected=len(disconnected_connections))
                    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return False
            
        disconnected_connections = []
        
        for connection_id in self.user_connections[user_id].copy():
            connection = self.connections.get(connection_id)
            if not connection:
                disconnected_connections.append(connection_id)
                continue
                
            success = await connection.send_message(message)
            if not success:
                disconnected_connections.append(connection_id)
                
        # Clean up disconnected connections
        for conn_id in disconnected_connections:
            if conn_id in self.connections:
                connection = self.connections[conn_id]
                for topic in connection.subscriptions.copy():
                    self.disconnect(connection.websocket, topic)
                    
        return len(self.user_connections.get(user_id, [])) > 0
        
    async def ping_all_connections(self):
        """Send ping to all active connections"""
        disconnected_connections = []
        
        for connection_id, connection in self.connections.items():
            success = await connection.ping()
            if not success:
                disconnected_connections.append(connection_id)
                
        # Clean up disconnected connections
        for conn_id in disconnected_connections:
            if conn_id in self.connections:
                connection = self.connections[conn_id]
                for topic in connection.subscriptions.copy():
                    self.disconnect(connection.websocket, topic)
                    
        logger.debug(f"Ping sent to connections", 
                    total=len(self.connections),
                    disconnected=len(disconnected_connections))
                    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.connections),
            "topics": list(self.topic_subscribers.keys()),
            "topic_subscriber_counts": {
                topic: len(subscribers) 
                for topic, subscribers in self.topic_subscribers.items()
            },
            "user_connection_counts": {
                user_id: len(conn_ids)
                for user_id, conn_ids in self.user_connections.items()
            }
        }
