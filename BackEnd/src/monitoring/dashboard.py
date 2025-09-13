"""
Simple monitoring dashboard for NewsPulse
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from .metrics import get_metrics_collector, HealthChecker
from .logger import get_logger

logger = get_logger("dashboard")

# Create router for monitoring endpoints
monitoring_router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@monitoring_router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        metrics_collector = get_metrics_collector()
        health_checker = HealthChecker(metrics_collector)
        
        health_status = health_checker.check_system_health()
        
        # Return appropriate HTTP status based on health
        if health_status['status'] == 'unhealthy':
            raise HTTPException(status_code=503, detail=health_status)
        elif health_status['status'] == 'warning':
            # Return 200 but with warning status
            return health_status
        else:
            return health_status
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@monitoring_router.get("/metrics")
async def get_metrics():
    """Get current system and application metrics"""
    try:
        metrics_collector = get_metrics_collector()
        metrics = metrics_collector.get_metrics_summary()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@monitoring_router.get("/metrics/history")
async def get_metrics_history(hours: int = 24):
    """Get historical metrics"""
    try:
        if hours > 168:  # Limit to 1 week
            hours = 168
        
        metrics_collector = get_metrics_collector()
        cache = metrics_collector.cache_manager.cache
        
        # Get historical metrics from cache
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        historical_metrics = []
        current_time = start_time
        
        while current_time <= end_time:
            timestamp_key = current_time.strftime("%Y%m%d_%H%M")
            metrics_key = f"metrics:history:{timestamp_key}"
            
            metrics_data = cache.get(metrics_key)
            if metrics_data:
                historical_metrics.append(metrics_data)
            
            current_time += timedelta(minutes=5)  # 5-minute intervals
        
        return {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'interval_minutes': 5,
            'data': historical_metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting historical metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get historical metrics")


@monitoring_router.get("/dashboard", response_class=HTMLResponse)
async def monitoring_dashboard():
    """Simple HTML monitoring dashboard"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NewsPulse Monitoring Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .metric-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .metric-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #2c3e50;
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            .metric-label {
                color: #7f8c8d;
                font-size: 14px;
            }
            .status-healthy { color: #27ae60; }
            .status-warning { color: #f39c12; }
            .status-unhealthy { color: #e74c3c; }
            .refresh-btn {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            .refresh-btn:hover {
                background-color: #2980b9;
            }
            .timestamp {
                color: #7f8c8d;
                font-size: 12px;
                margin-top: 10px;
            }
            .health-checks {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .health-check {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #ecf0f1;
            }
            .health-check:last-child {
                border-bottom: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NewsPulse Monitoring Dashboard</h1>
                <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">System Health</div>
                    <div class="metric-value" id="system-health">Loading...</div>
                    <div class="metric-label">Overall Status</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">CPU Usage</div>
                    <div class="metric-value" id="cpu-usage">-</div>
                    <div class="metric-label">Percentage</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Memory Usage</div>
                    <div class="metric-value" id="memory-usage">-</div>
                    <div class="metric-label">Percentage</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Total Articles</div>
                    <div class="metric-value" id="total-articles">-</div>
                    <div class="metric-label">In Database</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Articles Today</div>
                    <div class="metric-value" id="articles-today">-</div>
                    <div class="metric-label">Processed</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">API Requests</div>
                    <div class="metric-value" id="api-requests">-</div>
                    <div class="metric-label">Per Minute</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Response Time</div>
                    <div class="metric-value" id="response-time">-</div>
                    <div class="metric-label">Milliseconds (Avg)</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Error Rate</div>
                    <div class="metric-value" id="error-rate">-</div>
                    <div class="metric-label">Percentage</div>
                </div>
            </div>
            
            <div class="health-checks">
                <div class="metric-title">Health Checks</div>
                <div id="health-checks-content">Loading...</div>
            </div>
            
            <div class="timestamp" id="last-updated">Last updated: -</div>
        </div>
        
        <script>
            async function fetchMetrics() {
                try {
                    const response = await fetch('/monitoring/metrics');
                    const data = await response.json();
                    updateMetrics(data);
                } catch (error) {
                    console.error('Error fetching metrics:', error);
                }
            }
            
            async function fetchHealth() {
                try {
                    const response = await fetch('/monitoring/health');
                    const data = await response.json();
                    updateHealth(data);
                } catch (error) {
                    console.error('Error fetching health:', error);
                }
            }
            
            function updateMetrics(data) {
                const system = data.system || {};
                const app = data.application || {};
                
                document.getElementById('cpu-usage').textContent = 
                    system.cpu_percent ? system.cpu_percent.toFixed(1) + '%' : '-';
                document.getElementById('memory-usage').textContent = 
                    system.memory_percent ? system.memory_percent.toFixed(1) + '%' : '-';
                document.getElementById('total-articles').textContent = 
                    app.total_articles || '-';
                document.getElementById('articles-today').textContent = 
                    app.articles_processed_today || '-';
                document.getElementById('api-requests').textContent = 
                    app.api_requests_per_minute ? app.api_requests_per_minute.toFixed(1) : '-';
                document.getElementById('response-time').textContent = 
                    app.average_response_time_ms ? app.average_response_time_ms.toFixed(1) : '-';
                document.getElementById('error-rate').textContent = 
                    app.error_rate_percent ? app.error_rate_percent.toFixed(1) + '%' : '-';
                
                document.getElementById('last-updated').textContent = 
                    'Last updated: ' + new Date().toLocaleString();
            }
            
            function updateHealth(data) {
                const statusElement = document.getElementById('system-health');
                const status = data.status || 'unknown';
                
                statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
                statusElement.className = 'metric-value status-' + status;
                
                const checksContainer = document.getElementById('health-checks-content');
                checksContainer.innerHTML = '';
                
                if (data.checks) {
                    Object.entries(data.checks).forEach(([name, check]) => {
                        const checkDiv = document.createElement('div');
                        checkDiv.className = 'health-check';
                        
                        const nameSpan = document.createElement('span');
                        nameSpan.textContent = name.charAt(0).toUpperCase() + name.slice(1);
                        
                        const statusSpan = document.createElement('span');
                        statusSpan.textContent = check.status;
                        statusSpan.className = 'status-' + check.status;
                        
                        checkDiv.appendChild(nameSpan);
                        checkDiv.appendChild(statusSpan);
                        checksContainer.appendChild(checkDiv);
                    });
                }
            }
            
            function refreshData() {
                fetchMetrics();
                fetchHealth();
            }
            
            // Initial load
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@monitoring_router.get("/logs")
async def get_recent_logs(level: str = "INFO", limit: int = 100):
    """Get recent log entries"""
    try:
        import os
        import json
        from collections import deque
        
        log_file = "logs/newspulse.log"
        if not os.path.exists(log_file):
            return {"logs": [], "message": "Log file not found"}
        
        logs = deque(maxlen=limit)
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    if log_entry.get('level', '').upper() >= level.upper():
                        logs.append(log_entry)
                except json.JSONDecodeError:
                    # Skip non-JSON lines
                    continue
        
        return {
            "logs": list(logs),
            "count": len(logs),
            "level_filter": level
        }
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get logs")


def setup_monitoring_middleware(app):
    """Setup monitoring middleware for FastAPI app"""
    from fastapi import Request
    import time
    
    @app.middleware("http")
    async def monitoring_middleware(request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        process_time = time.time() - start_time
        metrics_collector = get_metrics_collector()
        
        metrics_collector.record_api_request(
            endpoint=str(request.url.path),
            method=request.method,
            response_time=process_time,
            status_code=response.status_code
        )
        
        # Add response time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    return app


def main():
    """Test monitoring dashboard"""
    print("Monitoring dashboard module loaded successfully")
    
    # Test metrics collection
    metrics_collector = get_metrics_collector()
    metrics = metrics_collector.get_metrics_summary()
    
    print("Current metrics:")
    print(json.dumps(metrics, indent=2, default=str))


if __name__ == "__main__":
    main()