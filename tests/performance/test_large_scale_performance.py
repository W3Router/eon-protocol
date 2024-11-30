# tests/performance/test_large_scale_performance.py
import pytest
import numpy as np
import asyncio
import time
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    node_count: int
    data_size: int
    batch_size: int
    total_time: float
    encryption_time: float
    computation_time: float
    decryption_time: float
    throughput: float
    latency: float
    success_rate: float
    timestamp: datetime

class DistributedPerformanceTester:
    """分布式性能测试器"""
    
    def __init__(self, base_config: Dict[str, Any]):
        self.base_config = base_config
        self.results: List[PerformanceMetrics] = []
        self.output_dir = Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    async def run_scale_test(self, 
                           node_counts: List[int],
                           data_sizes: List[int],
                           batch_sizes: List[int]):
        """运行规模测试"""
        for node_count in node_counts:
            for data_size in data_sizes:
                for batch_size in batch_sizes:
                    metrics = await self.test_configuration(
                        node_count=node_count,
                        data_size=data_size,
                        batch_size=batch_size
                    )
                    self.results.append(metrics)
                    
                    # 实时输出结果
                    self._print_metrics(metrics)
        
        # 生成报告
        self.generate_report()

    async def test_configuration(self, 
                               node_count: int,
                               data_size: int,
                               batch_size: int) -> PerformanceMetrics:
        """测试特定配置"""
        self.logger.info(f"\nTesting configuration:")
        self.logger.info(f"Nodes: {node_count}, Data Size: {data_size}, Batch Size: {batch_size}")

        # 配置测试环境
        env = await self._setup_environment(node_count)
        try:
            # 准备测试数据
            data = np.random.rand(data_size)
            batches = np.array_split(data, data_size // batch_size)

            start_time = time.time()
            successes = 0
            
            # 加密阶段
            encryption_start = time.time()
            encrypted_batches = []
            for batch in batches:
                encrypted_batch = env['coordinator'].encrypt_data(batch)
                encrypted_batches.append(encrypted_batch)
            encryption_time = time.time() - encryption_start

            # 计算阶段
            computation_start = time.time()
            tasks = []
            for encrypted_batch in encrypted_batches:
                task = await env['coordinator'].submit_task({
                    'operation': 'mean',
                    'data': encrypted_batch,
                    'batch_size': batch_size
                })
                tasks.append(task)

            # 等待结果
            results = await asyncio.gather(*[
                env['coordinator'].get_task_result(task['id'])
                for task in tasks
            ], return_exceptions=True)
            computation_time = time.time() - computation_start

            # 解密阶段
            decryption_start = time.time()
            decrypted_results = []
            for result in results:
                if not isinstance(result, Exception):
                    decrypted_result = env['coordinator'].decrypt_data(result)
                    decrypted_results.append(decrypted_result)
                    successes += 1
            decryption_time = time.time() - decryption_start

            total_time = time.time() - start_time
            success_rate = successes / len(batches)
            throughput = data_size / total_time
            latency = total_time / len(batches)

            return PerformanceMetrics(
                node_count=node_count,
                data_size=data_size,
                batch_size=batch_size,
                total_time=total_time,
                encryption_time=encryption_time,
                computation_time=computation_time,
                decryption_time=decryption_time,
                throughput=throughput,
                latency=latency,
                success_rate=success_rate,
                timestamp=datetime.now()
            )

        finally:
            await self._cleanup_environment(env)

    def _print_metrics(self, metrics: PerformanceMetrics):
        """打印性能指标"""
        self.logger.info("\n=== Performance Test Results ===")
        self.logger.info(f"Configuration:")
        self.logger.info(f"  Number of Nodes: {metrics.node_count}")
        self.logger.info(f"  Data Size: {metrics.data_size}")
        self.logger.info(f"  Batch Size: {metrics.batch_size}")
        self.logger.info("\nTiming Metrics:")
        self.logger.info(f"  Total Time: {metrics.total_time:.3f}s")
        self.logger.info(f"  Encryption Time: {metrics.encryption_time:.3f}s")
        self.logger.info(f"  Computation Time: {metrics.computation_time:.3f}s")
        self.logger.info(f"  Decryption Time: {metrics.decryption_time:.3f}s")
        self.logger.info("\nPerformance Metrics:")
        self.logger.info(f"  Throughput: {metrics.throughput:.2f} items/s")
        self.logger.info(f"  Latency: {metrics.latency*1000:.2f}ms")
        self.logger.info(f"  Success Rate: {metrics.success_rate*100:.2f}%")

    def generate_report(self):
        """生成性能报告"""
        # 转换为DataFrame
        df = pd.DataFrame([vars(m) for m in self.results])
        
        # 保存原始数据
        df.to_csv(self.output_dir / "performance_results.csv", index=False)
        
        # 生成图表
        self._generate_plots(df)
        
        # 生成HTML报告
        self._generate_html_report(df)

    def _generate_plots(self, df: pd.DataFrame):
        """生成性能图表"""
        # 设置风格
        plt.style.use('seaborn')
        
        # 节点扩展性图表
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x='node_count', y='throughput', hue='data_size')
        plt.title('Node Scalability Analysis')
        plt.xlabel('Number of Nodes')
        plt.ylabel('Throughput (items/s)')
        plt.savefig(self.output_dir / 'scalability.png')
        plt.close()
        
        # 延迟分布图
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x='node_count', y='latency')
        plt.title('Latency Distribution by Node Count')
        plt.xlabel('Number of Nodes')
        plt.ylabel('Latency (s)')
        plt.savefig(self.output_dir / 'latency.png')
        plt.close()
        
        # 时间分布图
        plt.figure(figsize=(12, 6))
        df_melted = pd.melt(df, 
                           id_vars=['node_count'],
                           value_vars=['encryption_time', 'computation_time', 'decryption_time'],
                           var_name='Phase',
                           value_name='Time')
        sns.boxplot(data=df_melted, x='node_count', y='Time', hue='Phase')
        plt.title('Time Distribution by Processing Phase')
        plt.xlabel('Number of Nodes')
        plt.ylabel('Time (s)')
        plt.savefig(self.output_dir / 'time_distribution.png')
        plt.close()

    def _generate_html_report(self, df: pd.DataFrame):
        """生成HTML报告"""
        html_content = f"""
        <html>
        <head>
            <title>Distributed Performance Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ margin: 20px 0; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Distributed Performance Test Report</h1>
            <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="metric">
                <h2>Summary Statistics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Mean</th>
                        <th>Min</th>
                        <th>Max</th>
                    </tr>
                    <tr>
                        <td>Throughput (items/s)</td>
                        <td>{df['throughput'].mean():.2f}</td>
                        <td>{df['throughput'].min():.2f}</td>
                        <td>{df['throughput'].max():.2f}</td>
                    </tr>
                    <tr>
                        <td>Latency (ms)</td>
                        <td>{df['latency'].mean()*1000:.2f}</td>
                        <td>{df['latency'].min()*1000:.2f}</td>
                        <td>{df['latency'].max()*1000:.2f}</td>
                    </tr>
                    <tr>
                        <td>Success Rate (%)</td>
                        <td>{df['success_rate'].mean()*100:.2f}</td>
                        <td>{df['success_rate'].min()*100:.2f}</td>
                        <td>{df['success_rate'].max()*100:.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div class="metric">
                <h2>Scalability Analysis</h2>
                <img src="scalability.png" alt="Scalability Analysis">
            </div>
            
            <div class="metric">
                <h2>Latency Analysis</h2>
                <img src="latency.png" alt="Latency Analysis">
            </div>
            
            <div class="metric">
                <h2>Processing Time Analysis</h2>
                <img src="time_distribution.png" alt="Time Distribution">
            </div>
            
            <div class="metric">
                <h2>Detailed Results</h2>
                {df.to_html()}
            </div>
        </body>
        </html>
        """
        
        with open(self.output_dir / "report.html", "w") as f:
            f.write(html_content)

@pytest.mark.asyncio
async def test_large_scale_performance():
    """大规模分布式性能测试"""
    base_config = {
        'coordinator': {
            'host': 'localhost',
            'port': 50051,
            'max_workers': 20
        },
        'compute_node': {
            'host': 'localhost',
            'base_port': 50052,
            'max_workers': 5
        }
    }
    
    tester = DistributedPerformanceTester(base_config)
    
    # 测试配置
    node_counts = [10, 20, 50, 100]  # 节点数量
    data_sizes = [10000, 50000, 100000]  # 数据大小
    batch_sizes = [1000, 5000]  # 批处理大小
    
    await tester.run_scale_test(
        node_counts=node_counts,
        data_sizes=data_sizes,
        batch_sizes=batch_sizes
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pytest.main(["-v", "--log-cli-level=INFO", __file__])