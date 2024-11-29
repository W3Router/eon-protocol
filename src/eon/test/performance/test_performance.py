
import pytest
import numpy as np
import time
from eon.core.fhe.engine import FHEEngine
from eon.utils.metrics import MetricsCollector

def measure_time(func):
    """测量函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, end - start
    return wrapper

@pytest.mark.performance
class TestPerformance:
    """性能测试类"""
    
    def setup_method(self):
        """测试设置"""
        self.engine = FHEEngine({
            'poly_modulus_degree': 8192,
            'coeff_mod_bit_sizes': [60, 40, 40, 60]
        })
        self.metrics = MetricsCollector()

    @measure_time
    def test_encryption_performance(self):
        """测试加密性能"""
        data_sizes = [100, 1000, 10000]
        results = []
        
        for size in data_sizes:
            data = np.random.rand(size)
            start = time.time()
            encrypted = self.engine.encrypt(data)
            duration = time.time() - start
            
            results.append({
                'size': size,
                'duration': duration,
                'throughput': size / duration
            })
            
        return results

    @measure_time
    def test_computation_performance(self):
        """测试计算性能"""
        operations = ['add', 'multiply', 'mean']
        data = np.random.rand(1000)
        encrypted = self.engine.encrypt(data)
        results = []
        
        for op in operations:
            start = time.time()
            _ = self.engine.compute(encrypted, op)
            duration = time.time() - start
            
            results.append({
                'operation': op,
                'duration': duration
            })
            
        return results

    @measure_time
    def test_concurrent_operations(self):
        """测试并发性能"""
        import concurrent.futures
        
        data = np.random.rand(1000)
        encrypted = self.engine.encrypt(data)
        results = []
        
        def run_operation():
            return self.engine.compute(encrypted, "mean")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            start = time.time()
            futures = [executor.submit(run_operation) for _ in range(10)]
            concurrent.futures.wait(futures)
            duration = time.time() - start
            
        return {'total_operations': len(futures), 'duration': duration}

    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # 执行大量操作
        data = np.random.rand(10000)
        encrypted = self.engine.encrypt(data)
        for _ in range(100):
            _ = self.engine.compute(encrypted, "mean")
            
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        return {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': memory_increase
        }
