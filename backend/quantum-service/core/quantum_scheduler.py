import asyncio
import heapq
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import structlog

logger = structlog.get_logger()

class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class JobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QuantumJob:
    """Quantum job representation"""
    job_id: str
    algorithm_type: str
    problem_data: Dict
    priority: JobPriority
    user_id: str
    submitted_at: datetime
    estimated_runtime: float  # in seconds
    quantum_requirements: Dict
    callback: Optional[Callable] = None
    status: JobStatus = JobStatus.QUEUED
    result: Optional[Dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __lt__(self, other):
        """For priority queue ordering"""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value  # Higher priority first
        return self.submitted_at < other.submitted_at  # Earlier submission first

class ResourceAllocation:
    """Quantum resource allocation tracking"""
    
    def __init__(self, processor_id: str, max_concurrent_jobs: int = 5):
        self.processor_id = processor_id
        self.max_concurrent_jobs = max_concurrent_jobs
        self.running_jobs: Dict[str, QuantumJob] = {}
        self.total_queue_time = 0.0
        self.total_execution_time = 0.0
        self.jobs_completed = 0
        
    def can_accept_job(self) -> bool:
        """Check if processor can accept new job"""
        return len(self.running_jobs) < self.max_concurrent_jobs
    
    def add_running_job(self, job: QuantumJob):
        """Add job to running jobs"""
        self.running_jobs[job.job_id] = job
    
    def remove_running_job(self, job_id: str) -> Optional[QuantumJob]:
        """Remove job from running jobs"""
        return self.running_jobs.pop(job_id, None)
    
    def get_utilization(self) -> float:
        """Get current processor utilization"""
        return len(self.running_jobs) / self.max_concurrent_jobs

class QuantumJobScheduler:
    """Advanced quantum job scheduler with priority queue and resource management"""
    
    def __init__(self):
        self.job_queue: List[QuantumJob] = []
        self.jobs: Dict[str, QuantumJob] = {}
        self.processors: Dict[str, ResourceAllocation] = {}
        self.scheduling_enabled = True
        self.performance_metrics = {
            'total_jobs_scheduled': 0,
            'total_jobs_completed': 0,
            'average_queue_time': 0.0,
            'average_execution_time': 0.0
        }
        
    async def initialize(self, processor_configs: Dict[str, Dict]):
        """Initialize scheduler with processor configurations"""
        logger.info("Initializing Quantum Job Scheduler")
        
        for processor_id, config in processor_configs.items():
            max_concurrent = config.get('max_concurrent_jobs', 5)
            self.processors[processor_id] = ResourceAllocation(processor_id, max_concurrent)
        
        # Start scheduling loop
        asyncio.create_task(self._scheduling_loop())
        
        logger.info(f"Scheduler initialized with {len(self.processors)} processors")
    
    async def submit_job(self, 
                        algorithm_type: str,
                        problem_data: Dict,
                        user_id: str,
                        priority: JobPriority = JobPriority.NORMAL,
                        quantum_requirements: Optional[Dict] = None,
                        callback: Optional[Callable] = None) -> str:
        """Submit quantum job to scheduler"""
        
        job_id = f"qjob_{datetime.utcnow().timestamp()}_{len(self.jobs)}"
        
        # Estimate runtime based on problem complexity
        estimated_runtime = await self._estimate_job_runtime(algorithm_type, problem_data)
        
        job = QuantumJob(
            job_id=job_id,
            algorithm_type=algorithm_type,
            problem_data=problem_data,
            priority=priority,
            user_id=user_id,
            submitted_at=datetime.utcnow(),
            estimated_runtime=estimated_runtime,
            quantum_requirements=quantum_requirements or {},
            callback=callback
        )
        
        # Add to queue and jobs registry
        heapq.heappush(self.job_queue, job)
        self.jobs[job_id] = job
        
        self.performance_metrics['total_jobs_scheduled'] += 1
        
        logger.info(f"Job {job_id} submitted with priority {priority.name}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status and details"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        queue_position = None
        if job.status == JobStatus.QUEUED:
            queue_position = self._get_queue_position(job_id)
        
        return {
            'job_id': job_id,
            'status': job.status.value,
            'algorithm_type': job.algorithm_type,
            'priority': job.priority.name,
            'submitted_at': job.submitted_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'estimated_runtime': job.estimated_runtime,
            'queue_position': queue_position,
            'result': job.result,
            'error_message': job.error_message
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel queued or running job"""
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        
        # Remove from queue if queued
        if job in self.job_queue:
            self.job_queue.remove(job)
            heapq.heapify(self.job_queue)
        
        # Remove from processor if running
        for processor in self.processors.values():
            if job_id in processor.running_jobs:
                processor.remove_running_job(job_id)
                break
        
        logger.info(f"Job {job_id} cancelled")
        return True
    
    async def _scheduling_loop(self):
        """Main scheduling loop"""
        while self.scheduling_enabled:
            try:
                await self._schedule_next_jobs()
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error("Scheduling loop error", error=str(e))
                await asyncio.sleep(5)
    
    async def _schedule_next_jobs(self):
        """Schedule next available jobs to processors"""
        if not self.job_queue:
            return
        
        # Find available processors
        available_processors = [
            (pid, proc) for pid, proc in self.processors.items() 
            if proc.can_accept_job()
        ]
        
        if not available_processors:
            return
        
        # Schedule jobs to available processors
        jobs_to_schedule = []
        temp_queue = []
        
        # Extract jobs that can be scheduled
        while self.job_queue and len(jobs_to_schedule) < len(available_processors):
            job = heapq.heappop(self.job_queue)
            
            if job.status == JobStatus.QUEUED:
                # Check if job requirements match available processors
                suitable_processor = await self._find_suitable_processor(job, available_processors)
                if suitable_processor:
                    jobs_to_schedule.append((job, suitable_processor))
                    available_processors.remove(suitable_processor)
                else:
                    temp_queue.append(job)
            
        # Put unscheduled jobs back in queue
        for job in temp_queue:
            heapq.heappush(self.job_queue, job)
        
        # Execute scheduled jobs
        for job, (processor_id, processor) in jobs_to_schedule:
            await self._execute_job(job, processor_id)
    
    async def _find_suitable_processor(self, job: QuantumJob, available_processors: List) -> Optional[tuple]:
        """Find suitable processor for job based on requirements"""
        requirements = job.quantum_requirements
        
        # Simple selection - would implement more sophisticated matching
        for processor_tuple in available_processors:
            processor_id, processor = processor_tuple
            
            # Check basic requirements (would be more comprehensive)
            required_qubits = requirements.get('min_qubits', 5)
            if required_qubits <= 100:  # Assume all processors have 100+ qubits
                return processor_tuple
        
        return available_processors[0] if available_processors else None
    
    async def _execute_job(self, job: QuantumJob, processor_id: str):
        """Execute job on specified processor"""
        processor = self.processors[processor_id]
        
        # Update job status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        # Add to processor's running jobs
        processor.add_running_job(job)
        
        logger.info(f"Starting job {job.job_id} on processor {processor_id}")
        
        # Execute job asynchronously
        asyncio.create_task(self._run_job_execution(job, processor_id))
    
    async def _run_job_execution(self, job: QuantumJob, processor_id: str):
        """Run job execution and handle completion"""
        try:
            # Simulate job execution time
            execution_time = min(job.estimated_runtime, 60)  # Cap at 60 seconds for demo
            await asyncio.sleep(execution_time)
            
            # Simulate successful job completion
            job.result = {
                'algorithm': job.algorithm_type,
                'optimal_weights': [0.3, 0.25, 0.25, 0.2],
                'expected_return': 0.08,
                'risk_level': 0.12,
                'quantum_advantage': 2.5,
                'execution_time': execution_time
            }
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            # Update metrics
            queue_time = (job.started_at - job.submitted_at).total_seconds()
            execution_time_actual = (job.completed_at - job.started_at).total_seconds()
            
            processor = self.processors[processor_id]
            processor.total_queue_time += queue_time
            processor.total_execution_time += execution_time_actual
            processor.jobs_completed += 1
            
            self.performance_metrics['total_jobs_completed'] += 1
            
            # Remove from processor's running jobs
            processor.remove_running_job(job.job_id)
            
            # Call callback if provided
            if job.callback:
                try:
                    await job.callback(job.result)
                except Exception as e:
                    logger.error(f"Job callback failed for {job.job_id}", error=str(e))
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            # Handle job failure
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            processor = self.processors[processor_id]
            processor.remove_running_job(job.job_id)
            
            logger.error(f"Job {job.job_id} failed", error=str(e))
    
    async def _estimate_job_runtime(self, algorithm_type: str, problem_data: Dict) -> float:
        """Estimate job runtime based on algorithm and problem size"""
        base_times = {
            'QAOA': 30.0,
            'VQE': 45.0,
            'GROVER': 20.0
        }
        
        base_time = base_times.get(algorithm_type.upper(), 30.0)
        
        # Adjust based on problem size
        problem_size_factor = 1.0
        
        if 'assets' in problem_data:
            n_assets = len(problem_data['assets'])
            problem_size_factor = 1.0 + (n_assets - 5) * 0.1  # +10% per additional asset
        
        return base_time * problem_size_factor
    
    def _get_queue_position(self, job_id: str) -> int:
        """Get position of job in queue"""
        for i, job in enumerate(self.job_queue):
            if job.job_id == job_id:
                return i + 1
        return -1
    
    async def get_scheduler_metrics(self) -> Dict:
        """Get scheduler performance metrics"""
        total_queue_time = sum(p.total_queue_time for p in self.processors.values())
        total_execution_time = sum(p.total_execution_time for p in self.processors.values())
        total_completed = sum(p.jobs_completed for p in self.processors.values())
        
        processor_metrics = {}
        for pid, processor in self.processors.items():
            processor_metrics[pid] = {
                'utilization': processor.get_utilization(),
                'running_jobs': len(processor.running_jobs),
                'jobs_completed': processor.jobs_completed
            }
        
        return {
            'total_jobs_scheduled': self.performance_metrics['total_jobs_scheduled'],
            'total_jobs_completed': total_completed,
            'jobs_in_queue': len(self.job_queue),
            'average_queue_time': total_queue_time / max(total_completed, 1),
            'average_execution_time': total_execution_time / max(total_completed, 1),
            'processor_metrics': processor_metrics
        }
    
    async def shutdown(self):
        """Gracefully shutdown scheduler"""
        logger.info("Shutting down quantum job scheduler")
        self.scheduling_enabled = False
        
        # Cancel all queued jobs
        for job in list(self.job_queue):
            await self.cancel_job(job.job_id)
