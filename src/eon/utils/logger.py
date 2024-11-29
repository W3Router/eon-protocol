```python
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any, Optional
import json
import threading
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """自定义日志格式化器"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def format(self, record):
        """格式化日志记录"""
        log_obj = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加异常信息
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, 'extra_data'):
            log_obj['extra_data'] = record.extra_data

        return json.dumps(log_obj)

class LoggerManager:
    """日志管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if hasattr(self, 'initialized'):
            return
            
        self.config = config or {}
        self.loggers = {}
        self.setup_default_logger()
        self.initialized = True

    def setup_default_logger(self):
        """设置默认日志记录器"""
        # 创建日志目录
        log_dir = Path(self.config.get('log_dir', 'logs'))
        log_dir.mkdir(parents=True, exist_ok=True)

        # 创建默认处理器
        handlers = []
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter())
        handlers.append(console_handler)

        # 文件处理器
        if self.config.get('file_logging', True):
            file_handler = RotatingFileHandler(
                log_dir / 'eon.log',
                maxBytes=self.config.get('max_bytes', 10_000_000),
                backupCount=self.config.get('backup_count', 5)
            )
            file_handler.setFormatter(CustomFormatter())
            handlers.append(file_handler)

        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config.get('level', 'INFO'))
        
        # 清除现有处理器并添加新处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        for handler in handlers:
            root_logger.addHandler(handler)

    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建命名日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]

    def log_with_context(self, logger: logging.Logger, level: str, 
                        message: str, context: Dict[str, Any]):
        """带上下文信息的日志记录"""
        extra = {'extra_data': context}
        logger_method = getattr(logger, level.lower())
        logger_method(message, extra=extra)

def setup_logging(config: Dict[str, Any]) -> LoggerManager:
    """设置日志系统"""
    return LoggerManager(config)

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    return LoggerManager().get_logger(name)
```