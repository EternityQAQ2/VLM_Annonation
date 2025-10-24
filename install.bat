@echo off
chcp 65001 >nul
echo ====================================
echo    VLM 依赖安装脚本
echo ====================================
echo.

echo 检测到的代理设置:
echo HTTP_PROXY: %HTTP_PROXY%
echo HTTPS_PROXY: %HTTPS_PROXY%
echo.

set /p USE_PROXY="是否使用代理? (Y/N): "

if /i "%USE_PROXY%"=="Y" (
    set /p PROXY_URL="请输入代理地址 (例如 http://174.34.84.1:7890): "
    echo.
    echo 配置npm代理...
    call npm config set proxy !PROXY_URL!
    call npm config set https-proxy !PROXY_URL!
    
    echo 配置Python代理环境变量...
    set HTTP_PROXY=!PROXY_URL!
    set HTTPS_PROXY=!PROXY_URL!
)

echo.
echo [1/3] 安装后端依赖...
echo ====================================
cd backend

set /p PIP_MIRROR="是否使用国内pip镜像源? (Y/N): "
if /i "%PIP_MIRROR%"=="Y" (
    echo 使用清华源安装...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    pip install -r requirements.txt
)

if errorlevel 1 (
    echo.
    echo ❌ 后端依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ✅ 后端依赖安装完成！
echo.

echo [2/3] 安装前端依赖...
echo ====================================
cd ..\frontend

set /p NPM_MIRROR="是否使用国内npm镜像源? (Y/N): "
if /i "%NPM_MIRROR%"=="Y" (
    echo 使用淘宝镜像源...
    call npm config set registry https://registry.npmmirror.com
)

call npm install

if errorlevel 1 (
    echo.
    echo ❌ 前端依赖安装失败！
    pause
    exit /b 1
)

echo.
echo ✅ 前端依赖安装完成！
echo.

echo [3/3] 验证安装...
echo ====================================
cd ..\backend
echo 检查Flask版本:
python -c "import flask; print(f'Flask {flask.__version__}')" 2>nul
if errorlevel 1 echo ⚠ Flask未正确安装

cd ..\frontend
echo.
echo 检查Vue版本:
call npm list vue --depth=0 2>nul

echo.
echo ====================================
echo ✅ 所有依赖安装完成！
echo ====================================
echo.
echo 下一步:
echo 1. 将图片放入 data\images\ 目录
echo 2. 运行 start.bat 启动服务
echo 3. 访问 http://localhost:3000
echo.
pause
