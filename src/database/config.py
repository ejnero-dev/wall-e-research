"""
Database configuration utilities
"""
import os
from typing import Dict, Any
import yaml
from pathlib import Path


class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize database configuration
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        
    def _find_config_file(self) -> str:
        """Find configuration file in project"""
        possible_paths = [
            "config/config.yaml",
            "config.yaml",
            "../config/config.yaml",
            "../../config/config.yaml"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
                
        # Return default path if none found
        return "config/config.yaml"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default configuration if file doesn't exist
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'wallapop_bot',
                'user': 'wallapop_user',
                'password': 'change_this_password'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'password': None
            }
        }
        
    def get_database_url(self, async_driver: bool = False) -> str:
        """
        Get PostgreSQL database URL
        
        Args:
            async_driver: Use asyncpg driver instead of psycopg2
            
        Returns:
            Database connection URL
        """
        db_config = self.config.get('database', {})
        
        # Override with environment variables if available
        host = os.getenv('DB_HOST', db_config.get('host', 'localhost'))
        port = os.getenv('DB_PORT', db_config.get('port', 5432))
        name = os.getenv('DB_NAME', db_config.get('name', 'wallapop_bot'))
        user = os.getenv('DB_USER', db_config.get('user', 'wallapop_user'))
        password = os.getenv('DB_PASSWORD', db_config.get('password', 'change_this_password'))
        
        # Choose driver
        driver = "postgresql+asyncpg" if async_driver else "postgresql+psycopg2"
        
        return f"{driver}://{user}:{password}@{host}:{port}/{name}"
        
    def get_redis_url(self) -> str:
        """
        Get Redis connection URL
        
        Returns:
            Redis connection URL
        """
        redis_config = self.config.get('redis', {})
        
        # Override with environment variables if available
        host = os.getenv('REDIS_HOST', redis_config.get('host', 'localhost'))
        port = os.getenv('REDIS_PORT', redis_config.get('port', 6379))
        db = os.getenv('REDIS_DB', redis_config.get('db', 0))
        password = os.getenv('REDIS_PASSWORD', redis_config.get('password'))
        
        # Build URL
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"
            
    def get_redis_config(self) -> Dict[str, Any]:
        """
        Get Redis configuration dictionary
        
        Returns:
            Redis configuration for redis-py
        """
        redis_config = self.config.get('redis', {})
        
        config = {
            'host': os.getenv('REDIS_HOST', redis_config.get('host', 'localhost')),
            'port': int(os.getenv('REDIS_PORT', redis_config.get('port', 6379))),
            'db': int(os.getenv('REDIS_DB', redis_config.get('db', 0))),
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'health_check_interval': 30,
        }
        
        password = os.getenv('REDIS_PASSWORD', redis_config.get('password'))
        if password:
            config['password'] = password
            
        return config
        
    def validate_connection(self) -> Dict[str, bool]:
        """
        Validate database and Redis connections
        
        Returns:
            Dictionary with connection status
        """
        results = {'database': False, 'redis': False}
        
        # Test PostgreSQL connection
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(self.get_database_url())
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            results['database'] = True
        except Exception as e:
            print(f"Database connection failed: {e}")
            
        # Test Redis connection
        try:
            import redis
            r = redis.Redis(**self.get_redis_config())
            r.ping()
            results['redis'] = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            
        return results