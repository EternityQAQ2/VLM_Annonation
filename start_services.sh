#!/bin/bash

# 停止所有旧进程
echo "停止旧进程..."
pkill -9 -f "python3 app.py"
pkill -9 -f "vite --host"
sleep 2

# 启动后端
echo "启动后端服务 (端口5000)..."
cd /app/backend
nohup python3 app.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/backend.pid
echo "后端PID: $BACKEND_PID"

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端服务 (端口3000)..."
cd /app/frontend
nohup npm run dev -- --host > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend.pid
echo "前端PID: $FRONTEND_PID"

# 等待前端启动
sleep 5

# 显示状态
echo ""
echo "=========================================="
echo "服务启动完成！"
echo "=========================================="
echo "后端: http://localhost:5000 (容器内)"
echo "      http://localhost:9011 (主机访问)"
echo "前端: http://localhost:3000 (容器内)"
echo "      http://localhost:9010 (主机访问)"
echo "=========================================="
echo ""
echo "后端日志: tail -f /tmp/backend.log"
echo "前端日志: tail -f /tmp/frontend.log"
echo ""

# 测试后端API
echo "测试后端API..."
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/config)
if [ "$RESPONSE" = "200" ]; then
    echo " 后端API正常 (HTTP $RESPONSE)"
else
    echo " 后端API异常 (HTTP $RESPONSE)"
fi

echo ""
echo "请在主机浏览器访问: http://localhost:9010"
