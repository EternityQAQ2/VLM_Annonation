# 代理配置说明

## NPM 代理配置

如果你使用代理，需要配置npm：

```powershell
# 设置HTTP代理
npm config set proxy http://174.34.84.1:7890

# 设置HTTPS代理
npm config set https-proxy http://174.34.84.1:7890

# （可选）使用国内镜像源
npm config set registry https://registry.npmmirror.com
```

### 查看当前配置
```powershell
npm config list
```

### 清除代理配置
```powershell
npm config delete proxy
npm config delete https-proxy
npm config set registry https://registry.npmjs.org
```

## Python pip 代理配置

如果pip也需要代理：

```powershell
# 临时使用代理安装
pip install -r requirements.txt --proxy http://174.34.84.1:7890

# 或者设置环境变量（当前会话）
$env:HTTP_PROXY="http://174.34.84.1:7890"
$env:HTTPS_PROXY="http://174.34.84.1:7890"
pip install -r requirements.txt
```

### 使用国内镜像源（推荐）
```powershell
# 使用清华源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里源
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 一键安装脚本

创建了 `install.bat` 文件，可以一键安装所有依赖。

## 验证安装

### 前端
```powershell
cd frontend
npm list
```

### 后端
```powershell
cd backend
pip list | findstr -i "flask"
```
