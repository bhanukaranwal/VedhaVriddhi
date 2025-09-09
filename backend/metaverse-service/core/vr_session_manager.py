import asyncio
import jwt
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
import json
import secrets

logger = structlog.get_logger()

class DeviceType(Enum):
    VR_HEADSET = "vr_headset"
    AR_GLASSES = "ar_glasses"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    HAPTIC_SUIT = "haptic_suit"

class SessionStatus(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    DISCONNECTED = "disconnected"
    TERMINATED = "terminated"

@dataclass
class DeviceCapabilities:
    """VR/AR device capabilities"""
    resolution: Tuple[int, int]
    refresh_rate: int
    field_of_view: float
    tracking_dof: int  # Degrees of freedom (3DOF, 6DOF)
    hand_tracking: bool
    eye_tracking: bool
    haptic_feedback: bool
    spatial_audio: bool
    inside_out_tracking: bool

@dataclass
class VRSession:
    """VR session data"""
    session_id: str
    user_id: str
    device_type: DeviceType
    device_capabilities: DeviceCapabilities
    environment_id: str
    avatar_id: str
    spawn_position: Tuple[float, float, float]
    session_status: SessionStatus
    created_at: datetime
    last_activity: datetime
    access_token: str
    settings: Dict[str, Any] = field(default_factory=dict)
    performance_stats: Dict[str, Any] = field(default_factory=dict)

class VRSessionManager:
    """Manages VR/AR sessions and device integration"""
    
    def __init__(self):
        self.active_sessions: Dict[str, VRSession] = {}
        self.device_manager = DeviceManager()
        self.session_security = SessionSecurity()
        self.performance_monitor = PerformanceMonitor()
        self.session_timeout = 3600  # 1 hour default timeout
        
    async def initialize(self):
        """Initialize VR session manager"""
        logger.info("Initializing VR Session Manager")
        
        await self.device_manager.initialize()
        await self.session_security.initialize()
        await self.performance_monitor.initialize()
        
        # Start background tasks
        asyncio.create_task(self._session_cleanup_task())
        asyncio.create_task(self._performance_monitoring_task())
        
        logger.info("VR Session Manager initialized successfully")
    
    async def create_session(self,
                           user_id: str,
                           device_type: DeviceType,
                           device_info: Dict,
                           environment_id: str,
                           avatar_id: str) -> Dict:
        """Create new VR session"""
        try:
            session_id = f"vr_session_{user_id}_{datetime.utcnow().timestamp()}"
            
            # Parse device capabilities
            device_capabilities = await self._parse_device_capabilities(device_type, device_info)
            
            # Generate secure access token
            access_token = await self.session_security.generate_session_token(user_id, session_id)
            
            # Determine spawn position
            spawn_position = await self._calculate_spawn_position(environment_id)
            
            # Create session
            vr_session = VRSession(
                session_id=session_id,
                user_id=user_id,
                device_type=device_type,
                device_capabilities=device_capabilities,
                environment_id=environment_id,
                avatar_id=avatar_id,
                spawn_position=spawn_position,
                session_status=SessionStatus.INITIALIZING,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                access_token=access_token,
                settings=self._get_default_session_settings(device_type),
                performance_stats={}
            )
            
            self.active_sessions[session_id] = vr_session
            
            # Initialize device connection
            await self.device_manager.initialize_device_connection(session_id, device_info)
            
            # Update session status
            vr_session.session_status = SessionStatus.ACTIVE
            
            logger.info(f"Created VR session {session_id} for user {user_id}")
            
            return {
                'session_id': session_id,
                'environment_url': f"vr://{environment_id}",
                'avatar_id': avatar_id,
                'access_token': access_token,
                'spawn_location': spawn_position,
                'session_expires': (datetime.utcnow() + timedelta(seconds=self.session_timeout)).isoformat(),
                'device_settings': self._optimize_settings_for_device(device_capabilities),
                'streaming_config': await self._get_streaming_config(device_capabilities)
            }
            
        except Exception as e:
            logger.error("VR session creation failed", error=str(e))
            raise
    
    async def _parse_device_capabilities(self, device_type: DeviceType, device_info: Dict) -> DeviceCapabilities:
        """Parse device capabilities from device info"""
        # Default capabilities
        default_caps = {
            'resolution': (1920, 1080),
            'refresh_rate': 60,
            'field_of_view': 110.0,
            'tracking_dof': 6,
            'hand_tracking': False,
            'eye_tracking': False,
            'haptic_feedback': False,
            'spatial_audio': True,
            'inside_out_tracking': True
        }
        
        # Device-specific overrides
        if device_type == DeviceType.VR_HEADSET:
            if device_info.get('model') == 'Meta Quest Pro':
                default_caps.update({
                    'resolution': (1800, 1920),
                    'refresh_rate': 90,
                    'hand_tracking': True,
                    'eye_tracking': True,
                    'haptic_feedback': True
                })
            elif device_info.get('model') == 'HTC Vive Pro 2':
                default_caps.update({
                    'resolution': (2448, 2448),
                    'refresh_rate': 120,
                    'field_of_view': 120.0
                })
            elif device_info.get('model') == 'Varjo Aero':
                default_caps.update({
                    'resolution': (2880, 2720),
                    'refresh_rate': 90,
                    'eye_tracking': True
                })
        
        elif device_type == DeviceType.AR_GLASSES:
            default_caps.update({
                'resolution': (1280, 720),
                'refresh_rate': 60,
                'field_of_view': 50.0,
                'tracking_dof': 6,
                'hand_tracking': True
            })
        
        # Override with provided device info
        for key, value in device_info.items():
            if key in default_caps:
                default_caps[key] = value
        
        return DeviceCapabilities(**default_caps)
    
    def _get_default_session_settings(self, device_type: DeviceType) -> Dict:
        """Get default session settings for device type"""
        base_settings = {
            'comfort_settings': {
                'snap_turning': True,
                'teleport_movement': True,
                'vignetting_on_movement': True,
                'comfort_mode_enabled': True
            },
            'graphics_settings': {
                'render_scale': 1.0,
                'anti_aliasing': True,
                'dynamic_resolution': True,
                'foveated_rendering': False
            },
            'audio_settings': {
                'spatial_audio_enabled': True,
                'voice_chat_enabled': True,
                'ambient_volume': 0.7,
                'voice_volume': 0.8
            },
            'interaction_settings': {
                'gesture_recognition': True,
                'voice_commands': True,
                'haptic_feedback_intensity': 0.5
            }
        }
        
        # Device-specific settings
        if device_type == DeviceType.VR_HEADSET:
            base_settings['graphics_settings']['foveated_rendering'] = True
            base_settings['graphics_settings']['render_scale'] = 1.2
        elif device_type == DeviceType.DESKTOP:
            base_settings['comfort_settings']['snap_turning'] = False
            base_settings['comfort_settings']['teleport_movement'] = False
            base_settings['interaction_settings']['gesture_recognition'] = False
        
        return base_settings
    
    def _optimize_settings_for_device(self, capabilities: DeviceCapabilities) -> Dict:
        """Optimize settings based on device capabilities"""
        optimized = {}
        
        # Graphics optimization
        if capabilities.resolution[0] > 2000:  # High resolution
            optimized['render_quality'] = 'high'
            optimized['texture_quality'] = 'ultra'
        else:
            optimized['render_quality'] = 'medium'
            optimized['texture_quality'] = 'high'
        
        # Performance optimization
        if capabilities.refresh_rate >= 90:
            optimized['frame_rate_target'] = capabilities.refresh_rate
            optimized['motion_smoothing'] = False
        else:
            optimized['frame_rate_target'] = 60
            optimized['motion_smoothing'] = True
        
        # Feature optimization
        optimized['foveated_rendering'] = capabilities.eye_tracking
        optimized['hand_tracking_enabled'] = capabilities.hand_tracking
        optimized['haptic_feedback_enabled'] = capabilities.haptic_feedback
        
        return optimized
    
    async def _get_streaming_config(self, capabilities: DeviceCapabilities) -> Dict:
        """Get streaming configuration for device"""
        config = {
            'video_codec': 'h264',
            'audio_codec': 'aac',
            'bitrate_mbps': 50,
            'latency_mode': 'low',
            'adaptive_bitrate': True
        }
        
        # Adjust based on capabilities
        if capabilities.resolution[0] > 2000:
            config['bitrate_mbps'] = 100
            config['video_codec'] = 'h265'
        
        if capabilities.refresh_rate >= 90:
            config['latency_mode'] = 'ultra_low'
        
        return config
    
    async def authenticate_session(self, session_id: str, access_token: str) -> str:
        """Authenticate session and return user ID"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError("Session not found")
            
            # Verify access token
            user_id = await self.session_security.verify_session_token(access_token, session_id)
            
            if user_id != session.user_id:
                raise ValueError("Token does not match session user")
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            
            return user_id
            
        except Exception as e:
            logger.error("Session authentication failed", error=str(e))
            raise
    
    async def update_session_activity(self, session_id: str, activity_data: Dict):
        """Update session activity and performance data"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        session.last_activity = datetime.utcnow()
        
        # Update performance stats
        if 'performance' in activity_data:
            perf_data = activity_data['performance']
            session.performance_stats.update({
                'fps': perf_data.get('fps'),
                'frame_time_ms': perf_data.get('frame_time_ms'),
                'gpu_utilization': perf_data.get('gpu_utilization'),
                'cpu_utilization': perf_data.get('cpu_utilization'),
                'memory_usage_mb': perf_data.get('memory_usage_mb'),
                'network_latency_ms': perf_data.get('network_latency_ms'),
                'last_updated': datetime.utcnow().isoformat()
            })
        
        # Monitor performance issues
        await self.performance_monitor.analyze_session_performance(session_id, session.performance_stats)
    
    async def pause_session(self, session_id: str) -> bool:
        """Pause VR session"""
        session = self.active_sessions.get(session_id)
        if session and session.session_status == SessionStatus.ACTIVE:
            session.session_status = SessionStatus.PAUSED
            logger.info(f"Paused VR session {session_id}")
            return True
        return False
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume VR session"""
        session = self.active_sessions.get(session_id)
        if session and session.session_status == SessionStatus.PAUSED:
            session.session_status = SessionStatus.ACTIVE
            session.last_activity = datetime.utcnow()
            logger.info(f"Resumed VR session {session_id}")
            return True
        return False
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate VR session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        # Cleanup device connection
        await self.device_manager.cleanup_device_connection(session_id)
        
        # Update session status
        session.session_status = SessionStatus.TERMINATED
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Terminated VR session {session_id}")
        return True
    
    async def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'device_type': session.device_type.value,
            'environment_id': session.environment_id,
            'avatar_id': session.avatar_id,
            'status': session.session_status.value,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'session_duration': (datetime.utcnow() - session.created_at).total_seconds(),
            'device_capabilities': {
                'resolution': session.device_capabilities.resolution,
                'refresh_rate': session.device_capabilities.refresh_rate,
                'hand_tracking': session.device_capabilities.hand_tracking,
                'eye_tracking': session.device_capabilities.eye_tracking
            },
            'performance_stats': session.performance_stats
        }
    
    async def _calculate_spawn_position(self, environment_id: str) -> Tuple[float, float, float]:
        """Calculate spawn position in environment"""
        # Mock spawn position calculation
        return (0.0, 1.8, 2.0)  # Default spawn position
    
    async def _session_cleanup_task(self):
        """Background task to cleanup inactive sessions"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    time_since_activity = (current_time - session.last_activity).total_seconds()
                    
                    if time_since_activity > self.session_timeout:
                        expired_sessions.append(session_id)
                
                # Cleanup expired sessions
                for session_id in expired_sessions:
                    await self.terminate_session(session_id)
                    logger.info(f"Cleaned up expired session: {session_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error("Session cleanup task error", error=str(e))
                await asyncio.sleep(600)
    
    async def _performance_monitoring_task(self):
        """Background task to monitor session performance"""
        while True:
            try:
                for session_id, session in list(self.active_sessions.items()):
                    if session.session_status == SessionStatus.ACTIVE:
                        await self.performance_monitor.check_session_health(session_id, session)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error("Performance monitoring task error", error=str(e))
                await asyncio.sleep(60)
    
    async def get_active_sessions_summary(self) -> Dict:
        """Get summary of all active sessions"""
        active_count = len([s for s in self.active_sessions.values() if s.session_status == SessionStatus.ACTIVE])
        paused_count = len([s for s in self.active_sessions.values() if s.session_status == SessionStatus.PAUSED])
        
        device_breakdown = {}
        for session in self.active_sessions.values():
            device_type = session.device_type.value
            device_breakdown[device_type] = device_breakdown.get(device_type, 0) + 1
        
        return {
            'total_sessions': len(self.active_sessions),
            'active_sessions': active_count,
            'paused_sessions': paused_count,
            'device_breakdown': device_breakdown,
            'average_session_duration': self._calculate_average_session_duration()
        }
    
    def _calculate_average_session_duration(self) -> float:
        """Calculate average session duration"""
        if not self.active_sessions:
            return 0.0
        
        total_duration = sum(
            (datetime.utcnow() - session.created_at).total_seconds()
            for session in self.active_sessions.values()
        )
        
        return total_duration / len(self.active_sessions)

# Support classes
class DeviceManager:
    """Manages VR/AR device connections"""
    
    async def initialize(self):
        self.device_connections = {}
    
    async def initialize_device_connection(self, session_id: str, device_info: Dict):
        """Initialize connection to VR/AR device"""
        # Mock device initialization
        self.device_connections[session_id] = {
            'connected': True,
            'last_ping': datetime.utcnow(),
            'device_info': device_info
        }
    
    async def cleanup_device_connection(self, session_id: str):
        """Cleanup device connection"""
        if session_id in self.device_connections:
            del self.device_connections[session_id]

class SessionSecurity:
    """Handles session security and authentication"""
    
    async def initialize(self):
        self.jwt_secret = secrets.token_hex(32)
    
    async def generate_session_token(self, user_id: str, session_id: str) -> str:
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'issued_at': datetime.utcnow().timestamp(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).timestamp()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token
    
    async def verify_session_token(self, token: str, session_id: str) -> str:
        """Verify JWT session token and return user ID"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            if payload['session_id'] != session_id:
                raise jwt.InvalidTokenError("Session ID mismatch")
            
            if payload['expires_at'] < datetime.utcnow().timestamp():
                raise jwt.ExpiredSignatureError("Token expired")
            
            return payload['user_id']
            
        except jwt.PyJWTError as e:
            raise ValueError(f"Invalid session token: {str(e)}")

class PerformanceMonitor:
    """Monitors VR session performance"""
    
    async def initialize(self):
        self.performance_thresholds = {
            'min_fps': 72,
            'max_frame_time_ms': 13.9,
            'max_latency_ms': 20,
            'max_gpu_utilization': 0.9,
            'max_memory_usage_mb': 8000
        }
    
    async def analyze_session_performance(self, session_id: str, stats: Dict):
        """Analyze session performance and trigger optimizations if needed"""
        issues = []
        
        # Check FPS
        fps = stats.get('fps')
        if fps and fps < self.performance_thresholds['min_fps']:
            issues.append(f"Low FPS: {fps}")
        
        # Check frame time
        frame_time = stats.get('frame_time_ms')
        if frame_time and frame_time > self.performance_thresholds['max_frame_time_ms']:
            issues.append(f"High frame time: {frame_time}ms")
        
        # Check network latency
        latency = stats.get('network_latency_ms')
        if latency and latency > self.performance_thresholds['max_latency_ms']:
            issues.append(f"High network latency: {latency}ms")
        
        if issues:
            await self._trigger_performance_optimization(session_id, issues)
    
    async def _trigger_performance_optimization(self, session_id: str, issues: List[str]):
        """Trigger performance optimizations"""
        logger.warning(f"Performance issues detected for session {session_id}: {issues}")
        # Would trigger automatic optimization adjustments
    
    async def check_session_health(self, session_id: str, session: VRSession):
        """Check overall session health"""
        # Mock health check
        pass
