"""
LLM Manager for Ollama Integration
Manages local LLM inference with Ollama for Wall-E AI Engine
"""

import logging
import time
import asyncio
import threading
import gc
import psutil
import weakref
from typing import Dict, List, Optional, Union
import requests
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import hashlib

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama client not available. Install with: pip install ollama")

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available for caching. Install with: pip install redis")


@dataclass
class LLMResponse:
    """Response from LLM inference"""

    text: str
    model: str
    tokens: int
    latency: float
    success: bool
    error: Optional[str] = None
    cached: bool = False
    memory_usage: Optional[float] = None


@dataclass
class ModelMetrics:
    """Model performance metrics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    total_tokens: int = 0
    memory_peak: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def success_rate(self) -> float:
        return self.successful_requests / max(self.total_requests, 1)

    @property
    def average_latency(self) -> float:
        return self.total_latency / max(self.successful_requests, 1)

    @property
    def cache_hit_rate(self) -> float:
        total_cache_attempts = self.cache_hits + self.cache_misses
        return self.cache_hits / max(total_cache_attempts, 1)


class ConnectionPool:
    """Connection pool for Ollama clients"""

    def __init__(self, host: str, pool_size: int = 5, timeout: int = 30):
        self.host = host
        self.pool_size = pool_size
        self.timeout = timeout
        self._pool = deque(maxlen=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0
        self.logger = logging.getLogger(__name__)

        # Initialize pool
        self._fill_pool()

    def _fill_pool(self):
        """Fill the connection pool"""
        with self._lock:
            while (
                len(self._pool) < self.pool_size
                and self._created_connections < self.pool_size
            ):
                try:
                    client = ollama.Client(host=self.host, timeout=self.timeout)
                    # Test connection
                    client.list()
                    self._pool.append(client)
                    self._created_connections += 1
                    self.logger.debug(f"Created connection {self._created_connections}")
                except Exception as e:
                    self.logger.error(f"Failed to create connection: {e}")
                    break

    def get_connection(self) -> Optional["ollama.Client"]:
        """Get a connection from the pool"""
        with self._lock:
            if self._pool:
                return self._pool.popleft()
            elif self._created_connections < self.pool_size:
                try:
                    client = ollama.Client(host=self.host, timeout=self.timeout)
                    client.list()  # Test connection
                    self._created_connections += 1
                    return client
                except Exception as e:
                    self.logger.error(f"Failed to create new connection: {e}")
                    return None
            else:
                return None

    def return_connection(self, client: "ollama.Client"):
        """Return a connection to the pool"""
        if client:
            with self._lock:
                if len(self._pool) < self.pool_size:
                    self._pool.append(client)

    def close_all(self):
        """Close all connections"""
        with self._lock:
            self._pool.clear()
            self._created_connections = 0


class PromptCache:
    """Cache for prompts and responses"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600, redis_client=None):
        self.max_size = max_size
        self.ttl = ttl
        self.redis_client = redis_client
        self.local_cache = {}
        self.cache_times = {}
        self.logger = logging.getLogger(__name__)

    def _get_cache_key(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        """Generate cache key from prompt parameters"""
        content = f"{prompt}|{system_prompt}|{temperature}|{max_tokens}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Get cached response"""
        cache_key = self._get_cache_key(prompt, system_prompt, temperature, max_tokens)

        # Try Redis first if available
        if self.redis_client:
            try:
                cached = self.redis_client.get(f"llm_cache:{cache_key}")
                if cached:
                    return cached.decode("utf-8")
            except Exception as e:
                self.logger.warning(f"Redis cache read failed: {e}")

        # Try local cache
        if cache_key in self.local_cache:
            cache_time = self.cache_times.get(cache_key, 0)
            if time.time() - cache_time < self.ttl:
                return self.local_cache[cache_key]
            else:
                # Expired
                del self.local_cache[cache_key]
                del self.cache_times[cache_key]

        return None

    def set(
        self,
        prompt: str,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
        response: str,
    ):
        """Cache response"""
        cache_key = self._get_cache_key(prompt, system_prompt, temperature, max_tokens)

        # Cache in Redis if available
        if self.redis_client:
            try:
                self.redis_client.setex(f"llm_cache:{cache_key}", self.ttl, response)
            except Exception as e:
                self.logger.warning(f"Redis cache write failed: {e}")

        # Cache locally
        if len(self.local_cache) >= self.max_size:
            # Remove oldest entries
            oldest_keys = sorted(
                self.cache_times.keys(), key=lambda k: self.cache_times[k]
            )[:50]
            for key in oldest_keys:
                self.local_cache.pop(key, None)
                self.cache_times.pop(key, None)

        self.local_cache[cache_key] = response
        self.cache_times[cache_key] = time.time()

    def clear(self):
        """Clear all caches"""
        self.local_cache.clear()
        self.cache_times.clear()

        if self.redis_client:
            try:
                # Delete all llm_cache keys
                for key in self.redis_client.scan_iter(match="llm_cache:*"):
                    self.redis_client.delete(key)
            except Exception as e:
                self.logger.warning(f"Redis cache clear failed: {e}")


class LLMManager:
    """Manager for local LLM inference using Ollama with performance optimizations"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model_name = config.model_name
        self.host = config.ollama_host
        self.timeout = config.timeout

        # Connection pool for concurrent requests
        self.connection_pool = None

        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(
            max_workers=getattr(config, "max_concurrent_requests", 10),
            thread_name_prefix="llm_worker",
        )

        # Performance tracking
        self.metrics = ModelMetrics()
        self.current_memory_usage = 0.0

        # Caching
        redis_client = None
        if REDIS_AVAILABLE and getattr(config, "enable_caching", True):
            try:
                redis_host = getattr(config, "redis_host", "localhost")
                redis_port = getattr(config, "redis_port", 6379)
                redis_client = redis.Redis(
                    host=redis_host, port=redis_port, decode_responses=False
                )
                redis_client.ping()  # Test connection
                self.logger.info("Connected to Redis for caching")
            except Exception as e:
                self.logger.warning(
                    f"Redis connection failed, using local cache only: {e}"
                )
                redis_client = None

        self.cache = PromptCache(
            max_size=getattr(config, "cache_size", 1000),
            ttl=getattr(config, "cache_ttl", 3600),
            redis_client=redis_client,
        )

        # Memory monitoring
        self._memory_monitor_active = False
        self._start_memory_monitoring()

        # Initialize connection pool
        self._initialize_connection_pool()

        # Ensure model is available
        if self.connection_pool:
            self._ensure_model_available()

    def _initialize_connection_pool(self):
        """Initialize connection pool"""
        if not OLLAMA_AVAILABLE:
            self.logger.error("Ollama not available")
            return

        try:
            # Test connection
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                pool_size = getattr(self.config, "connection_pool_size", 5)
                self.connection_pool = ConnectionPool(
                    host=self.host, pool_size=pool_size, timeout=self.timeout
                )
                self.logger.info(
                    f"Initialized connection pool with {pool_size} connections to {self.host}"
                )
            else:
                self.logger.error(f"Ollama server not responding at {self.host}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Cannot connect to Ollama server: {e}")

    def _start_memory_monitoring(self):
        """Start memory monitoring thread"""
        if self._memory_monitor_active:
            return

        def monitor_memory():
            process = psutil.Process()
            while self._memory_monitor_active:
                try:
                    memory_info = process.memory_info()
                    self.current_memory_usage = memory_info.rss / 1024 / 1024  # MB

                    # Update peak memory
                    if self.current_memory_usage > self.metrics.memory_peak:
                        self.metrics.memory_peak = self.current_memory_usage

                    # Trigger GC if memory usage is high
                    if self.current_memory_usage > getattr(
                        self.config, "memory_threshold_mb", 12000
                    ):
                        self.logger.warning(
                            f"High memory usage: {self.current_memory_usage:.1f}MB, triggering GC"
                        )
                        gc.collect()

                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    self.logger.error(f"Memory monitoring error: {e}")
                    break

        self._memory_monitor_active = True
        threading.Thread(
            target=monitor_memory, daemon=True, name="memory_monitor"
        ).start()
        self.logger.info("Started memory monitoring")

    def _ensure_model_available(self):
        """Ensure the required model is available"""
        try:
            models_response = self.client.list()
            available_models = [
                model["name"] for model in models_response.get("models", [])
            ]

            if self.model_name not in available_models:
                self.logger.warning(
                    f"Model {self.model_name} not found. Available models: {available_models}"
                )

                # Try to pull the model
                self.logger.info(f"Attempting to pull model {self.model_name}")
                self._pull_model()
            else:
                self.logger.info(f"Model {self.model_name} is available")

        except Exception as e:
            self.logger.error(f"Error checking model availability: {e}")

    def _pull_model(self):
        """Pull model from Ollama registry"""
        try:
            self.logger.info(
                f"Pulling model {self.model_name}... This may take a while."
            )

            # Use streaming pull to show progress
            stream = self.client.pull(self.model_name, stream=True)

            for chunk in stream:
                if "status" in chunk:
                    status = chunk["status"]
                    if "progress" in chunk:
                        self.logger.info(
                            f"Pull progress: {status} - {chunk['progress']}%"
                        )
                    else:
                        self.logger.info(f"Pull status: {status}")

            self.logger.info(f"Successfully pulled model {self.model_name}")

        except Exception as e:
            self.logger.error(f"Failed to pull model {self.model_name}: {e}")

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate response using local LLM with caching and optimization"""

        if not self.connection_pool:
            return LLMResponse(
                text="",
                model=self.model_name,
                tokens=0,
                latency=0.0,
                success=False,
                error="Ollama connection pool not available",
            )

        start_time = time.time()
        memory_before = self.current_memory_usage

        # Update metrics
        self.metrics.total_requests += 1

        # Normalize parameters
        temp = temperature or self.config.temperature
        max_tok = max_tokens or self.config.max_tokens
        sys_prompt = system_prompt or ""

        # Check cache first
        if getattr(self.config, "enable_caching", True):
            cached_response = self.cache.get(prompt, sys_prompt, temp, max_tok)
            if cached_response:
                self.metrics.cache_hits += 1
                latency = time.time() - start_time
                tokens = len(cached_response.split()) + len(prompt.split())

                self.logger.debug(f"Cache hit for prompt: {prompt[:50]}...")

                return LLMResponse(
                    text=cached_response,
                    model=self.model_name,
                    tokens=tokens,
                    latency=latency,
                    success=True,
                    cached=True,
                )
            else:
                self.metrics.cache_misses += 1

        # Get connection from pool
        client = self.connection_pool.get_connection()
        if not client:
            self.metrics.failed_requests += 1
            return LLMResponse(
                text="",
                model=self.model_name,
                tokens=0,
                latency=time.time() - start_time,
                success=False,
                error="No available connections in pool",
            )

        try:
            # Prepare options with memory-conscious settings
            options = {
                "temperature": temp,
                "num_predict": max_tok,
                "num_ctx": min(
                    getattr(self.config, "context_window", 4096), 8192
                ),  # Limit context for memory
                "num_thread": getattr(self.config, "num_threads", 4),
            }

            # Prepare messages
            messages = []
            if sys_prompt:
                messages.append({"role": "system", "content": sys_prompt})

            messages.append({"role": "user", "content": prompt})

            # Generate response
            response = client.chat(
                model=self.model_name, messages=messages, options=options, stream=False
            )

            latency = time.time() - start_time

            # Extract response text
            response_text = response.get("message", {}).get("content", "").strip()

            # Count tokens (approximate)
            tokens = len(response_text.split()) + len(prompt.split())

            # Update metrics
            self.metrics.successful_requests += 1
            self.metrics.total_latency += latency
            self.metrics.total_tokens += tokens

            # Cache the response
            if getattr(self.config, "enable_caching", True) and response_text:
                self.cache.set(prompt, sys_prompt, temp, max_tok, response_text)

            memory_after = self.current_memory_usage
            memory_usage = memory_after - memory_before

            self.logger.debug(
                f"Generated response in {latency:.2f}s, memory delta: {memory_usage:.1f}MB"
            )

            return LLMResponse(
                text=response_text,
                model=self.model_name,
                tokens=tokens,
                latency=latency,
                success=True,
                memory_usage=memory_usage,
            )

        except Exception as e:
            self.metrics.failed_requests += 1
            latency = time.time() - start_time

            error_msg = f"LLM generation failed: {str(e)}"
            self.logger.error(error_msg)

            return LLMResponse(
                text="",
                model=self.model_name,
                tokens=0,
                latency=latency,
                success=False,
                error=error_msg,
            )

        finally:
            # Return connection to pool
            self.connection_pool.return_connection(client)

    async def generate_response_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Async version of generate_response using optimized thread pool"""

        # Use dedicated thread pool for better resource management
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.generate_response,
            prompt,
            system_prompt,
            temperature,
            max_tokens,
        )

    async def generate_batch_async(self, requests: List[Dict]) -> List[LLMResponse]:
        """Generate multiple responses concurrently"""

        tasks = []
        for req in requests:
            task = self.generate_response_async(
                prompt=req.get("prompt", ""),
                system_prompt=req.get("system_prompt"),
                temperature=req.get("temperature"),
                max_tokens=req.get("max_tokens"),
            )
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    def test_connection(self) -> bool:
        """Test connection to Ollama server"""
        try:
            if not self.client:
                return False

            # Simple test generation
            response = self.generate_response(prompt="Responde solo 'OK'", max_tokens=5)

            return response.success and "ok" in response.text.lower()

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_model_info(self) -> Dict:
        """Get information about current model"""
        if not self.client:
            return {}

        try:
            models = self.client.list()
            for model in models.get("models", []):
                if model["name"] == self.model_name:
                    return model
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get model info: {e}")
            return {}

    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""

        return {
            "requests": {
                "total": self.metrics.total_requests,
                "successful": self.metrics.successful_requests,
                "failed": self.metrics.failed_requests,
                "success_rate": self.metrics.success_rate,
            },
            "latency": {
                "total": self.metrics.total_latency,
                "average": self.metrics.average_latency,
                "per_token": self.metrics.total_latency
                / max(self.metrics.total_tokens, 1),
            },
            "tokens": {
                "total": self.metrics.total_tokens,
                "average_per_request": self.metrics.total_tokens
                / max(self.metrics.successful_requests, 1),
            },
            "memory": {
                "current_mb": self.current_memory_usage,
                "peak_mb": self.metrics.memory_peak,
            },
            "cache": {
                "hits": self.metrics.cache_hits,
                "misses": self.metrics.cache_misses,
                "hit_rate": self.metrics.cache_hit_rate,
            },
            "pool": {
                "size": self.connection_pool.pool_size if self.connection_pool else 0,
                "active_connections": (
                    self.connection_pool._created_connections
                    if self.connection_pool
                    else 0
                ),
            },
        }

    def is_available(self) -> bool:
        """Check if LLM is available for inference"""
        return self.connection_pool is not None and OLLAMA_AVAILABLE

    def get_health_status(self) -> Dict:
        """Get detailed health status"""
        status = {
            "ollama_available": OLLAMA_AVAILABLE,
            "pool_available": self.connection_pool is not None,
            "model_loaded": False,
            "memory_usage_mb": self.current_memory_usage,
            "cache_enabled": getattr(self.config, "enable_caching", True),
            "redis_available": REDIS_AVAILABLE
            and hasattr(self.cache, "redis_client")
            and self.cache.redis_client is not None,
        }

        # Test model availability
        if self.connection_pool:
            client = self.connection_pool.get_connection()
            if client:
                try:
                    models = client.list()
                    available_models = [m["name"] for m in models.get("models", [])]
                    status["model_loaded"] = self.model_name in available_models
                    status["available_models"] = available_models
                except Exception as e:
                    status["model_error"] = str(e)
                finally:
                    self.connection_pool.return_connection(client)

        return status

    def switch_model(self, new_model: str) -> bool:
        """Switch to a different model"""
        try:
            # Test if new model is available
            models_response = self.client.list()
            available_models = [
                model["name"] for model in models_response.get("models", [])
            ]

            if new_model not in available_models:
                self.logger.warning(f"Model {new_model} not available")
                return False

            self.model_name = new_model
            self.logger.info(f"Switched to model {new_model}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to switch model: {e}")
            return False

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up LLM Manager...")

        # Stop memory monitoring
        self._memory_monitor_active = False

        # Clear cache
        if hasattr(self, "cache"):
            self.cache.clear()

        # Shutdown connection pool
        if self.connection_pool:
            self.connection_pool.close_all()
            self.connection_pool = None

        # Shutdown thread pool
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)

        # Force garbage collection
        gc.collect()

        self.logger.info("LLM Manager cleanup completed")
