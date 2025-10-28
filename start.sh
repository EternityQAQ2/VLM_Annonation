#!/bin/bash
# VLM Annotation Tool 启动脚本

echo "======================================"
echo "VLM Annotation Tool"
echo "======================================"

# 启动后端
echo "启动后端服务..."
cd /app/backend
python3 app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端服务..."
cd /app/frontend
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "服务已启动！"
echo "======================================"
echo "前端: http://localhost:9010"
echo "后端: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "======================================"

# 等待任意进程退出
wait -n

# 清理
echo "停止服务..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
wait

echo "已停止"
