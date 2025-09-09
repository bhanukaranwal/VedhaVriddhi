import asyncio
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

@pytest.fixture
def agi_app():
    from backend.agi_service.main import app
    return app

@pytest.fixture
async def client(agi_app):
    async with AsyncClient(app=agi_app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
class TestAGIService:
    
    async def test_reasoning_endpoint(self, client):
        """Test AGI reasoning capabilities"""
        payload = {
            "reasoning_type": "deductive",
            "premises": [
                "All financial markets are volatile",
                "The stock market is a financial market"
            ],
            "query": "Is the stock market volatile?"
        }
        
        with patch('backend.agi_service.core.reasoning_engine.ReasoningEngine.reason') as mock_reason:
            mock_reason.return_value = {
                "conclusion": "Yes, the stock market is volatile",
                "reasoning_chain": ["premise1", "premise2", "conclusion"],
                "confidence": 0.95,
                "logical_validity": True
            }
            
            response = await client.post("/agi/reason", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == True
            assert "reasoning" in data
            assert data["reasoning"]["confidence"] > 0.9
            
    async def test_multi_agent_decision(self, client):
        """Test multi-agent decision making"""
        payload = {
            "decision_context": "Portfolio rebalancing",
            "options": ["Aggressive growth", "Balanced", "Conservative"],
            "criteria": ["risk_tolerance", "time_horizon", "market_conditions"],
            "agent_count": 5
        }
        
        response = await client.post("/agi/decide", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "decision" in data
        
    async def test_natural_language_processing(self, client):
        """Test NLP capabilities"""
        payload = {
            "text": "Analyze the market sentiment for Tesla stock based on recent news",
            "task": "sentiment_analysis",
            "context": "financial_market"
        }
        
        response = await client.post("/agi/process_language", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "processed" in data
