import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
import json

logger = structlog.get_logger()

class EnvironmentType(Enum):
    TRADING_FLOOR = "trading_floor"
    ANALYTICS_LAB = "analytics_lab" 
    MEETING_ROOM = "meeting_room"
    SOCIAL_SPACE = "social_space"
    EDUCATIONAL = "educational"

@dataclass
class VirtualEnvironmentConfig:
    """Virtual environment configuration"""
    environment_id: str
    name: str
    environment_type: EnvironmentType
    max_capacity: int
    spatial_dimensions: Tuple[float, float, float]  # width, height, depth
    physics_enabled: bool = True
    audio_enabled: bool = True
    haptic_feedback: bool = False
    lighting_preset: str = "professional"
    background_music: bool = False

@dataclass
class EnvironmentObject:
    """3D objects in virtual environment"""
    object_id: str
    object_type: str
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    interactive: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)

class VirtualTradingEnvironment:
    """Manages virtual trading environments and 3D spaces"""
    
    def __init__(self):
        self.environments: Dict[str, VirtualEnvironmentConfig] = {}
        self.environment_objects: Dict[str, List[EnvironmentObject]] = {}
        self.active_sessions: Dict[str, Dict] = {}
        self.physics_engine = PhysicsEngine()
        self.audio_manager = AudioManager()
        
    async def initialize(self):
        """Initialize virtual environment system"""
        logger.info("Initializing Virtual Trading Environment")
        
        await self.physics_engine.initialize()
        await self.audio_manager.initialize()
        
        # Create default environments
        await self._create_default_environments()
        
        logger.info("Virtual Trading Environment initialized successfully")
    
    async def _create_default_environments(self):
        """Create default virtual environments"""
        default_environments = [
            {
                'environment_id': 'nyse_floor',
                'name': 'NYSE Trading Floor',
                'environment_type': EnvironmentType.TRADING_FLOOR,
                'max_capacity': 200,
                'spatial_dimensions': (100.0, 15.0, 80.0),  # Large trading floor
                'lighting_preset': 'bright_professional'
            },
            {
                'environment_id': 'quantum_lab',
                'name': 'Quantum Analytics Laboratory',
                'environment_type': EnvironmentType.ANALYTICS_LAB,
                'max_capacity': 50,
                'spatial_dimensions': (50.0, 10.0, 30.0),
                'physics_enabled': True,
                'haptic_feedback': True,
                'lighting_preset': 'futuristic_blue'
            },
            {
                'environment_id': 'executive_boardroom',
                'name': 'Executive Boardroom',
                'environment_type': EnvironmentType.MEETING_ROOM,
                'max_capacity': 20,
                'spatial_dimensions': (15.0, 8.0, 12.0),
                'audio_enabled': True,
                'lighting_preset': 'warm_professional'
            },
            {
                'environment_id': 'defi_plaza',
                'name': 'DeFi Protocol Plaza',
                'environment_type': EnvironmentType.SOCIAL_SPACE,
                'max_capacity': 500,
                'spatial_dimensions': (150.0, 25.0, 150.0),
                'background_music': True,
                'lighting_preset': 'cyberpunk_neon'
            }
        ]
        
        for env_config in default_environments:
            await self.create_environment(env_config)
    
    async def create_environment(self, config: Dict) -> str:
        """Create new virtual environment"""
        try:
            environment_config = VirtualEnvironmentConfig(
                environment_id=config['environment_id'],
                name=config['name'],
                environment_type=config['environment_type'],
                max_capacity=config['max_capacity'],
                spatial_dimensions=config['spatial_dimensions'],
                physics_enabled=config.get('physics_enabled', True),
                audio_enabled=config.get('audio_enabled', True),
                haptic_feedback=config.get('haptic_feedback', False),
                lighting_preset=config.get('lighting_preset', 'professional'),
                background_music=config.get('background_music', False)
            )
            
            self.environments[config['environment_id']] = environment_config
            self.environment_objects[config['environment_id']] = []
            
            # Create environment-specific objects
            await self._populate_environment_objects(config['environment_id'])
            
            logger.info(f"Created virtual environment: {config['name']}")
            return config['environment_id']
            
        except Exception as e:
            logger.error("Failed to create virtual environment", error=str(e))
            raise
    
    async def _populate_environment_objects(self, environment_id: str):
        """Populate environment with appropriate 3D objects"""
        environment = self.environments.get(environment_id)
        if not environment:
            return
        
        objects = []
        
        if environment.environment_type == EnvironmentType.TRADING_FLOOR:
            # Trading floor objects
            objects.extend([
                EnvironmentObject(
                    object_id=f"{environment_id}_ticker_board",
                    object_type="ticker_board",
                    position=(0.0, 8.0, -40.0),  # Center wall, elevated
                    rotation=(0.0, 0.0, 0.0),
                    scale=(20.0, 5.0, 0.5),
                    interactive=True,
                    properties={'display_type': 'live_market_data', 'refresh_rate': 1.0}
                ),
                EnvironmentObject(
                    object_id=f"{environment_id}_trading_desk_01",
                    object_type="trading_desk",
                    position=(-20.0, 0.0, 10.0),
                    rotation=(0.0, 0.0, 0.0),
                    scale=(4.0, 1.0, 2.0),
                    interactive=True,
                    properties={'desk_type': 'multi_monitor', 'user_capacity': 4}
                )
            ])
            
        elif environment.environment_type == EnvironmentType.ANALYTICS_LAB:
            # Analytics lab objects
            objects.extend([
                EnvironmentObject(
                    object_id=f"{environment_id}_holographic_display",
                    object_type="holographic_display",
                    position=(0.0, 5.0, 0.0),
                    rotation=(0.0, 0.0, 0.0),
                    scale=(10.0, 6.0, 10.0),
                    interactive=True,
                    properties={'display_mode': '3d_visualization', 'data_types': ['portfolio', 'risk', 'quantum']}
                ),
                EnvironmentObject(
                    object_id=f"{environment_id}_quantum_computer",
                    object_type="quantum_computer",
                    position=(15.0, 0.0, -10.0),
                    rotation=(0.0, 45.0, 0.0),
                    scale=(3.0, 2.0, 3.0),
                    interactive=True,
                    properties={'processor_type': 'IBM_Quantum', 'qubit_count': 1000}
                )
            ])
        
        self.environment_objects[environment_id] = objects
    
    async def get_environment_info(self, environment_id: str) -> Optional[Dict]:
        """Get detailed environment information"""
        environment = self.environments.get(environment_id)
        if not environment:
            return None
        
        objects = self.environment_objects.get(environment_id, [])
        active_users = len([s for s in self.active_sessions.values() if s.get('environment_id') == environment_id])
        
        return {
            'environment_id': environment.environment_id,
            'name': environment.name,
            'type': environment.environment_type.value,
            'capacity': {
                'max': environment.max_capacity,
                'current': active_users,
                'available': environment.max_capacity - active_users
            },
            'dimensions': {
                'width': environment.spatial_dimensions[0],
                'height': environment.spatial_dimensions[1], 
                'depth': environment.spatial_dimensions[2]
            },
            'features': {
                'physics_enabled': environment.physics_enabled,
                'audio_enabled': environment.audio_enabled,
                'haptic_feedback': environment.haptic_feedback,
                'background_music': environment.background_music
            },
            'objects_count': len(objects),
            'lighting_preset': environment.lighting_preset
        }
    
    async def join_environment(self, user_id: str, environment_id: str, spawn_position: Optional[Tuple[float, float, float]] = None) -> Dict:
        """Add user to virtual environment"""
        try:
            environment = self.environments.get(environment_id)
            if not environment:
                raise ValueError(f"Environment {environment_id} not found")
            
            # Check capacity
            active_users = len([s for s in self.active_sessions.values() if s.get('environment_id') == environment_id])
            if active_users >= environment.max_capacity:
                raise ValueError(f"Environment {environment_id} is at capacity")
            
            # Determine spawn position
            if not spawn_position:
                spawn_position = await self._get_default_spawn_position(environment_id)
            
            # Create session
            session_id = f"env_session_{user_id}_{datetime.utcnow().timestamp()}"
            self.active_sessions[session_id] = {
                'user_id': user_id,
                'environment_id': environment_id,
                'position': spawn_position,
                'rotation': (0.0, 0.0, 0.0),
                'joined_at': datetime.utcnow(),
                'active': True
            }
            
            logger.info(f"User {user_id} joined environment {environment_id}")
            
            return {
                'session_id': session_id,
                'environment_id': environment_id,
                'spawn_position': spawn_position,
                'environment_objects': [obj.__dict__ for obj in self.environment_objects.get(environment_id, [])],
                'other_users': [
                    {'user_id': s['user_id'], 'position': s['position']} 
                    for s in self.active_sessions.values() 
                    if s['environment_id'] == environment_id and s['user_id'] != user_id
                ]
            }
            
        except Exception as e:
            logger.error("Failed to join environment", error=str(e))
            raise
    
    async def _get_default_spawn_position(self, environment_id: str) -> Tuple[float, float, float]:
        """Get default spawn position for environment"""
        environment = self.environments.get(environment_id)
        if not environment:
            return (0.0, 1.8, 0.0)  # Default position
        
        # Calculate spawn position based on environment type and size
        width, height, depth = environment.spatial_dimensions
        
        # Spawn users in a semi-circle near the entrance
        spawn_x = np.random.uniform(-width/4, width/4)
        spawn_y = 1.8  # Standard height for standing avatar
        spawn_z = depth/3  # Near front of environment
        
        return (spawn_x, spawn_y, spawn_z)
    
    async def update_user_position(self, session_id: str, position: Tuple[float, float, float], rotation: Tuple[float, float, float]) -> bool:
        """Update user position and rotation in environment"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        # Validate position is within environment bounds
        environment = self.environments.get(session['environment_id'])
        if environment:
            width, height, depth = environment.spatial_dimensions
            x, y, z = position
            
            # Clamp position to environment bounds
            x = max(-width/2, min(width/2, x))
            y = max(0, min(height, y))
            z = max(-depth/2, min(depth/2, z))
            
            position = (x, y, z)
        
        session['position'] = position
        session['rotation'] = rotation
        
        return True
    
    async def leave_environment(self, session_id: str) -> bool:
        """Remove user from virtual environment"""
        session = self.active_sessions.get(session_id)
        if session:
            session['active'] = False
            del self.active_sessions[session_id]
            
            logger.info(f"User {session['user_id']} left environment {session['environment_id']}")
            return True
        
        return False
    
    async def get_all_environments(self) -> List[Dict]:
        """Get list of all available environments"""
        environments = []
        
        for env_id, environment in self.environments.items():
            env_info = await self.get_environment_info(env_id)
            if env_info:
                environments.append(env_info)
        
        return environments
    
    async def interact_with_object(self, session_id: str, object_id: str, interaction_type: str, parameters: Dict = None) -> Dict:
        """Handle user interaction with environment object"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError("Invalid session")
            
            environment_id = session['environment_id']
            objects = self.environment_objects.get(environment_id, [])
            
            # Find object
            target_object = None
            for obj in objects:
                if obj.object_id == object_id:
                    target_object = obj
                    break
            
            if not target_object:
                raise ValueError(f"Object {object_id} not found")
            
            if not target_object.interactive:
                raise ValueError(f"Object {object_id} is not interactive")
            
            # Process interaction based on object type
            interaction_result = await self._process_object_interaction(
                target_object, interaction_type, parameters or {}
            )
            
            return {
                'object_id': object_id,
                'interaction_type': interaction_type,
                'success': True,
                'result': interaction_result
            }
            
        except Exception as e:
            logger.error("Object interaction failed", error=str(e))
            return {
                'object_id': object_id,
                'interaction_type': interaction_type,
                'success': False,
                'error': str(e)
            }
    
    async def _process_object_interaction(self, obj: EnvironmentObject, interaction_type: str, parameters: Dict) -> Dict:
        """Process specific object interaction"""
        if obj.object_type == "ticker_board" and interaction_type == "view_data":
            return {
                'display_data': {
                    'SPY': {'price': 428.50, 'change': '+1.2%'},
                    'QQQ': {'price': 368.75, 'change': '+0.8%'},
                    'IWM': {'price': 195.30, 'change': '-0.3%'}
                },
                'last_updated': datetime.utcnow().isoformat()
            }
        
        elif obj.object_type == "holographic_display" and interaction_type == "load_visualization":
            return {
                'visualization_type': parameters.get('type', 'portfolio'),
                'data_loaded': True,
                'render_time': 0.5
            }
        
        elif obj.object_type == "quantum_computer" and interaction_type == "run_calculation":
            return {
                'calculation_type': parameters.get('calculation', 'portfolio_optimization'),
                'estimated_time': 30,
                'job_id': f"qjob_{datetime.utcnow().timestamp()}"
            }
        
        return {'interaction_processed': True}

# Support classes
class PhysicsEngine:
    """3D physics simulation for virtual environments"""
    
    async def initialize(self):
        self.gravity = -9.81
        self.physics_objects = {}
    
    async def simulate_physics(self, environment_id: str, delta_time: float):
        """Run physics simulation for environment"""
        # Mock physics simulation
        pass

class AudioManager:
    """3D spatial audio management"""
    
    async def initialize(self):
        self.audio_sources = {}
    
    async def play_spatial_audio(self, source_position: Tuple[float, float, float], audio_file: str, volume: float = 1.0):
        """Play 3D spatial audio"""
        # Mock spatial audio
        pass
