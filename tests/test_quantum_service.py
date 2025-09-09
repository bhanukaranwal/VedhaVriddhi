import asyncio
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import json

# Mock the quantum service app
@pytest.fixture
def quantum_app():
    from backend.quantum_computing_service.main import app
    return app

@pytest.fixture
async def client(quantum_app):
    async with AsyncClient(app=quantum_app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
class TestQuantumService:
    
    async def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        
    async def test_quantum_optimization(self, client):
        """Test quantum portfolio optimization"""
        payload = {
            "portfolio": {
                "assets": ["AAPL", "GOOGL", "TSLA", "MSFT"],
                "expected_returns": [0.12, 0.15, 0.20, 0.14],
                "covariance_matrix": [[0.1, 0.02, 0.03, 0.01]] * 4,
                "constraints": {
                    "min_weight": 0.0,
                    "max_weight": 0.5,
                    "target_return": 0.15
                }
            },
            "optimization_params": {
                "algorithm": "QAOA",
                "layers": 3,
                "shots": 1024,
                "maxiter": 100
            }
        }
        
        with patch('backend.quantum_computing_service.core.quantum_optimizer.QuantumOptimizer.optimize_portfolio') as mock_optimize:
            mock_optimize.return_value = {
                "optimal_weights": [0.25, 0.25, 0.25, 0.25],
                "expected_return": 0.1525,
                "risk_level": 0.082,
                "sharpe_ratio": 1.86,
                "quantum_advantage": 3.2
            }
            
            response = await client.post("/quantum/optimize", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == True
            assert "result" in data
            assert "optimal_weights" in data["result"]
            assert len(data["result"]["optimal_weights"]) == 4
            
    async def test_quantum_simulation(self, client):
        """Test quantum circuit simulation"""
        payload = {
            "circuit": {
                "qubits": 4,
                "gates": [
                    {"type": "H", "target": 0},
                    {"type": "CNOT", "control": 0, "target": 1},
                    {"type": "RY", "target": 2, "parameter": 0.5}
                ]
            },
            "shots": 1024,
            "backend": "qiskit_aer"
        }
        
        response = await client.post("/quantum/simulate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "result" in data
        
    async def test_invalid_optimization_request(self, client):
        """Test invalid optimization request handling"""
        payload = {
            "portfolio": {
                "assets": [],  # Empty assets list
                "constraints": {}
            }
        }
        
        response = await client.post("/quantum/optimize", json=payload)
        assert response.status_code == 422 or response.status_code == 400

@pytest.mark.asyncio
class TestQuantumAlgorithms:
    
    async def test_qaoa_algorithm(self):
        """Test QAOA algorithm implementation"""
        from backend.quantum_computing_service.core.quantum_algorithms import QAOAOptimizer
        
        optimizer = QAOAOptimizer()
        await optimizer.initialize()
        
        problem_data = {
            "cost_matrix": [[0, 1, 2], [1, 0, 1], [2, 1, 0]],
            "num_layers": 2
        }
        
        result = await optimizer.solve(problem_data)
        assert "solution" in result
        assert "cost" in result
        assert "quantum_advantage" in result
        
    async def test_vqe_algorithm(self):
        """Test VQE algorithm implementation"""
        from backend.quantum_computing_service.core.quantum_algorithms import VQEOptimizer
        
        optimizer = VQEOptimizer()
        await optimizer.initialize()
        
        hamiltonian = {
            "terms": [
                {"pauli": "ZZ", "coefficient": -1.0, "qubits": [0, 1]},
                {"pauli": "X", "coefficient": 0.5, "qubits": [0]}
            ]
        }
        
        result = await optimizer.find_ground_state(hamiltonian)
        assert "ground_state_energy" in result
        assert "optimal_parameters" in result

# Integration tests
@pytest.mark.integration
@pytest.mark.asyncio
class TestQuantumIntegration:
    
    async def test_end_to_end_portfolio_optimization(self, client):
        """End-to-end portfolio optimization test"""
        # Step 1: Create portfolio
        portfolio_payload = {
            "name": "Test Portfolio",
            "assets": ["AAPL", "GOOGL", "TSLA"],
            "initial_weights": [0.33, 0.33, 0.34]
        }
        
        # Step 2: Optimize portfolio
        optimization_payload = {
            "portfolio": portfolio_payload,
            "optimization_params": {
                "algorithm": "QAOA",
                "risk_tolerance": 0.5,
                "target_return": 0.12
            }
        }
        
        response = await client.post("/quantum/optimize", json=optimization_payload)
        assert response.status_code == 200
        
        # Step 3: Verify results
        data = response.json()
        assert data["success"] == True
        assert "quantum_advantage" in data["result"]
        assert data["result"]["quantum_advantage"] > 1.0  # Should show quantum advantage
