
#!/bin/bash

# 设置环境变量
export EON_ENV="production"
export EON_CONFIG_PATH="/etc/eon/config.yaml"

# 检查参数
if [ $# -eq 0 ]; then
    echo "Usage: $0 {coordinator|compute|api}"
    exit 1
fi

# 创建必要的目录
mkdir -p /var/log/eon
mkdir -p /var/lib/eon/data
mkdir -p /etc/eon

# 复制配置文件
cp config/production.yaml $EON_CONFIG_PATH

# 安装依赖
pip install -e .

# 根据参数启动不同的组件
case "$1" in
    coordinator)
        echo "Starting coordinator node..."
        eon start -c $EON_CONFIG_PATH -r coordinator
        ;;
    compute)
        if [ -z "$2" ]; then
            echo "Node ID required for compute node"
            exit 1
        fi
        echo "Starting compute node $2..."
        eon start -c $EON_CONFIG_PATH -r compute -n "$2"
        ;;
    api)
        echo "Starting API server..."
        uvicorn eon.api.main:app --host 0.0.0.0 --port 8000
        ;;
    *)
        echo "Invalid component: $1"
        exit 1
        ;;
esac
