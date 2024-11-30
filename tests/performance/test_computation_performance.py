def test_computation_latency(distributed_setup):
    """测试计算延迟"""
    from eon.core.proto import computation_pb2
    import json
    
    node = distributed_setup[0]
    latencies = []
    
    for _ in range(100):
        start_time = time.time()
        request = computation_pb2.ComputationRequest(
            data_id="test-data",
            operation="add",
            params=json.dumps({"value": 1.0}).encode()
        )
        node.SubmitComputation(request, None)
        latencies.append(time.time() - start_time)
    
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = np.percentile(latencies, 95)
    
    print(f"\nLatency Statistics:")
    print(f"- Average: {avg_latency*1000:.2f}ms")
    print(f"- 95th percentile: {p95_latency*1000:.2f}ms")

def test_concurrent_load(distributed_setup):
    """测试并发负载"""
    from eon.core.proto import computation_pb2
    import json
    
    concurrent_users = [10, 50, 100]
    task_per_user = 100
    
    for num_users in concurrent_users:
        metrics = PerformanceMetrics()
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = []
            for user in range(num_users):
                for task in range(task_per_user):
                    node = distributed_setup[task % len(distributed_setup)]
                    request = computation_pb2.ComputationRequest(
                        data_id=f"user-{user}-task-{task}",
                        operation="add",
                        params=json.dumps({"value": 1.0}).encode()
                    )
                    futures.append(executor.submit(node.SubmitComputation, request, None))
            
            for future in as_completed(futures):
                try:
                    response = future.result()
                    if response.status == "submitted":
                        metrics.completed_tasks += 1
                    else:
                        metrics.errors += 1
                except Exception:
                    metrics.errors += 1
        
        metrics.stop()
        print(f"\nLoad Test Results ({num_users} concurrent users):")
        print(f"- Throughput: {metrics.throughput:.2f} tasks/s")
        print(f"- Error rate: {(metrics.errors/(num_users*task_per_user))*100:.1f}%")