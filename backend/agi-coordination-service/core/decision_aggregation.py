import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import structlog

logger = structlog.get_logger()

class DecisionMethod(Enum):
    MAJORITY_VOTING = "majority_voting"
    WEIGHTED_VOTING = "weighted_voting"
    CONSENSUS_BUILDING = "consensus_building"
    EXPERT_JUDGMENT = "expert_judgment"
    BAYESIAN_AGGREGATION = "bayesian_aggregation"

@dataclass
class Decision:
    """Individual agent decision"""
    decision_id: str
    agent_id: str
    decision_value: Any
    confidence: float
    reasoning: str
    supporting_data: Dict
    timestamp: datetime

@dataclass
class AggregatedDecision:
    """Aggregated multi-agent decision"""
    aggregation_id: str
    final_decision: Any
    confidence: float
    method_used: DecisionMethod
    contributing_decisions: List[str]
    consensus_level: float
    decision_quality: float

class DecisionAggregationEngine:
    """Advanced multi-agent decision aggregation system"""
    
    def __init__(self):
        self.individual_decisions: Dict[str, Decision] = {}
        self.aggregated_decisions: Dict[str, AggregatedDecision] = {}
        self.agent_expertise: Dict[str, Dict[str, float]] = {}
        self.decision_history: List[Dict] = []
        
    async def initialize(self):
        """Initialize decision aggregation engine"""
        logger.info("Initializing Decision Aggregation Engine")
        
        # Initialize aggregation methods
        self.aggregation_methods = {
            DecisionMethod.MAJORITY_VOTING: self._majority_voting,
            DecisionMethod.WEIGHTED_VOTING: self._weighted_voting,
            DecisionMethod.CONSENSUS_BUILDING: self._consensus_building,
            DecisionMethod.EXPERT_JUDGMENT: self._expert_judgment,
            DecisionMethod.BAYESIAN_AGGREGATION: self._bayesian_aggregation
        }
        
        logger.info("Decision Aggregation Engine initialized successfully")
    
    async def aggregate_decisions(self,
                                decisions: List[Dict],
                                decision_context: Dict,
                                method: DecisionMethod = DecisionMethod.WEIGHTED_VOTING) -> AggregatedDecision:
        """Aggregate multiple agent decisions"""
        try:
            aggregation_id = f"agg_{datetime.utcnow().timestamp()}"
            
            # Convert to Decision objects
            decision_objects = []
            for decision_data in decisions:
                decision_obj = Decision(
                    decision_id=decision_data['decision_id'],
                    agent_id=decision_data['agent_id'],
                    decision_value=decision_data['decision_value'],
                    confidence=decision_data['confidence'],
                    reasoning=decision_data.get('reasoning', ''),
                    supporting_data=decision_data.get('supporting_data', {}),
                    timestamp=datetime.utcnow()
                )
                decision_objects.append(decision_obj)
                self.individual_decisions[decision_obj.decision_id] = decision_obj
            
            # Select aggregation method based on context and decision types
            optimal_method = await self._select_optimal_method(
                decision_objects, decision_context, method
            )
            
            # Apply aggregation method
            aggregation_function = self.aggregation_methods[optimal_method]
            aggregation_result = await aggregation_function(
                decision_objects, decision_context
            )
            
            # Calculate decision quality metrics
            quality_metrics = await self._calculate_decision_quality(
                decision_objects, aggregation_result
            )
            
            # Create aggregated decision
            aggregated_decision = AggregatedDecision(
                aggregation_id=aggregation_id,
                final_decision=aggregation_result['final_decision'],
                confidence=aggregation_result['confidence'],
                method_used=optimal_method,
                contributing_decisions=[d.decision_id for d in decision_objects],
                consensus_level=aggregation_result['consensus_level'],
                decision_quality=quality_metrics['overall_quality']
            )
            
            self.aggregated_decisions[aggregation_id] = aggregated_decision
            
            # Update decision history
            self.decision_history.append({
                'aggregation_id': aggregation_id,
                'method_used': optimal_method.value,
                'num_decisions': len(decision_objects),
                'final_confidence': aggregation_result['confidence'],
                'timestamp': datetime.utcnow()
            })
            
            logger.info(f"Aggregated {len(decision_objects)} decisions using {optimal_method.value}")
            return aggregated_decision
            
        except Exception as e:
            logger.error("Decision aggregation failed", error=str(e))
            raise
    
    async def _select_optimal_method(self,
                                   decisions: List[Decision],
                                   context: Dict,
                                   preferred_method: DecisionMethod) -> DecisionMethod:
        """Select optimal aggregation method based on context"""
        # Analyze decision characteristics
        confidence_variance = np.var([d.confidence for d in decisions])
        num_decisions = len(decisions)
        decision_complexity = len(str(context))
        
        # Method selection logic
        if num_decisions < 3:
            return DecisionMethod.EXPERT_JUDGMENT
        elif confidence_variance > 0.3:  # High disagreement
            return DecisionMethod.CONSENSUS_BUILDING
        elif context.get('requires_expertise', False):
            return DecisionMethod.EXPERT_JUDGMENT
        elif context.get('uncertainty_high', False):
            return DecisionMethod.BAYESIAN_AGGREGATION
        else:
            return preferred_method
    
    async def _majority_voting(self, decisions: List[Decision], context: Dict) -> Dict:
        """Simple majority voting aggregation"""
        try:
            # Count votes for each decision value
            vote_counts = {}
            total_confidence = 0.0
            
            for decision in decisions:
                decision_str = str(decision.decision_value)
                vote_counts[decision_str] = vote_counts.get(decision_str, 0) + 1
                total_confidence += decision.confidence
            
            # Find majority decision
            majority_decision = max(vote_counts.items(), key=lambda x: x[1])
            final_decision = majority_decision[0]
            
            # Calculate consensus level
            consensus_level = majority_decision[1] / len(decisions)
            
            # Average confidence
            avg_confidence = total_confidence / len(decisions)
            
            return {
                'final_decision': final_decision,
                'confidence': avg_confidence * consensus_level,
                'consensus_level': consensus_level,
                'vote_distribution': vote_counts
            }
            
        except Exception as e:
            logger.error("Majority voting failed", error=str(e))
            return {'final_decision': None, 'confidence': 0.0, 'consensus_level': 0.0}
    
    async def _weighted_voting(self, decisions: List[Decision], context: Dict) -> Dict:
        """Confidence-weighted voting aggregation"""
        try:
            # Group decisions by value and weight by confidence
            decision_weights = {}
            total_weight = 0.0
            
            for decision in decisions:
                decision_str = str(decision.decision_value)
                weight = decision.confidence
                
                if decision_str not in decision_weights:
                    decision_weights[decision_str] = 0.0
                
                decision_weights[decision_str] += weight
                total_weight += weight
            
            # Normalize weights
            for decision_value in decision_weights:
                decision_weights[decision_value] /= total_weight
            
            # Select decision with highest weight
            final_decision = max(decision_weights.items(), key=lambda x: x[1])
            
            # Calculate weighted confidence
            weighted_confidence = final_decision[1]
            
            # Calculate consensus (weight distribution entropy)
            weights = list(decision_weights.values())
            entropy = -sum(w * np.log(w) for w in weights if w > 0)
            max_entropy = np.log(len(weights))
            consensus_level = 1.0 - (entropy / max_entropy if max_entropy > 0 else 0)
            
            return {
                'final_decision': final_decision[0],
                'confidence': weighted_confidence,
                'consensus_level': consensus_level,
                'weight_distribution': decision_weights
            }
            
        except Exception as e:
            logger.error("Weighted voting failed", error=str(e))
            return {'final_decision': None, 'confidence': 0.0, 'consensus_level': 0.0}
    
    async def _consensus_building(self, decisions: List[Decision], context: Dict) -> Dict:
        """Consensus building through iterative refinement"""
        try:
            # Start with weighted average of numerical decisions
            if all(isinstance(d.decision_value, (int, float)) for d in decisions):
                # Numerical consensus
                weighted_sum = sum(d.decision_value * d.confidence for d in decisions)
                total_weight = sum(d.confidence for d in decisions)
                consensus_value = weighted_sum / total_weight if total_weight > 0 else 0
                
                # Calculate agreement level
                deviations = [abs(d.decision_value - consensus_value) for d in decisions]
                avg_deviation = np.mean(deviations)
                max_possible_deviation = max(abs(d.decision_value - consensus_value) for d in decisions) or 1
                consensus_level = 1.0 - (avg_deviation / max_possible_deviation)
                
            else:
                # Categorical consensus - find most supported option
                return await self._weighted_voting(decisions, context)
            
            return {
                'final_decision': consensus_value,
                'confidence': total_weight / len(decisions),
                'consensus_level': max(0.0, consensus_level),
                'convergence_iterations': 3  # Mock iteration count
            }
            
        except Exception as e:
            logger.error("Consensus building failed", error=str(e))
            return {'final_decision': None, 'confidence': 0.0, 'consensus_level': 0.0}
    
    async def _expert_judgment(self, decisions: List[Decision], context: Dict) -> Dict:
        """Expert judgment based aggregation"""
        try:
            decision_domain = context.get('domain', 'general')
            
            # Weight decisions by agent expertise in domain
            weighted_decisions = []
            total_expertise_weight = 0.0
            
            for decision in decisions:
                # Get agent expertise in this domain
                agent_expertise = self.agent_expertise.get(
                    decision.agent_id, {}
                ).get(decision_domain, 0.5)  # Default 0.5 expertise
                
                # Combine expertise with confidence
                expert_weight = agent_expertise * decision.confidence
                weighted_decisions.append((decision, expert_weight))
                total_expertise_weight += expert_weight
            
            # Select decision from most expert agent or weighted combination
            if context.get('single_expert', False):
                # Select single best expert decision
                best_decision, best_weight = max(weighted_decisions, key=lambda x: x[1])
                final_decision = best_decision.decision_value
                confidence = best_weight
            else:
                # Weighted combination of expert decisions
                if all(isinstance(wd[0].decision_value, (int, float)) for wd in weighted_decisions):
                    weighted_sum = sum(wd[0].decision_value * wd[1] for wd in weighted_decisions)
                    final_decision = weighted_sum / total_expertise_weight if total_expertise_weight > 0 else 0
                    confidence = total_expertise_weight / len(decisions)
                else:
                    # For categorical decisions, use expert-weighted voting
                    decision_weights = {}
                    for decision, weight in weighted_decisions:
                        decision_str = str(decision.decision_value)
                        decision_weights[decision_str] = decision_weights.get(decision_str, 0.0) + weight
                    
                    final_decision = max(decision_weights.items(), key=lambda x: x[1])[0]
                    confidence = max(decision_weights.values()) / total_expertise_weight if total_expertise_weight > 0 else 0
            
            # Calculate consensus based on expert agreement
            expert_weights = [wd[1] for wd in weighted_decisions]
            consensus_level = 1.0 - (np.std(expert_weights) / np.mean(expert_weights)) if np.mean(expert_weights) > 0 else 0
            
            return {
                'final_decision': final_decision,
                'confidence': confidence,
                'consensus_level': max(0.0, consensus_level),
                'expert_weights': {wd[0].agent_id: wd[1] for wd in weighted_decisions}
            }
            
        except Exception as e:
            logger.error("Expert judgment failed", error=str(e))
            return {'final_decision': None, 'confidence': 0.0, 'consensus_level': 0.0}
    
    async def _bayesian_aggregation(self, decisions: List[Decision], context: Dict) -> Dict:
        """Bayesian decision aggregation with uncertainty"""
        try:
            # For numerical decisions, use Bayesian model averaging
            if all(isinstance(d.decision_value, (int, float)) for d in decisions):
                # Treat each decision as a Gaussian with confidence-based variance
                decision_values = [d.decision_value for d in decisions]
                confidences = [d.confidence for d in decisions]
                
                # Calculate precision (inverse variance) from confidence
                precisions = [c * 10 for c in confidences]  # Scale confidence to precision
                
                # Bayesian weighted average
                weighted_sum = sum(val * prec for val, prec in zip(decision_values, precisions))
                total_precision = sum(precisions)
                
                final_decision = weighted_sum / total_precision if total_precision > 0 else np.mean(decision_values)
                
                # Posterior confidence based on total precision
                posterior_variance = 1.0 / total_precision if total_precision > 0 else 1.0
                confidence = 1.0 / (1.0 + posterior_variance)  # Convert variance to confidence
                
                # Calculate consensus based on prediction interval overlap
                consensus_level = await self._calculate_bayesian_consensus(
                    decision_values, confidences
                )
                
            else:
                # For categorical decisions, use Bayesian categorical aggregation
                return await self._weighted_voting(decisions, context)
            
            return {
                'final_decision': final_decision,
                'confidence': confidence,
                'consensus_level': consensus_level,
                'posterior_variance': posterior_variance,
                'bayesian_evidence': len(decisions)
            }
            
        except Exception as e:
            logger.error("Bayesian aggregation failed", error=str(e))
            return {'final_decision': None, 'confidence': 0.0, 'consensus_level': 0.0}
    
    async def _calculate_bayesian_consensus(self, values: List[float], confidences: List[float]) -> float:
        """Calculate Bayesian consensus level"""
        if len(values) < 2:
            return 1.0
        
        # Calculate pairwise prediction interval overlaps
        overlaps = []
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                # Create confidence intervals
                margin_i = 2.0 / (confidences[i] * 10)  # Rough confidence interval
                margin_j = 2.0 / (confidences[j] * 10)
                
                interval_i = (values[i] - margin_i, values[i] + margin_i)
                interval_j = (values[j] - margin_j, values[j] + margin_j)
                
                # Calculate overlap
                overlap_start = max(interval_i[0], interval_j[0])
                overlap_end = min(interval_i[1], interval_j[1])
                overlap = max(0, overlap_end - overlap_start)
                
                # Normalize by average interval size
                avg_interval_size = ((interval_i[1] - interval_i[0]) + (interval_j[1] - interval_j[0])) / 2
                normalized_overlap = overlap / avg_interval_size if avg_interval_size > 0 else 0
                
                overlaps.append(normalized_overlap)
        
        return np.mean(overlaps) if overlaps else 0.0
    
    async def _calculate_decision_quality(self, 
                                        individual_decisions: List[Decision],
                                        aggregation_result: Dict) -> Dict:
        """Calculate quality metrics for aggregated decision"""
        try:
            # Diversity of input decisions
            if all(isinstance(d.decision_value, (int, float)) for d in individual_decisions):
                values = [d.decision_value for d in individual_decisions]
                diversity = np.std(values) / (np.mean(values) + 1e-6)  # Coefficient of variation
            else:
                unique_decisions = len(set(str(d.decision_value) for d in individual_decisions))
                diversity = unique_decisions / len(individual_decisions)
            
            # Confidence consistency
            confidences = [d.confidence for d in individual_decisions]
            confidence_consistency = 1.0 - np.std(confidences)
            
            # Information richness (based on supporting data)
            total_data_points = sum(len(d.supporting_data) for d in individual_decisions)
            information_richness = min(total_data_points / (len(individual_decisions) * 10), 1.0)  # Normalize
            
            # Overall quality score
            overall_quality = (
                diversity * 0.3 +
                confidence_consistency * 0.3 +
                information_richness * 0.2 +
                aggregation_result.get('consensus_level', 0.0) * 0.2
            )
            
            return {
                'overall_quality': overall_quality,
                'diversity_score': diversity,
                'confidence_consistency': confidence_consistency,
                'information_richness': information_richness,
                'consensus_level': aggregation_result.get('consensus_level', 0.0)
            }
            
        except Exception as e:
            logger.error("Decision quality calculation failed", error=str(e))
            return {'overall_quality': 0.5}
    
    async def update_agent_expertise(self, agent_id: str, domain: str, performance_score: float):
        """Update agent expertise based on decision performance"""
        if agent_id not in self.agent_expertise:
            self.agent_expertise[agent_id] = {}
        
        current_expertise = self.agent_expertise[agent_id].get(domain, 0.5)
        # Exponential moving average update
        updated_expertise = 0.8 * current_expertise + 0.2 * performance_score
        self.agent_expertise[agent_id][domain] = max(0.0, min(1.0, updated_expertise))
    
    async def get_aggregation_analytics(self) -> Dict:
        """Get comprehensive decision aggregation analytics"""
        try:
            total_aggregations = len(self.aggregated_decisions)
            
            if total_aggregations == 0:
                return {'analytics_available': False}
            
            # Method usage statistics
            method_usage = {}
            for decision in self.aggregated_decisions.values():
                method = decision.method_used.value
                method_usage[method] = method_usage.get(method, 0) + 1
            
            # Quality statistics
            quality_scores = [d.decision_quality for d in self.aggregated_decisions.values()]
            avg_quality = np.mean(quality_scores)
            
            # Consensus statistics
            consensus_levels = [d.consensus_level for d in self.aggregated_decisions.values()]
            avg_consensus = np.mean(consensus_levels)
            
            # Confidence statistics
            confidences = [d.confidence for d in self.aggregated_decisions.values()]
            avg_confidence = np.mean(confidences)
            
            return {
                'analytics_available': True,
                'total_aggregations': total_aggregations,
                'method_usage': method_usage,
                'quality_metrics': {
                    'average_quality': avg_quality,
                    'average_consensus': avg_consensus,
                    'average_confidence': avg_confidence
                },
                'agent_expertise_domains': len(set().union(
                    *[domains.keys() for domains in self.agent_expertise.values()]
                )) if self.agent_expertise else 0,
                'total_individual_decisions': len(self.individual_decisions)
            }
            
        except Exception as e:
            logger.error("Aggregation analytics generation failed", error=str(e))
            return {'analytics_available': False, 'error': str(e)}
