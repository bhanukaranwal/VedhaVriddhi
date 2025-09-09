import asyncio
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import structlog
import json

logger = structlog.get_logger()

class QueryType(Enum):
    QUESTION = "question"
    COMMAND = "command"
    REQUEST = "request"
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"

class ResponseType(Enum):
    INFORMATIONAL = "informational"
    ACTIONABLE = "actionable"
    CLARIFICATION = "clarification"
    ERROR = "error"

@dataclass
class Intent:
    """Natural language intent representation"""
    intent_type: str
    confidence: float
    entities: Dict[str, Any]
    parameters: Dict[str, Any]
    context: Dict[str, Any]

@dataclass
class NLQuery:
    """Natural language query structure"""
    query_id: str
    original_text: str
    processed_text: str
    query_type: QueryType
    intent: Intent
    user_id: str
    session_id: str
    timestamp: datetime

@dataclass
class NLResponse:
    """Natural language response structure"""
    response_id: str
    query_id: str
    response_text: str
    response_type: ResponseType
    confidence: float
    supporting_data: Dict[str, Any]
    suggested_actions: List[Dict]
    follow_up_questions: List[str]
    timestamp: datetime

class NaturalLanguageInterface:
    """Advanced Natural Language Processing interface for financial AI"""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.intent_recognizer = IntentRecognizer()
        self.entity_extractor = EntityExtractor()
        self.response_generator = ResponseGenerator()
        self.conversation_manager = ConversationManager()
        
        # Financial domain knowledge
        self.financial_ontology = FinancialOntology()
        self.market_terminology = {}
        self.trading_patterns = {}
        
        # Query history and learning
        self.query_history = []
        self.user_preferences = {}
        self.learning_enabled = True
        
    async def initialize(self):
        """Initialize Natural Language Interface"""
        logger.info("Initializing Natural Language Interface")
        
        await self.query_processor.initialize()
        await self.intent_recognizer.initialize()
        await self.entity_extractor.initialize()
        await self.response_generator.initialize()
        await self.conversation_manager.initialize()
        await self.financial_ontology.initialize()
        
        # Load financial terminology and patterns
        await self._load_financial_knowledge()
        
        logger.info("Natural Language Interface initialized successfully")
    
    async def process_natural_language_query(self, 
                                           query_text: str,
                                           user_id: str,
                                           session_id: str,
                                           context: Optional[Dict] = None) -> NLResponse:
        """Process natural language query and generate response"""
        query_id = f"nlq_{datetime.utcnow().timestamp()}"
        
        try:
            # Preprocess query
            processed_text = await self.query_processor.preprocess(query_text)
            
            # Classify query type
            query_type = await self._classify_query_type(processed_text)
            
            # Recognize intent
            intent = await self.intent_recognizer.recognize_intent(
                processed_text, context or {}
            )
            
            # Create NL query object
            nl_query = NLQuery(
                query_id=query_id,
                original_text=query_text,
                processed_text=processed_text,
                query_type=query_type,
                intent=intent,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
            
            # Generate response
            response = await self._generate_contextual_response(nl_query, context)
            
            # Store query for learning
            if self.learning_enabled:
                self.query_history.append(nl_query)
                await self._update_user_preferences(user_id, nl_query, response)
            
            return response
            
        except Exception as e:
            logger.error("Natural language processing failed", error=str(e))
            return self._generate_error_response(query_id, str(e))
    
    async def process_financial_conversation(self,
                                           messages: List[Dict],
                                           user_id: str,
                                           session_id: str) -> Dict:
        """Process multi-turn financial conversation"""
        try:
            conversation_context = await self.conversation_manager.build_context(
                messages, user_id, session_id
            )
            
            # Process latest message
            latest_message = messages[-1]['content']
            response = await self.process_natural_language_query(
                latest_message, user_id, session_id, conversation_context
            )
            
            # Update conversation state
            await self.conversation_manager.update_conversation_state(
                session_id, messages, response
            )
            
            return {
                'response': response,
                'conversation_context': conversation_context,
                'conversation_flow': 'continuing'
            }
            
        except Exception as e:
            logger.error("Conversation processing failed", error=str(e))
            return {
                'response': self._generate_error_response("conv_error", str(e)),
                'conversation_flow': 'error'
            }
    
    async def explain_financial_concept(self, concept: str, complexity_level: str = "intermediate") -> Dict:
        """Explain financial concepts with adaptive complexity"""
        try:
            # Look up concept in financial ontology
            concept_definition = await self.financial_ontology.get_concept_definition(concept)
            
            if not concept_definition:
                return {
                    'explanation': f"I don't have information about '{concept}'. Could you provide more context?",
                    'confidence': 0.0,
                    'related_concepts': []
                }
            
            # Generate explanation based on complexity level
            explanation = await self._generate_adaptive_explanation(
                concept_definition, complexity_level
            )
            
            # Find related concepts
            related_concepts = await self.financial_ontology.get_related_concepts(concept)
            
            # Generate examples if available
            examples = await self._generate_concept_examples(concept, complexity_level)
            
            return {
                'concept': concept,
                'explanation': explanation,
                'complexity_level': complexity_level,
                'related_concepts': related_concepts,
                'examples': examples,
                'confidence': 0.9
            }
            
        except Exception as e:
            logger.error("Concept explanation failed", error=str(e))
            return {
                'explanation': f"Sorry, I encountered an error explaining '{concept}'.",
                'confidence': 0.0,
                'error': str(e)
            }
    
    async def generate_trading_insights(self, query: str, market_data: Dict) -> Dict:
        """Generate trading insights based on natural language query"""
        try:
            # Extract trading intent and parameters
            trading_intent = await self.intent_recognizer.recognize_trading_intent(query)
            
            if trading_intent.intent_type == "market_analysis":
                insights = await self._generate_market_analysis(trading_intent, market_data)
            elif trading_intent.intent_type == "trade_recommendation":
                insights = await self._generate_trade_recommendations(trading_intent, market_data)
            elif trading_intent.intent_type == "risk_assessment":
                insights = await self._generate_risk_insights(trading_intent, market_data)
            else:
                insights = await self._generate_general_insights(trading_intent, market_data)
            
            # Generate natural language explanation
            explanation = await self.response_generator.generate_trading_explanation(
                insights, trading_intent
            )
            
            return {
                'query': query,
                'intent': trading_intent,
                'insights': insights,
                'explanation': explanation,
                'confidence': insights.get('confidence', 0.7)
            }
            
        except Exception as e:
            logger.error("Trading insight generation failed", error=str(e))
            return {
                'query': query,
                'error': str(e),
                'explanation': "I couldn't generate trading insights for your query.",
                'confidence': 0.0
            }
    
    async def _classify_query_type(self, query_text: str) -> QueryType:
        """Classify the type of natural language query"""
        # Simple rule-based classification - would use ML in practice
        query_lower = query_text.lower()
        
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which']
        command_words = ['buy', 'sell', 'execute', 'cancel', 'update', 'create']
        request_words = ['please', 'could', 'would', 'can', 'help', 'show']
        analysis_words = ['analyze', 'compare', 'evaluate', 'assess', 'review']
        
        if any(word in query_lower for word in question_words):
            return QueryType.QUESTION
        elif any(word in query_lower for word in command_words):
            return QueryType.COMMAND
        elif any(word in query_lower for word in request_words):
            return QueryType.REQUEST
        elif any(word in query_lower for word in analysis_words):
            return QueryType.ANALYSIS
        else:
            return QueryType.CONVERSATION
    
    async def _generate_contextual_response(self, nl_query: NLQuery, context: Optional[Dict]) -> NLResponse:
        """Generate contextual response based on query and context"""
        response_id = f"nlr_{datetime.utcnow().timestamp()}"
        
        # Determine response strategy based on query type and intent
        if nl_query.query_type == QueryType.QUESTION:
            response_text, supporting_data = await self._answer_question(nl_query, context)
            response_type = ResponseType.INFORMATIONAL
            
        elif nl_query.query_type == QueryType.COMMAND:
            response_text, supporting_data = await self._process_command(nl_query, context)
            response_type = ResponseType.ACTIONABLE
            
        elif nl_query.query_type == QueryType.ANALYSIS:
            response_text, supporting_data = await self._perform_analysis(nl_query, context)
            response_type = ResponseType.INFORMATIONAL
            
        else:
            response_text, supporting_data = await self._generate_conversational_response(nl_query, context)
            response_type = ResponseType.INFORMATIONAL
        
        # Generate follow-up questions
        follow_ups = await self._generate_follow_up_questions(nl_query, response_text)
        
        # Generate suggested actions
        suggested_actions = await self._generate_suggested_actions(nl_query, supporting_data)
        
        return NLResponse(
            response_id=response_id,
            query_id=nl_query.query_id,
            response_text=response_text,
            response_type=response_type,
            confidence=nl_query.intent.confidence,
            supporting_data=supporting_data,
            suggested_actions=suggested_actions,
            follow_up_questions=follow_ups,
            timestamp=datetime.utcnow()
        )
    
    async def _load_financial_knowledge(self):
        """Load financial terminology and knowledge"""
        # Mock financial knowledge - would load from databases/APIs
        self.market_terminology = {
            'portfolio': 'A collection of financial investments',
            'bond': 'A debt security issued by corporations or governments',
            'yield': 'The income return on an investment',
            'duration': 'A measure of interest rate sensitivity',
            'spread': 'The difference between two rates or prices'
        }
        
        self.trading_patterns = {
            'buy_low_sell_high': 'Purchase securities when prices are low and sell when high',
            'dollar_cost_averaging': 'Invest fixed amounts regularly regardless of price',
            'momentum_trading': 'Trade based on price movement trends'
        }
    
    def _generate_error_response(self, query_id: str, error_message: str) -> NLResponse:
        """Generate error response"""
        return NLResponse(
            response_id=f"error_{datetime.utcnow().timestamp()}",
            query_id=query_id,
            response_text=f"I encountered an error processing your request: {error_message}",
            response_type=ResponseType.ERROR,
            confidence=0.0,
            supporting_data={'error': error_message},
            suggested_actions=[],
            follow_up_questions=[],
            timestamp=datetime.utcnow()
        )

# Support classes
class QueryProcessor:
    """Process and normalize natural language queries"""
    
    async def initialize(self):
        self.stopwords = {'a', 'an', 'the', 'is', 'are', 'was', 'were'}
        self.financial_synonyms = {
            'stock': ['equity', 'share', 'security'],
            'bond': ['fixed income', 'debt security'],
            'portfolio': ['holdings', 'investments']
        }
    
    async def preprocess(self, text: str) -> str:
        """Preprocess query text"""
        # Basic preprocessing
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        return text

class IntentRecognizer:
    """Recognize user intents from natural language"""
    
    async def initialize(self):
        self.intent_patterns = {
            'portfolio_query': [r'.*portfolio.*balance', r'.*my.*holdings', r'.*investments.*'],
            'price_query': [r'.*price.*of.*', r'.*quote.*for.*', r'.*current.*value.*'],
            'trade_execution': [r'.*buy.*', r'.*sell.*', r'.*purchase.*', r'.*liquidate.*'],
            'market_analysis': [r'.*market.*analysis', r'.*trends.*', r'.*outlook.*']
        }
    
    async def recognize_intent(self, query: str, context: Dict) -> Intent:
        """Recognize intent from query text"""
        # Simple pattern matching - would use ML models in practice
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.match(pattern, query):
                    return Intent(
                        intent_type=intent_type,
                        confidence=0.8,
                        entities={},
                        parameters={},
                        context=context
                    )
        
        # Default intent
        return Intent(
            intent_type='general_query',
            confidence=0.5,
            entities={},
            parameters={},
            context=context
        )
    
    async def recognize_trading_intent(self, query: str) -> Intent:
        """Recognize trading-specific intents"""
        return Intent(
            intent_type='market_analysis',
            confidence=0.7,
            entities={},
            parameters={},
            context={}
        )

class EntityExtractor:
    """Extract entities from natural language"""
    
    async def initialize(self):
        self.entity_patterns = {
            'ticker': r'\b[A-Z]{1,5}\b',
            'currency': r'\b(USD|EUR|GBP|JPY|CAD)\b',
            'amount': r'\$?\d+(?:,\d{3})*(?:\.\d{2})?[kmb]?'
        }
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities

class ResponseGenerator:
    """Generate natural language responses"""
    
    async def initialize(self):
        self.response_templates = {
            'portfolio_query': "Your portfolio currently shows {balance} with {holdings} holdings.",
            'price_query': "The current price of {symbol} is {price}.",
            'general': "Based on your query, here's what I found: {information}"
        }
    
    async def generate_response(self, intent: Intent, data: Dict) -> str:
        """Generate response based on intent and data"""
        template = self.response_templates.get(intent.intent_type, self.response_templates['general'])
        
        try:
            return template.format(**data)
        except KeyError:
            return "I found relevant information but couldn't format it properly."
    
    async def generate_trading_explanation(self, insights: Dict, intent: Intent) -> str:
        """Generate trading explanation"""
        return f"Based on the analysis, {insights.get('summary', 'the market shows mixed signals')}."

class ConversationManager:
    """Manage multi-turn conversations"""
    
    async def initialize(self):
        self.conversation_states = {}
    
    async def build_context(self, messages: List[Dict], user_id: str, session_id: str) -> Dict:
        """Build conversation context"""
        return {
            'message_count': len(messages),
            'user_id': user_id,
            'session_id': session_id,
            'topics_discussed': []
        }
    
    async def update_conversation_state(self, session_id: str, messages: List[Dict], response: NLResponse):
        """Update conversation state"""
        self.conversation_states[session_id] = {
            'last_response': response,
            'message_count': len(messages),
            'updated_at': datetime.utcnow()
        }

class FinancialOntology:
    """Financial domain knowledge ontology"""
    
    async def initialize(self):
        self.concepts = {
            'portfolio': {
                'definition': 'A collection of financial investments held by an individual or institution',
                'category': 'investment',
                'related': ['asset', 'holding', 'allocation']
            },
            'bond': {
                'definition': 'A debt security representing a loan made by an investor to a borrower',
                'category': 'fixed_income',
                'related': ['yield', 'maturity', 'coupon', 'duration']
            }
        }
    
    async def get_concept_definition(self, concept: str) -> Optional[Dict]:
        """Get definition of financial concept"""
        return self.concepts.get(concept.lower())
    
    async def get_related_concepts(self, concept: str) -> List[str]:
        """Get concepts related to given concept"""
        concept_data = self.concepts.get(concept.lower())
        return concept_data.get('related', []) if concept_data else []
