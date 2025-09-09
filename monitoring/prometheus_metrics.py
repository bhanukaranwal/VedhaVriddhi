from prometheus_client import Counter, Gauge, Histogram, Summary, Info
import time
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

# System-wide metrics
system_info = Info('vedhavriddhi_system_info', 'VedhaVriddhi system information')
system_uptime = Gauge('vedhavriddhi_system_uptime_seconds', 'System uptime in seconds')
system_health_score = Gauge('vedhavriddhi_system_health_score', 'Overall system health score (0-1)')

# Quantum Computing Service Metrics
quantum_jobs_total = Counter('quantum_jobs_total', 'Total quantum jobs submitted', ['algorithm', 'status'])
quantum_jobs_duration = Histogram('quantum_job_duration_seconds', 'Quantum job execution time', ['algorithm'])
quantum_advantage_factor = Histogram('quantum_advantage_factor', 'Quantum advantage over classical methods')
quantum_error_rate = Gauge('quantum_error_rate', 'Quantum computation error rate', ['backend'])
quantum_active_jobs = Gauge('quantum_active_jobs', 'Currently running quantum jobs')

# AGI Service Metrics  
agi_agents_active = Gauge('agi_agents_active', 'Number of active AGI agents')
agi_reasoning_requests = Counter('agi_reasoning_requests_total', 'AGI reasoning requests', ['reasoning_type'])
agi_decision_quality = Histogram('agi_decision_quality_score', 'AGI decision quality scores')
agi_collective_intelligence = Gauge('agi_collective_intelligence_level', 'Collective intelligence level (0-1)')
agi_response_time = Histogram('agi_response_time_seconds', 'AGI response times', ['agent_type'])

# Consciousness Gateway Metrics
global_consciousness_level = Gauge('global_consciousness_level', 'Global consciousness level (0-1)')
wisdom_synthesis_events = Counter('wisdom_synthesis_events_total', 'Wisdom synthesis events')
collective_insights_generated = Counter('collective_insights_generated_total', 'Collective insights generated')
mindfulness_score = Gauge('collective_mindfulness_score', 'Collective mindfulness score (0-1)')
consciousness_evolution_rate = Gauge('consciousness_evolution_rate', 'Rate of consciousness evolution')

# Planetary Impact Metrics
planetary_health_score = Gauge('planetary_health_score', 'Overall planetary health score (0-1)')
carbon_footprint_total = Gauge('carbon_footprint_tons_co2e', 'Total carbon footprint in tons CO2e')
carbon_offsets_total = Gauge('carbon_offsets_tons_co2e', 'Total carbon offsets in tons CO2e')
biodiversity_index = Gauge('biodiversity_index', 'Biodiversity index score')
ecosystem_projects_active = Gauge('ecosystem_projects_active', 'Number of active ecosystem projects')
regeneration_rate = Gauge('planetary_regeneration_rate', 'Planetary regeneration rate (0-1)')

# DeFi Service Metrics
defi_protocols_connected = Gauge('defi_protocols_connected', 'Number of connected DeFi protocols')
defi_total_value_locked = Gauge('defi_total_value_locked_usd', 'Total value locked in USD')
yield_strategies_active = Gauge('yield_strategies_active', 'Number of active yield strategies')
cross_chain_transfers = Counter('cross_chain_transfers_total', 'Cross-chain transfers', ['source_chain', 'target_chain'])
defi_transaction_volume = Counter('defi_transaction_volume_usd', 'DeFi transaction volume in USD')

# Neural Interface Metrics
biometric_authentications = Counter('biometric_authentications_total', 'Biometric authentications', ['type', 'result'])
neural_interface_sessions = Gauge('neural_interface_sessions_active', 'Active neural interface sessions')
stress_level_average = Gauge('user_stress_level_average', 'Average user stress level (0-1)')
emotional_coherence = Gauge('collective_emotional_coherence', 'Collective emotional coherence (0-1)')

