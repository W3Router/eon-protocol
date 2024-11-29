from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
from ..core.monitoring import MetricsCollector

router = APIRouter()
metrics_collector: Optional[MetricsCollector] = None

def init_monitoring(config: Dict[str, Any]):
    """初始化监控模块"""
    global metrics_collector
    metrics_collector = MetricsCollector(config)

@router.get("/metrics/node/{node_id}")
async def get_node_metrics(node_id: str) -> Dict[str, Any]:
    """获取节点当前指标"""
    try:
        if not metrics_collector:
            raise HTTPException(
                status_code=500,
                detail="监控模块未初始化"
            )
            
        metrics = metrics_collector.collect_node_metrics(node_id, 0)
        return {
            'node_id': metrics.node_id,
            'cpu_percent': metrics.cpu_percent,
            'memory_percent': metrics.memory_percent,
            'disk_usage_percent': metrics.disk_usage_percent,
            'network': {
                'sent_bytes': metrics.network_sent_bytes,
                'recv_bytes': metrics.network_recv_bytes
            },
            'active_tasks': metrics.active_tasks,
            'timestamp': metrics.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取节点指标失败: {str(e)}"
        )

@router.get("/metrics/history/{node_id}")
async def get_node_history(
    node_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> List[Dict[str, Any]]:
    """获取节点历史指标"""
    try:
        if not metrics_collector:
            raise HTTPException(
                status_code=500,
                detail="监控模块未初始化"
            )
            
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None
        
        metrics = metrics_collector.get_node_history(node_id, start, end)
        return [
            {
                'node_id': m.node_id,
                'cpu_percent': m.cpu_percent,
                'memory_percent': m.memory_percent,
                'disk_usage_percent': m.disk_usage_percent,
                'network': {
                    'sent_bytes': m.network_sent_bytes,
                    'recv_bytes': m.network_recv_bytes
                },
                'active_tasks': m.active_tasks,
                'timestamp': m.timestamp.isoformat()
            }
            for m in metrics
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取节点历史指标失败: {str(e)}"
        )

@router.get("/metrics/summary")
async def get_system_summary() -> Dict[str, Any]:
    """获取系统总体状况"""
    try:
        if not metrics_collector:
            raise HTTPException(
                status_code=500,
                detail="监控模块未初始化"
            )
            
        return metrics_collector.get_system_summary()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取系统摘要失败: {str(e)}"
        )