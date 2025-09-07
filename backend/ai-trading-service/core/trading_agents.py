import asyncio
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog

from models import TradeSignal, TradingAgent, AgentPerformanceMetrics, StrategyType

logger = structlog.get_logger()

class BaseTradingAgent:
    """Base class for all trading agents"""
    
    def __init__(self, agent_id: str, agent_type: str, parameters: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.parameters = parameters or {}
        self.performance = {
            'total_signals': 0,
            'successful_signals': 0,
            'returns': [],
            'drawdowns': [],
            'last_update': datetime.utcnow()
        }
        self.active = True
        
    async def process_signal(self, signal: TradeSignal) -> bool:
        """Process incoming trading signal"""
        try:
            # Validate signal
            if not await self._validate_signal(signal):
                return False
            
            # Apply risk management
            adjusted_signal = await self._apply_risk_management(signal)
            
            # Execute trade
            execution_result = await self._execute_trade(adjusted_signal)
            
            # Update performance metrics
            await self._update_performance(execution_result)
            
            return execution_result['success']
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} signal processing failed", error=str(e))
            return False
    
    async def _validate_signal(self, signal: TradeSignal) -> bool:
        """Validate signal quality and parameters"""
        # Check confidence threshold
        min_confidence = self.parameters.get('min_confidence', 0.6)
        if signal.confidence < min_confidence:
            return False
        
        # Check time horizon
        max_horizon = self.parameters.get('max_time_horizon', 1440)  # 24 hours
        if signal.time_horizon_minutes > max_horizon:
            return False
        
        return True
    
    async def _apply_risk_management(self, signal: TradeSignal) -> TradeSignal:
        """Apply risk management rules to signal"""
        # Position sizing based on confidence
        position_multiplier = signal.confidence * self.parameters.get('base_position_size', 1.0)
        
        # Adjust stop loss based on volatility
        if signal.stop_loss and 'volatility_adjustment' in self.parameters:
            volatility_multiplier = self.parameters['volatility_adjustment']
            # Apply volatility-based adjustment (simplified)
            signal.stop_loss = signal.stop_loss * (1 + volatility_multiplier)
        
        return signal
    
    async def _execute_trade(self, signal: TradeSignal) -> Dict[str, Any]:
        """Execute the trade (simulated)"""
        # Simulate trade execution
        await asyncio.sleep(0.1)  # Simulate execution time
        
        # Simulate success rate based on confidence
        success_probability = signal.confidence * 0.8  # 80% max success rate
        success = np.random.random() < success_probability
        
        # Simulate return based on success and market conditions
        if success:
            base_return = np.random.normal(0.01, 0.005)  # 1% mean, 0.5% std
            actual_return = base_return * signal.confidence
        else:
            actual_return = np.random.normal(-0.005, 0.002)  # Small loss
        
        return {
            'success': success,
            'return': actual_return,
            'execution_time': datetime.utcnow(),
            'signal_id': signal.signal_id
        }
    
    async def _update_performance(self, execution_result: Dict[str, Any]):
        """Update agent performance metrics"""
        self.performance['total_signals'] += 1
        
        if execution_result['success']:
            self.performance['successful_signals'] += 1
        
        self.performance['returns'].append(execution_result['return'])
        self.performance['last_update'] = datetime.utcnow()
        
        # Keep only last 1000 returns for memory efficiency
        if len(self.performance['returns']) > 1000:
            self.performance['returns'] = self.performance['returns'][-1000:]
    
    async def get_performance_metrics(self) -> AgentPerformanceMetrics:
        """Calculate and return performance metrics"""
        returns = np.array(self.performance['returns'])
        
        metrics = AgentPerformanceMetrics(
            agent_id=self.agent_id,
            total_signals=self.performance['total_signals'],
            successful_signals=self.performance['successful_signals'],
            last_updated=datetime.utcnow()
        )
        
        if len(returns) > 0:
            metrics.win_rate = self.performance['successful_signals'] / self.performance['total_signals']
            metrics.average_return = float(np.mean(returns))
            
            # Calculate Sharpe ratio (assuming daily returns)
            if np.std(returns) > 0:
                metrics.sharpe_ratio = float(np.mean(returns) / np.std(returns) * np.sqrt(252))
            
            # Calculate maximum drawdown
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            metrics.max_drawdown = float(np.min(drawdowns))
        
        return metrics

class MomentumAgent(BaseTradingAgent):
    """Momentum-based trading agent"""
    
    def __init__(self, agent_id: str, parameters: Dict[str, Any] = None):
        default_params = {
            'lookback_period': 20,
            'momentum_threshold': 0.02,
            'min_confidence': 0.7,
            'base_position_size': 1.0
        }
        if parameters:
            default_params.update(parameters)
        
        super().__init__(agent_id, "momentum", default_params)
    
    async def _validate_signal(self, signal: TradeSignal) -> bool:
        """Momentum-specific signal validation"""
        if not await super()._validate_signal(signal):
            return False
        
        # Only accept momentum-based signals
        if signal.strategy_type != StrategyType.MOMENTUM:
            return False
        
        return True

