@echo off
chcp 65001 >nul
echo ====================================
echo    VLM 工业标签检测标注工具
echo ====================================
echo.

echo [1/3] 启动后端服务...
cd backend
start "VLM Backend" cmd /k "python app.py"
timeout /t 3 /nobreak >nul

echo [2/3] 启动前端服务...
cd ..\frontend
start "VLM Frontend" cmd /k "npm run dev"
timeout /t 5 /nobreak >nul

echo [3/3] 完成!
echo.
echo 后端服务: http://localhost:5000
echo 前端服务: http://localhost:3000
echo.
echo 浏览器将自动打开...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo 提示: 关闭此窗口不会停止服务
echo 请手动关闭后端和前端的命令行窗口来停止服务
echo.
pause
