import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class MindfulnessRecord:
    """Mindfulness measurement record"""
    record_id: str
    user_id: str
    mindfulness_score: float
    attention_quality: float
    present_moment_awareness: float
    emotional_balance: float
    stress_level: float
    timestamp: datetime

class MindfulnessMonitor:
    """Advanced mindfulness and mental state monitoring"""
    
    def __init__(self):
        self.mindfulness_records: Dict[str, MindfulnessRecord] = {}
        self.user_trends: Dict[str, List[float]] = {}
        
    async def initialize(self):
        """Initialize mindfulness monitor"""
        logger.info("Initializing Mindfulness Monitor")
        
        # Start monitoring loops
        asyncio.create_task(self._mindfulness_trend_analysis())
        
        logger.info("Mindfulness Monitor initialized successfully")
    
    async def record_mindfulness_state(self,
                                     user_id: str,
                                     mindfulness_data: Dict) -> str:
        """Record user mindfulness state"""
        try:
            record_id = f"mindfulness_{user_id}_{datetime.utcnow().timestamp()}"
            
            # Extract mindfulness metrics
            mindfulness_score = mindfulness_data.get('overall_mindfulness', 0.5)
            attention_quality = mindfulness_data.get('attention_focus', 0.5)
            present_awareness = mindfulness_data.get('present_moment', 0.5)
            emotional_balance = mindfulness_data.get('emotional_state', 0.5)
            stress_level = mindfulness_data.get('stress_indicators', 0.5)
            
            # Create record
            record = MindfulnessRecord(
                record_id=record_id,
                user_id=user_id,
                mindfulness_score=mindfulness_score,
                attention_quality=attention_quality,
                present_moment_awareness=present_awareness,
                emotional_balance=emotional_balance,
                stress_level=stress_level,
                timestamp=datetime.utcnow()
            )
            
            self.mindfulness_records[record_id] = record
            
            # Update user trends
            if user_id not in self.user_trends:
                self.user_trends[user_id] = []
            self.user_trends[user_id].append(mindfulness_score)
            
            # Keep only recent trends
            if len(self.user_trends[user_id]) > 100:
                self.user_trends[user_id] = self.user_trends[user_id][-100:]
            
            logger.info(f"Recorded mindfulness state for user {user_id}")
            return record_id
            
        except Exception as e:
            logger.error("Mindfulness recording failed", error=str(e))
            raise
    
    async def analyze_collective_mindfulness(self) -> Dict:
        """Analyze collective mindfulness across all users"""
        try:
            if not self.mindfulness_records:
                return {'collective_mindfulness_available': False}
            
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_records = [
                record for record in self.mindfulness_records.values()
                if record.timestamp > recent_cutoff
            ]
            
            if not recent_records:
                return {'collective_mindfulness_available': False}
            
            # Calculate collective metrics
            avg_mindfulness = np.mean([r.mindfulness_score for r in recent_records])
            avg_attention = np.mean([r.attention_quality for r in recent_records])
            avg_awareness = np.mean([r.present_moment_awareness for r in recent_records])
            avg_emotional_balance = np.mean([r.emotional_balance for r in recent_records])
            avg_stress = np.mean([r.stress_level for r in recent_records])
            
            # Mindfulness coherence
            mindfulness_scores = [r.mindfulness_score for r in recent_records]
            coherence = 1.0 - (np.std(mindfulness_scores) / np.mean(mindfulness_scores)) if np.mean(mindfulness_scores) > 0 else 0.0
            
            return {
                'collective_mindfulness_available': True,
                'collective_metrics': {
                    'average_mindfulness': float(avg_mindfulness),
                    'average_attention_quality': float(avg_attention),
                    'average_present_awareness': float(avg_awareness),
                    'average_emotional_balance': float(avg_emotional_balance),
                    'average_stress_level': float(avg_stress),
                    'mindfulness_coherence': float(max(0.0, coherence))
                },
                'participating_users': len(set(r.user_id for r in recent_records)),
                'total_measurements': len(recent_records),
                'collective_wellbeing_score': float((avg_mindfulness + avg_attention + avg_awareness + avg_emotional_balance + (1 - avg_stress)) / 5),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Collective mindfulness analysis failed", error=str(e))
            return {'collective_mindfulness_available': False, 'error': str(e)}
    
    async def _mindfulness_trend_analysis(self):
        """Analyze mindfulness trends"""
        while True:
            try:
                for user_id, trend_data in self.user_trends.items():
                    if len(trend_data) >= 10:
                        # Calculate trend
                        recent_avg = np.mean(trend_data[-5:])
                        historical_avg = np.mean(trend_data[:-5])
                        
                        if recent_avg > historical_avg + 0.2:
                            logger.info(f"Positive mindfulness trend detected for user {user_id}")
                        elif recent_avg < historical_avg - 0.2:
                            logger.warning(f"Declining mindfulness trend for user {user_id}")
                
                await asyncio.sleep(3600)  # Analyze hourly
                
            except Exception as e:
                logger.error("Mindfulness trend analysis error", error=str(e))
                await asyncio.sleep(1800)
