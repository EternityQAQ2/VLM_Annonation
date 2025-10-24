<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 头部 -->
      <el-header class="app-header">
        <div class="header-content">
          <h1><el-icon><PictureFilled /></el-icon> VLM 工业标签检测标注工具</h1>
          <div class="header-actions">
            <el-button type="primary" @click="openSettings" :icon="Setting">
              设置
            </el-button>
            <el-button type="success" @click="handleExport" :icon="Download">
              导出数据集
            </el-button>
            <el-button @click="handleRefresh" :icon="Refresh">刷新</el-button>
          </div>
        </div>
      </el-header>

      <el-container class="main-container">
        <!-- 左侧图片列表 -->
        <el-aside width="300px" class="image-list-sidebar">
          <div class="sidebar-header">
            <h3>图片列表 ({{ images.length }})</h3>
            <el-input
              v-model="searchText"
              placeholder="搜索图片..."
              :prefix-icon="Search"
              clearable
              size="small"
            />
          </div>
          <el-scrollbar class="image-list">
            <div
              v-for="image in filteredImages"
              :key="image.name"
              :class="['image-item', { active: currentImage?.name === image.name }]"
              @click="selectImage(image)"
            >
              <div class="image-thumbnail">
                <img :src="getImageUrl(image.name)" :alt="image.name" />
              </div>
              <div class="image-info">
                <div class="image-name" :title="image.name">{{ image.name }}</div>
                <div class="image-status">
                  <el-tag v-if="image.annotated" type="success" size="small">
                    已标注
                  </el-tag>
                  <el-tag v-else type="info" size="small">未标注</el-tag>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </el-aside>

        <!-- 主要内容区 -->
        <el-main class="main-content">
          <div v-if="!currentImage" class="empty-state">
            <el-empty description="请从左侧选择一张图片开始标注" />
          </div>

          <div v-else-if="currentImage" class="annotation-workspace">
            <!-- 调试信息 -->
            <div style="background: #f0f0f0; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
              <strong>调试信息：</strong><br>
              当前图片: {{ currentImage?.name }}<br>
              标注数据存在: {{ annotation ? '是' : '否' }}<br>
              缩放级别: {{ zoomLevel }}
            </div>

            <!-- 图片查看器 -->
            <el-card class="image-viewer-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Picture /></el-icon> 图片预览 - {{ currentImage.name }}</span>
                  <el-button-group size="small">
                    <el-button @click="zoomIn" :icon="ZoomIn">放大</el-button>
                    <el-button @click="zoomOut" :icon="ZoomOut">缩小</el-button>
                    <el-button @click="resetZoom" :icon="RefreshLeft">重置</el-button>
                  </el-button-group>
                </div>
              </template>
              <div class="image-viewer">
                <img
                  :src="getImageUrl(currentImage.name)"
                  :alt="currentImage.name"
                  :style="{ transform: `scale(${zoomLevel})` }"
                  class="preview-image"
                  @error="handleImageError"
                  @load="handleImageLoad"
                />
              </div>
            </el-card>

            <!-- 标注表单 -->
            <el-card class="annotation-form-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Edit /></el-icon> 标注信息</span>
                  <div>
                    <el-button type="success" @click="saveAnnotation" :icon="Check">
                      保存标注
                    </el-button>
                  </div>
                </div>
              </template>

              <!-- 加载中提示 -->
              <div v-if="!annotation" style="padding: 40px; text-align: center;">
                <el-icon :size="40" style="color: #409eff;">
                  <Loading />
                </el-icon>
                <p style="margin-top: 20px; color: #909399;">加载标注数据中...</p>
              </div>

              <el-form v-if="annotation" :model="annotation" label-width="120px" label-position="left">
                <!-- 整体状态 -->
                <el-form-item label="整体状态">
                  <el-radio-group v-model="annotation.overall_status" size="large">
                    <el-radio-button label="PASS" class="status-pass">通过</el-radio-button>
                    <el-radio-button label="FAIL" class="status-fail">不通过</el-radio-button>
                  </el-radio-group>
                </el-form-item>

                <el-divider />

                <!-- 缺陷类型标注 -->
                <h3 class="section-title">缺陷分类检测</h3>
                
                <div v-if="annotation && annotation.defect_categories">
                  <div
                    v-for="(category, index) in annotation.defect_categories"
                    :key="category.number"
                    class="defect-category-section"
                  >
                    <el-card :body-style="{ padding: '15px' }">
                      <div class="category-header">
                        <h4>
                          <el-tag :type="category.compliance ? 'success' : 'danger'" size="large">
                            {{ category.number }}. {{ category.category }}
                          </el-tag>
                        </h4>
                        <span class="category-desc">{{ getCategoryDescription(category.number) }}</span>
                      </div>

                    <el-form-item label="合规性">
                      <el-radio-group v-model="category.compliance" size="default">
                        <el-radio :label="true">
                          <el-icon color="#67C23A"><CircleCheck /></el-icon> 合规 (TRUE)
                        </el-radio>
                        <el-radio :label="false">
                          <el-icon color="#F56C6C"><CircleClose /></el-icon> 不合规 (FALSE)
                        </el-radio>
                      </el-radio-group>
                    </el-form-item>

                    <el-form-item label="检测结果">
                      <el-input
                        v-model="category.result"
                        type="textarea"
                        :rows="3"
                        placeholder="请用自然语言描述检测结果..."
                      />
                    </el-form-item>

                    <el-form-item label="详细信息">
                      <el-input
                        v-model="category.details"
                        type="textarea"
                        :rows="2"
                        placeholder="可选：补充详细信息（逗号分隔）"
                      />
                    </el-form-item>
                  </el-card>
                </div>
                </div>

                <el-divider />

                <!-- 其他信息 -->
                <el-form-item label="置信度分数" v-if="annotation">
                  <el-slider
                    v-model="annotation.confidence_score"
                    :min="0"
                    :max="1"
                    :step="0.05"
                    show-input
                    :marks="{ 0: '0', 0.5: '0.5', 1: '1' }"
                    style="padding-right: 20px;"
                  />
                </el-form-item>
              </el-form>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 设置对话框 -->
    <el-dialog
      v-model="settingsVisible"
      title="应用设置"
      width="900px"
      :close-on-click-modal="false"
      class="settings-dialog"
    >
      <el-tabs v-model="activeTab" type="card">
        <!-- 基础设置 -->
        <el-tab-pane label="基础设置" name="basic">
          <el-form :model="settings" label-width="140px" label-position="top" class="settings-form">
            <el-form-item label="图片文件夹">
              <div class="folder-select">
                <el-input v-model="settings.images_dir" readonly placeholder="请选择图片文件夹" />
                <el-button type="primary" @click="selectImagesFolder" :icon="FolderOpened">
                  选择文件夹
                </el-button>
              </div>
            </el-form-item>

            <el-form-item label="标注文件夹">
              <div class="folder-select">
                <el-input v-model="settings.annotations_dir" readonly placeholder="请选择标注文件夹" />
                <el-button type="primary" @click="selectAnnotationsFolder" :icon="FolderOpened">
                  选择文件夹
                </el-button>
              </div>
            </el-form-item>

            <el-form-item label="导出格式">
              <el-select v-model="settings.export_format" style="width: 100%;">
                <el-option label="VLM 格式（带 Prompt）" value="vlm" />
                <el-option label="标准格式" value="standard" />
              </el-select>
            </el-form-item>

            <el-form-item label="JSON 缩进空格">
              <div class="indent-setting">
                <el-input-number
                  v-model="settings.json_indent"
                  :min="0"
                  :max="8"
                  :step="1"
                />
                <span class="setting-hint">
                  设置为 0 则压缩成一行
                </span>
              </div>
            </el-form-item>

            <el-form-item label="自动保存">
              <div class="switch-setting">
                <el-switch v-model="settings.auto_save" />
                <span class="setting-hint">
                  切换图片时自动保存当前标注
                </span>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- VLM Prompt 配置 -->
        <el-tab-pane label="Prompt 配置" name="prompt">
          <el-form label-width="140px" label-position="top" class="settings-form">
            <el-form-item label="VLM 提示词模板">
              <el-alert
                title="提示"
                type="info"
                :closable="false"
                style="margin-bottom: 15px;"
              >
                此提示词将在导出 VLM 格式时自动注入到每个样本的 messages 中作为 user 角色的内容。
              </el-alert>
              <el-input
                v-model="settings.prompt_template"
                type="textarea"
                :rows="20"
                placeholder="输入您的 VLM 提示词模板..."
                style="font-family: 'Consolas', 'Monaco', monospace; font-size: 13px;"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- JSON 字段配置（未来功能） -->
        <el-tab-pane label="字段配置" name="schema" disabled>
          <el-empty description="字段配置功能即将推出，敬请期待！" />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="settingsVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Picture, PictureFilled, Edit, Download, Refresh, Search,
  ZoomIn, ZoomOut, RefreshLeft, Check, CircleCheck, CircleClose, FolderOpened, Setting, Loading
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from './api'

