# VLM Annotation Tool

VLM 标注工具 - 用于图片标注和 VLM 训练数据生成

## 项目结构

```
/app
├── backend/           # Flask 后端
│   ├── app.py        # 主应用
│   └── requirements.txt
├── frontend/         # Vue 前端
│   ├── src/
│   ├── public/
│   └── package.json
├── data/            # 数据目录
│   ├── images/      # 图片文件
│   └── annotations/ # 标注文件
├── examples/        # 示例文件
└── start.bat        # Windows 启动脚本
```

## 快速开始

### 本地运行（Windows）

双击 `start.bat` 或在命令行运行：

```bash
start.bat
```

### Docker 容器运行

1. 创建容器并挂载数据目录：

```bash
docker run -d \
  --name Linxaura_Vlm \
  -p 9010:3000 \
  -v /host/data:/app/data \
  ubuntu:22.04
```

2. 进入容器并启动服务：

```bash
docker exec -it Linxaura_Vlm bash
cd /app/backend
python3 app.py
```

3. 另开终端启动前端：

```bash
docker exec -it Linxaura_Vlm bash
cd /app/frontend
npm run dev -- --host 0.0.0.0 --port 3000
```

## 配置路径

### GUI 环境（Windows/Mac/Linux 桌面）
- 点击"选择文件夹"按钮会自动打开文件选择对话框

### 容器环境（Docker）
- 点击"选择文件夹"按钮会显示输入框
- 输入容器内路径，例如：
  - 图片文件夹: `/app/data/images`
  - 标注文件夹: `/app/data/annotations`

## 功能特性

- 图片标注管理
- 自定义 JSON 字段配置
- VLM 训练数据导出
- 自动保存标注
- 智能路径选择（自动适配 GUI/容器环境）

## 技术栈

- 后端: Flask + Python 3
- 前端: Vue 3 + Element Plus + Vite
- 数据: JSON 格式
