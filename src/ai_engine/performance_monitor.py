"""
Performance Monitoring System for AI Engine
Comprehensive monitoring of AI Engine performance with real-time metrics and alerting
"""

import time
import logging
import threading
import psutil
import gc
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import deque, defaultdict
from datetime import datetime, timedelta
import json
import weakref

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Single performance metric"""

    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Performance alert rule"""

    name: str
    metric_name: str
    threshold: float
    operator: str  # 'gt', 'lt', 'eq'
    window_seconds: int
    min_samples: int = 1
    callback: Optional[Callable] = None
    enabled: bool = True

    def evaluate(self, values: List[float]) -> bool:
        """Evaluate if alert should trigger"""
        if len(values) < self.min_samples:
            return False

        avg_value = sum(values) / len(values)

        if self.operator == "gt":
            return avg_value > self.threshold
        elif self.operator == "lt":
            return avg_value < self.threshold
        elif self.operator == "eq":
            return abs(avg_value - self.threshold) < 0.001

        return False


class MetricsCollector:
    """Collects and stores performance metrics"""

    def __init__(self, max_metrics: int = 10000, retention_hours: int = 24):
        self.max_metrics = max_metrics
        self.retention_seconds = retention_hours * 3600
        self.metrics = defaultdict(deque)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # Start cleanup thread
        self._cleanup_active = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_old_metrics, daemon=True
        )
        self._cleanup_thread.start()

    def record_metric(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name, value=value, timestamp=time.time(), tags=tags or {}
        )

        with self.lock:
            self.metrics[name].append(metric)

            # Limit memory usage
            if len(self.metrics[name]) > self.max_metrics:
                self.metrics[name].popleft()

    def get_metrics(
        self, name: str, since_seconds: Optional[int] = None
    ) -> List[PerformanceMetric]:
        """Get metrics for a specific name"""
        with self.lock:
            if name not in self.metrics:
                return []

            if since_seconds is None:
                return list(self.metrics[name])

            cutoff_time = time.time() - since_seconds
            return [m for m in self.metrics[name] if m.timestamp > cutoff_time]

    def get_metric_values(
        self, name: str, since_seconds: Optional[int] = None
    ) -> List[float]:
        """Get metric values only"""
        metrics = self.get_metrics(name, since_seconds)
        return [m.value for m in metrics]

    def get_metric_stats(
        self, name: str, since_seconds: Optional[int] = None
    ) -> Dict[str, float]:
        """Get statistical summary of metrics"""
        values = self.get_metric_values(name, since_seconds)

        if not values:
            return {}

        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1] if values else 0,
        }

    def _cleanup_old_metrics(self):
        """Remove old metrics to prevent memory buildup"""
        while self._cleanup_active:
            try:
                cutoff_time = time.time() - self.retention_seconds

                with self.lock:
                    for name, metric_deque in self.metrics.items():
                        # Remove old metrics
                        while metric_deque and metric_deque[0].timestamp < cutoff_time:
                            metric_deque.popleft()

                time.sleep(300)  # Cleanup every 5 minutes

            except Exception as e:
                self.logger.error(f"Metrics cleanup error: {e}")
                time.sleep(60)

    def cleanup(self):
        """Cleanup collector"""
        self._cleanup_active = False
        if hasattr(self, "_cleanup_thread"):
            self._cleanup_thread.join(timeout=1)


