# VLM 工业标签检测标注工具

一个用于工业打印标签质量检测的图片标注工具，支持自然语言标注和JSON格式导出。

## 功能特性

✨ **核心功能**
- 📷 图片查看器（支持缩放、平移）
- 🏷️ 多类型缺陷标注（5大类）
- 📝 自然语言标注界面
- 💾 自动保存标注数据
- 📊 数据导出为标准JSON格式
- 🔍 图片搜索和过滤

🎯 **缺陷分类**
1. **缺失元素** - 文字、二维码等关键元素丢失或过多
2. **偏移问题** - 标签位置偏移、字符偏移
3. **物理缺陷** - 气泡、皱褶、划痕、污渍、墨点等
4. **打印质量** - 字迹模糊、字符不完整、二维码质量等
5. **整体布局** - 元素排版问题

## 技术栈

### 前端
- Vue 3 - 渐进式框架
- Element Plus - UI组件库
- Vite - 构建工具
- Axios - HTTP客户端

### 后端
- Python 3.8+
- Flask - Web框架
- Flask-CORS - 跨域支持

## 项目结构

```
VLMlabelme/
├── backend/                 # 后端服务
│   ├── app.py              # Flask应用主文件
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── App.vue        # 主应用组件
│   │   ├── api.js         # API接口
│   │   └── main.js        # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── data/                   # 数据目录
│   ├── images/            # 原始图片存放目录
│   └── annotations/       # 标注数据存放目录
├── test.py
├── README.md
└── start.bat              # Windows启动脚本
```

## 快速开始

### 前置要求
- Python 3.8 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

### 安装步骤

#### 1. 安装后端依赖

```powershell
cd backend
pip install -r requirements.txt
```

#### 2. 安装前端依赖

```powershell
cd frontend
npm install
# 或使用 yarn
yarn install
```

### 运行项目

#### 方法一：使用启动脚本（推荐）

Windows用户可以直接双击 `start.bat` 文件，或在命令行中运行：

```powershell
.\start.bat
```

#### 方法二：手动启动

**启动后端服务：**
```powershell
cd backend
python app.py
```
后端服务将在 `http://localhost:5000` 运行

**启动前端服务：**
```powershell
cd frontend
npm run dev
```
前端服务将在 `http://localhost:3000` 运行

### 访问应用

打开浏览器访问：`http://localhost:3000`

## 使用指南

### 1. 准备图片
将需要标注的图片放入 `data/images/` 目录中。支持的图片格式：
- JPG/JPEG
- PNG
- BMP

### 2. 开始标注
1. 从左侧图片列表中选择一张图片
2. 查看图片预览（可缩放）
3. 在右侧表单中进行标注：
   - 选择整体状态（PASS/FAIL）
   - 对每个缺陷类型进行标注
   - 选择合规性（TRUE/FALSE）
   - 填写自然语言检测结果
   - 调整置信度分数

### 3. 保存标注
点击"保存标注"按钮，数据将保存到 `data/annotations/` 目录

### 4. 导出数据集
点击右上角"导出数据集"按钮，将所有标注数据导出为标准JSON格式

## API接口

### 获取配置
```
GET /api/config
```

### 获取图片列表
```
GET /api/images
```

### 获取图片
```
GET /api/images/<filename>
```

### 获取标注数据
```
GET /api/annotations/<image_name>
```

### 保存标注数据
```
POST /api/annotations/<image_name>
Content-Type: application/json
```

### 导出数据集
```
GET /api/export
```

## 数据格式

### 标注数据结构
```json
{
  "image_name": "example.jpg",
  "image_path": "images/example.jpg",
  "overall_status": "PASS",
  "defect_categories": [
    {
      "number": 1,
      "category": "缺失元素",
      "compliance": true,
      "result": "所有关键元素完整存在",
      "details": []
    }
  ],
  "confidence_score": 0.95,
  "processing_info": {
    "stage": "defect_classification",
    "template_matched": true,
    "categories_checked": ["缺失元素", "偏移问题", "物理缺陷", "打印质量", "整体布局"]
  },
  "created_at": "2025-10-24T10:00:00",
  "updated_at": "2025-10-24T10:30:00"
}
```

### 导出格式
导出的数据集将包含所有标注，格式兼容VLM训练：
```json
{
  "export_time": "2025-10-24T12:00:00",
  "data": [
    {
      "images": ["images/example.jpg"],
      "messages": [
        {
          "content": "提示词内容...",
          "role": "user"
        },
        {
          "content": "JSON格式的检测结果...",
          "role": "assistant"
        }
      ]
    }
  ]
}
```

## 开发指南

### 前端开发
```powershell
cd frontend
npm run dev      # 开发模式
npm run build    # 构建生产版本
npm run preview  # 预览生产版本
```

### 后端开发
修改 `backend/app.py` 后，Flask会自动重载（开发模式）

### 自定义缺陷类型
在 `backend/app.py` 中修改 `DEFECT_CATEGORIES` 配置

## 常见问题

### Q: 图片无法加载？
A: 确保图片放在 `data/images/` 目录中，且文件格式正确

### Q: 标注数据保存失败？
A: 检查 `data/annotations/` 目录是否有写入权限

### Q: 前端无法连接后端？
A: 确保后端服务在5000端口正常运行，检查防火墙设置

### Q: 如何批量导入图片？
A: 直接将图片复制到 `data/images/` 目录，然后点击"刷新"按钮

## 许可证

MIT License

## 作者

VLM Label Tool Team

## 更新日志

### v1.0.0 (2025-10-24)
- ✨ 初始版本发布
- 🎨 完整的UI界面
- 📝 支持5大类缺陷标注
- 💾 数据导出功能
- 🔍 图片搜索功能

---

**Good Luck! 🚀**
