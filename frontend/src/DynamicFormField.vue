<template>
  <div :style="{ marginLeft: `${level * 20}px` }">
    <!-- 布尔类型 - 检查实际数据类型或配置类型 -->
    <el-form-item v-if="getActualType() === 'boolean'" :label="fieldConfig.description || fieldConfig.name">
      <el-radio-group v-model="modelValue[fieldConfig.name]">
        <el-radio :label="true">
          <el-icon color="#67C23A"><CircleCheck /></el-icon> TRUE
        </el-radio>
        <el-radio :label="false">
          <el-icon color="#F56C6C"><CircleClose /></el-icon> FALSE
        </el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 数字类型 -->
    <el-form-item v-else-if="getActualType() === 'number'" :label="fieldConfig.description || fieldConfig.name">
      <el-input-number 
        v-model="modelValue[fieldConfig.name]" 
        :placeholder="`请输入${fieldConfig.description || fieldConfig.name}`"
        style="width: 100%;"
      />
    </el-form-item>

    <!-- 字符串类型 -->
    <el-form-item v-else-if="getActualType() === 'string'" :label="fieldConfig.description || fieldConfig.name">
      <el-input 
        v-model="modelValue[fieldConfig.name]" 
        :placeholder="`请输入${fieldConfig.description || fieldConfig.name}`"
      />
    </el-form-item>

    <!-- 数组类型 - 显示每个数组项 -->
    <div v-else-if="getActualType() === 'array'" class="array-field">
      <div class="array-header">
        <h4>{{ fieldConfig.description || fieldConfig.name }}</h4>
        <el-button 
          type="primary" 
          size="small" 
          :icon="Plus"
          @click="addArrayItem"
        >
          添加项
        </el-button>
      </div>

      <div 
        v-for="(item, index) in modelValue[fieldConfig.name]" 
        :key="index"
        class="array-item"
      >
        <el-card :body-style="{ padding: '15px' }">
          <div class="array-item-header">
            <span class="item-number">#{{ index + 1 }}</span>
            <el-button 
              type="danger" 
              size="small"
              :icon="Delete"
              @click="removeArrayItem(index)"
            >
              删除
            </el-button>
          </div>

          <!-- 递归渲染子字段 -->
          <DynamicFormField
            v-for="childConfig in fieldConfig.children"
            :key="childConfig.name"
            :fieldConfig="childConfig"
            :modelValue="item"
            :level="level + 1"
          />
        </el-card>
      </div>
    </div>

    <!-- 对象类型 - 递归渲染子字段 -->
    <div v-else-if="getActualType() === 'object'" class="object-field">
      <el-divider content-position="left">
        <h4>{{ fieldConfig.description || fieldConfig.name }}</h4>
      </el-divider>
      
      <DynamicFormField
        v-for="childConfig in fieldConfig.children"
        :key="childConfig.name"
        :fieldConfig="childConfig"
        :modelValue="ensureObject(fieldConfig.name)"
        :level="level + 1"
      />
    </div>
  </div>
</template>

<script setup>
import { CircleCheck, CircleClose, Plus, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  fieldConfig: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
})

// 获取字段的实际类型（优先使用数据的实际类型，而不是配置类型）
const getActualType = () => {
  const fieldName = props.fieldConfig.name
  const actualValue = props.modelValue[fieldName]
  
  // 如果字段已存在，根据实际值判断类型
  if (actualValue !== undefined && actualValue !== null && actualValue !== '') {
    if (typeof actualValue === 'boolean') {
      return 'boolean'
    }
    if (typeof actualValue === 'number') {
      return 'number'
    }
    if (typeof actualValue === 'string') {
      return 'string'
    }
    if (Array.isArray(actualValue)) {
      return 'array'
    }
    if (typeof actualValue === 'object') {
      return 'object'
    }
  }
  
  // 否则使用配置的类型
  return props.fieldConfig.type
}

// 初始化字段默认值
const initializeField = () => {
  // 确保 modelValue 是对象
  if (!props.modelValue || typeof props.modelValue !== 'object') {
    return
  }
  
  if (!(props.fieldConfig.name in props.modelValue)) {
    const defaultValue = getDefaultValue(props.fieldConfig)
    props.modelValue[props.fieldConfig.name] = defaultValue
  }
}

const getDefaultValue = (config) => {
  if (config.defaultValue !== undefined && config.defaultValue !== '') {
    // 尝试解析默认值
    if (config.type === 'boolean') {
      return config.defaultValue === 'true' || config.defaultValue === true
    } else if (config.type === 'number') {
      return parseFloat(config.defaultValue) || 0
    }
    return config.defaultValue
  }

  // 根据类型返回默认值
  switch (config.type) {
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

// 确保对象字段存在
const ensureObject = (fieldName) => {
  if (!props.modelValue[fieldName]) {
    props.modelValue[fieldName] = {}
  }
  return props.modelValue[fieldName]
}

// 添加数组项
const addArrayItem = () => {
  if (!props.modelValue[props.fieldConfig.name]) {
    props.modelValue[props.fieldConfig.name] = []
  }

  // 根据子字段配置创建新项
  const newItem = createItemFromConfig(props.fieldConfig.children || [])

  props.modelValue[props.fieldConfig.name].push(newItem)
}

// 递归创建对象结构
const createItemFromConfig = (childConfigs) => {
  const item = {}
  childConfigs.forEach(childConfig => {
    item[childConfig.name] = getDefaultValue(childConfig)
    
    // 如果子字段也是容器类型且有children，递归创建
    if ((childConfig.type === 'array' || childConfig.type === 'object') && childConfig.children && childConfig.children.length > 0) {
      if (childConfig.type === 'array') {
        item[childConfig.name] = [] // 数组默认为空
      } else {
        item[childConfig.name] = createItemFromConfig(childConfig.children)
      }
    }
  })
  return item
}

// 删除数组项
const removeArrayItem = (index) => {
  props.modelValue[props.fieldConfig.name].splice(index, 1)
}

// 组件挂载时初始化字段
initializeField()
</script>

<style scoped>
.array-field {
  margin: 20px 0;
}

.array-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.array-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.array-item {
  margin-bottom: 15px;
}

.array-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.item-number {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

.object-field {
  margin: 15px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.object-field h4 {
  margin: 0;
  font-size: 15px;
  color: #606266;
  font-weight: 600;
}
</style>
