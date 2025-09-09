import asyncio
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog

logger = structlog.get_logger()

class ResourceType(Enum):
    QUANTUM_PROCESSOR = "quantum_processor"
    CLASSICAL_CPU = "classical_cpu"
    GPU = "gpu"
    MEMORY = "memory"
    NETWORK_BANDWIDTH = "network_bandwidth"

@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    allocation_id: str
    resource_type: ResourceType
    amount: int
    user_id: str
    job_id: str
    allocated_at: datetime
    expires_at: Optional[datetime] = None
    priority: int = 5

class QuantumResourceManager:
    """Advanced quantum resource allocation and optimization"""
    
    def __init__(self):
        self.resource_pools = {
            ResourceType.QUANTUM_PROCESSOR: 1000,  # 1000 quantum processing units
            ResourceType.CLASSICAL_CPU: 10000,     # 10000 CPU cores
            ResourceType.GPU: 500,                 # 500 GPU units
            ResourceType.MEMORY: 100000,           # 100TB memory
            ResourceType.NETWORK_BANDWIDTH: 10000  # 10Gbps
        }
        
        self.allocated_resources = {resource_type: 0 for resource_type in ResourceType}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.resource_queue: List[Dict] = []
        
    async def initialize(self):
        """Initialize resource manager"""
        logger.info("Initializing Quantum Resource Manager")
        
        # Start background tasks
        asyncio.create_task(self._resource_optimization_loop())
        asyncio.create_task(self._allocation_cleanup_loop())
        
        logger.info("Quantum Resource Manager initialized successfully")
    
    async def allocate_resources(self, 
                               user_id: str,
                               job_id: str,
                               resource_requirements: Dict[ResourceType, int],
                               priority: int = 5,
                               duration_minutes: int = 60) -> str:
        """Allocate resources for quantum job"""
        try:
            allocation_id = f"alloc_{datetime.utcnow().timestamp()}"
            
            # Check resource availability
            can_allocate = True
            for resource_type, required_amount in resource_requirements.items():
                available = self.resource_pools[resource_type] - self.allocated_resources[resource_type]
                if available < required_amount:
                    can_allocate = False
                    break
            
            if not can_allocate:
                # Queue the request
                await self._queue_resource_request(user_id, job_id, resource_requirements, priority)
                return "queued"
            
            # Allocate resources
            expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            for resource_type, amount in resource_requirements.items():
                allocation = ResourceAllocation(
                    allocation_id=f"{allocation_id}_{resource_type.value}",
                    resource_type=resource_type,
                    amount=amount,
                    user_id=user_id,
                    job_id=job_id,
                    allocated_at=datetime.utcnow(),
                    expires_at=expires_at,
                    priority=priority
                )
                
                self.allocations[allocation.allocation_id] = allocation
                self.allocated_resources[resource_type] += amount
            
            logger.info(f"Allocated resources for job {job_id}: {resource_requirements}")
            return allocation_id
            
        except Exception as e:
            logger.error("Resource allocation failed", error=str(e))
            raise
    
    async def release_resources(self, allocation_id: str) -> bool:
        """Release allocated resources"""
        try:
            # Find all allocations with this base ID
            to_release = [
                alloc for alloc in self.allocations.values()
                if alloc.allocation_id.startswith(allocation_id)
            ]
            
            if not to_release:
                return False
            
            for allocation in to_release:
                self.allocated_resources[allocation.resource_type] -= allocation.amount
                del self.allocations[allocation.allocation_id]
            
            logger.info(f"Released resources for allocation {allocation_id}")
            
            # Process queued requests
            await self._process_resource_queue()
            
            return True
            
        except Exception as e:
            logger.error("Resource release failed", error=str(e))
            return False
    
    async def _queue_resource_request(self, user_id: str, job_id: str, 
                                    requirements: Dict, priority: int):
        """Queue resource request when resources unavailable"""
        request = {
            'user_id': user_id,
            'job_id': job_id,
            'requirements': requirements,
            'priority': priority,
            'queued_at': datetime.utcnow()
        }
        
        # Insert based on priority
        inserted = False
        for i, queued_request in enumerate(self.resource_queue):
            if priority > queued_request['priority']:
                self.resource_queue.insert(i, request)
                inserted = True
                break
        
        if not inserted:
            self.resource_queue.append(request)
        
        logger.info(f"Queued resource request for job {job_id}")
    
    async def _process_resource_queue(self):
        """Process queued resource requests"""
        processed = []
        
        for request in self.resource_queue:
            # Check if we can now fulfill this request
            can_fulfill = True
            for resource_type, required_amount in request['requirements'].items():
                available = self.resource_pools[resource_type] - self.allocated_resources[resource_type]
                if available < required_amount:
                    can_fulfill = False
                    break
            
            if can_fulfill:
                # Allocate resources
                allocation_id = await self.allocate_resources(
                    request['user_id'],
                    request['job_id'],
                    request['requirements'],
                    request['priority']
                )
                
                if allocation_id != "queued":
                    processed.append(request)
        
        # Remove processed requests
        for request in processed:
            self.resource_queue.remove(request)
    
    async def _resource_optimization_loop(self):
        """Optimize resource allocation continuously"""
        while True:
            try:
                # Optimize resource distribution
                await self._optimize_resource_distribution()
                await asyncio.sleep(30)  # Optimize every 30 seconds
                
            except Exception as e:
                logger.error("Resource optimization error", error=str(e))
                await asyncio.sleep(60)
    
    async def _optimize_resource_distribution(self):
        """Optimize current resource distribution"""
        # Analyze current allocations
        resource_utilization = {}
        for resource_type in ResourceType:
            total = self.resource_pools[resource_type]
            allocated = self.allocated_resources[resource_type]
            resource_utilization[resource_type] = allocated / total if total > 0 else 0
        
        # Log utilization metrics
        high_utilization = [
            rt.value for rt, util in resource_utilization.items() 
            if util > 0.9
        ]
        
        if high_utilization:
            logger.warning(f"High resource utilization: {high_utilization}")
    
    async def _allocation_cleanup_loop(self):
        """Clean up expired allocations"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_allocations = []
                
                for allocation_id, allocation in self.allocations.items():
                    if allocation.expires_at and current_time > allocation.expires_at:
                        expired_allocations.append(allocation_id)
                
                # Clean up expired allocations
                for allocation_id in expired_allocations:
                    await self.release_resources(allocation_id.split('_')[0])
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Allocation cleanup error", error=str(e))
                await asyncio.sleep(120)
    
    async def get_resource_status(self) -> Dict:
        """Get comprehensive resource status"""
        status = {}
        
        for resource_type in ResourceType:
            total = self.resource_pools[resource_type]
            allocated = self.allocated_resources[resource_type]
            available = total - allocated
            utilization = allocated / total if total > 0 else 0
            
            status[resource_type.value] = {
                'total': total,
                'allocated': allocated,
                'available': available,
                'utilization_percentage': utilization * 100
            }
        
        return {
            'resource_pools': status,
            'active_allocations': len(self.allocations),
            'queued_requests': len(self.resource_queue),
            'total_jobs_served': len(set(
                alloc.job_id for alloc in self.allocations.values()
            ))
        }
