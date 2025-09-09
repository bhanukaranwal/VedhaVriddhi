import asyncio
import heapq
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger()

class JobPriority(Enum):
    CRITICAL = 1
    HIGH = 2  
    MEDIUM = 3
    LOW = 4
    BATCH = 5

class JobStatus(Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QuantumJob:
    """Quantum job definition"""
    job_id: str
    user_id: str
    algorithm_type: str
    circuit_data: Dict
    priority: JobPriority
    estimated_runtime: float
    resource_requirements: Dict
    submitted_at: datetime
    dependencies: List[str] = field(default_factory=list)
    callback_url: Optional[str] = None
    status: JobStatus = JobStatus.QUEUED
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_data: Optional[Dict] = None
    error_message: Optional[str] = None
    
    def __lt__(self, other):
        # For priority queue ordering
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.submitted_at < other.submitted_at

class AdvancedJobScheduler:
    """Advanced quantum job scheduling with dependency resolution"""
    
    def __init__(self):
        self.job_queue = []  # Priority queue
        self.jobs: Dict[str, QuantumJob] = {}
        self.running_jobs: Dict[str, QuantumJob] = {}
        self.completed_jobs: Dict[str, QuantumJob] = {}
        
        self.max_concurrent_jobs = 10
        self.resource_manager = None  # Will be injected
        
    async def initialize(self, resource_manager):
        """Initialize job scheduler"""
        logger.info("Initializing Advanced Job Scheduler")
        
        self.resource_manager = resource_manager
        
        # Start background tasks
        asyncio.create_task(self._job_scheduling_loop())
        asyncio.create_task(self._job_monitoring_loop())
        asyncio.create_task(self._dependency_resolution_loop())
        
        logger.info("Advanced Job Scheduler initialized successfully")
    
    async def submit_job(self, 
                        user_id: str,
                        algorithm_type: str,
                        circuit_data: Dict,
                        priority: JobPriority = JobPriority.MEDIUM,
                        dependencies: List[str] = None,
                        callback_url: str = None) -> str:
        """Submit new quantum job"""
        try:
            job_id = f"qjob_{datetime.utcnow().timestamp()}_{len(self.jobs)}"
            
            # Estimate resource requirements
            resource_requirements = await self._estimate_resource_requirements(
                algorithm_type, circuit_data
            )
            
            # Estimate runtime
            estimated_runtime = await self._estimate_job_runtime(
                algorithm_type, circuit_data
            )
            
            # Create job
            job = QuantumJob(
                job_id=job_id,
                user_id=user_id,
                algorithm_type=algorithm_type,
                circuit_data=circuit_data,
                priority=priority,
                estimated_runtime=estimated_runtime,
                resource_requirements=resource_requirements,
                submitted_at=datetime.utcnow(),
                dependencies=dependencies or [],
                callback_url=callback_url
            )
            
            # Add to job tracking
            self.jobs[job_id] = job
            heapq.heappush(self.job_queue, job)
            
            logger.info(f"Job {job_id} submitted with priority {priority.name}")
            return job_id
            
        except Exception as e:
            logger.error("Job submission failed", error=str(e))
            raise
    
    async def _job_scheduling_loop(self):
        """Main job scheduling loop"""
        while True:
            try:
                await self._schedule_next_jobs()
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error("Job scheduling loop error", error=str(e))
                await asyncio.sleep(5)
    
    async def _schedule_next_jobs(self):
        """Schedule next available jobs"""
        if len(self.running_jobs) >= self.max_concurrent_jobs:
            return
        
        # Find jobs ready to run (dependencies satisfied)
        ready_jobs = []
        temp_queue = []
        
        while self.job_queue and len(ready_jobs) < (self.max_concurrent_jobs - len(self.running_jobs)):
            job = heapq.heappop(self.job_queue)
            
            if job.status == JobStatus.QUEUED:
                # Check if dependencies are satisfied
                if await self._dependencies_satisfied(job):
                    ready_jobs.append(job)
                else:
                    temp_queue.append(job)
            else:
                temp_queue.append(job)
        
        # Put non-ready jobs back in queue
        for job in temp_queue:
            heapq.heappush(self.job_queue, job)
        
        # Schedule ready jobs
        for job in ready_jobs:
            success = await self._attempt_job_scheduling(job)
            if not success:
                # Put back in queue if scheduling failed
                heapq.heappush(self.job_queue, job)
    
    async def _attempt_job_scheduling(self, job: QuantumJob) -> bool:
        """Attempt to schedule a specific job"""
        try:
            # Try to allocate resources
            allocation_id = await self.resource_manager.allocate_resources(
                job.user_id,
                job.job_id,
                job.resource_requirements,
                job.priority.value
            )
            
            if allocation_id == "queued":
                # Resources not available, keep in queue
                return False
            
            # Resources allocated, start job
            job.status = JobStatus.SCHEDULED
            job.scheduled_at = datetime.utcnow()
            
            # Start job execution
            asyncio.create_task(self._execute_job(job))
            
            return True
            
        except Exception as e:
            logger.error(f"Job scheduling failed for {job.job_id}", error=str(e))
            return False
    
    async def _execute_job(self, job: QuantumJob):
        """Execute quantum job"""
        try:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            self.running_jobs[job.job_id] = job
            
            logger.info(f"Executing job {job.job_id}")
            
            # Simulate job execution based on algorithm type
            result_data = await self._run_quantum_algorithm(job)
            
            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result_data = result_data
            
            # Move to completed jobs
            self.completed_jobs[job.job_id] = self.running_jobs.pop(job.job_id)
            
            # Send callback if specified
            if job.callback_url:
                await self._send_job_callback(job)
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            
            self.completed_jobs[job.job_id] = self.running_jobs.pop(job.job_id, job)
            
            logger.error(f"Job {job.job_id} failed", error=str(e))
        
        finally:
            # Release resources
            if self.resource_manager:
                await self.resource_manager.release_resources(job.job_id)
    
    async def _run_quantum_algorithm(self, job: QuantumJob) -> Dict:
        """Execute specific quantum algorithm"""
        # Simulate algorithm execution time
        await asyncio.sleep(min(job.estimated_runtime, 30))  # Cap at 30 seconds for demo
        
        # Generate mock results based on algorithm type
        if job.algorithm_type == "QAOA":
            return {
                'optimal_weights': np.random.dirichlet(np.ones(5)).tolist(),
                'expected_return': np.random.uniform(0.05, 0.15),
                'risk_level': np.random.uniform(0.05, 0.2),
                'quantum_advantage': np.random.uniform(2.0, 10.0),
                'execution_time': job.estimated_runtime
            }
        
        elif job.algorithm_type == "VQE":
            return {
                'ground_state_energy': np.random.uniform(-2.0, 0.0),
                'convergence_iterations': np.random.randint(50, 200),
                'final_gradient_norm': np.random.uniform(1e-6, 1e-3),
                'quantum_advantage': np.random.uniform(1.5, 5.0)
            }
        
        else:
            return {
                'algorithm': job.algorithm_type,
                'result': 'success',
                'quantum_advantage': np.random.uniform(1.0, 3.0)
            }
    
    async def _dependencies_satisfied(self, job: QuantumJob) -> bool:
        """Check if job dependencies are satisfied"""
        for dep_job_id in job.dependencies:
            dep_job = self.jobs.get(dep_job_id)
            if not dep_job or dep_job.status != JobStatus.COMPLETED:
                return False
        return True
    
    async def _estimate_resource_requirements(self, algorithm_type: str, circuit_data: Dict) -> Dict:
        """Estimate resource requirements for job"""
        from .resource_manager import ResourceType
        
        base_requirements = {
            ResourceType.QUANTUM_PROCESSOR: 1,
            ResourceType.CLASSICAL_CPU: 2,
            ResourceType.GPU: 0,
            ResourceType.MEMORY: 1000,  # MB
            ResourceType.NETWORK_BANDWIDTH: 10  # Mbps
        }
        
        # Scale based on problem complexity
        complexity_factor = max(1, len(circuit_data.get('gates', [])) // 100)
        
        scaled_requirements = {}
        for resource_type, base_amount in base_requirements.items():
            scaled_requirements[resource_type] = int(base_amount * complexity_factor)
        
        return scaled_requirements
    
    async def _estimate_job_runtime(self, algorithm_type: str, circuit_data: Dict) -> float:
        """Estimate job runtime in seconds"""
        base_times = {
            'QAOA': 30.0,
            'VQE': 45.0,
            'Grover': 20.0,
            'Shor': 60.0
        }
        
        base_time = base_times.get(algorithm_type, 30.0)
        
        # Adjust for circuit complexity
        n_gates = len(circuit_data.get('gates', []))
        complexity_factor = 1.0 + (n_gates / 1000.0)  # +100% for every 1000 gates
        
        return base_time * complexity_factor
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get comprehensive job status"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'user_id': job.user_id,
            'algorithm_type': job.algorithm_type,
            'status': job.status.value,
            'priority': job.priority.name,
            'submitted_at': job.submitted_at.isoformat(),
            'scheduled_at': job.scheduled_at.isoformat() if job.scheduled_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'estimated_runtime': job.estimated_runtime,
            'dependencies': job.dependencies,
            'result_data': job.result_data,
            'error_message': job.error_message
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job if possible"""
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False
        
        if job.status == JobStatus.RUNNING:
            # Cannot cancel running jobs in this implementation
            return False
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        
        # Remove from queue
        temp_queue = []
        while self.job_queue:
            queued_job = heapq.heappop(self.job_queue)
            if queued_job.job_id != job_id:
                temp_queue.append(queued_job)
        
        for queued_job in temp_queue:
            heapq.heappush(self.job_queue, queued_job)
        
        logger.info(f"Job {job_id} cancelled")
        return True
