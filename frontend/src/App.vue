<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 头部 -->
      <el-header class="app-header">
        <div class="header-content">
          <h1><el-icon><PictureFilled /></el-icon> VLM 工业标签检测标注工具</h1>
          <div class="header-actions">
            <el-button type="primary" @click="selectFolder" :icon="FolderOpened">
              选择图片文件夹
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

          <div v-else class="annotation-workspace">
            <!-- 图片查看器 -->
            <el-card class="image-viewer-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Picture /></el-icon> 图片预览</span>
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

              <el-form :model="annotation" label-width="120px" label-position="left">
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

                <el-divider />

                <!-- 其他信息 -->
                <el-form-item label="置信度分数">
                  <el-slider
                    v-model="annotation.confidence_score"
                    :min="0"
                    :max="1"
                    :step="0.05"
                    show-input
                    :marks="{ 0: '0', 0.5: '0.5', 1: '1' }"
                  />
                </el-form-item>

                <el-form-item label="图片路径">
                  <el-input v-model="annotation.image_path" />
                </el-form-item>
              </el-form>
            </el-card>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Picture, PictureFilled, Edit, Download, Refresh, Search,
  ZoomIn, ZoomOut, RefreshLeft, Check, CircleCheck, CircleClose, FolderOpened
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
    config.value = await api.getConfig()
  } catch (error) {
    ElMessage.error('加载配置失败')
  }
}

const selectImage = async (image) => {
  currentImage.value = image
  zoomLevel.value = 1
  try {
    annotation.value = await api.getAnnotation(image.name)
  } catch (error) {
    ElMessage.error('加载标注数据失败')
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
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dataset_export_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('数据集导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
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

const selectFolder = () => {
  ElMessageBox.alert(
    '请将图片文件复制到以下文件夹中：\n\nD:\\VLMlabelme\\data\\images\n\n然后点击"刷新"按钮重新加载图片列表。',
    '选择图片文件夹',
    {
      confirmButtonText: '打开文件夹',
      callback: async (action) => {
        if (action === 'confirm') {
          try {
            // 使用后端 API 打开文件夹
            await api.openFolder('images')
            ElMessage.success('文件夹已打开，请复制图片后点击刷新')
          } catch (error) {
            ElMessage.info('请手动打开文件夹：D:\\VLMlabelme\\data\\images')
          }
        }
      }
    }
  )
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
</style>
