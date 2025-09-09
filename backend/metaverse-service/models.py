from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class VirtualEnvironment(Base):
    __tablename__ = 'virtual_environments'

    id = Column(Integer, primary_key=True, index=True)
    environment_id = Column(String, unique=True, index=True)
    environment_name = Column(String)
    environment_type = Column(String)  # trading_floor, meeting_room, social_space
    max_capacity = Column(Integer)
    current_occupancy = Column(Integer, default=0)
    spatial_dimensions = Column(JSON)  # {width, height, depth}
    physics_enabled = Column(Boolean, default=True)
    audio_enabled = Column(Boolean, default=True)
    haptic_feedback = Column(Boolean, default=False)
    lighting_config = Column(JSON)
    background_music = Column(Boolean, default=False)
    environment_objects = Column(JSON)
    access_permissions = Column(JSON)
    creation_date = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)

class UserAvatar(Base):
    __tablename__ = 'user_avatars'
    
    id = Column(Integer, primary_key=True, index=True)
    avatar_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    display_name = Column(String)
    avatar_type = Column(String)  # professional, casual, futuristic, custom
    appearance_config = Column(JSON)
    height_meters = Column(Float, default=1.75)
    clothing_config = Column(JSON)
    accessories = Column(JSON)
    voice_settings = Column(JSON)
    animation_preferences = Column(JSON)
    interaction_settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)

class VRSession(Base):
    __tablename__ = 'vr_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    environment_id = Column(String, index=True)
    avatar_id = Column(String, index=True)
    device_type = Column(String)  # oculus, vive, pico, etc.
    device_specifications = Column(JSON)
    session_quality = Column(String, default='high')  # low, medium, high, ultra
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    interactions_count = Column(Integer, default=0)
    data_transmitted_mb = Column(Float, default=0.0)
    average_latency_ms = Column(Float, nullable=True)
    motion_sickness_reported = Column(Boolean, default=False)
    user_satisfaction_score = Column(Float, nullable=True)

class SpatialInteraction(Base):
    __tablename__ = 'spatial_interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String, unique=True, index=True)
    session_id = Column(String, index=True)
    user_id = Column(String, index=True)
    interaction_type = Column(String)  # touch, gesture, voice, gaze
    target_object = Column(String, nullable=True)
    interaction_data = Column(JSON)
    success = Column(Boolean, default=True)
    response_time_ms = Column(Float)
    accuracy_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
