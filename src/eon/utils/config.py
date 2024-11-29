import yaml
from typing import Dict, Any
import logging

class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"配置加载成功: {self.config_path}")
            return config
        except Exception as e:
            self.logger.error(f"配置加载失败: {str(e)}")
            raise
            
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value.get(k, default)
                if value is None:
                    return default
            return value
        except Exception:
            return default