# Metaverse Service Metrics
vr_sessions_active = Gauge('vr_sessions_active', 'Active VR sessions')
virtual_environments_loaded = Gauge('virtual_environments_loaded', 'Loaded virtual environments')
avatar_interactions = Counter('avatar_interactions_total', 'Avatar interactions', ['interaction_type'])
vr_session_quality = Histogram('vr_session_quality_score', 'VR session quality scores')

# Climate Intelligence Metrics
climate_data_points = Counter('climate_data_points_processed_total', 'Climate data points processed')
tipping_point_alerts = Counter('tipping_point_alerts_total', 'Climate tipping point alerts', ['indicator'])
conservation_funding_usd = Gauge('conservation_funding_usd', 'Conservation funding in USD')
species_monitored = Gauge('species_monitored_count', 'Number of species being monitored')

# Performance Metrics
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['service', 'endpoint', 'method'])
api_requests_total = Counter('api_requests_total', 'Total API requests', ['service', 'endpoint', 'method', 'status'])
memory_usage_bytes = Gauge('memory_usage_bytes', 'Memory usage in bytes', ['service'])
cpu_usage_percent = Gauge('cpu_usage_percent', 'CPU usage percentage', ['service'])
database_connections = Gauge('database_connections_active', 'Active database connections', ['service'])

class VedhaVriddhiMetricsCollector:
    """Centralized metrics collection for VedhaVriddhi system"""
    
    def __init__(self):
        self.start_time = time.time()
        self._setup_system_info()
        
    def _setup_system_info(self):
        """Set up system information metrics"""
        system_info.info({
            'version': '4.0.0',
            'phase': 'Universal Financial Intelligence',
            'quantum_enabled': 'true',
            'consciousness_active': 'true',
            'planetary_regeneration': 'true'
        })
    
    def record_quantum_job(self, algorithm: str, duration: float, advantage_factor: float, success: bool):
        """Record quantum job metrics"""
        status = 'success' if success else 'failed'
        quantum_jobs_total.labels(algorithm=algorithm, status=status).inc()
        
        if success:
            quantum_jobs_duration.labels(algorithm=algorithm).observe(duration)
            quantum_advantage_factor.observe(advantage_factor)
    
    def update_consciousness_metrics(self, level: float, wisdom_events: int, insights: int):
        """Update consciousness-related metrics"""
        global_consciousness_level.set(level)
        wisdom_synthesis_events.inc(wisdom_events)
        collective_insights_generated.inc(insights)
    
    def update_planetary_health(self, health_score: float, carbon_footprint: float, 
                              carbon_offsets: float, biodiversity: float):
        """Update planetary health metrics"""
        planetary_health_score.set(health_score)
        carbon_footprint_total.set(carbon_footprint)
        carbon_offsets_total.set(carbon_offsets)
        biodiversity_index.set(biodiversity)
    
    def record_api_request(self, service: str, endpoint: str, method: str, 
                          duration: float, status_code: int):
        """Record API request metrics"""
        status = 'success' if 200 <= status_code < 300 else 'error'
        
        api_requests_total.labels(
            service=service, 
            endpoint=endpoint, 
            method=method, 
            status=status
        ).inc()
        
        api_request_duration.labels(
            service=service, 
            endpoint=endpoint, 
            method=method
        ).observe(duration)
    
    def update_system_health(self):
        """Update overall system health metrics"""
        current_uptime = time.time() - self.start_time
        system_uptime.set(current_uptime)
        
        # Calculate composite health score
        health_components = [
            planetary_health_score._value._value if planetary_health_score._value._value else 0.8,
            global_consciousness_level._value._value if global_consciousness_level._value._value else 0.7,
            min(agi_agents_active._value._value / 10.0, 1.0) if agi_agents_active._value._value else 0.8,
            min(quantum_active_jobs._value._value / 50.0, 1.0) if quantum_active_jobs._value._value else 0.9
        ]
        
        overall_health = sum(health_components) / len(health_components)
        system_health_score.set(overall_health)

# Global metrics collector instance
metrics_collector = VedhaVriddhiMetricsCollector()

def get_metrics_collector() -> VedhaVriddhiMetricsCollector:
    """Get the global metrics collector instance"""
    return metrics_collector
