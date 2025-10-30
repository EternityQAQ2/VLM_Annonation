<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 头部 -->
      <el-header class="app-header">
        <div class="header-content">
          <h1><el-icon><PictureFilled /></el-icon> VLM Annotation <span class="author-info">by LINXAURA</span></h1>
          <div class="header-actions">
            <el-button type="primary" @click="openSettings" :icon="Setting">
              设置
            </el-button>
            <el-button type="success" @click="exportAllAnnotations" :icon="Download">
              输出所有标注
            </el-button>
            <el-button type="warning" @click="exportCurrentAnnotation" :icon="Document" :disabled="!currentImage">
              输出当前标注
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
                <img 
                  :src="getThumbnailUrl(image.name)" 
                  :alt="image.name"
                  :data-filename="image.name"
                  @error="handleThumbnailError($event)"
                  @load="handleThumbnailLoad($event)"
                />
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

          <div v-else-if="currentImage">
            <!-- 调试信息 -->
            <div class="debug-info" :title="currentImage?.name">
              <span class="debug-filename">{{ currentImage?.name }}</span>
              <span class="debug-status">{{ annotation ? '已加载' : '未加载' }}</span>
              <span class="debug-zoom">{{ zoomLevel }}x</span>
            </div>

            <div class="annotation-workspace">
            <!-- 图片查看器 -->
            <el-card class="image-viewer-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span class="card-title" :title="currentImage.name">
                    <el-icon><Picture /></el-icon> 
                    <span class="image-name-text">图片预览 - {{ currentImage.name }}</span>
                  </span>
                  <div style="display: flex; gap: 10px;">
                    <el-button 
                      type="danger" 
                      size="small" 
                      @click="deleteCurrentImage"
                      :icon="Delete"
                    >
                      删除图片
                    </el-button>
                    <el-button-group size="small" class="zoom-controls">
                      <el-button @click="zoomIn" :icon="ZoomIn">放大</el-button>
                      <el-button @click="zoomOut" :icon="ZoomOut">缩小</el-button>
                      <el-button @click="resetZoom" :icon="RefreshLeft">重置</el-button>
                    </el-button-group>
                  </div>
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
              
              <!-- 标注摘要 -->
              <div v-if="annotationSummary" class="annotation-summary">
                <div class="summary-header">
                  <el-icon><DocumentChecked /></el-icon>
                  <span>标注摘要</span>
                </div>
                <div class="summary-content">
                  <!-- 图片路径 -->
                  <div class="summary-item">
                    <span class="summary-label">图片路径:</span>
                    <span class="summary-value">{{ annotationSummary.image_path }}</span>
                  </div>
                  
                  <!-- 动态显示所有顶级字段 -->
                  <div 
                    v-for="(fieldData, fieldName) in annotationSummary.fields" 
                    :key="fieldName"
                    class="summary-item"
                    :class="{ 'summary-item-array': fieldData.type === 'array' }"
                  >
                    <span class="summary-label">{{ fieldData.description || fieldName }}:</span>
                    
                    <!-- 根据字段类型渲染不同的显示 -->
                    <!-- 字符串类型 - 特殊处理 overall_status -->
                    <el-tag 
                      v-if="fieldData.type === 'string' && fieldName === 'overall_status'"
                      :type="fieldData.value === 'PASS' ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ fieldData.value }}
                    </el-tag>
                    
                    <!-- 普通字符串 -->
                    <span v-else-if="fieldData.type === 'string'" class="summary-value">
                      {{ fieldData.value }}
                    </span>
                    
                    <!-- 数字类型 - 特殊处理 confidence_score -->
                    <el-tag 
                      v-else-if="fieldData.type === 'number' && fieldName === 'confidence_score'"
                      type="info" 
                      size="small"
                    >
                      {{ (fieldData.value * 100).toFixed(1) }}%
                    </el-tag>
                    
                    <!-- 普通数字 -->
                    <span v-else-if="fieldData.type === 'number'" class="summary-value">
                      {{ fieldData.value }}
                    </span>
                    
                    <!-- 布尔类型 -->
                    <el-tag 
                      v-else-if="fieldData.type === 'boolean'"
                      :type="fieldData.value ? 'success' : 'danger'"
                      size="small"
                    >
                      {{ fieldData.value ? 'TRUE' : 'FALSE' }}
                    </el-tag>
                    
                    <!-- 对象类型 -->
                    <span v-else-if="fieldData.type === 'object'" class="summary-value">
                      {{ JSON.stringify(fieldData.value) }}
                    </span>
                    
                    <!-- 数组类型 - 超紧凑的内联展示 -->
                    <div v-else-if="fieldData.type === 'array'" class="summary-array-inline">
                      <el-tag size="small" type="info">{{ fieldData.value.length }} 项</el-tag>
                      <el-button 
                        v-if="fieldData.value.length > 0"
                        text 
                        size="small" 
                        @click="toggleArrayExpand(fieldName)"
                        class="inline-expand-btn"
                      >
                        {{ expandedArrays[fieldName] ? '▲' : '▼' }}
                      </el-button>
                      
                      <!-- 超紧凑展示：每项一行 -->
                      <div v-if="expandedArrays[fieldName] && fieldData.array_items && fieldData.array_items.length > 0" 
                           class="inline-items">
                        <div 
                          v-for="arrayItem in fieldData.array_items" 
                          :key="arrayItem.index"
                          class="inline-item"
                        >
                          <span class="item-num">#{{ arrayItem.index }}</span>
                          <span class="item-content">
                            <template v-if="typeof arrayItem.data === 'object' && !Array.isArray(arrayItem.data)">
                              <span 
                                v-for="(val, key, idx) in arrayItem.data" 
                                :key="key"
                                class="field-pair"
                              >
                                <template v-if="!Array.isArray(val) && typeof val !== 'object'">
                                  <span class="k">{{ key }}</span>: 
                                  <span v-if="typeof val === 'boolean'" class="v-bool">{{ val ? '✓' : '✗' }}</span>
                                  <span v-else class="v">{{ val }}</span>
                                  <span v-if="idx < Object.keys(arrayItem.data).length - 1" class="sep">, </span>
                                </template>
                                <template v-else-if="Array.isArray(val)">
                                  <span class="k">{{ key }}</span>: 
                                  <span class="nested-toggle" @click="toggleNestedArray(`${fieldName}_${arrayItem.index}_${key}`)">
                                    [{{ val.length }}项{{ expandedArrays[`${fieldName}_${arrayItem.index}_${key}`] ? '▲' : '▼' }}]
                                  </span>
                                  <div v-if="expandedArrays[`${fieldName}_${arrayItem.index}_${key}`]" class="nested-block">
                                    <div 
                                      v-for="(nested, nIdx) in val" 
                                      :key="nIdx"
                                      class="nested-line"
                                    >
                                      <span class="n-num">#{{ nIdx + 1 }}</span>
                                      <template v-if="typeof nested === 'object' && !Array.isArray(nested)">
                                        <span 
                                          v-for="(nVal, nKey, nKeyIdx) in nested" 
                                          :key="nKey"
                                          class="field-pair"
                                        >
                                          <template v-if="!Array.isArray(nVal) && typeof nVal !== 'object'">
                                            <span class="k">{{ nKey }}</span>: 
                                            <span class="v">{{ nVal }}</span>
                                            <span v-if="nKeyIdx < Object.keys(nested).length - 1">, </span>
                                          </template>
                                          <template v-else-if="Array.isArray(nVal)">
                                            <span class="k">{{ nKey }}</span>: 
                                            <span class="nested-toggle" @click="toggleNestedArray(`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}`)">
                                              [{{ nVal.length }}项{{ expandedArrays[`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}`] ? '▲' : '▼' }}]
                                            </span>
                                            <div v-if="expandedArrays[`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}`]" class="nested-block">
                                              <div v-for="(deepItem, deepIdx) in nVal" :key="deepIdx" class="nested-line">
                                                <span class="n-num">#{{ deepIdx + 1 }}</span>
                                                <!-- 递归渲染对象字段 -->
                                                <template v-if="typeof deepItem === 'object' && !Array.isArray(deepItem)">
                                                  <span 
                                                    v-for="(dVal, dKey, dKeyIdx) in deepItem" 
                                                    :key="dKey"
                                                    class="field-pair"
                                                  >
                                                    <template v-if="!Array.isArray(dVal) && typeof dVal !== 'object'">
                                                      <span class="k">{{ dKey }}</span>: 
                                                      <span v-if="typeof dVal === 'boolean'" class="v-bool">{{ dVal ? '✓' : '✗' }}</span>
                                                      <span v-else class="v">{{ dVal }}</span>
                                                      <span v-if="dKeyIdx < Object.keys(deepItem).length - 1">, </span>
                                                    </template>
                                                    <template v-else-if="Array.isArray(dVal)">
                                                      <span class="k">{{ dKey }}</span>: 
                                                      <span class="nested-toggle" @click="toggleNestedArray(`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}_${deepIdx}_${dKey}`)">
                                                        [{{ dVal.length }}项{{ expandedArrays[`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}_${deepIdx}_${dKey}`] ? '▲' : '▼' }}]
                                                      </span>
                                                      <div v-if="expandedArrays[`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}_${deepIdx}_${dKey}`]" class="nested-block">
                                                        <div v-for="(deeperItem, deeperIdx) in dVal" :key="deeperIdx" class="nested-line">
                                                          <span class="n-num">#{{ deeperIdx + 1 }}</span>
                                                          <span class="v">{{ typeof deeperItem === 'object' ? '[对象]' : deeperItem }}</span>
                                                        </div>
                                                      </div>
                                                    </template>
                                                    <template v-else>
                                                      <span class="k">{{ dKey }}</span>: <span class="v-obj">{obj}</span>
                                                    </template>
                                                  </span>
                                                </template>
                                                <!-- 简单值 -->
                                                <template v-else-if="Array.isArray(deepItem)">
                                                  <span class="nested-toggle" @click="toggleNestedArray(`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}_${deepIdx}`)">
                                                    [{{ deepItem.length }}项{{ expandedArrays[`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}_${deepIdx}`] ? '▲' : '▼' }}]
                                                  </span>
                                                  <div v-if="expandedArrays[`${fieldName}_${arrayItem.index}_${key}_${nIdx}_${nKey}_${deepIdx}`]" class="nested-block">
                                                    <div v-for="(item5, idx5) in deepItem" :key="idx5" class="nested-line">
                                                      <span class="n-num">#{{ idx5 + 1 }}</span>
                                                      <span class="v">{{ typeof item5 === 'object' ? '[对象]' : item5 }}</span>
                                                    </div>
                                                  </div>
                                                </template>
                                                <template v-else>
                                                  <span class="v">{{ deepItem }}</span>
                                                </template>
                                              </div>
                                            </div>
                                          </template>
                                          <template v-else>
                                            <span class="k">{{ nKey }}</span>: <span class="v-obj">{obj}</span>
                                          </template>
                                        </span>
                                      </template>
                                      <template v-else>
                                        <span class="v">{{ nested }}</span>
                                      </template>
                                    </div>
                                  </div>
                                </template>
                                <template v-else>
                                  <span class="k">{{ key }}</span>: <span class="v-obj">{obj}</span>
                                </template>
                              </span>
                            </template>
                            <template v-else>
                              {{ arrayItem.data }}
                            </template>
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 其他类型 -->
                    <span v-else class="summary-value">
                      {{ fieldData.value }}
                    </span>
                  </div>
                  
                  <!-- 缺陷详情（特殊处理 defect_categories - 向后兼容） -->
                  <div v-if="annotationSummary.defects && annotationSummary.defects.length > 0" class="summary-defects">
                    <div class="summary-label">缺陷详情 (旧版格式):</div>
                    <div 
                      v-for="defect in annotationSummary.defects" 
                      :key="defect.number"
                      class="defect-item"
                    >
                      <div class="defect-header">
                        <span class="defect-number">{{ defect.number }}.</span>
                        <span class="defect-category">{{ defect.category }}</span>
                        <el-tag 
                          :type="defect.compliance ? 'success' : 'warning'"
                          size="small"
                        >
                          {{ defect.compliance ? '✓' : '✗' }}
                        </el-tag>
                      </div>
                      <div v-if="defect.result" class="defect-result">
                        {{ defect.result }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>

            <!-- 标注表单 -->
            <el-card class="annotation-form-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Edit /></el-icon> 标注信息</span>
                  <div>
                    <el-button type="primary" @click="applyToAllImages" :icon="CopyDocument" :disabled="!annotation">
                      应用到所有图片
                    </el-button>
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

              <!-- 动态表单 - 根据配置生成 -->
              <el-form v-if="annotation && config && config.app_config && config.app_config.json_fields" :model="annotation" label-width="180px" label-position="left">
                <DynamicFormField
                  v-for="fieldConfig in config.app_config.json_fields"
                  :key="`${currentImage?.name}-${fieldConfig.name}`"
                  :fieldConfig="fieldConfig"
                  :modelValue="annotation"
                  :level="0"
                />
              </el-form>
            </el-card>
            </div>
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

        <!-- JSON 字段配置 -->
        <el-tab-pane label="字段配置" name="schema">
          <el-form label-width="140px" label-position="top" class="settings-form">
            <el-alert
              title="说明"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            >
              配置导出 JSON 的字段结构。定义每个字段的名称、类型和是否必填。支持无限嵌套子字段。
            </el-alert>

            <!-- 导入导出按钮 -->
            <div style="display: flex; gap: 12px; margin-bottom: 20px;">
              <el-button :icon="Download" @click="exportFieldConfig">
                导出字段配置
              </el-button>
              <el-upload
                :show-file-list="false"
                :before-upload="importFieldConfig"
                accept=".json"
                style="display: inline-block;"
              >
                <el-button :icon="Upload">
                  导入字段配置
                </el-button>
              </el-upload>
            </div>

            <!-- 字段列表 - 使用递归组件 -->
            <FieldEditor 
              v-for="(field, index) in settings.json_fields" 
              :key="index"
              :field="field"
              :level="0"
              @remove="removeField(index)"
            />

            <!-- 添加字段按钮 -->
            <el-button type="primary" :icon="Plus" @click="addField" style="width: 100%; margin-top: 10px;">
              添加顶级字段
            </el-button>
          </el-form>
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
  ZoomIn, ZoomOut, RefreshLeft, Check, CircleCheck, CircleClose, FolderOpened, Setting, Loading, Document, Delete, Plus, Upload, CopyDocument, DocumentChecked
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from './api'
import FieldEditor from './FieldEditor.vue'
import DynamicFormField from './DynamicFormField.vue'

// 数据状态
const images = ref([])
const currentImage = ref(null)
const annotation = ref(null)
const annotationSummary = ref(null)  // 标注摘要
const config = ref(null)
const searchText = ref('')
const zoomLevel = ref(1)
const settingsVisible = ref(false)
const activeTab = ref('basic')
const settings = ref({
  images_dir: '',
  annotations_dir: '',
  auto_save: true,
  json_indent: 2,
  prompt_template: '',
  json_fields: [
    { 
      name: 'overall_status', 
      type: 'string', 
      required: true, 
      defaultValue: 'PASS', 
      description: '整体检测状态',
      children: []
    },
    { 
      name: 'defect_categories', 
      type: 'array', 
      required: true, 
      defaultValue: '', 
      description: '缺陷分类列表',
      children: [
        { name: 'number', type: 'number', required: true, defaultValue: '', description: '序号', children: [] },
        { name: 'category', type: 'string', required: true, defaultValue: '', description: '分类名称', children: [] },
        { name: 'compliance', type: 'boolean', required: true, defaultValue: 'true', description: '是否合规', children: [] },
        { name: 'result', type: 'string', required: false, defaultValue: '', description: '检测结果', children: [] },
        { name: 'details', type: 'array', required: false, defaultValue: '', description: '详细信息', children: [] }
      ]
    },
    { 
      name: 'confidence_score', 
      type: 'number', 
      required: true, 
      defaultValue: '0.95', 
      description: '置信度分数',
      children: []
    },
    {
      name: 'processing_info',
      type: 'object',
      required: false,
      defaultValue: '',
      description: '处理信息',
      children: []
    }
  ]
})

// 数组展开状态管理
const expandedArrays = ref({})

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
    console.log('[图片列表已加载]', images.value.length, '张图片')
    console.log('[前3张图片]', images.value.slice(0, 3).map(img => img.name))
  } catch (error) {
    console.error('[加载图片列表失败]', error)
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
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

const selectImage = async (image) => {
  // 如果启用了自动保存，先保存当前标注
  if (settings.value.auto_save && currentImage.value && annotation.value) {
    try {
      await api.saveAnnotation(currentImage.value.name, annotation.value)
    } catch (error) {
      console.error('自动保存失败:', error)
    }
  }
  
  // 清空当前标注，防止旧数据渲染导致错误
  annotation.value = null
  annotationSummary.value = null
  
  // 设置当前图片
  currentImage.value = image
  zoomLevel.value = 1
  
  try {
    // 加载标注数据和摘要
    annotation.value = await api.getAnnotation(image.name)
    
    // 加载标注摘要
    try {
      annotationSummary.value = await api.getAnnotationSummary(image.name)
    } catch (error) {
      console.error('加载标注摘要失败:', error)
      // 摘要加载失败不影响主流程
    }
  } catch (error) {
    console.error('加载标注数据失败:', error)
    ElMessage.error('加载标注数据失败: ' + (error.message || '未知错误'))
  }
}

const getImageUrl = (filename) => {
  return api.getImageUrl(filename)
}

const getThumbnailUrl = (filename) => {
  return api.getThumbnailUrl(filename)
}

const saveAnnotation = async () => {
  try {
    // 验证必填字段
    const validationErrors = validateRequiredFields(annotation.value, config.value?.app_config?.json_fields || [])
    
    if (validationErrors.length > 0) {
      // 显示验证错误
      const errorMessage = '以下必填字段未填写：\n' + validationErrors.join('\n')
      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
      return
    }
    
    await api.saveAnnotation(currentImage.value.name, annotation.value)
    ElMessage.success('标注已保存')
    
    // 更新图片列表中的标注状态
    const img = images.value.find(i => i.name === currentImage.value.name)
    if (img) img.annotated = true
    
    // 自动刷新标注摘要
    try {
      annotationSummary.value = await api.getAnnotationSummary(currentImage.value.name)
      console.log('[标注摘要已更新]')
    } catch (error) {
      console.error('更新标注摘要失败:', error)
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

// 验证必填字段
const validateRequiredFields = (data, fieldConfigs, parentPath = '') => {
  const errors = []
  
  for (const fieldConfig of fieldConfigs) {
    const fieldName = fieldConfig.name
    const fieldPath = parentPath ? `${parentPath}.${fieldName}` : fieldName
    const fieldValue = data[fieldName]
    
    // 检查必填字段
    if (fieldConfig.required) {
      if (fieldConfig.type === 'string') {
        if (!fieldValue || fieldValue.trim() === '') {
          errors.push(`• ${fieldConfig.description || fieldName}`)
        }
      } else if (fieldConfig.type === 'number') {
        if (fieldValue === null || fieldValue === undefined || fieldValue === '') {
          errors.push(`• ${fieldConfig.description || fieldName}`)
        }
      } else if (fieldConfig.type === 'boolean') {
        if (fieldValue === null || fieldValue === undefined) {
          errors.push(`• ${fieldConfig.description || fieldName}`)
        }
      } else if (fieldConfig.type === 'array') {
        if (!Array.isArray(fieldValue) || fieldValue.length === 0) {
          errors.push(`• ${fieldConfig.description || fieldName}（至少需要一项）`)
        } else {
          // 验证数组中每一项的必填字段
          fieldValue.forEach((item, index) => {
            if (fieldConfig.children && fieldConfig.children.length > 0) {
              const itemErrors = validateRequiredFields(
                item, 
                fieldConfig.children, 
                `${fieldPath}[${index}]`
              )
              errors.push(...itemErrors)
            }
          })
        }
      } else if (fieldConfig.type === 'object') {
        if (!fieldValue || typeof fieldValue !== 'object') {
          errors.push(`• ${fieldConfig.description || fieldName}`)
        } else if (fieldConfig.children && fieldConfig.children.length > 0) {
          // 递归验证对象的子字段
          const childErrors = validateRequiredFields(
            fieldValue, 
            fieldConfig.children, 
            fieldPath
          )
          errors.push(...childErrors)
        }
      }
    }
    
    // 即使不是必填，如果有值，也要验证其子字段（针对对象和数组）
    if (!fieldConfig.required) {
      if (fieldConfig.type === 'array' && Array.isArray(fieldValue) && fieldValue.length > 0) {
        fieldValue.forEach((item, index) => {
          if (fieldConfig.children && fieldConfig.children.length > 0) {
            const itemErrors = validateRequiredFields(
              item, 
              fieldConfig.children, 
              `${fieldPath}[${index}]`
            )
            errors.push(...itemErrors)
          }
        })
      } else if (fieldConfig.type === 'object' && fieldValue && typeof fieldValue === 'object') {
        if (fieldConfig.children && fieldConfig.children.length > 0) {
          const childErrors = validateRequiredFields(
            fieldValue, 
            fieldConfig.children, 
            fieldPath
          )
          errors.push(...childErrors)
        }
      }
    }
  }
  
  return errors
}

// 应用当前配置到所有图片
const applyToAllImages = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要将当前标注配置应用到所有 ${images.value.length} 张图片吗？此操作会覆盖所有图片的现有标注。`,
      '批量应用配置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const currentAnnotation = JSON.parse(JSON.stringify(annotation.value))
    
    // 显示进度提示
    const loading = ElMessage({
      message: '正在应用配置...',
      type: 'info',
      duration: 0
    })
    
    // 使用并发请求优化性能（每批10个）
    const batchSize = 10
    let successCount = 0
    let failCount = 0
    
    for (let i = 0; i < images.value.length; i += batchSize) {
      const batch = images.value.slice(i, i + batchSize)
      const promises = batch.map(image => 
        api.saveAnnotation(image.name, currentAnnotation)
          .then(() => {
            successCount++
            image.annotated = true
            return { success: true, name: image.name }
          })
          .catch(error => {
            console.error(`应用到 ${image.name} 失败:`, error)
            failCount++
            return { success: false, name: image.name, error }
          })
      )
      
      await Promise.all(promises)
      
      // 更新进度提示
      loading.close()
      ElMessage({
        message: `进度: ${successCount + failCount}/${images.value.length}`,
        type: 'info',
        duration: 500
      })
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功应用配置到 ${successCount} 张图片`)
    } else {
      ElMessage.warning(`完成：成功 ${successCount} 张，失败 ${failCount} 张`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量应用失败: ' + error.message)
    }
  }
}

// 输出所有标注信息
const exportAllAnnotations = async () => {
  try {
    // 显示加载提示
    const loading = ElMessage({
      message: '正在加载标注数据...',
      type: 'info',
      duration: 0
    })
    
    const response = await api.getAllAnnotations()
    const annotations = response.annotations || []
    
    loading.close()
    
    if (annotations.length === 0) {
      ElMessage.warning('没有标注数据可以导出')
      return
    }
    
    // 转换所有标注为VLM格式
    const vlmDataList = annotations.map(item => {
      return convertToVLMFormat(item.image_name + '.jpeg', item.annotation)
    })
    
    const blob = new Blob([JSON.stringify(vlmDataList, null, settings.value.json_indent)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `all_annotations_vlm_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success(`成功导出 ${annotations.length} 条标注数据`)
  } catch (error) {
    console.error('Export all error:', error)
    ElMessage.error('导出失败：' + (error.message || '未知错误'))
  }
}

// 输出当前图片的标注信息
const exportCurrentAnnotation = async () => {
  if (!currentImage.value || !annotation.value) {
    ElMessage.warning('请先选择图片并完成标注')
    return
  }
  
  try {
    // 构建VLM格式的输出
    const vlmFormat = convertToVLMFormat(currentImage.value.name, annotation.value)
    
    const blob = new Blob([JSON.stringify(vlmFormat, null, settings.value.json_indent)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `annotation_${currentImage.value.name.replace(/\.[^/.]+$/, '')}_${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success(`成功导出 ${currentImage.value.name} 的标注数据`)
  } catch (error) {
    console.error('Export current error:', error)
    ElMessage.error('导出失败：' + (error.message || '未知错误'))
  }
}

// 转换为VLM格式
const convertToVLMFormat = (imageName, annotationData) => {
  // 计算相对于data目录的路径
  const imagePath = getRelativeImagePath(imageName)
  
  // 获取Prompt配置 - 直接从settings读取
  const userPrompt = settings.value.prompt_template || ''
  
  // 构建user content（prompt + 返回格式要求）
  let userContent = '<image>'
  if (userPrompt) {
    userContent += ' \n' + userPrompt
  }
  
  // 按照前端配置的字段顺序重新构建标注数据对象
  const orderedAnnotation = {}
  
  // 获取字段配置顺序
  const fieldConfigs = config.value?.app_config?.json_fields || []
  
  // 按照配置顺序添加字段
  fieldConfigs.forEach(fieldConfig => {
    const fieldName = fieldConfig.name
    if (annotationData[fieldName] !== undefined) {
      orderedAnnotation[fieldName] = annotationData[fieldName]
    }
  })
  
  // 添加配置中没有但数据中存在的其他字段（排除内部字段）
  for (const key in annotationData) {
    if (!orderedAnnotation.hasOwnProperty(key) &&
        key !== 'image_name' &&
        key !== 'image_path' &&
        key !== 'created_at' &&
        key !== 'updated_at') {
      orderedAnnotation[key] = annotationData[key]
    }
  }
  
  const assistantContent = JSON.stringify(orderedAnnotation, null, 2)
  
  // 构建VLM格式
  const vlmData = {
    images: [imagePath],
    messages: [
      {
        content: userContent,
        role: 'user'
      },
      {
        content: assistantContent,
        role: 'assistant'
      }
    ]
  }
  
  return vlmData
}

// 获取相对于data目录的图片路径
const getRelativeImagePath = (imageName) => {
  const imagesDir = settings.value.images_dir || ''
  
  // 标准化路径分隔符为反斜杠
  const normalizedPath = imagesDir.replace(/\//g, '\\')
  
  // 查找data目录的位置（不区分大小写）
  const dataIndex = normalizedPath.toLowerCase().indexOf('\\data\\')
  if (dataIndex === -1) {
    // 如果没有找到data目录，尝试查找/data/格式
    const dataIndexSlash = imagesDir.toLowerCase().indexOf('/data/')
    if (dataIndexSlash === -1) {
      // 都没找到，返回简单路径
      return imageName
    }
    // 提取data之后的路径（使用正斜杠）
    const relativePath = imagesDir.substring(dataIndexSlash + 6) // +6 跳过 /data/
    return relativePath + '/' + imageName
  }
  
  // 提取data之后的路径（使用反斜杠格式）
  const relativePath = normalizedPath.substring(dataIndex + 6) // +6 跳过 \data\
  // 转换为正斜杠格式（VLM标准格式）
  return relativePath.replace(/\\/g, '/') + '/' + imageName
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

// 删除当前图片
const deleteCurrentImage = async () => {
  if (!currentImage.value) {
    ElMessage.warning('没有选中的图片')
    return
  }
  
  try {
    // 确认删除
    await ElMessageBox.confirm(
      `确定要删除图片 "${currentImage.value.name}" 及其相关文件吗？此操作不可恢复！`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 执行删除
    const result = await api.deleteImage(currentImage.value.name)
    
    if (result.success) {
      ElMessage.success('删除成功')
      
      // 记录当前图片索引
      const currentIndex = images.value.findIndex(img => img.name === currentImage.value.name)
      
      // 重新加载图片列表
      await loadImages()
      
      // 选择下一张图片
      if (images.value.length > 0) {
        // 如果有下一张，选择下一张；否则选择前一张；否则清空
        const nextIndex = Math.min(currentIndex, images.value.length - 1)
        if (nextIndex >= 0) {
          selectImage(images.value[nextIndex])
        } else {
          currentImage.value = null
          annotation.value = null
        }
      } else {
        currentImage.value = null
        annotation.value = null
      }
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除图片失败:', error)
      ElMessage.error(error.message || '删除图片时发生错误')
    }
  }
}

const openSettings = async () => {
  // 打开设置前先加载最新配置
  await loadConfig()
  settingsVisible.value = true
}

const selectImagesFolder = async () => {
  // 检查是否支持 GUI
  const guiAvailable = config.value?.gui_available || false
  
  if (guiAvailable) {
    // GUI 模式：直接调用对话框
    try {
      const result = await api.selectFolder('images', '', true) // use_dialog = true
      if (result.success) {
        settings.value.images_dir = result.folder_path
        ElMessage.success(result.message || '图片文件夹设置成功')
      }
    } catch (error) {
      // 如果对话框失败，回退到手动输入
      if (error.response?.data?.use_manual_input) {
        await selectImagesFolderManually()
      } else {
        ElMessage.error('选择文件夹失败: ' + (error.message || error))
      }
    }
  } else {
    // 容器模式：手动输入
    await selectImagesFolderManually()
  }
}

const selectImagesFolderManually = async () => {
  try {
    const { value: folderPath } = await ElMessageBox.prompt(
      '请输入图片文件夹的完整路径' + (config.value?.gui_available ? '' : '（容器内路径）'), 
      '设置图片文件夹', 
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '例如: /app/data/images 或 /mnt/host_data/images',
        inputValue: settings.value.images_dir || '/app/data/images',
        inputValidator: (value) => {
          if (!value || value.trim() === '') {
            return '路径不能为空'
          }
          return true
        }
      }
    )
    
    // 验证路径
    const result = await api.selectFolder('images', folderPath.trim(), false) // use_dialog = false
    if (result.success) {
      settings.value.images_dir = result.folder_path
      ElMessage.success(result.message || '图片文件夹设置成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('设置文件夹失败: ' + (error.message || error))
    }
  }
}

const selectAnnotationsFolder = async () => {
  // 检查是否支持 GUI
  const guiAvailable = config.value?.gui_available || false
  
  if (guiAvailable) {
    // GUI 模式：直接调用对话框
    try {
      const result = await api.selectFolder('annotations', '', true) // use_dialog = true
      if (result.success) {
        settings.value.annotations_dir = result.folder_path
        ElMessage.success(result.message || '标注文件夹设置成功')
      }
    } catch (error) {
      // 如果对话框失败，回退到手动输入
      if (error.response?.data?.use_manual_input) {
        await selectAnnotationsFolderManually()
      } else {
        ElMessage.error('选择文件夹失败: ' + (error.message || error))
      }
    }
  } else {
    // 容器模式：手动输入
    await selectAnnotationsFolderManually()
  }
}

const selectAnnotationsFolderManually = async () => {
  try {
    const { value: folderPath } = await ElMessageBox.prompt(
      '请输入标注文件夹的完整路径' + (config.value?.gui_available ? '' : '（容器内路径）'), 
      '设置标注文件夹', 
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '例如: /app/data/annotations 或 /mnt/host_data/annotations',
        inputValue: settings.value.annotations_dir || '/app/data/annotations',
        inputValidator: (value) => {
          if (!value || value.trim() === '') {
            return '路径不能为空'
          }
          return true
        }
      }
    )
    
    // 验证路径
    const result = await api.selectFolder('annotations', folderPath.trim(), false) // use_dialog = false
    if (result.success) {
      settings.value.annotations_dir = result.folder_path
      ElMessage.success(result.message || '标注文件夹设置成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('设置文件夹失败: ' + (error.message || error))
    }
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
    
    // 如果当前有打开的标注，强制重新加载以应用新配置
    if (currentImage.value) {
      try {
        annotation.value = await api.getAnnotation(currentImage.value.name)
        ElMessage.info('标注数据已根据新配置重新加载')
      } catch (error) {
        console.error('重新加载标注失败:', error)
      }
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败: ' + error.message)
  }
}

// 同步标注数据结构与配置
const syncAnnotationWithConfig = (annotationData) => {
  if (!config.value || !config.value.app_config || !config.value.app_config.json_fields) {
    return annotationData
  }

  const newAnnotation = {}
  
  // 根据配置字段重建标注数据
  config.value.app_config.json_fields.forEach(fieldConfig => {
    const fieldName = fieldConfig.name
    
    // 保留原有值，如果不存在则使用默认值
    if (fieldName in annotationData) {
      newAnnotation[fieldName] = annotationData[fieldName]
    } else {
      newAnnotation[fieldName] = getDefaultValueForField(fieldConfig)
    }
    
    // 递归同步嵌套字段
    if (fieldConfig.type === 'object' && fieldConfig.children && fieldConfig.children.length > 0) {
      newAnnotation[fieldName] = syncObjectField(newAnnotation[fieldName], fieldConfig.children)
    } else if (fieldConfig.type === 'array' && fieldConfig.children && fieldConfig.children.length > 0) {
      if (Array.isArray(newAnnotation[fieldName])) {
        newAnnotation[fieldName] = newAnnotation[fieldName].map(item => 
          syncObjectField(item, fieldConfig.children)
        )
      }
    }
  })
  
  return newAnnotation
}

// 同步对象字段
const syncObjectField = (obj, childConfigs) => {
  const syncedObj = {}
  
  childConfigs.forEach(childConfig => {
    const fieldName = childConfig.name
    if (obj && fieldName in obj) {
      syncedObj[fieldName] = obj[fieldName]
    } else {
      syncedObj[fieldName] = getDefaultValueForField(childConfig)
    }
    
    // 递归处理嵌套
    if (childConfig.type === 'object' && childConfig.children && childConfig.children.length > 0) {
      syncedObj[fieldName] = syncObjectField(syncedObj[fieldName], childConfig.children)
    } else if (childConfig.type === 'array' && childConfig.children && childConfig.children.length > 0) {
      if (Array.isArray(syncedObj[fieldName])) {
        syncedObj[fieldName] = syncedObj[fieldName].map(item => 
          syncObjectField(item, childConfig.children)
        )
      }
    }
  })
  
  return syncedObj
}

// 获取字段默认值
const getDefaultValueForField = (fieldConfig) => {
  if (fieldConfig.defaultValue !== undefined && fieldConfig.defaultValue !== '') {
    if (fieldConfig.type === 'boolean') {
      return fieldConfig.defaultValue === 'true' || fieldConfig.defaultValue === true
    } else if (fieldConfig.type === 'number') {
      return parseFloat(fieldConfig.defaultValue) || 0
    }
    return fieldConfig.defaultValue
  }

  switch (fieldConfig.type) {
    case 'string':
      return ''
    case 'number':
      return 0
    case 'boolean':
      return false
    case 'array':
      return []
    case 'object':
      return {}
    default:
      return null
  }
}

// 获取数组项字段的显示标签
const getFieldLabel = (fieldKey, childrenConfig) => {
  if (!childrenConfig || childrenConfig.length === 0) {
    return fieldKey
  }
  
  // 查找对应的子字段配置
  const fieldConfig = childrenConfig.find(c => c.name === fieldKey)
  if (fieldConfig && fieldConfig.description && fieldConfig.description.trim()) {
    return fieldConfig.description
  }
  
  return fieldKey
}

// 切换数组展开/收起状态
const toggleArrayExpand = (fieldName) => {
  expandedArrays.value[fieldName] = !expandedArrays.value[fieldName]
}

// 切换嵌套数组展开/收起状态
const toggleNestedArray = (key) => {
  expandedArrays.value[key] = !expandedArrays.value[key]
}

// 获取数组项的摘要信息（显示前2-3个关键字段）
const getArrayItemSummary = (data, childrenConfig) => {
  if (typeof data !== 'object' || Array.isArray(data)) {
    return String(data)
  }
  
  // 获取关键字段的优先级顺序
  const priorityFields = ['name', 'title', 'category', 'type', 'status', 'number', 'id']
  
  // 找出关键字段
  const keyFields = []
  for (const field of priorityFields) {
    if (field in data && data[field] !== null && data[field] !== undefined) {
      const label = getFieldLabel(field, childrenConfig)
      keyFields.push(`${label}: ${data[field]}`)
      if (keyFields.length >= 2) break
    }
  }
  
  // 如果没有关键字段，取前2个字段
  if (keyFields.length === 0) {
    const entries = Object.entries(data).slice(0, 2)
    entries.forEach(([key, value]) => {
      const label = getFieldLabel(key, childrenConfig)
      keyFields.push(`${label}: ${value}`)
    })
  }
  
  return keyFields.join(', ') || '(空)'
}

// 添加字段
const addField = () => {
  settings.value.json_fields.push({
    name: '',
    type: 'string',
    required: false,
    defaultValue: '',
    description: '',
    children: []
  })
}

// 删除字段
const removeField = (index) => {
  settings.value.json_fields.splice(index, 1)
}

// 导出字段配置
const exportFieldConfig = () => {
  try {
    const config = {
      version: '1.0',
      exportTime: new Date().toISOString(),
      json_fields: settings.value.json_fields
    }
    
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `field-config-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('字段配置已导出')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 导入字段配置
const importFieldConfig = (file) => {
  const reader = new FileReader()
  
  reader.onload = (e) => {
    try {
      const config = JSON.parse(e.target.result)
      
      // 验证配置格式
      if (!config.json_fields || !Array.isArray(config.json_fields)) {
        throw new Error('配置文件格式不正确')
      }
      
      // 验证每个字段的必需属性
      for (const field of config.json_fields) {
        if (!field.name || !field.type) {
          throw new Error('字段配置缺少必需属性 name 或 type')
        }
      }
      
      // 确保每个字段都有 children 属性
      const processFields = (fields) => {
        return fields.map(field => ({
          ...field,
          children: field.children ? processFields(field.children) : []
        }))
      }
      
      settings.value.json_fields = processFields(config.json_fields)
      
      ElMessage.success('字段配置已导入，请点击"保存设置"生效')
    } catch (error) {
      ElMessage.error('导入失败: ' + error.message)
    }
  }
  
  reader.onerror = () => {
    ElMessage.error('读取文件失败')
  }
  
  reader.readAsText(file)
  
  // 阻止默认上传行为
  return false
}

const selectFolder = () => {
  // 打开设置对话框
  openSettings()
}

const handleImageError = (event) => {
  console.error('图片加载失败:', event.target.src)
  ElMessage.error('图片加载失败，请检查图片路径')
}

const handleThumbnailLoad = (event) => {
  // 缩略图加载成功
  const filename = event.target.alt
  console.log('[缩略图加载成功]', filename, `${event.target.naturalWidth}x${event.target.naturalHeight}`)
}

const handleThumbnailError = (event) => {
  // 缩略图加载失败时，回退到原图
  const filename = event.target.alt || event.target.dataset.filename
  const currentSrc = event.target.src
  const thumbnailUrl = api.getThumbnailUrl(filename)
  const imageUrl = api.getImageUrl(filename)
  
  console.warn('[缩略图加载失败]', {
    filename,
    currentSrc,
    thumbnailUrl,
    imageUrl,
    isThumbnailUrl: currentSrc.includes('/thumbnails/')
  })
  
  // 如果当前是缩略图URL，尝试回退到原图
  if (currentSrc.includes('/thumbnails/')) {
    console.log('[回退到原图]', filename, imageUrl)
    event.target.src = imageUrl
    // 移除任何错误样式
    event.target.style.opacity = '1'
    event.target.style.filter = 'none'
  } else {
    // 如果原图也失败，显示占位符但不要完全隐藏
    console.error('[原图也加载失败]', filename)
    // 不再设置低透明度，而是显示明显的错误状态
    event.target.style.border = '2px solid red'
    event.target.style.background = '#ffebee'
  }
}

const handleImageLoad = () => {
  // 图片加载成功的回调（可以用于加载动画等）
}

// 生命周期
onMounted(async () => {
  console.log('[应用已挂载]')
  await loadConfig()
  await loadImages()
  console.log('[初始化完成]')
})
</script>

<style scoped>
/* 全局优化 */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper):hover {
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

:deep(.el-card) {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

:deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  background: #ffffff;
  color: #303133;
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-dialog__title) {
  color: #303133;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #909399;
  font-size: 20px;
}

:deep(.el-dialog__headerbtn .el-dialog__close):hover {
  color: #303133;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-tabs__item) {
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-tabs__item.is-active) {
  color: #667eea;
  font-weight: 600;
}

:deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  height: 3px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app-container {
  height: 100vh;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
}

.app-header {
  background: #ffffff;
  color: #303133;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.app-header h1 {
  font-size: 22px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #303133;
}

.app-header h1 .el-icon {
  font-size: 26px;
  color: #667eea;
}

.app-header h1 .author-info {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
  margin-left: 8px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.header-actions .el-button {
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 20px;
  transition: all 0.3s ease;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  color: #606266;
}

.header-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
  color: #667eea;
}

.header-actions .el-button.el-button--primary {
  background: #667eea;
  border-color: #667eea;
  color: #ffffff;
}

.header-actions .el-button.el-button--primary:hover {
  background: #5568d3;
  border-color: #5568d3;
}

.header-actions .el-button.el-button--success {
  background: #67c23a;
  border-color: #67c23a;
  color: #ffffff;
}

.header-actions .el-button.el-button--success:hover {
  background: #5daf34;
  border-color: #5daf34;
}

.header-actions .el-button.el-button--warning {
  background: #e6a23c;
  border-color: #e6a23c;
  color: #ffffff;
}

.header-actions .el-button.el-button--warning:hover {
  background: #cf9236;
  border-color: #cf9236;
}

.main-container {
  height: calc(100vh - 60px);
}

.image-list-sidebar {
  background: #f8f9fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #ffffff;
}

.sidebar-header h3 {
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.sidebar-header .el-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.sidebar-header .el-input :deep(.el-input__wrapper):hover {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.image-list {
  flex: 1;
  height: calc(100vh - 180px);
  overflow-y: auto;
}

.image-item {
  display: flex;
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #e4e7ed;
  transition: all 0.3s ease;
  background: #ffffff;
  margin: 0 8px 4px 8px;
  border-radius: 8px;
}

.image-item:hover {
  background: #f0f7ff;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.image-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-left: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.image-item.active .image-name,
.image-item.active .image-status {
  color: #ffffff;
}

.image-thumbnail {
  width: 60px !important;
  height: 60px !important;
  min-width: 60px !important;
  min-height: 60px !important;
  margin-right: 10px;
  border-radius: 6px;
  overflow: hidden;
  background: #f5f5f7;
  border: 1px solid #e5e5e7;
  display: flex !important;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.image-thumbnail img {
  width: 100% !important;
  height: 100% !important;
  max-width: 100% !important;
  max-height: 100% !important;
  object-fit: cover;
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  color: #999;
}

.thumbnail-placeholder svg {
  width: 30px;
  height: 30px;
  opacity: 0.5;
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
  padding: 24px;
  overflow-y: auto;
  background: #f5f6fa;
  height: 100%;
}

.debug-info {
  background: #f5f5f7;
  padding: 4px 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.debug-filename {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.debug-status,
.debug-zoom {
  flex-shrink: 0;
  padding: 0 6px;
  background: #e4e7ed;
  border-radius: 2px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.annotation-workspace {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr 1fr;
  align-items: start;
}

@media (max-width: 1400px) {
  .annotation-workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .card-header {
    padding: 12px 16px;
  }
  
  .card-header .card-title {
    font-size: 14px;
  }
  
  .card-header .zoom-controls .el-button span:not(.el-icon) {
    display: none;
  }
  
  .card-header .zoom-controls .el-button {
    padding: 8px;
  }
}

.image-viewer-card,
.annotation-form-card {
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.image-viewer-card:hover,
.annotation-form-card:hover {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.12);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
  padding: 16px 20px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  gap: 16px;
  min-height: 60px;
}

.card-header .card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.card-header .image-name-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.card-header .zoom-controls {
  flex-shrink: 0;
}

.card-header .el-icon {
  font-size: 20px;
  color: #667eea;
  flex-shrink: 0;
}

.image-viewer-card {
  height: fit-content;
  border: 1px solid #d2d2d7;
  margin-top: 0px;
}

.image-viewer {
  background: #ffffff;
  border-radius: 8px;
  min-height: 300px;
  max-height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 450px;
  transition: transform 0.3s;
  cursor: zoom-in;
  border-radius: 4px;
}

/* 标注摘要样式 */
.annotation-summary {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
  font-size: 14px;
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.summary-item-array {
  flex-direction: column;
  align-items: flex-start;
}

.summary-label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.summary-value {
  color: #1d1d1f;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

/* 超紧凑内联数组展示 */
.summary-array-inline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.inline-expand-btn {
  font-size: 11px;
  padding: 0 4px;
  height: 20px;
  min-width: 24px;
}

.inline-items {
  width: 100%;
  margin-top: 4px;
  font-size: 11px;
  line-height: 1.5;
}

.inline-item {
  display: flex;
  gap: 6px;
  padding: 2px 0;
  border-left: 2px solid #e4e7ed;
  padding-left: 8px;
  margin-bottom: 2px;
}

.item-num {
  font-weight: 600;
  color: #667eea;
  min-width: 22px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  color: #606266;
  display: inline;
}

.field-pair {
  display: inline;
}

.field-pair .k {
  font-weight: 500;
  color: #909399;
}

.field-pair .v {
  color: #303133;
}

.field-pair .v-bool {
  color: #67c23a;
  font-weight: 600;
}

.field-pair .v-obj {
  color: #909399;
  font-style: italic;
  font-size: 10px;
}

.field-pair .sep {
  color: #dcdfe6;
}

/* 嵌套数组紧凑样式 */
.nested-toggle {
  display: inline-block;
  cursor: pointer;
  color: #409eff;
  font-size: 10px;
  padding: 0 4px;
  border-radius: 2px;
  background: #ecf5ff;
  margin: 0 2px;
  user-select: none;
}

.nested-toggle:hover {
  background: #d9ecff;
}

.nested-block {
  width: 100%;
  margin-top: 2px;
  margin-left: 16px;
  padding-left: 8px;
  border-left: 1px solid #e4e7ed;
}

.nested-line {
  display: flex;
  gap: 6px;
  padding: 1px 0;
  font-size: 10px;
}

.n-num {
  font-weight: 600;
  color: #909399;
  min-width: 18px;
  flex-shrink: 0;
  font-size: 10px;
}

/* 旧版兼容样式 - 保留但标记 */
.summary-array {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.array-summary {
  display: flex;
  align-items: center;
  gap: 8px;
}

.array-items-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.array-item-card {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  padding: 10px 12px;
  transition: all 0.2s ease;
}

.array-item-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.array-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f0f0;
}

.array-item-number {
  font-weight: 600;
  color: #667eea;
  font-size: 13px;
}

.array-item-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.array-item-field {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  line-height: 1.5;
}

.field-key {
  font-weight: 500;
  color: #666;
  min-width: 60px;
  flex-shrink: 0;
}

.field-value {
  color: #1d1d1f;
  flex: 1;
  word-break: break-word;
}

.array-item-simple {
  color: #1d1d1f;
  font-size: 12px;
}

.nested-array,
.nested-object {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #909399;
}

.summary-defects {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.defect-item {
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  font-size: 12px;
}

.defect-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.defect-number {
  font-weight: 600;
  color: #666;
  min-width: 20px;
}

.defect-category {
  font-weight: 500;
  color: #1d1d1f;
  flex: 1;
}

.defect-result {
  margin-top: 4px;
  padding-left: 28px;
  color: #666;
  line-height: 1.5;
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
  margin-top: 0px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 140px);
}

.annotation-form-card :deep(.el-card__body) {
  overflow-y: auto;
  flex: 1;
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
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.folder-select:hover {
  border-color: #409eff;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.folder-select .el-input {
  flex: 1;
}

.folder-select .el-input :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none;
  border: none;
  font-size: 14px;
}

.folder-select .el-button {
  flex-shrink: 0;
  min-width: 120px;
  white-space: nowrap;
  height: 38px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.folder-select .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.settings-form {
  padding: 20px 0;
}

.settings-form .el-form-item {
  margin-bottom: 28px;
}

.settings-form .el-form-item__label {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

/* 置信度分数滑块优化 - 解决重合问题 */
.confidence-slider-wrapper {
  display: flex;
  align-items: center;
  gap: 20px;
  width: 100%;
  padding: 10px 0;
}

.confidence-slider-wrapper :deep(.el-slider) {
  flex: 1;
  min-width: 200px;
}

.confidence-slider-wrapper :deep(.el-slider__runway) {
  margin: 16px 0;
  height: 6px;
}

.confidence-slider-wrapper :deep(.el-slider__bar) {
  height: 6px;
  background: linear-gradient(90deg, #409eff, #0071e3);
}

.confidence-slider-wrapper :deep(.el-slider__button) {
  width: 20px;
  height: 20px;
  border: 2px solid #0071e3;
}

.confidence-slider-wrapper :deep(.el-slider__button-wrapper) {
  z-index: 1;
}

.confidence-value {
  font-size: 18px;
  font-weight: 600;
  color: #0071e3;
  min-width: 60px;
  text-align: right;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
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

/* 字段配置样式 */
.field-config-item {
  margin-bottom: 15px;
}

.field-config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.field-config-header h4 {
  margin: 0;
  font-size: 16px;
  color: #1d1d1f;
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
