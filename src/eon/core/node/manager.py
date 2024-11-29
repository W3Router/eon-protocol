```python
from typing import Dict, List, Any, Optional
import threading
import logging
from .client import ComputationClient

class NodeManager:
    """节点管理器，处理节点注册和状态管理"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.clients: Dict[str, ComputationClient] = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def register_node(self, node_info: Dict[str, Any]) -> bool:
        """注册新节点"""
        try:
            with self.lock:
                node_id = node_info['id']
                if node_id in self.nodes:
                    self.logger.warning(f"节点已存在: {node_id}")
                    return False

                # 创建到新节点的客户端连接
                client = ComputationClient(node_info['address'])
                self.clients[node_id] = client
                
                # 存储节点信息
                self.nodes[node_id] = {
                    'info': node_info,
                    'status': 'CONNECTED',
                    'active_tasks': 0,
                    'last_seen': datetime.now()
                }
                
                self.logger.info(f"节点注册成功: {node_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"节点注册失败: {str(e)}")
            return False

    def get_available_nodes(self) -> List[str]:
        """获取可用节点列表"""
        try:
            with self.lock:
                return [
                    node_id for node_id, node in self.nodes.items()
                    if node['status'] == 'CONNECTED' and 
                    node['active_tasks'] < self.config.get('max_tasks_per_node', 5)
                ]
        except Exception as e:
            self.logger.error(f"获取可用节点失败: {str(e)}")
            return []

    def assign_task(self, node_id: str) -> bool:
        """分配任务给节点"""
        try:
            with self.lock:
                if node_id not in self.nodes:
                    return False
                    
                node = self.nodes[node_id]
                if node['status'] != 'CONNECTED':
                    return False
                    
                node['active_tasks'] += 1
                return True
                
        except Exception as e:
            self.logger.error(f"任务分配失败: {str(e)}")
            return False

    def complete_task(self, node_id: str):
        """标记节点任务完成"""
        try:
            with self.lock:
                if node_id in self.nodes:
                    self.nodes[node_id]['active_tasks'] -= 1
        except Exception as e:
            self.logger.error(f"标记任务完成失败: {str(e)}")

    def get_node_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点状态"""
        try:
            with self.lock:
                if node_id not in self.nodes:
                    return None
                    
                client = self.clients[node_id]
                status = client.get_node_status(node_id)
                
                # 更新本地状态
                self.nodes[node_id].update({
                    'status': status['status'],
                    'active_tasks': status['active_tasks'],
                    'metrics': status['metrics'],
                    'last_seen': datetime.now()
                })
                
                return self.nodes[node_id]
                
        except Exception as e:
            self.logger.error(f"获取节点状态失败: {str(e)}")
            return None

    def check_nodes_health(self):
        """检查所有节点健康状态"""
        try:
            with self.lock:
                offline_threshold = timedelta(
                    seconds=self.config.get('node_offline_threshold', 30)
                )
                current_time = datetime.now()
                
                for node_id, node in list(self.nodes.items()):
                    # 检查节点最后响应时间
                    if current_time - node['last_seen'] > offline_threshold:
                        node['status'] = 'DISCONNECTED'
                        self.logger.warning(f"节点离线: {node_id}")
                    
                    # 获取最新状态
                    self.get_node_status(node_id)
                    
        except Exception as e:
            self.logger.error(f"节点健康检查失败: {str(e)}")

    def shutdown(self):
        """关闭所有连接"""
        try:
            with self.lock:
                for client in self.clients.values():
                    client.close()
                self.clients.clear()
                self.nodes.clear()
        except Exception as e:
            self.logger.error(f"关闭连接失败: {str(e)}")
```
