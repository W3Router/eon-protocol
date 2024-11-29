```python
import streamlit as st
import pandas as pd
import plotly.express as px
from eon.utils.metrics import MetricsCollector
import time

def render_dashboard():
    """渲染性能监控面板"""
    st.title("EON Protocol Performance Dashboard")
    
    # 获取指标数据
    metrics_collector = MetricsCollector()
    metrics = metrics_collector.get_metrics_summary()
    
    # 系统状态
    st.header("System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "CPU Usage",
            f"{metrics['system']['average_cpu']:.1f}%"
        )
        
    with col2:
        st.metric(
            "Memory Usage",
            f"{metrics['system']['average_memory']:.1f}%"
        )
        
    with col3:
        st.metric(
            "Disk Usage",
            f"{metrics['system']['average_disk']:.1f}%"
        )
    
    # 请求统计
    st.header("Request Statistics")
    requests_df = pd.DataFrame(metrics['requests'])
    
    # 请求响应时间图表
    fig_response_time = px.line(
        requests_df,
        x='timestamp',
        y='duration',
        title='Request Response Time'
    )
    st.plotly_chart(fig_response_time)
    
    # 状态码分布
    status_codes = pd.Series(metrics['requests']['status_codes'])
    fig_status = px.pie(
        values=status_codes.values,
        names=status_codes.index,
        title='Status Code Distribution'
    )
    st.plotly_chart(fig_status)
    
    # 计算性能
    st.header("Computation Performance")
    comp_df = pd.DataFrame(metrics['computations'])
    
    # 计算耗时分布
    fig_comp_time = px.histogram(
        comp_df,
        x='duration',
        title='Computation Duration Distribution'
    )
    st.plotly_chart(fig_comp_time)
    
    # 成功率指标
    success_rate = metrics['computations']['success_rate'] * 100
    st.metric("Computation Success Rate", f"{success_rate:.1f}%")
    
    # 自动刷新
    if st.button("Refresh"):
        st.experimental_rerun()
    st.text("Dashboard auto-refreshes every 60 seconds")
    time.sleep(60)
    st.experimental_rerun()

if __name__ == '__main__':
    render_dashboard()
```