class ArbitrageAgent(BaseTradingAgent):
    """Arbitrage opportunity trading agent"""
    
    def __init__(self, agent_id: str, parameters: Dict[str, Any] = None):
        default_params = {
            'min_spread': 0.001,  # 0.1% minimum spread
            'max_execution_time': 30,  # 30 seconds max
            'min_confidence': 0.9,  # High confidence required
            'base_position_size': 2.0  # Larger positions for arb
        }
        if parameters:
            default_params.update(parameters)
        
        super().__init__(agent_id, "arbitrage", default_params)
    
    async def _validate_signal(self, signal: TradeSignal) -> bool:
        """Arbitrage-specific validation"""
        if not await super()._validate_signal(signal):
            return False
        
        # Only accept arbitrage signals
        if signal.strategy_type != StrategyType.ARBITRAGE:
            return False
        
        # Check time sensitivity
        if signal.time_horizon_minutes > self.parameters['max_execution_time']:
            return False
        
        return True

class TradingAgentManager:
    """Manages multiple trading agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseTradingAgent] = {}
        self.signal_queue = asyncio.Queue()
        self.running = False
        
    async def initialize(self):
        """Initialize agent manager with default agents"""
        logger.info("Initializing Trading Agent Manager")
        
        # Create default agents
        self.agents['momentum_1'] = MomentumAgent('momentum_1')
        self.agents['arbitrage_1'] = ArbitrageAgent('arbitrage_1')
        
        # Start signal processing
        self.running = True
        asyncio.create_task(self._process_signal_queue())
        
        logger.info(f"Initialized {len(self.agents)} trading agents")
    
    async def _process_signal_queue(self):
        """Process signals from queue"""
        while self.running:
            try:
                # Wait for signal with timeout
                signal = await asyncio.wait_for(self.signal_queue.get(), timeout=1.0)
                
                # Route signal to appropriate agents
                await self._route_signal(signal)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Signal processing error", error=str(e))
                await asyncio.sleep(1)
    
    async def _route_signal(self, signal: TradeSignal):
        """Route signal to appropriate agents"""
        relevant_agents = []
        
        # Route based on strategy type
        for agent in self.agents.values():
            if (signal.strategy_type.value in agent.agent_type or 
                agent.agent_type in signal.strategy_type.value):
                relevant_agents.append(agent)
        
        # If no specific match, send to all active agents
        if not relevant_agents:
            relevant_agents = [agent for agent in self.agents.values() if agent.active]
        
        # Process signal with relevant agents
        tasks = [agent.process_signal(signal) for agent in relevant_agents]
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_executions = sum(1 for result in results if result is True)
            logger.info(f"Signal {signal.signal_id} processed by {successful_executions}/{len(tasks)} agents")
    
    async def process_signal(self, signal: TradeSignal):
        """Add signal to processing queue"""
        await self.signal_queue.put(signal)
    
    async def get_performance_metrics(self) -> List[AgentPerformanceMetrics]:
        """Get performance metrics for all agents"""
        metrics = []
        for agent in self.agents.values():
            agent_metrics = await agent.get_performance_metrics()
            metrics.append(agent_metrics)
        
        return metrics
    
    async def adjust_agent_parameters(self, performance_data: List[AgentPerformanceMetrics]):
        """Adjust agent parameters based on performance"""
        for metrics in performance_data:
            agent = self.agents.get(metrics.agent_id)
            if not agent:
                continue
            
            # Simple performance-based adjustment
            if metrics.sharpe_ratio < 0.5:
                # Poor performance - reduce position size
                agent.parameters['base_position_size'] *= 0.9
                logger.info(f"Reduced position size for agent {metrics.agent_id}")
            elif metrics.sharpe_ratio > 2.0:
                # Excellent performance - increase position size
                agent.parameters['base_position_size'] *= 1.1
                agent.parameters['base_position_size'] = min(agent.parameters['base_position_size'], 3.0)
                logger.info(f"Increased position size for agent {metrics.agent_id}")
    
    async def add_agent(self, agent: BaseTradingAgent):
        """Add new agent to manager"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Added agent {agent.agent_id} of type {agent.agent_type}")
    
    async def remove_agent(self, agent_id: str):
        """Remove agent from manager"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_id}")
    
    async def stop(self):
        """Stop agent manager"""
        self.running = False
        logger.info("Trading Agent Manager stopped")
