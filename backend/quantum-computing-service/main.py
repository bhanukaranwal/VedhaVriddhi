from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from core.quantum_processor import QuantumProcessor
from core.quantum_algorithms import QuantumAlgorithmSuite
from core.quantum_optimization import QuantumOptimizer
from core.quantum_simulation import QuantumSimulator
from core.quantum_error_correction import QuantumErrorCorrection
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="Quantum Computing Service",
    description="Advanced quantum computing for financial optimization",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize quantum components
quantum_processor = QuantumProcessor()
algorithm_suite = QuantumAlgorithmSuite()
quantum_optimizer = QuantumOptimizer()
quantum_simulator = QuantumSimulator()
error_correction = QuantumErrorCorrection()

@app.on_event("startup")
async def startup():
    await quantum_processor.initialize()
    await algorithm_suite.initialize()
    await quantum_optimizer.initialize()
    await quantum_simulator.initialize()
    await error_correction.initialize()
    logger.info("Quantum Computing Service started successfully")

@app.get("/")
async def root():
    return {
        "service": "Quantum Computing Service",
        "version": "4.0.0",
        "status": "operational",
        "quantum_advantage": True
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "quantum_processors_available": True}

@app.post("/quantum/optimize")
async def quantum_optimize(optimization_request: dict):
    try:
        result = await quantum_optimizer.optimize_portfolio(optimization_request)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quantum/simulate")
async def quantum_simulate(simulation_request: dict):
    try:
        result = await quantum_simulator.run_simulation(simulation_request)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quantum/algorithm/{algorithm_name}")
async def run_algorithm(algorithm_name: str, algorithm_params: dict):
    try:
        result = await algorithm_suite.run_algorithm(algorithm_name, algorithm_params)
        return {"success": True, "algorithm": algorithm_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quantum/status")
async def quantum_status():
    try:
        status = await quantum_processor.get_system_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)
