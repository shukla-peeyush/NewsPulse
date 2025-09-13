"""
Enhanced logging configuration for NewsPulse
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
import json

try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class NewsLogger:
    """Enhanced logger for NewsPulse application"""
    
    def __init__(self, name: str = "newspulse", log_level: str = "INFO"):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Console formatter
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        console_formatter = logging.Formatter(console_format)
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
        
        # File handler for general logs
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{self.name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, f"{self.name}_errors.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        
        self.logger.addHandler(error_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.debug(message, extra=extra)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        extra = {'extra_fields': kwargs} if kwargs else {}
        self.logger.critical(message, extra=extra)


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = NewsLogger("performance")
    
    def log_api_request(self, endpoint: str, method: str, duration: float, status_code: int, user_id: Optional[str] = None):
        """Log API request performance"""
        self.logger.info(
            f"API Request: {method} {endpoint}",
            endpoint=endpoint,
            method=method,
            duration_ms=round(duration * 1000, 2),
            status_code=status_code,
            user_id=user_id,
            metric_type="api_request"
        )
    
    def log_database_query(self, query_type: str, duration: float, table: Optional[str] = None):
        """Log database query performance"""
        self.logger.info(
            f"Database Query: {query_type}",
            query_type=query_type,
            duration_ms=round(duration * 1000, 2),
            table=table,
            metric_type="database_query"
        )
    
    def log_processing_job(self, job_type: str, duration: float, items_processed: int, success_count: int, error_count: int):
        """Log processing job performance"""
        self.logger.info(
            f"Processing Job: {job_type}",
            job_type=job_type,
            duration_seconds=round(duration, 2),
            items_processed=items_processed,
            success_count=success_count,
            error_count=error_count,
            success_rate=round((success_count / items_processed * 100), 2) if items_processed > 0 else 0,
            metric_type="processing_job"
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, duration: float):
        """Log cache operation performance"""
        self.logger.info(
            f"Cache {operation}: {key}",
            operation=operation,
            cache_key=key,
            cache_hit=hit,
            duration_ms=round(duration * 1000, 2),
            metric_type="cache_operation"
        )


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self):
        self.logger = NewsLogger("security")
    
    def log_authentication_attempt(self, user_id: str, success: bool, ip_address: str, user_agent: str):
        """Log authentication attempt"""
        self.logger.info(
            f"Authentication attempt: {'SUCCESS' if success else 'FAILED'}",
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            event_type="authentication"
        )
    
    def log_rate_limit_exceeded(self, identifier: str, endpoint: str, ip_address: str):
        """Log rate limit exceeded"""
        self.logger.warning(
            f"Rate limit exceeded: {identifier}",
            identifier=identifier,
            endpoint=endpoint,
            ip_address=ip_address,
            event_type="rate_limit_exceeded"
        )
    
    def log_suspicious_activity(self, description: str, ip_address: str, details: dict):
        """Log suspicious activity"""
        self.logger.warning(
            f"Suspicious activity: {description}",
            ip_address=ip_address,
            event_type="suspicious_activity",
            **details
        )


def setup_logging(log_level: str = "INFO", use_loguru: bool = False):
    """
    Setup application-wide logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_loguru: Whether to use loguru for enhanced logging
    """
    
    if use_loguru and LOGURU_AVAILABLE:
        # Configure loguru
        loguru_logger.remove()  # Remove default handler
        
        # Add console handler
        loguru_logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # Add file handler
        os.makedirs("logs", exist_ok=True)
        loguru_logger.add(
            "logs/newspulse.log",
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            serialize=True  # JSON format
        )
        
        # Add error file handler
        loguru_logger.add(
            "logs/newspulse_errors.log",
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            serialize=True
        )
        
        return loguru_logger
    
    else:
        # Use standard logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.handlers.RotatingFileHandler(
                    "logs/newspulse.log",
                    maxBytes=10*1024*1024,
                    backupCount=5
                )
            ]
        )
        
        return logging.getLogger("newspulse")


# Global logger instances
app_logger = NewsLogger("newspulse")
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()


def get_logger(name: str = "newspulse") -> NewsLogger:
    """Get a logger instance"""
    return NewsLogger(name)


def main():
    """Test logging functionality"""
    
    # Setup logging
    logger = setup_logging("INFO")
    
    # Test different log levels
    app_logger.info("Application started", version="1.0.0", environment="development")
    app_logger.warning("This is a warning message", component="test")
    app_logger.error("This is an error message", error_code="TEST_001")
    
    # Test performance logging
    performance_logger.log_api_request("/articles", "GET", 0.150, 200, "user123")
    performance_logger.log_database_query("SELECT", 0.025, "articles")
    performance_logger.log_processing_job("rss_fetch", 45.5, 100, 95, 5)
    
    # Test security logging
    security_logger.log_authentication_attempt("user123", True, "192.168.1.1", "Mozilla/5.0")
    security_logger.log_rate_limit_exceeded("user456", "/articles", "192.168.1.2")
    
    print("Logging test completed. Check logs/ directory for output files.")


if __name__ == "__main__":
    main()