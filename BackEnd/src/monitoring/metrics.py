"""
Metrics collection and monitoring for NewsPulse
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

from ..cache.redis_client import get_cache_manager
from .logger import get_logger

logger = get_logger("metrics")


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int


@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""
    timestamp: datetime
    total_articles: int
    articles_processed_today: int
    articles_classified_today: int
    api_requests_per_minute: float
    average_response_time_ms: float
    error_rate_percent: float
    cache_hit_rate_percent: float
    active_sources: int
    failed_sources: int


@dataclass
class ProcessingMetrics:
    """Processing job metrics"""
    timestamp: datetime
    job_type: str
    duration_seconds: float
    items_processed: int
    success_count: int
    error_count: int
    success_rate_percent: float


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager or get_cache_manager()
        self.api_requests = deque(maxlen=1000)  # Last 1000 requests
        self.response_times = deque(maxlen=1000)  # Last 1000 response times
        self.errors = deque(maxlen=1000)  # Last 1000 errors
        self.cache_operations = deque(maxlen=1000)  # Last 1000 cache operations
        self.processing_jobs = []
        self._lock = threading.Lock()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            # Network usage
            network = psutil.net_io_counters()
            network_bytes_sent = network.bytes_sent
            network_bytes_recv = network.bytes_recv
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_free_gb=disk_free_gb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_application_metrics(self, db_session=None) -> ApplicationMetrics:
        """Collect application-specific metrics"""
        try:
            from ..storage.models import Article, NewsSource
            from ..storage.database import get_db_session
            
            if db_session is None:
                db_session = get_db_session()
                should_close = True
            else:
                should_close = False
            
            try:
                # Database metrics
                total_articles = db_session.query(Article).count()
                
                # Articles processed today
                today = datetime.utcnow().date()
                articles_today = db_session.query(Article).filter(
                    Article.scraped_date >= today
                ).count()
                
                # Articles classified today
                classified_today = db_session.query(Article).filter(
                    Article.scraped_date >= today,
                    Article.classified == True
                ).count()
                
                # Source metrics
                active_sources = db_session.query(NewsSource).filter(
                    NewsSource.enabled == True
                ).count()
                
                failed_sources = db_session.query(NewsSource).filter(
                    NewsSource.enabled == True,
                    NewsSource.last_scraped < datetime.utcnow() - timedelta(hours=24)
                ).count()
                
                # API metrics
                api_requests_per_minute = self._calculate_requests_per_minute()
                average_response_time = self._calculate_average_response_time()
                error_rate = self._calculate_error_rate()
                cache_hit_rate = self._calculate_cache_hit_rate()
                
                return ApplicationMetrics(
                    timestamp=datetime.utcnow(),
                    total_articles=total_articles,
                    articles_processed_today=articles_today,
                    articles_classified_today=classified_today,
                    api_requests_per_minute=api_requests_per_minute,
                    average_response_time_ms=average_response_time,
                    error_rate_percent=error_rate,
                    cache_hit_rate_percent=cache_hit_rate,
                    active_sources=active_sources,
                    failed_sources=failed_sources
                )
                
            finally:
                if should_close:
                    db_session.close()
                    
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return None
    
    def record_api_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Record API request metrics"""
        with self._lock:
            timestamp = datetime.utcnow()
            self.api_requests.append({
                'timestamp': timestamp,
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code
            })
            self.response_times.append({
                'timestamp': timestamp,
                'response_time': response_time
            })
            
            if status_code >= 400:
                self.errors.append({
                    'timestamp': timestamp,
                    'endpoint': endpoint,
                    'status_code': status_code
                })
    
    def record_cache_operation(self, operation: str, hit: bool, response_time: float):
        """Record cache operation metrics"""
        with self._lock:
            self.cache_operations.append({
                'timestamp': datetime.utcnow(),
                'operation': operation,
                'hit': hit,
                'response_time': response_time
            })
    
    def record_processing_job(self, job_type: str, duration: float, items_processed: int, success_count: int, error_count: int):
        """Record processing job metrics"""
        success_rate = (success_count / items_processed * 100) if items_processed > 0 else 0
        
        metrics = ProcessingMetrics(
            timestamp=datetime.utcnow(),
            job_type=job_type,
            duration_seconds=duration,
            items_processed=items_processed,
            success_count=success_count,
            error_count=error_count,
            success_rate_percent=success_rate
        )
        
        with self._lock:
            self.processing_jobs.append(metrics)
            
            # Keep only last 100 jobs
            if len(self.processing_jobs) > 100:
                self.processing_jobs = self.processing_jobs[-100:]
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate API requests per minute"""
        if not self.api_requests:
            return 0.0
        
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        recent_requests = [
            req for req in self.api_requests
            if req['timestamp'] > one_minute_ago
        ]
        
        return len(recent_requests)
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time in milliseconds"""
        if not self.response_times:
            return 0.0
        
        now = datetime.utcnow()
        five_minutes_ago = now - timedelta(minutes=5)
        
        recent_times = [
            rt['response_time'] for rt in self.response_times
            if rt['timestamp'] > five_minutes_ago
        ]
        
        if not recent_times:
            return 0.0
        
        return sum(recent_times) / len(recent_times) * 1000  # Convert to ms
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if not self.api_requests:
            return 0.0
        
        now = datetime.utcnow()
        five_minutes_ago = now - timedelta(minutes=5)
        
        recent_requests = [
            req for req in self.api_requests
            if req['timestamp'] > five_minutes_ago
        ]
        
        recent_errors = [
            err for err in self.errors
            if err['timestamp'] > five_minutes_ago
        ]
        
        if not recent_requests:
            return 0.0
        
        return (len(recent_errors) / len(recent_requests)) * 100
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        if not self.cache_operations:
            return 0.0
        
        now = datetime.utcnow()
        five_minutes_ago = now - timedelta(minutes=5)
        
        recent_operations = [
            op for op in self.cache_operations
            if op['timestamp'] > five_minutes_ago
        ]
        
        if not recent_operations:
            return 0.0
        
        hits = sum(1 for op in recent_operations if op['hit'])
        return (hits / len(recent_operations)) * 100
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        system_metrics = self.collect_system_metrics()
        app_metrics = self.collect_application_metrics()
        
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': asdict(system_metrics) if system_metrics else None,
            'application': asdict(app_metrics) if app_metrics else None,
            'recent_processing_jobs': [
                asdict(job) for job in self.processing_jobs[-10:]  # Last 10 jobs
            ]
        }
        
        return summary
    
    def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in cache for monitoring dashboard"""
        try:
            # Store current metrics
            self.cache_manager.cache.set("metrics:current", metrics, ttl=300)  # 5 minutes
            
            # Store historical metrics (keep last 24 hours)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")
            self.cache_manager.cache.set(f"metrics:history:{timestamp}", metrics, ttl=86400)  # 24 hours
            
            logger.info("Metrics stored successfully")
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")


class HealthChecker:
    """Health check functionality"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        # System resource checks
        system_metrics = self.metrics_collector.collect_system_metrics()
        if system_metrics:
            health_status['checks']['cpu'] = {
                'status': 'healthy' if system_metrics.cpu_percent < 80 else 'warning',
                'value': system_metrics.cpu_percent,
                'threshold': 80
            }
            
            health_status['checks']['memory'] = {
                'status': 'healthy' if system_metrics.memory_percent < 85 else 'warning',
                'value': system_metrics.memory_percent,
                'threshold': 85
            }
            
            health_status['checks']['disk'] = {
                'status': 'healthy' if system_metrics.disk_usage_percent < 90 else 'warning',
                'value': system_metrics.disk_usage_percent,
                'threshold': 90
            }
        
        # Database check
        try:
            from ..storage.database import test_connection
            db_healthy = test_connection()
            health_status['checks']['database'] = {
                'status': 'healthy' if db_healthy else 'unhealthy',
                'connected': db_healthy
            }
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Cache check
        try:
            cache_healthy = self.metrics_collector.cache_manager.cache.connected
            health_status['checks']['cache'] = {
                'status': 'healthy' if cache_healthy else 'warning',
                'connected': cache_healthy
            }
        except Exception as e:
            health_status['checks']['cache'] = {
                'status': 'warning',
                'error': str(e)
            }
        
        # Determine overall status
        check_statuses = [check['status'] for check in health_status['checks'].values()]
        if 'unhealthy' in check_statuses:
            health_status['status'] = 'unhealthy'
        elif 'warning' in check_statuses:
            health_status['status'] = 'warning'
        
        return health_status


# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def main():
    """Test metrics collection"""
    collector = MetricsCollector()
    
    # Collect metrics
    system_metrics = collector.collect_system_metrics()
    app_metrics = collector.collect_application_metrics()
    
    print("System Metrics:")
    if system_metrics:
        print(f"  CPU: {system_metrics.cpu_percent}%")
        print(f"  Memory: {system_metrics.memory_percent}%")
        print(f"  Disk: {system_metrics.disk_usage_percent}%")
    
    print("\nApplication Metrics:")
    if app_metrics:
        print(f"  Total Articles: {app_metrics.total_articles}")
        print(f"  Articles Today: {app_metrics.articles_processed_today}")
        print(f"  API Requests/min: {app_metrics.api_requests_per_minute}")
    
    # Test health check
    health_checker = HealthChecker(collector)
    health = health_checker.check_system_health()
    print(f"\nSystem Health: {health['status']}")


if __name__ == "__main__":
    main()