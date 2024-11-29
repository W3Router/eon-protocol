
from typing import Dict, Any, Optional, List
import numpy as np
from enum import Enum
import logging

class DataType(str, Enum):
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BINARY = "binary"

class ValidationError(Exception):
    """数据验证错误"""
    pass

class DataValidator:
    """数据验证器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def validate_data(self, data: np.ndarray, 
                     schema: Dict[str, Any]) -> bool:
        """验证数据"""
        try:
            # 验证数据类型
            if not self._validate_dtype(data, schema.get('dtype')):
                return False

            # 验证数据形状
            if not self._validate_shape(data, schema.get('shape')):
                return False

            # 验证数值范围
            if not self._validate_range(data, schema.get('range')):
                return False

            # 验证非空值
            if not self._validate_non_null(data, schema.get('allow_null', False)):
                return False

            return True
            
        except Exception as e:
            self.logger.error(f"Data validation failed: {str(e)}")
            raise ValidationError(str(e))

    def _validate_dtype(self, data: np.ndarray, expected_dtype: Optional[str]) -> bool:
        """验证数据类型"""
        if not expected_dtype:
            return True
            
        return str(data.dtype) == expected_dtype

    def _validate_shape(self, data: np.ndarray, expected_shape: Optional[tuple]) -> bool:
        """验证数据形状"""
        if not expected_shape:
            return True
            
        return data.shape == tuple(expected_shape)

    def _validate_range(self, data: np.ndarray, 
                       value_range: Optional[tuple]) -> bool:
        """验证数值范围"""
        if not value_range:
            return True
            
        min_val, max_val = value_range
        return np.all((data >= min_val) & (data <= max_val))

    def _validate_non_null(self, data: np.ndarray, allow_null: bool) -> bool:
        """验证非空值"""
        if allow_null:
            return True
            
        return not np.any(np.isnan(data))

    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """验证架构定义"""
        required_fields = ['dtype', 'shape']
        return all(field in schema for field in required_fields)

    def generate_validation_report(self, data: np.ndarray) -> Dict[str, Any]:
        """生成数据验证报告"""
        return {
            'shape': data.shape,
            'dtype': str(data.dtype),
            'missing_values': np.isnan(data).sum(),
            'unique_values': len(np.unique(data)),
            'min_value': float(np.nanmin(data)),
            'max_value': float(np.nanmax(data)),
            'mean_value': float(np.nanmean(data)),
            'std_value': float(np.nanstd(data))
        }
