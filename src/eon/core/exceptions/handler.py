
from typing import Dict, Any
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import logging
from .exceptions import (
    EONBaseException,
    ValidationError,
    AuthenticationError,
    ComputationError,
    DataError
)

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def register(self, app: FastAPI):
        """注册错误处理器"""
        @app.exception_handler(EONBaseException)
        async def base_exception_handler(request: Request, exc: EONBaseException):
            return self._handle_exception(exc)

        @app.exception_handler(ValidationError)
        async def validation_error_handler(request: Request, exc: ValidationError):
            return self._handle_exception(exc, status_code=400)

        @app.exception_handler(AuthenticationError)
        async def auth_error_handler(request: Request, exc: AuthenticationError):
            return self._handle_exception(exc, status_code=401)

        @app.exception_handler(ComputationError)
        async def computation_error_handler(request: Request, exc: ComputationError):
            return self._handle_exception(exc, status_code=500)

        @app.exception_handler(DataError)
        async def data_error_handler(request: Request, exc: DataError):
            return self._handle_exception(exc, status_code=422)

    def _handle_exception(self, exc: Exception, status_code: int = 500) -> JSONResponse:
        """处理异常"""
        self.logger.error(f"Error occurred: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": exc.__class__.__name__,
                "message": str(exc),
                "details": getattr(exc, 'details', None)
            }
        )

