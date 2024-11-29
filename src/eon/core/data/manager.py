from typing import Dict, Any, Optional
import numpy as np
import json
from pathlib import Path
import logging

class DataManager:
    """数据管理器，处理数据存储和检索"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = Path(config.get('storage_path', './data'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def store_data(self, 
                   data: np.ndarray, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """存储数据和元数据"""
        try:
            data_id = self._generate_id()
            data_path = self.storage_path / f"{data_id}.npz"
            meta_path = self.storage_path / f"{data_id}.json"
            
            # 存储数据
            np.savez_compressed(data_path, data=data)
            
            # 存储元数据
            if metadata:
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f)
                    
            self.logger.info(f"数据存储成功: {data_id}")
            return data_id
            
        except Exception as e:
            self.logger.error(f"数据存储失败: {str(e)}")
            raise
            
    def retrieve_data(self, data_id: str) -> tuple[np.ndarray, Optional[Dict[str, Any]]]:
        """检索数据和元数据"""
        try:
            data_path = self.storage_path / f"{data_id}.npz"
            meta_path = self.storage_path / f"{data_id}.json"
            
            # 加载数据
            data = np.load(data_path)['data']
            
            # 加载元数据
            metadata = None
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
                    
            self.logger.info(f"数据检索成功: {data_id}")
            return data, metadata
            
        except Exception as e:
            self.logger.error(f"数据检索失败: {str(e)}")
            raise
            
    def _generate_id(self) -> str:
        """生成唯一数据ID"""
        import uuid
        return str(uuid.uuid4())
        