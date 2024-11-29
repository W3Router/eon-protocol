
from typing import Dict, Any, Optional
import json
import hashlib
import base64
import uuid
import time
from datetime import datetime, timezone
import logging

class Utils:
    """工具类"""
    
    @staticmethod
    def generate_id() -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())

    @staticmethod
    def hash_data(data: bytes) -> str:
        """计算数据哈希"""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def encode_base64(data: bytes) -> str:
        """Base64编码"""
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def decode_base64(data: str) -> bytes:
        """Base64解码"""
        return base64.b64decode(data.encode('utf-8'))

    @staticmethod
    def to_json(obj: Any) -> str:
        """对象转JSON"""
        return json.dumps(obj, default=str)

    @staticmethod
    def from_json(data: str) -> Any:
        """JSON转对象"""
        return json.loads(data)

    @staticmethod
    def timestamp_to_iso(timestamp: float) -> str:
        """时间戳转ISO格式"""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

    @staticmethod
    def iso_to_timestamp(iso_time: str) -> float:
        """ISO格式转时间戳"""
        return datetime.fromisoformat(iso_time).timestamp()

class Timer:
    """计时器"""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.start_time = None
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if self.name:
            self.logger.info(f"{self.name} took {duration:.3f} seconds")
        return False

    def elapsed(self) -> float:
        """获取经过时间"""
        return time.time() - self.start_time