class AlertManager:
    """Manages performance alerts"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # Start alert evaluation thread
        self._alert_active = True
        self._alert_thread = threading.Thread(target=self._evaluate_alerts, daemon=True)
        self._alert_thread.start()

    def add_alert_rule(self, alert_rule: AlertRule):
        """Add an alert rule"""
        with self.lock:
            self.alert_rules[alert_rule.name] = alert_rule
            self.logger.info(f"Added alert rule: {alert_rule.name}")

    def remove_alert_rule(self, name: str):
        """Remove an alert rule"""
        with self.lock:
            if name in self.alert_rules:
                del self.alert_rules[name]
                self.logger.info(f"Removed alert rule: {name}")

    def _evaluate_alerts(self):
        """Continuously evaluate alert rules"""
        while self._alert_active:
            try:
                current_time = time.time()

                with self.lock:
                    rules_to_evaluate = list(self.alert_rules.values())

                for rule in rules_to_evaluate:
                    if not rule.enabled:
                        continue

                    # Get recent metric values
                    values = self.metrics_collector.get_metric_values(
                        rule.metric_name, rule.window_seconds
                    )

                    # Evaluate rule
                    should_alert = rule.evaluate(values)

                    # Check if alert state changed
                    was_active = rule.name in self.active_alerts

                    if should_alert and not was_active:
                        # New alert
                        self._trigger_alert(rule, values)
                    elif not should_alert and was_active:
                        # Alert resolved
                        self._resolve_alert(rule)

                time.sleep(30)  # Evaluate every 30 seconds

            except Exception as e:
                self.logger.error(f"Alert evaluation error: {e}")
                time.sleep(60)

    def _trigger_alert(self, rule: AlertRule, values: List[float]):
        """Trigger an alert"""
        alert_info = {
            "rule_name": rule.name,
            "metric_name": rule.metric_name,
            "threshold": rule.threshold,
            "current_value": sum(values) / len(values) if values else 0,
            "triggered_at": time.time(),
            "values": values[-10:],  # Last 10 values
        }

        with self.lock:
            self.active_alerts[rule.name] = alert_info
            self.alert_history.append({**alert_info, "action": "triggered"})

        self.logger.warning(
            f"Alert triggered: {rule.name} - {alert_info['current_value']:.2f} {rule.operator} {rule.threshold}"
        )

        # Call callback if provided
        if rule.callback:
            try:
                rule.callback(alert_info)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")

    def _resolve_alert(self, rule: AlertRule):
        """Resolve an alert"""
        with self.lock:
            if rule.name in self.active_alerts:
                alert_info = self.active_alerts.pop(rule.name)
                self.alert_history.append(
                    {**alert_info, "action": "resolved", "resolved_at": time.time()}
                )

        self.logger.info(f"Alert resolved: {rule.name}")

    def get_active_alerts(self) -> Dict[str, Dict]:
        """Get currently active alerts"""
        with self.lock:
            return dict(self.active_alerts)

    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history"""
        with self.lock:
            return list(self.alert_history)[-limit:]

    def cleanup(self):
        """Cleanup alert manager"""
        self._alert_active = False
        if hasattr(self, "_alert_thread"):
            self._alert_thread.join(timeout=1)


