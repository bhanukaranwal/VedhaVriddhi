from pydantic import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "metaverse-service"
    service_version: str = "4.0.0"
    service_port: int = 8203
    debug: bool = False
    
    # Virtual Environment Configuration
    max_environments: int = 100
    max_users_per_environment: int = 500
    default_environment_timeout: int = 3600  # 1 hour
    physics_simulation_enabled: bool = True
    spatial_audio_enabled: bool = True
    
    # VR/AR Device Support
    supported_vr_devices: List[str] = [
        "meta_quest_2", "meta_quest_pro", "htc_vive_pro", "valve_index",
        "pico_4", "varjo_aero", "apple_vision_pro"
    ]
    supported_ar_devices: List[str] = [
        "microsoft_hololens", "magic_leap_2", "nreal_light"
    ]
    
    # Session Management
    session_timeout_seconds: int = 3600  # 1 hour
    max_concurrent_sessions: int = 10000
    session_cleanup_interval: int = 300  # 5 minutes
    
    # Performance Optimization
    dynamic_quality_adjustment: bool = True
    foveated_rendering_enabled: bool = True
    adaptive_bitrate_streaming: bool = True
    motion_prediction_enabled: bool = True
    
    # Streaming Configuration
    default_video_codec: str = "h264"
    default_audio_codec: str = "aac"
    max_bitrate_mbps: int = 200
    min_bitrate_mbps: int = 10
    target_latency_ms: int = 20
    
    # Spatial Computing
    hand_tracking_enabled: bool = True
    eye_tracking_enabled: bool = True
    gesture_recognition_enabled: bool = True
    haptic_feedback_enabled: bool = True
    spatial_anchors_enabled: bool = True
    
    # Avatar System
    max_avatars_per_user: int = 10
    avatar_customization_enabled: bool = True
    voice_morphing_enabled: bool = True
    facial_animation_quality: str = "high"  # low, medium, high, ultra
    
    # Security
    session_encryption_enabled: bool = True
    biometric_authentication: bool = False
    parental_controls_enabled: bool = True
    content_filtering_enabled: bool = True
    
    # Database Configuration
    metaverse_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_metaverse"
    redis_url: str = "redis://localhost:6379/13"
    
    # External Services
    avatar_service_url: str = "http://localhost:8203/avatars"
    spatial_service_url: str = "http://localhost:8203/spatial"
    streaming_service_url: str = "http://localhost:8203/streaming"
    
    # Content Delivery
    cdn_endpoint: str = "https://cdn.vedhavriddhi.com/metaverse"
    asset_storage_bucket: str = "vedhavriddhi-metaverse-assets"
    texture_compression_enabled: bool = True
    mesh_optimization_enabled: bool = True
    
    # Analytics
    user_behavior_tracking: bool = True
    performance_analytics: bool = True
    engagement_metrics: bool = True
    
    # Accessibility
    accessibility_features_enabled: bool = True
    subtitle_support: bool = True
    colorblind_support: bool = True
    motion_sickness_reduction: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
