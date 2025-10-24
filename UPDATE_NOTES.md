# 更新说明

## 2025-10-24 更新

### ✨ 新功能

1. **macOS 风格 UI**
   - 采用白底黑字的简洁设计
   - 灵感来自 macOS 界面风格
   - 更清晰的视觉层次和阅读体验
   - 柔和的边框和圆角设计

2. **选择图片文件夹**
   - 点击顶部"选择图片文件夹"按钮
   - 自动打开系统文件管理器到 `D:\VLMlabelme\data\images` 文件夹
   - 将图片文件复制到该文件夹后，点击"刷新"按钮即可加载

### 🎨 UI 改进

- **配色方案**：
  - 主背景：纯白 (#ffffff)
  - 侧边栏：浅灰 (#fafafa)
  - 边框：淡灰 (#d2d2d7)
  - 文字：深灰黑 (#1d1d1f)
  - 高亮：iOS 蓝 (#007aff)

- **字体优化**：
  - 标题字重：600
  - 更清晰的字体层级

- **圆角优化**：
  - 卡片圆角：8px
  - 缩略图圆角：6px

### 🔧 使用说明

#### 升级 Node.js（重要）

如果您看到 `Unexpected token '??='` 错误，需要升级 Node.js：

1. 访问 https://nodejs.org/
2. 下载并安装 LTS 版本（v18+ 或 v20+）
3. 重启终端
4. 在项目文件夹运行：
   ```bash
   cd D:\VLMlabelme\frontend
   npm install
   npm run dev
   ```

#### 添加图片文件

1. 点击顶部的"选择图片文件夹"按钮
2. 系统会自动打开 `D:\VLMlabelme\data\images` 文件夹
3. 将您的图片文件复制到该文件夹
4. 回到应用，点击"刷新"按钮
5. 图片列表会自动更新

### 📂 文件结构

```
D:\VLMlabelme\
├── data/
│   ├── images/          # 在这里放置您的图片文件
│   └── annotations/     # 标注数据自动保存在这里
├── backend/
│   └── app.py          # 后端服务（已更新）
└── frontend/
    └── src/
        ├── App.vue     # 主界面（已更新 UI 风格）
        └── api.js      # API 接口（已添加文件夹功能）
```

### 🚀 启动应用

Windows 用户：
```bash
# 双击运行
start.bat
```

或手动启动：
```bash
# 启动后端
cd backend
python app.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 💡 提示

- 支持的图片格式：JPG, JPEG, PNG, BMP
- 标注数据自动以 JSON 格式保存
- 可以通过"导出数据集"按钮导出所有标注
