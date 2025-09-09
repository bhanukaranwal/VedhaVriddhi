import asyncio
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

@pytest.fixture
def consciousness_app():
    from backend.consciousness_gateway_service.main import app
    return app

@pytest.fixture
async def client(consciousness_app):
    async with AsyncClient(app=consciousness_app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
class TestConsciousnessService:
    
    async def test_consciousness_synthesis(self, client):
        """Test consciousness synthesis endpoint"""
        payload = {
            "consciousness_inputs": [
                {
                    "entity_id": "trader_001",
                    "awareness": 0.8,
                    "emotional_resonance": 0.7,
                    "integration": 0.9
                },
                {
                    "entity_id": "ai_agent_002",
                    "awareness": 0.95,
                    "emotional_resonance": 0.6,
                    "integration": 0.85
                }
            ]
        }
        
        with patch('backend.consciousness_gateway_service.core.processor.GlobalConsciousnessProcessor.synthesize_collective_consciousness') as mock_synthesize:
            mock_synthesize.return_value = {
                "collective_consciousness_active": True,
                "global_consciousness_level": 0.87,
                "wisdom_synthesis": "Advanced collective financial wisdom"
            }
            
            response = await client.post("/consciousness/synthesize", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == True
            assert "synthesis" in data
            assert data["synthesis"]["collective_consciousness_active"] == True
    
    async def test_wisdom_contribution(self, client):
        """Test wisdom contribution endpoint"""
        payload = {
            "entity_id": "wise_trader_001",
            "wisdom_data": {
                "content": "Market timing is less important than time in market",
                "depth": 0.9,
                "universality": 0.8,
                "practical_application": 0.95
            }
        }
        
        response = await client.post("/consciousness/contribute_wisdom", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "wisdom_element_id" in data
    
    async def test_mindfulness_monitoring(self, client):
        """Test mindfulness monitoring"""
        payload = {
            "user_id": "user_123",
            "mindfulness_data": {
                "overall_mindfulness": 0.75,
                "attention_focus": 0.8,
                "present_moment": 0.7,
                "emotional_state": 0.65,
                "stress_indicators": 0.3
            }
        }
        
        response = await client.post("/consciousness/record_mindfulness", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "record_id" in data
