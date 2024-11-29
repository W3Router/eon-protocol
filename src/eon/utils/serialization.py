```python
import pickle
import base64
from typing import Any
import logging
import numpy as np
import tenseal as ts

class Serializer:
    """序列化工具"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def serialize_encrypted_data(self, data: ts.CKKSVector) -> bytes:
        """序列化加密数据"""
        try:
            return data.serialize()
        except Exception as e:
            self.logger.error(f"Failed to serialize encrypted data: {str(e)}")
            raise

    def deserialize_encrypted_data(self, data: bytes) -> ts.CKKSVector:
        """反序列化加密数据"""
        try:
            return ts.lazy_ckks_vector_from(data)
        except Exception as e:
            self.logger.error(f"Failed to deserialize encrypted data: {str(e)}")
            raise

    def serialize_numpy(self, array: np.ndarray) -> str:
        """序列化NumPy数组"""
        try:
            return base64.b64encode(pickle.dumps(array)).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to serialize numpy array: {str(e)}")
            raise

    def deserialize_numpy(self, data: str) -> np.ndarray:
        """反序列化NumPy数组"""
        try:
            return pickle.loads(base64.b64decode(data.encode('utf-8')))
        except Exception as e:
            self.logger.error(f"Failed to deserialize numpy array: {str(e)}")
            raise
```