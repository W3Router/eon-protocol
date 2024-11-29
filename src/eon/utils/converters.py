
from typing import Dict, Any, Union, List
import numpy as np
import pandas as pd
import json
from datetime import datetime

class DataConverter:
    """数据格式转换器"""
    
    @staticmethod
    def to_numpy(data: Union[List, pd.DataFrame, Dict]) -> np.ndarray:
        """转换为NumPy数组"""
        if isinstance(data, np.ndarray):
            return data
        elif isinstance(data, list):
            return np.array(data)
        elif isinstance(data, pd.DataFrame):
            return data.to_numpy()
        elif isinstance(data, dict):
            return np.array(list(data.values()))
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    @staticmethod
    def to_pandas(data: Union[np.ndarray, List, Dict]) -> pd.DataFrame:
        """转换为Pandas DataFrame"""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, np.ndarray):
            return pd.DataFrame(data)
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame.from_dict(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    @staticmethod
    def to_json(data: Union[np.ndarray, pd.DataFrame]) -> str:
        """转换为JSON字符串"""
        if isinstance(data, np.ndarray):
            return json.dumps({
                'type': 'numpy',
                'data': data.tolist(),
                'dtype': str(data.dtype),
                'shape': data.shape
            })
        elif isinstance(data, pd.DataFrame):
            return data.to_json()
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    @staticmethod
    def from_json(json_str: str) -> Union[np.ndarray, pd.DataFrame]:
        """从JSON字符串转换"""
        data = json.loads(json_str)
        if isinstance(data, dict) and data.get('type') == 'numpy':
            arr = np.array(data['data'], dtype=data['dtype'])
            return arr.reshape(data['shape'])
        else:
            return pd.read_json(json_str)
