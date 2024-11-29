import numpy as np
import tenseal as ts
from typing import List, Dict, Any, Optional
import logging

class FHEEngine:
    """同态加密核心引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化FHE引擎
        Args:
            config: FHE配置参数
        """
        self.config = config
        self.context = self._create_context()
        self.logger = logging.getLogger(__name__)
        
    def _create_context(self) -> ts.Context:
        """创建FHE上下文"""
        try:
            context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=self.config.get('poly_modulus_degree', 8192),
                coeff_mod_bit_sizes=self.config.get('coeff_mod_bit_sizes', [60, 40, 40, 60])
            )
            context.global_scale = 2**40
            return context
        except Exception as e:
            self.logger.error(f"创建FHE上下文失败: {str(e)}")
            raise

    def encrypt(self, data: np.ndarray) -> ts.CKKSVector:
        """加密数据"""
        try:
            return ts.ckks_vector(self.context, data)
        except Exception as e:
            self.logger.error(f"数据加密失败: {str(e)}")
            raise

    def decrypt(self, encrypted_data: ts.CKKSVector) -> np.ndarray:
        """解密数据"""
        try:
            return encrypted_data.decrypt()
        except Exception as e:
            self.logger.error(f"数据解密失败: {str(e)}")
            raise

    def compute(self, 
                encrypted_data: ts.CKKSVector, 
                operation: str, 
                params: Optional[Dict[str, Any]] = None) -> ts.CKKSVector:
        """执行同态计算"""
        try:
            if operation == "add":
                return encrypted_data + params.get("value", 0)
            elif operation == "multiply":
                return encrypted_data * params.get("value", 1)
            elif operation == "mean":
                return encrypted_data.mean()
            elif operation == "sum":
                return encrypted_data.sum()
            else:
                raise ValueError(f"不支持的操作: {operation}")
        except Exception as e:
            self.logger.error(f"同态计算失败: {str(e)}")
            raise