// 数据状态
const images = ref([])
const currentImage = ref(null)
const annotation = ref(null)
const config = ref(null)
const searchText = ref('')
const zoomLevel = ref(1)
const settingsVisible = ref(false)
const activeTab = ref('basic')
const settings = ref({
  images_dir: '',
  annotations_dir: '',
  export_format: 'vlm',
  auto_save: true,
  json_indent: 2,
  prompt_template: ''
})

// 计算属性
const filteredImages = computed(() => {
  if (!searchText.value) return images.value
  return images.value.filter(img =>
    img.name.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 方法
const loadImages = async () => {
  try {
    const data = await api.getImages()
    images.value = data.images
  } catch (error) {
    ElMessage.error('加载图片列表失败')
  }
}

const loadConfig = async () => {
  try {
    const data = await api.getConfig()
    config.value = data
    // 加载应用配置到设置
    if (data.app_config) {
      settings.value = { ...settings.value, ...data.app_config }
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
}

const selectImage = async (image) => {
  console.log('=== 开始选择图片 ===')
  console.log('图片信息:', image)
  
  // 如果启用了自动保存，先保存当前标注
  if (settings.value.auto_save && currentImage.value && annotation.value) {
    try {
      await api.saveAnnotation(currentImage.value.name, annotation.value)
      console.log('自动保存成功')
    } catch (error) {
      console.error('自动保存失败:', error)
    }
  }
  
  // 设置当前图片
  currentImage.value = image
  zoomLevel.value = 1
  
  console.log('当前图片已设置:', currentImage.value)
  console.log('图片 URL:', getImageUrl(image.name))
  
  try {
    annotation.value = await api.getAnnotation(image.name)
    console.log('加载的标注数据:', annotation.value)
  } catch (error) {
    console.error('加载标注数据失败:', error)
    ElMessage.error('加载标注数据失败: ' + (error.message || '未知错误'))
  }
}

const getImageUrl = (filename) => {
  return api.getImageUrl(filename)
}

const getCategoryDescription = (number) => {
  if (!config.value) return ''
  const cat = config.value.defect_categories.find(c => c.number === number)
  return cat ? cat.description : ''
}

const saveAnnotation = async () => {
  try {
    await api.saveAnnotation(currentImage.value.name, annotation.value)
    ElMessage.success('标注已保存')
    // 更新图片列表中的标注状态
    const img = images.value.find(i => i.name === currentImage.value.name)
    if (img) img.annotated = true
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

const handleExport = async () => {
  try {
    const data = await api.exportDataset()
    const blob = new Blob([JSON.stringify(data.data, null, settings.value.json_indent)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vlm_dataset_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success({
      message: `成功导出 ${data.total} 条标注数据（${data.format} 格式）`,
      duration: 3000
    })
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败：' + (error.message || '未知错误'))
  }
}

const handleRefresh = async () => {
  await loadImages()
  ElMessage.success('刷新成功')
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value + 0.2, 3)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value - 0.2, 0.5)
}

const resetZoom = () => {
  zoomLevel.value = 1
}

const openSettings = () => {
  settingsVisible.value = true
}

const selectImagesFolder = async () => {
  try {
    const result = await api.selectFolder('images')
    if (result.success) {
      settings.value.images_dir = result.folder_path
      ElMessage.success('已选择图片文件夹')
    }
  } catch (error) {
    ElMessage.error('选择文件夹失败: ' + error.message)
  }
}

const selectAnnotationsFolder = async () => {
  try {
    const result = await api.selectFolder('annotations')
    if (result.success) {
      settings.value.annotations_dir = result.folder_path
      ElMessage.success('已选择标注文件夹')
    }
  } catch (error) {
    ElMessage.error('选择文件夹失败: ' + error.message)
  }
}

const saveSettings = async () => {
  try {
    await api.updateConfig(settings.value)
    settingsVisible.value = false
    ElMessage.success('设置已保存，正在重新加载...')
    // 重新加载配置和图片列表
    await loadConfig()
    await loadImages()
  } catch (error) {
    ElMessage.error('保存设置失败: ' + error.message)
  }
}

const selectFolder = () => {
  // 打开设置对话框
  openSettings()
}

const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  ElMessage.error('图片加载失败，请检查图片路径')
}

const handleImageLoad = () => {
  console.log('图片加载成功')
}

// 生命周期
onMounted(async () => {
  await loadConfig()
  await loadImages()
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  height: 100vh;
  background: #ffffff;
}

.app-header {
  background: #f5f5f7;
  color: #1d1d1f;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #d2d2d7;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-header h1 {
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1d1d1f;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-container {
  height: calc(100vh - 60px);
}

.image-list-sidebar {
  background: #fafafa;
  border-right: 1px solid #d2d2d7;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #d2d2d7;
  background: #f5f5f7;
}

.sidebar-header h3 {
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
}

.image-list {
  flex: 1;
  height: calc(100vh - 180px);
}

.image-item {
  display: flex;
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #e5e5e7;
  transition: all 0.2s;
  background: #ffffff;
}

.image-item:hover {
  background: #f5f5f7;
}

.image-item.active {
  background: #e8f4fd;
  border-left: 3px solid #007aff;
}

.image-thumbnail {
  width: 60px;
  height: 60px;
  margin-right: 10px;
  border-radius: 6px;
  overflow: hidden;
  background: #f5f5f7;
  border: 1px solid #e5e5e7;
}

.image-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
}

.image-name {
  font-size: 13px;
  color: #1d1d1f;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
  background: #ffffff;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.annotation-workspace {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr 1fr;
}

@media (max-width: 1400px) {
  .annotation-workspace {
    grid-template-columns: 1fr;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1d1d1f;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.image-viewer-card {
  height: fit-content;
  position: sticky;
  top: 0;
  border: 1px solid #d2d2d7;
}

.image-viewer {
  background: #fafafa;
  border-radius: 8px;
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 600px;
  transition: transform 0.3s;
  cursor: zoom-in;
  border-radius: 4px;
}

.section-title {
  margin: 20px 0;
  padding: 10px 15px;
  background: #f5f5f7;
  border-left: 4px solid #007aff;
  color: #1d1d1f;
  font-weight: 600;
  border-radius: 4px;
}

.defect-category-section {
  margin-bottom: 15px;
}

.defect-category-section :deep(.el-card) {
  border: 1px solid #d2d2d7;
  border-radius: 8px;
}

.category-header {
  margin-bottom: 15px;
}

.category-header h4 {
  margin-bottom: 8px;
}

.category-desc {
  color: #86868b;
  font-size: 13px;
}

.annotation-form-card {
  border: 1px solid #d2d2d7;
}

.status-pass :deep(.el-radio-button__inner) {
  border-color: #67c23a;
}

.status-pass.is-active :deep(.el-radio-button__inner) {
  background-color: #67c23a;
  border-color: #67c23a;
}

.status-fail :deep(.el-radio-button__inner) {
  border-color: #f56c6c;
}

.status-fail.is-active :deep(.el-radio-button__inner) {
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.folder-select {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.folder-select .el-input {
  flex: 1;
}

.folder-select .el-button {
  flex-shrink: 0;
  min-width: 120px;
  white-space: nowrap;
}

.settings-form {
  padding: 20px 0;
}

.settings-form .el-form-item {
  margin-bottom: 24px;
}

.indent-setting,
.switch-setting {
  display: flex;
  align-items: center;
  gap: 16px;
}

.setting-hint {
  color: #86868b;
  font-size: 13px;
  line-height: 1.5;
}

/* 滑块样式优化 */
:deep(.el-slider) {
  padding-right: 20px;
}

:deep(.el-slider__runway) {
  margin: 16px 0;
}

/* 表单项标签样式 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 8px;
  padding: 0;
}

:deep(.el-form-item__content) {
  line-height: normal;
}

/* 对话框样式 */
:deep(.el-dialog__header) {
  border-bottom: 1px solid #e5e5e7;
  padding: 20px 24px;
  margin: 0;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

/* Tabs 样式 */
:deep(.el-tabs__header) {
  margin: 0 0 20px 0;
}

:deep(.el-tabs__item) {
  font-weight: 500;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
}

:deep(.el-tabs__item.is-active) {
  color: #0071e3;
}

/* 文本域样式 */
:deep(.el-textarea__inner) {
  padding: 12px;
  line-height: 1.6;
  border-radius: 8px;
  border-color: #d2d2d7;
}

:deep(.el-textarea__inner:focus) {
  border-color: #0071e3;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid #e5e5e7;
  padding: 16px 24px;
}

:deep(.el-input__wrapper) {
  padding: 8px 12px;
  border-radius: 6px;
  box-shadow: 0 0 0 1px #d2d2d7 inset;
  transition: all 0.2s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #b3b3b8 inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #007aff inset;
}

:deep(.el-button) {
  border-radius: 6px;
  padding: 9px 16px;
  font-weight: 500;
  transition: all 0.2s;
}

:deep(.el-button--primary) {
  background-color: #007aff;
  border-color: #007aff;
}

:deep(.el-button--primary:hover) {
  background-color: #0051d5;
  border-color: #0051d5;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
}
</style>
