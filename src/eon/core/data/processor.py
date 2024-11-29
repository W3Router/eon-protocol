
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
import logging
from ..fhe.engine import FHEEngine

@dataclass
class DataBatch:
    id: str
    data: np.ndarray
    metadata: Dict[str, Any]

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fhe_engine = FHEEngine(config.get('fhe', {}))
        self.logger = logging.getLogger(__name__)

    def preprocess_data(self, data: np.ndarray, 
                       params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """数据预处理"""
        try:
            # 数据标准化
            if params and params.get('normalize', False):
                data = (data - np.mean(data)) / np.std(data)
                
            # 处理缺失值
            if params and params.get('handle_missing', False):
                data = np.nan_to_num(data, nan=0.0)
                
            # 数据裁剪
            if params and 'clip_range' in params:
                min_val, max_val = params['clip_range']
                data = np.clip(data, min_val, max_val)
                
            return data
        except Exception as e:
            self.logger.error(f"数据预处理失败: {str(e)}")
            raise

    def split_data(self, data: np.ndarray, 
                  batch_size: int) -> List[DataBatch]:
        """数据分片"""
        try:
            batches = []
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                batch = DataBatch(
                    id=f"batch-{i//batch_size}",
                    data=batch_data,
                    metadata={
                        'start_index': i,
                        'size': len(batch_data)
                    }
                )
                batches.append(batch)
            return batches
        except Exception as e:
            self.logger.error(f"数据分片失败: {str(e)}")
            raise

    def encrypt_batch(self, batch: DataBatch) -> DataBatch:
        """加密数据批次"""
        try:
            encrypted_data = self.fhe_engine.encrypt(batch.data)
            return DataBatch(
                id=batch.id,
                data=encrypted_data,
                metadata={
                    **batch.metadata,
                    'encrypted': True
                }
            )
        except Exception as e:
            self.logger.error(f"数据批次加密失败: {str(e)}")
            raise

    def validate_data(self, data: np.ndarray, 
                     schema: Dict[str, Any]) -> bool:
        """数据验证"""
        try:
            # 检查维度
            if 'shape' in schema:
                if data.shape != tuple(schema['shape']):
                    return False
                    
            # 检查数据类型
            if 'dtype' in schema:
                if str(data.dtype) != schema['dtype']:
                    return False
                    
            # 检查值范围
            if 'range' in schema:
                min_val, max_val = schema['range']
                if np.any(data < min_val) or np.any(data > max_val):
                    return False
                    
            return True
        except Exception as e:
            self.logger.error(f"数据验证失败: {str(e)}")
            return False
