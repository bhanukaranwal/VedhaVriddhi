import re
import spacy
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()

class NLPEngine:
    """Natural Language Processing engine for voice commands"""
    
    def __init__(self):
        self.nlp_model = None
        self.trading_patterns = {}
        
    async def initialize(self):
        """Initialize NLP engine"""
        logger.info("Initializing NLP Engine")
        
        # Load spaCy model (in production, load actual model)
        try:
            import spacy
            self.nlp_model = spacy.load("en_core_web_sm")
        except:
            logger.warning("SpaCy model not available, using pattern matching")
        
        # Define trading command patterns
        self.trading_patterns = {
            'buy_order': {
                'patterns': [
                    r'buy\s+(\d+)\s+(shares?\s+of\s+)?(\w+)',
                    r'purchase\s+(\d+)\s+(shares?\s+of\s+)?(\w+)',
                    r'get\s+(\d+)\s+(shares?\s+of\s+)?(\w+)'
                ],
                'intent': 'buy',
                'parameters': ['quantity', 'symbol']
            },
            'sell_order': {
                'patterns': [
                    r'sell\s+(\d+)\s+(shares?\s+of\s+)?(\w+)',
                    r'sell\s+all\s+(my\s+)?(\w+)',
                    r'dump\s+(\d+)?\s*(shares?\s+of\s+)?(\w+)'
                ],
                'intent': 'sell',
                'parameters': ['quantity', 'symbol']
            },
            'price_query': {
                'patterns': [
                    r'what\'?s\s+the\s+(current\s+)?price\s+of\s+(\w+)',
                    r'(\w+)\s+price',
                    r'quote\s+(for\s+)?(\w+)'
                ],
                'intent': 'price_query',
                'parameters': ['symbol']
            },
            'portfolio_query': {
                'patterns': [
                    r'show\s+(me\s+)?(my\s+)?portfolio',
                    r'what\'?s\s+my\s+balance',
                    r'portfolio\s+value',
                    r'total\s+value'
                ],
                'intent': 'portfolio_query',
                'parameters': []
            },
            'cancel_orders': {
                'patterns': [
                    r'cancel\s+all\s+(pending\s+)?orders',
                    r'cancel\s+order\s+(\w+)',
                    r'stop\s+all\s+orders'
                ],
                'intent': 'cancel_orders',
                'parameters': ['order_id']
            }
        }
        
        logger.info("NLP Engine initialized with trading patterns")
    
    async def parse_command(self, command_text: str) -> Dict[str, Any]:
        """Parse voice command and extract intent and parameters"""
        try:
            command_text = command_text.lower().strip()
            
            # Try to match against patterns
            for command_type, config in self.trading_patterns.items():
                for pattern in config['patterns']:
                    match = re.search(pattern, command_text, re.IGNORECASE)
                    if match:
                        return await self._extract_parameters(match, config, command_text)
            
            # If no pattern matches, try general NLP
            if self.nlp_model:
                return await self._process_with_nlp(command_text)
            
            return {
                'valid': False,
                'intent': 'unknown',
                'confidence': 0.0,
                'parameters': {},
                'error': 'Command not recognized'
            }
            
        except Exception as e:
            logger.error("Command parsing failed", error=str(e))
            return {
                'valid': False,
                'intent': 'error',
                'confidence': 0.0,
                'parameters': {},
                'error': str(e)
            }
    
    async def _extract_parameters(self, match, config: Dict, command_text: str) -> Dict[str, Any]:
        """Extract parameters from regex match"""
        parameters = {}
        groups = match.groups()
        
        if config['intent'] in ['buy', 'sell']:
            # Extract quantity and symbol
            for i, group in enumerate(groups):
                if group and group.isdigit():
                    parameters['quantity'] = int(group)
                elif group and not group.isdigit() and len(group) <= 5:
                    # Likely a stock symbol
                    parameters['symbol'] = group.upper()
            
            # Handle "all" quantity
            if 'all' in command_text:
                parameters['quantity'] = 'all'
        
        elif config['intent'] == 'price_query':
            # Extract symbol
            for group in groups:
                if group and len(group) <= 5 and group.isalpha():
                    parameters['symbol'] = group.upper()
        
        elif config['intent'] == 'cancel_orders':
            # Extract order ID if specified
            for group in groups:
                if group and (group.isdigit() or len(group) > 5):
                    parameters['order_id'] = group
        
        return {
            'valid': True,
            'intent': config['intent'],
            'confidence': 0.9,  # High confidence for pattern matches
            'parameters': parameters
        }
    
    async def _process_with_nlp(self, command_text: str) -> Dict[str, Any]:
        """Process command using advanced NLP"""
        try:
            doc = self.nlp_model(command_text)
            
            # Extract entities and analyze intent
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Simple intent classification based on keywords
            intent = 'unknown'
            confidence = 0.5
            
            if any(word in command_text for word in ['buy', 'purchase', 'get']):
                intent = 'buy'
                confidence = 0.8
            elif any(word in command_text for word in ['sell', 'dump', 'liquidate']):
                intent = 'sell'
                confidence = 0.8
            elif any(word in command_text for word in ['price', 'quote', 'cost']):
                intent = 'price_query'
                confidence = 0.8
            elif any(word in command_text for word in ['portfolio', 'balance', 'holdings']):
                intent = 'portfolio_query'
                confidence = 0.8
            
            return {
                'valid': confidence > 0.6,
                'intent': intent,
                'confidence': confidence,
                'parameters': {},
                'entities': entities
            }
            
        except Exception as e:
            logger.error("NLP processing failed", error=str(e))
            return {
                'valid': False,
                'intent': 'error',
                'confidence': 0.0,
                'parameters': {},
                'error': str(e)
            }
