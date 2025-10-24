# VLM 工业标签检测标注工具

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Node](https://img.shields.io/badge/node-18+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

**专业的工业标签缺陷标注工具 | macOS 风格 UI | 灵活配置**

[快速开始](./QUICK_START.md) · [使用指南](./USER_GUIDE.md) · [更新日志](./UPDATE_NOTES.md)

</div>

---

## ✨ 核心特性

### 🎨 **现代化 UI**
- macOS 风格的简洁设计
- 白底黑字，清晰易读
- 响应式布局，适配各种屏幕
- 流畅的交互体验

### 🗂️ **灵活的文件管理**
- ✅ 自定义图片文件夹路径
- ✅ 自定义标注文件夹路径
- ✅ 配置自动保存，永久生效
- ✅ 轻松管理多个标注项目

### ⚙️ **强大的设置功能**
- 📁 文件夹路径配置
- 📤 多种导出格式（标准/COCO/YOLO）
- 🔧 JSON 格式自定义（缩进 0-8 空格）
- 💾 自动保存标注
- 🔄 实时配置更新

### 📊 **专业的标注系统**
- 5 大缺陷类型分类
- PASS/FAIL 状态判定
- 自然语言描述
- 置信度评分
- 完整的时间戳记录

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **Node.js**: 18.0 或更高版本（重要！）
- **浏览器**: Chrome、Edge、Firefox 等现代浏览器

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd VLMlabelme
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 启动应用

#### Windows 用户（推荐）

双击 `start.bat` 文件，自动启动前后端服务。

#### 手动启动

**启动后端：**
```bash
cd backend
python app.py
```
后端服务运行在：`http://localhost:5000`

**启动前端：**（新终端窗口）
```bash
cd frontend
npm run dev
```
前端服务运行在：`http://localhost:5173`

### 首次配置

1. 浏览器打开 `http://localhost:5173`
2. 点击顶部 **"设置"** 按钮
3. 选择图片文件夹和标注文件夹
4. 调整 JSON 缩进和其他选项
5. 保存设置
6. 开始标注！

## 📖 使用说明

### 基本工作流程

```
选择文件夹 → 加载图片 → 选择图片 → 填写标注 → 保存 → 下一张
```

### 详细步骤

1. **配置路径**
   - 点击"设置"按钮
   - 选择图片和标注文件夹
   - 保存配置

2. **选择图片**
   - 左侧列表显示所有图片
   - 点击任意图片开始标注
   - 支持搜索过滤

3. **填写标注**
   - 选择整体状态（PASS/FAIL）
   - 对每个缺陷类型进行判定
   - 填写自然语言描述
   - 调整置信度分数

4. **保存标注**
   - 手动点击"保存标注"按钮
   - 或开启自动保存功能

5. **导出数据**
   - 点击"导出数据集"按钮
   - 下载完整的 JSON 数据集

### 设置选项说明

| 选项 | 说明 | 推荐值 |
|------|------|--------|
| 图片文件夹 | 待标注图片的位置 | 任意可读文件夹 |
| 标注文件夹 | 保存标注文件的位置 | 独立文件夹 |
| 导出格式 | 数据集导出格式 | standard |
| JSON 缩进 | JSON 文件的缩进空格数 | 2 |
| 自动保存 | 切换图片时自动保存 | 开启 |

## 🏗️ 项目结构

```
VLMlabelme/
├── backend/                 # 后端服务
│   ├── app.py              # Flask 应用
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── App.vue        # 主界面组件
│   │   ├── api.js         # API 接口
│   │   └── main.js        # 入口文件
│   ├── package.json       # Node 依赖
│   └── vite.config.js     # Vite 配置
│
├── data/                   # 默认数据目录
│   ├── images/            # 默认图片文件夹
│   └── annotations/       # 默认标注文件夹
│
├── config.json            # 应用配置（自动生成）
├── config.json.example    # 配置文件示例
├── start.bat              # Windows 启动脚本
├── QUICK_START.md         # 快速开始指南
├── USER_GUIDE.md          # 详细使用指南
└── UPDATE_NOTES.md        # 更新日志
```

## 🎯 标注数据格式

### 单个标注文件示例

```json
{
  "image_name": "sample.jpg",
  "image_path": "images/sample.jpg",
  "overall_status": "FAIL",
  "defect_categories": [
    {
      "number": 1,
      "category": "缺失元素",
      "compliance": false,
      "result": "标签缺少二维码",
      "details": ["二维码", "缺失"]
    },
    {
      "number": 2,
      "category": "偏移问题",
      "compliance": true,
      "result": "位置正常",
      "details": []
    }
  ],
  "confidence_score": 0.92,
  "created_at": "2025-10-24T10:00:00",
  "updated_at": "2025-10-24T10:30:00"
}
```

### 缺陷类型

1. **缺失元素** - 文字、二维码等关键元素丢失或过多元素
2. **偏移问题** - 标签位置偏移、字符偏移
3. **物理缺陷** - 气泡、皱褶、划痕、污渍、墨点等
4. **打印质量** - 字迹模糊、字迹黯淡、字符打印不完整等
5. **整体布局** - 元素排版问题

## 💡 高级功能

### 多项目管理

通过切换文件夹路径，轻松管理多个标注项目：

```
D:/
├── ProjectA/
│   ├── images/
│   └── annotations/
├── ProjectB/
│   ├── images/
│   └── annotations/
└── ProjectC/
    ├── images/
    └── annotations/
```

在设置中切换路径即可切换项目。

### JSON 格式优化

根据需求选择合适的缩进：

| 缩进 | 适用场景 | 文件大小 | 可读性 |
|------|---------|---------|--------|
| 0 | 机器处理、存储优化 | 最小 | ⭐ |
| 2 | **日常标注（推荐）** | 适中 | ⭐⭐⭐⭐ |
| 4 | 高可读性需求 | 较大 | ⭐⭐⭐⭐⭐ |

### 导出格式

- **Standard**: 标准 JSON 格式，包含完整信息
- **COCO**: 兼容 COCO 数据集格式
- **YOLO**: 兼容 YOLO 训练格式

## 🛠️ 技术栈

### 后端
- **Flask** - Web 框架
- **Flask-CORS** - 跨域支持
- **Python 3.8+** - 运行环境

### 前端
- **Vue 3** - 渐进式框架
- **Vite** - 构建工具
- **Element Plus** - UI 组件库
- **Axios** - HTTP 客户端

## ⚠️ 常见问题

### Q: 看到 `Unexpected token '??='` 错误？

**A:** Node.js 版本过低，需要升级到 v18 或更高版本。

访问 https://nodejs.org/ 下载最新 LTS 版本。

### Q: 为什么选择文件夹后没有显示图片？

**A:** 点击"刷新"按钮重新加载图片列表。确保：
- 文件夹中有图片文件
- 图片格式为 JPG, PNG, BMP
- 文件夹有读取权限

### Q: 标注数据保存在哪里？

**A:** 保存在您设置的"标注文件夹"中，每张图片对应一个同名的 `.json` 文件。

### Q: 可以同时管理多个项目吗？

**A:** 可以！在设置中切换不同的文件夹路径即可切换项目。

### Q: JSON 文件太大怎么办？

**A:** 在设置中将"JSON 缩进"设置为 0，文件会压缩成一行。

### Q: 支持哪些图片格式？

**A:** 支持 JPG, JPEG, PNG, BMP 格式。

## 📚 文档

- **[快速开始](./QUICK_START.md)** - 5 分钟上手指南
- **[使用指南](./USER_GUIDE.md)** - 详细功能说明
- **[更新日志](./UPDATE_NOTES.md)** - 版本更新记录

## 🔧 开发

### 开发模式

```bash
# 后端热重载
cd backend
python app.py  # 已启用 debug 模式

# 前端热重载
cd frontend
npm run dev
```

### 构建生产版本

```bash
cd frontend
npm run build
```

## 📝 配置文件

`config.json` 会在首次保存设置时自动生成：

```json
{
  "images_dir": "D:/VLMlabelme/data/images",
  "annotations_dir": "D:/VLMlabelme/data/annotations",
  "export_format": "standard",
  "auto_save": true,
  "json_indent": 2
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请通过 Issue 反馈。

---

<div align="center">

**专业 · 灵活 · 易用**

Made with ❤️ by VLM Team

</div>
