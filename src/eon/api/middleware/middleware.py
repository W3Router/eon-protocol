
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict, Any
from ..utils.metrics import MetricsCollector

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = None
        
        try:
            response = await call_next(request)
            return response
        finally:
            process_time = time.time() - start_time
            self.logger.info(
                f"{request.method} {request.url.path} "
                f"completed in {process_time:.3f}s "
                f"status_code={getattr(response, 'status_code', 500)}"
            )

class MetricsMiddleware(BaseHTTPMiddleware):
    """指标收集中间件"""
    
    def __init__(self, app, metrics_collector: MetricsCollector):
        super().__init__(app)
        self.metrics_collector = metrics_collector

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录请求指标
        self.metrics_collector.record_request_metrics({
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration': process_time
        })
        
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """CORS中间件"""
    
    def __init__(self, app, allow_origins: list = None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response
