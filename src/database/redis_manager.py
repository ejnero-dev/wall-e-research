"""
Redis Manager for Wallapop Bot
Handles Redis operations for caching and session management
"""
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

import redis
from redis.exceptions import RedisError, ConnectionError

logger = logging.getLogger(__name__)


class RedisManager:
    """Manages Redis connections and operations"""
    
    def __init__(self, redis_config: Dict[str, Any]):
        """
        Initialize Redis manager
        
        Args:
            redis_config: Redis configuration dictionary
        """
        self.config = redis_config
        self.client = None
        self._connect()
        
    def _connect(self):
        """Establish Redis connection"""
        try:
            self.client = redis.Redis(**self.config)
            # Test connection
            self.client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None
            
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False
            
    def set_cache(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """
        Cache a value with expiration
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire_seconds: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            serialized_value = json.dumps(value, default=str)
            return self.client.setex(key, expire_seconds, serialized_value)
        except Exception as e:
            logger.error(f"Redis cache set failed for key {key}: {e}")
            return False
            
    def get_cache(self, key: str) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.is_connected():
            return None
            
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis cache get failed for key {key}: {e}")
            return None
            
    def delete_cache(self, key: str) -> bool:
        """
        Delete cached value
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis cache delete failed for key {key}: {e}")
            return False
            
    def get_cache_keys(self, pattern: str = "*") -> List[str]:
        """
        Get all cache keys matching pattern
        
        Args:
            pattern: Key pattern (default: all keys)
            
        Returns:
            List of matching keys
        """
        if not self.is_connected():
            return []
            
        try:
            keys = self.client.keys(pattern)
            return [key.decode() if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Redis keys scan failed for pattern {pattern}: {e}")
            return []
            
    # Session Management
    
    def set_session(self, session_id: str, session_data: Dict[str, Any], 
                   expire_hours: int = 24) -> bool:
        """
        Store session data
        
        Args:
            session_id: Session identifier
            session_data: Session data dictionary
            expire_hours: Session expiration in hours
            
        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        expire_seconds = expire_hours * 3600
        return self.set_cache(key, session_data, expire_seconds)
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        key = f"session:{session_id}"
        return self.get_cache(key)
        
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        return self.delete_cache(key)
        
    def extend_session(self, session_id: str, expire_hours: int = 24) -> bool:
        """
        Extend session expiration
        
        Args:
            session_id: Session identifier
            expire_hours: New expiration in hours
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        key = f"session:{session_id}"
        expire_seconds = expire_hours * 3600
        
        try:
            return bool(self.client.expire(key, expire_seconds))
        except Exception as e:
            logger.error(f"Redis session extend failed for {session_id}: {e}")
            return False
            
    # Rate Limiting
    
    def is_rate_limited(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """
        Check if identifier is rate limited
        
        Args:
            identifier: Unique identifier (user ID, IP, etc.)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if rate limited, False otherwise
        """
        if not self.is_connected():
            return False  # Allow if Redis is down
            
        key = f"rate_limit:{identifier}"
        
        try:
            current_count = self.client.get(key)
            if current_count and int(current_count) >= limit:
                return True
                
            # Increment counter
            pipe = self.client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            pipe.execute()
            
            return False
        except Exception as e:
            logger.error(f"Redis rate limit check failed for {identifier}: {e}")
            return False  # Allow if error occurs
            
    def get_rate_limit_info(self, identifier: str) -> Dict[str, Any]:
        """
        Get rate limit information
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Dictionary with rate limit info
        """
        if not self.is_connected():
            return {'count': 0, 'ttl': 0}
            
        key = f"rate_limit:{identifier}"
        
        try:
            count = self.client.get(key)
            ttl = self.client.ttl(key)
            
            return {
                'count': int(count) if count else 0,
                'ttl': ttl if ttl > 0 else 0
            }
        except Exception as e:
            logger.error(f"Redis rate limit info failed for {identifier}: {e}")
            return {'count': 0, 'ttl': 0}
            
    # Conversation State Management
    
    def set_conversation_state(self, conversation_id: str, state: Dict[str, Any]) -> bool:
        """
        Store conversation state
        
        Args:
            conversation_id: Conversation identifier
            state: Conversation state data
            
        Returns:
            True if successful, False otherwise
        """
        key = f"conversation_state:{conversation_id}"
        return self.set_cache(key, state, expire_seconds=86400)  # 24 hours
        
    def get_conversation_state(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation state
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation state or None if not found
        """
        key = f"conversation_state:{conversation_id}"
        return self.get_cache(key)
        
    def update_conversation_state(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update conversation state
        
        Args:
            conversation_id: Conversation identifier
            updates: State updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        current_state = self.get_conversation_state(conversation_id) or {}
        current_state.update(updates)
        return self.set_conversation_state(conversation_id, current_state)
        
    # Message Queue (Simple pub/sub)
    
    def publish_message(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        Publish message to channel
        
        Args:
            channel: Channel name
            message: Message data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
            
        try:
            serialized_message = json.dumps(message, default=str)
            self.client.publish(channel, serialized_message)
            return True
        except Exception as e:
            logger.error(f"Redis publish failed for channel {channel}: {e}")
            return False
            
    def subscribe_to_channel(self, channel: str):
        """
        Subscribe to channel (returns pubsub object)
        
        Args:
            channel: Channel name
            
        Returns:
            Redis pubsub object or None
        """
        if not self.is_connected():
            return None
            
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            logger.error(f"Redis subscribe failed for channel {channel}: {e}")
            return None
            
    # Health Check
    
    def health_check(self) -> Dict[str, Any]:
        """
        Get Redis health information
        
        Returns:
            Health check results
        """
        if not self.is_connected():
            return {
                'status': 'down',
                'error': 'Not connected'
            }
            
        try:
            info = self.client.info()
            return {
                'status': 'up',
                'version': info.get('redis_version'),
                'uptime_seconds': info.get('uptime_in_seconds'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'total_connections_received': info.get('total_connections_received'),
                'total_commands_processed': info.get('total_commands_processed')
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }