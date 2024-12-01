
import pytest
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class DistributedPerformanceTester:
    def __init__(self, base_config: Dict[str, Any], logger: logging.Logger):
        self.base_config = base_config
        self.logger = logger
        self.results_data = []
        
    async def _setup_environment(self, node_count: int) -> Dict[str, Any]:
        """设置测试环境"""
        self.logger.info(f"Setting up test environment with {node_count} nodes")
        return {
            'coordinator': {
                'host': self.base_config['coordinator']['host'],
                'port': self.base_config['coordinator']['port']
            },
            'compute_nodes': [
                {
                    'host': self.base_config['compute_node']['host'],
                    'port': self.base_config['compute_node']['base_port'] + i
                }
                for i in range(node_count)
            ]
        }

    async def test_configuration(self, 
                               node_count: int, 
                               data_size: int, 
                               batch_size: int) -> Dict[str, float]:
        """测试特定配置"""
        start_time = datetime.now()
        self.logger.info(f"\nTesting configuration:")
        self.logger.info(f"Nodes: {node_count}, Data Size: {data_size}, Batch Size: {batch_size}")
        
        env = await self._setup_environment(node_count)
        
        # 模拟数据处理时间，根据节点数和数据量计算
        process_time = data_size / (node_count * batch_size) * 0.1
        await asyncio.sleep(process_time)  # 模拟实际处理时间
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 计算性能指标
        throughput = data_size / duration
        latency = duration * 1000  # 转换为毫秒
        cpu_usage = 50 + (node_count * 2)  # 模拟CPU使用率随节点数增加
        memory_usage = 1024 * node_count  # 模拟内存使用随节点数线性增长
        
        metrics = {
            'throughput': throughput,
            'latency': latency,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'duration': duration,
            'process_time': process_time
        }
        
        # 记录结果数据
        self.results_data.append({
            'node_count': node_count,
            'data_size': data_size,
            'batch_size': batch_size,
            **metrics
        })
        
        return metrics

    async def run_scale_test(self,
                           performance_config: Dict[str, Any]) -> List[Dict]:
        """运行可扩展性测试"""
        results = []
        total_start_time = datetime.now()
        
        node_counts = performance_config['node_counts']
        data_sizes = performance_config['data_sizes']
        batch_sizes = performance_config['batch_sizes']
        
        for node_count in node_counts:
            for data_size in data_sizes:
                for batch_size in batch_sizes:
                    try:
                        metrics = await self.test_configuration(
                            node_count=node_count,
                            data_size=data_size,
                            batch_size=batch_size
                        )
                        
                        results.append({
                            'config': {
                                'node_count': node_count,
                                'data_size': data_size,
                                'batch_size': batch_size
                            },
                            'metrics': metrics
                        })
                    except Exception as e:
                        self.logger.error(f"Error testing configuration: {str(e)}")
                        
        total_duration = (datetime.now() - total_start_time).total_seconds()
        self.logger.info(f"Total test duration: {total_duration:.2f} seconds")
        
        # 分析和可视化结果
        self.analyze_results()
        
        return results
    
    def analyze_results(self):
        """分析和可视化测试结果"""
        df = pd.DataFrame(self.results_data)
        
        # 1. 吞吐量分析
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='node_count', y='throughput')
        plt.title('Throughput by Node Count')
        plt.ylabel('Throughput (ops/sec)')
        plt.xlabel('Number of Nodes')
        plt.savefig('throughput_analysis.png')
        plt.close()
        
        # 2. 延迟分析
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='node_count', y='latency')
        plt.title('Latency by Node Count')
        plt.ylabel('Latency (ms)')
        plt.xlabel('Number of Nodes')
        plt.savefig('latency_analysis.png')
        plt.close()
        
        # 3. 资源使用分析
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        sns.boxplot(data=df, x='node_count', y='cpu_usage')
        plt.title('CPU Usage by Node Count')
        plt.ylabel('CPU Usage (%)')
        
        plt.subplot(1, 2, 2)
        sns.boxplot(data=df, x='node_count', y='memory_usage')
        plt.title('Memory Usage by Node Count')
        plt.ylabel('Memory Usage (MB)')
        plt.savefig('resource_analysis.png')
        plt.close()
        
        # 打印统计结果
        print("\n=== Performance Analysis ===")
        for node_count in df['node_count'].unique():
            node_data = df[df['node_count'] == node_count]
            print(f"\nNode Count: {node_count}")
            print(f"Average Throughput: {node_data['throughput'].mean():.2f} ops/sec")
            print(f"Average Latency: {node_data['latency'].mean():.2f} ms")
            print(f"Average CPU Usage: {node_data['cpu_usage'].mean():.2f}%")
            print(f"Average Memory Usage: {node_data['memory_usage'].mean():.2f} MB")

@pytest.mark.performance
@pytest.mark.asyncio(scope="function")
async def test_large_scale_performance(base_config: Dict[str, Any], 
                                     performance_config: Dict[str, Any], 
                                     logger: logging.Logger):
    """大规模分布式性能测试"""
    logger.info("Starting performance test")
    
    # 修改性能配置以包含更多节点
    performance_config['node_counts'] = [2, 4, 20]  # 测试2、4和20个节点
    performance_config['data_sizes'] = [1000, 5000, 10000]  # 增加数据规模
    performance_config['batch_sizes'] = [100, 500, 1000]  # 增加批处理大小选项
    
    # 初始化测试器
    tester = DistributedPerformanceTester(base_config, logger)
    
    # 运行测试
    results = await tester.run_scale_test(performance_config)
    
    # 验证结果
    assert len(results) > 0, "No test results were generated"
    for result in results:
        assert result['metrics']['throughput'] > 0, "Throughput should be positive"
        assert result['metrics']['latency'] > 0, "Latency should be positive"
        assert result['metrics']['duration'] > 0, "Duration should be positive"
        assert 'config' in result, "Result should contain configuration"
        
    logger.info("Test completed successfully")
    logger.info(f"Total configurations tested: {len(results)}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])

