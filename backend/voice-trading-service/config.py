from pydantic import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "voice-trading-service"
    service_version: str = "3.0.0"
    service_port: int = 8104
    debug: bool = False
    
    # Speech Recognition Configuration
    speech_recognition_provider: str = "google"  # google, aws, azure, openai
    google_speech_api_key: str = ""
    aws_transcribe_region: str = "us-east-1"
    azure_speech_key: str = ""
    azure_speech_region: str = ""
    
    # NLP Configuration
    nlp_model_provider: str = "spacy"  # spacy, transformers, openai
    spacy_model: str = "en_core_web_sm"
    openai_api_key: str = ""
    
    # Voice Command Settings
    max_audio_file_size_mb: int = 50
    supported_audio_formats: List[str] = ["wav", "mp3", "flac", "ogg"]
    command_timeout_seconds: int = 30
    min_confidence_threshold: float = 0.7
    
    # Session Management
    max_concurrent_sessions: int = 100
    session_timeout_minutes: int = 15
    max_commands_per_session: int = 50
    
    # Trading Command Configuration
    enable_high_value_voice_trading: bool = False  # Require confirmation for large trades
    max_voice_trade_amount: float = 100000.0  # Max trade amount without confirmation
    
    # Language Support
    supported_languages: List[str] = ["en-US", "en-GB", "en-AU", "en-IN"]
    default_language: str = "en-US"
    
    # Voice Patterns and Intents
    trading_intents: Dict[str, List[str]] = {
        "buy": ["buy", "purchase", "acquire", "get", "long"],
        "sell": ["sell", "dispose", "liquidate", "short", "dump"],
        "query": ["what", "show", "display", "tell", "how much"],
        "cancel": ["cancel", "stop", "abort", "kill"],
        "help": ["help", "assist", "support", "guide"]
    }
    
    # Audio Processing
    sample_rate: int = 16000
    audio_chunk_duration_ms: int = 1000
    noise_reduction_enabled: bool = True
    
    # External Services
    trading_engine_url: str = "http://localhost:8080"
    portfolio_service_url: str = "http://localhost:8002"
    market_data_url: str = "http://localhost:8001"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
