
# src/eon/core/node/__init__.py
from .manager import NodeManager
from .compute import ComputeNode
from .coordinator import CoordinatorNode
from .client import ComputationClient  # 修改这行

__all__ = ['NodeManager', 'ComputeNode', 'CoordinatorNode', 'ComputationClient']  # 修改这里