class SystemMonitor:
    """Monitors system resources"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)

        # Start monitoring thread
        self._monitor_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_system, daemon=True
        )
        self._monitor_thread.start()

    def _monitor_system(self):
        """Monitor system resources"""
        process = psutil.Process()

        while self._monitor_active:
            try:
                # Memory metrics
                memory_info = process.memory_info()
                memory_percent = process.memory_percent()
                system_memory = psutil.virtual_memory()

                self.metrics_collector.record_metric(
                    "memory.rss_mb", memory_info.rss / 1024 / 1024
                )
                self.metrics_collector.record_metric(
                    "memory.vms_mb", memory_info.vms / 1024 / 1024
                )
                self.metrics_collector.record_metric("memory.percent", memory_percent)
                self.metrics_collector.record_metric(
                    "system.memory.available_gb", system_memory.available / 1024**3
                )
                self.metrics_collector.record_metric(
                    "system.memory.percent", system_memory.percent
                )

                # CPU metrics
                cpu_percent = process.cpu_percent()
                system_cpu = psutil.cpu_percent(interval=None)

                self.metrics_collector.record_metric("cpu.process_percent", cpu_percent)
                self.metrics_collector.record_metric("system.cpu.percent", system_cpu)

                # Thread metrics
                num_threads = process.num_threads()
                self.metrics_collector.record_metric("threads.count", num_threads)

                # File descriptor metrics (Linux/Unix)
                try:
                    num_fds = process.num_fds()
                    self.metrics_collector.record_metric("fds.count", num_fds)
                except (AttributeError, psutil.AccessDenied):
                    pass

                time.sleep(10)  # Monitor every 10 seconds

            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
                time.sleep(30)

    def cleanup(self):
        """Cleanup system monitor"""
        self._monitor_active = False
        if hasattr(self, "_monitor_thread"):
            self._monitor_thread.join(timeout=1)


class PerformanceMonitor:
    """Main performance monitoring system"""

    def __init__(self, config=None, redis_client=None):
        self.config = config
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager(self.metrics_collector)
        self.system_monitor = SystemMonitor(self.metrics_collector)

        # Performance tracking
        self.request_timers = {}
        self.request_counter = 0
        self.gc_counter = 0

        # Setup default alerts
        self._setup_default_alerts()

        self.logger.info("Performance monitor initialized")

    def _setup_default_alerts(self):
        """Setup default performance alerts"""

        # Memory alerts
        self.alert_manager.add_alert_rule(
            AlertRule(
                name="high_memory_usage",
                metric_name="memory.percent",
                threshold=80.0,
                operator="gt",
                window_seconds=300,
                min_samples=3,
                callback=self._memory_alert_callback,
            )
        )

        # Response time alerts
        self.alert_manager.add_alert_rule(
            AlertRule(
                name="slow_response_time",
                metric_name="ai.response_time",
                threshold=5.0,
                operator="gt",
                window_seconds=180,
                min_samples=5,
                callback=self._performance_alert_callback,
            )
        )

        # Error rate alerts
        self.alert_manager.add_alert_rule(
            AlertRule(
                name="high_error_rate",
                metric_name="ai.error_rate",
                threshold=0.1,  # 10%
                operator="gt",
                window_seconds=300,
                min_samples=10,
            )
        )

        # System CPU alerts
        self.alert_manager.add_alert_rule(
            AlertRule(
                name="high_cpu_usage",
                metric_name="system.cpu.percent",
                threshold=90.0,
                operator="gt",
                window_seconds=300,
                min_samples=5,
            )
        )

    def _memory_alert_callback(self, alert_info: Dict):
        """Handle memory alerts"""
        self.logger.warning(
            f"High memory usage detected: {alert_info['current_value']:.1f}%"
        )

        # Trigger garbage collection
        self.gc_counter += 1
        collected = gc.collect()
        self.logger.info(
            f"Forced garbage collection #{self.gc_counter}, collected {collected} objects"
        )

        # Record GC metrics
        self.record_metric("gc.collections", self.gc_counter)
        self.record_metric("gc.collected_objects", collected)

    def _performance_alert_callback(self, alert_info: Dict):
        """Handle performance alerts"""
        self.logger.warning(
            f"Slow response time detected: {alert_info['current_value']:.2f}s"
        )

        # Could trigger adaptive performance adjustments here
        # For example, reducing concurrent requests or enabling more aggressive caching

    def start_request_timer(self, request_id: str) -> str:
        """Start timing a request"""
        if not request_id:
            request_id = f"req_{self.request_counter}"
            self.request_counter += 1

        self.request_timers[request_id] = time.time()
        return request_id

    def end_request_timer(
        self,
        request_id: str,
        success: bool = True,
        tags: Optional[Dict[str, str]] = None,
    ):
        """End timing a request and record metrics"""
        if request_id in self.request_timers:
            duration = time.time() - self.request_timers.pop(request_id)

            # Record timing metrics
            self.record_metric("ai.response_time", duration, tags)

            # Record success/error metrics
            if success:
                self.record_metric("ai.requests.success", 1, tags)
            else:
                self.record_metric("ai.requests.error", 1, tags)

            # Calculate error rate
            recent_success = len(
                self.metrics_collector.get_metric_values("ai.requests.success", 300)
            )
            recent_errors = len(
                self.metrics_collector.get_metric_values("ai.requests.error", 300)
            )
            total_recent = recent_success + recent_errors

            if total_recent > 0:
                error_rate = recent_errors / total_recent
                self.record_metric("ai.error_rate", error_rate)

    def record_metric(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ):
        """Record a custom metric"""
        self.metrics_collector.record_metric(name, value, tags)

        # Also send to Redis if available
        if self.redis_client:
            try:
                metric_data = {
                    "name": name,
                    "value": value,
                    "timestamp": time.time(),
                    "tags": tags or {},
                }
                self.redis_client.lpush("ai_metrics", json.dumps(metric_data))
                self.redis_client.ltrim("ai_metrics", 0, 10000)  # Keep last 10k metrics
            except Exception as e:
                self.logger.warning(f"Failed to send metric to Redis: {e}")

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard"""

        # Get recent metrics (last 5 minutes)
        recent_window = 300

        return {
            "timestamp": time.time(),
            "system": {
                "memory_usage_mb": self.metrics_collector.get_metric_stats(
                    "memory.rss_mb", recent_window
                ),
                "memory_percent": self.metrics_collector.get_metric_stats(
                    "memory.percent", recent_window
                ),
                "cpu_percent": self.metrics_collector.get_metric_stats(
                    "cpu.process_percent", recent_window
                ),
                "threads": self.metrics_collector.get_metric_stats(
                    "threads.count", recent_window
                ),
            },
            "ai_engine": {
                "response_time": self.metrics_collector.get_metric_stats(
                    "ai.response_time", recent_window
                ),
                "error_rate": self.metrics_collector.get_metric_stats(
                    "ai.error_rate", recent_window
                ),
                "requests_success": self.metrics_collector.get_metric_stats(
                    "ai.requests.success", recent_window
                ),
                "requests_error": self.metrics_collector.get_metric_stats(
                    "ai.requests.error", recent_window
                ),
            },
            "alerts": {
                "active": self.alert_manager.get_active_alerts(),
                "recent_history": self.alert_manager.get_alert_history(10),
            },
            "garbage_collection": {
                "collections": self.metrics_collector.get_metric_stats(
                    "gc.collections", recent_window
                ),
                "collected_objects": self.metrics_collector.get_metric_stats(
                    "gc.collected_objects", recent_window
                ),
            },
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""

        # Check recent metrics
        recent_errors = len(
            self.metrics_collector.get_metric_values("ai.requests.error", 300)
        )
        recent_success = len(
            self.metrics_collector.get_metric_values("ai.requests.success", 300)
        )
        total_recent = recent_errors + recent_success

        # Determine health status
        health_score = 100.0
        status = "healthy"
        issues = []

        # Check error rate
        if total_recent > 10:
            error_rate = recent_errors / total_recent
            if error_rate > 0.2:  # >20% error rate
                health_score -= 30
                status = "unhealthy"
                issues.append(f"High error rate: {error_rate:.1%}")
            elif error_rate > 0.1:  # >10% error rate
                health_score -= 15
                status = "degraded"
                issues.append(f"Elevated error rate: {error_rate:.1%}")

        # Check response time
        avg_response_time = self.metrics_collector.get_metric_stats(
            "ai.response_time", 300
        ).get("avg", 0)
        if avg_response_time > 5.0:
            health_score -= 25
            status = "degraded" if status == "healthy" else status
            issues.append(f"Slow response time: {avg_response_time:.2f}s")

        # Check memory usage
        memory_percent = self.metrics_collector.get_metric_stats(
            "memory.percent", 60
        ).get("latest", 0)
        if memory_percent > 90:
            health_score -= 20
            status = "unhealthy"
            issues.append(f"Critical memory usage: {memory_percent:.1f}%")
        elif memory_percent > 80:
            health_score -= 10
            status = "degraded" if status == "healthy" else status
            issues.append(f"High memory usage: {memory_percent:.1f}%")

        # Check active alerts
        active_alerts = len(self.alert_manager.get_active_alerts())
        if active_alerts > 0:
            health_score -= min(active_alerts * 10, 30)
            status = "degraded" if status == "healthy" else status
            issues.append(f"{active_alerts} active alerts")

        return {
            "status": status,
            "health_score": max(0, health_score),
            "issues": issues,
            "metrics": {
                "total_requests": total_recent,
                "error_rate": recent_errors / max(total_recent, 1),
                "avg_response_time": avg_response_time,
                "memory_percent": memory_percent,
                "active_alerts": active_alerts,
            },
        }

    def cleanup(self):
        """Cleanup performance monitor"""
        self.logger.info("Shutting down performance monitor...")

        self.system_monitor.cleanup()
        self.alert_manager.cleanup()
        self.metrics_collector.cleanup()

        self.logger.info("Performance monitor shutdown complete")


# Singleton instance for global access
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """Get the global performance monitor instance"""
    return _performance_monitor


def initialize_performance_monitor(
    config=None, redis_client=None
) -> PerformanceMonitor:
    """Initialize the global performance monitor"""
    global _performance_monitor

    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor(config, redis_client)

    return _performance_monitor


def cleanup_performance_monitor():
    """Cleanup the global performance monitor"""
    global _performance_monitor

    if _performance_monitor:
        _performance_monitor.cleanup()
        _performance_monitor = None
