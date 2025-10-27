<template>
  <el-collapse 
    v-model="activeNames"
    :style="{ marginLeft: `${level * 15}px`, marginBottom: '12px' }"
  >
    <el-collapse-item :name="1">
      <template #title>
        <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
          <el-tag :type="getTypeColor(field.type)" size="small">{{ field.type }}</el-tag>
          <span style="font-weight: 600; flex: 1;">
            {{ field.name || '未命名字段' }}
            <span v-if="field.description" style="color: #909399; font-weight: normal; font-size: 13px;">
              - {{ field.description }}
            </span>
          </span>
          <el-tag v-if="field.required" type="danger" size="small">必填</el-tag>
          <el-tag v-if="canHaveChildren && field.children" type="info" size="small">
            {{ field.children.length }} 个子字段
          </el-tag>
        </div>
      </template>

      <div style="padding: 15px; background: #fafbfc; border-radius: 8px;">
        <!-- 删除按钮 -->
        <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
          <el-button type="danger" size="small" @click="$emit('remove')" :icon="Delete">
            删除此字段
          </el-button>
        </div>

        <el-form label-width="120px" size="small" label-position="left">

    <!-- 字段名称 -->
    <el-form-item label="字段名称">
      <el-input v-model="field.name" placeholder="例如：overall_status" style="width: 100%;" />
    </el-form-item>

    <!-- 字段类型 -->
    <el-form-item label="字段类型">
      <el-select v-model="field.type" @change="onTypeChange" style="width: 100%;">
        <el-option label="字符串 (string)" value="string" />
        <el-option label="数字 (number)" value="number" />
        <el-option label="布尔值 (boolean)" value="boolean" />
        <el-option label="数组 (array)" value="array" />
        <el-option label="对象 (object)" value="object" />
      </el-select>
    </el-form-item>

    <!-- 是否必填 -->
    <el-form-item label="是否必填">
      <div style="height: 32px; display: flex; align-items: center;">
        <el-switch v-model="field.required" />
      </div>
    </el-form-item>

    <!-- 默认值（非容器类型） -->
    <el-form-item label="默认值" v-if="!canHaveChildren">
      <el-input v-model="field.defaultValue" placeholder="可选" style="width: 100%;" />
    </el-form-item>

    <!-- 说明 -->
    <el-form-item label="说明">
      <el-input v-model="field.description" type="textarea" :rows="2" placeholder="字段用途说明" style="width: 100%;" />
    </el-form-item>

    <!-- 子字段区域 -->
    <div v-if="canHaveChildren" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dcdfe6;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h5 style="margin: 0; color: #606266; font-weight: 600;">
          <el-icon style="vertical-align: middle;"><FolderOpened /></el-icon>
          子字段 ({{ field.children?.length || 0 }} 个)
        </h5>
        <el-button type="primary" size="small" @click="addChildField" :icon="Plus">
          添加子字段
        </el-button>
      </div>
      
      <!-- 递归渲染子字段 -->
      <FieldEditor
        v-for="(child, index) in field.children"
        :key="index"
        :field="child"
        :level="level + 1"
        @remove="removeChildField(index)"
      />
      
      <!-- 空状态提示 -->
      <div v-if="!field.children || field.children.length === 0" style="text-align: center; padding: 20px; color: #909399;">
        暂无子字段，点击上方按钮添加
      </div>
    </div>
        </el-form>
      </div>
    </el-collapse-item>
  </el-collapse>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Delete, Plus, FolderOpened } from '@element-plus/icons-vue'

const activeNames = ref([1]) // 默认展开

const props = defineProps({
  field: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
})

defineEmits(['remove'])

const canHaveChildren = computed(() => {
  return props.field.type === 'array' || props.field.type === 'object'
})

const getTypeColor = (type) => {
  const colors = {
    'string': 'success',
    'number': 'warning',
    'boolean': 'danger',
    'array': 'primary',
    'object': 'info'
  }
  return colors[type] || ''
}

const onTypeChange = (newType) => {
  // 如果改为非容器类型，清空子字段
  if (newType !== 'array' && newType !== 'object' && props.field.children) {
    props.field.children = []
  } else if ((newType === 'array' || newType === 'object') && !props.field.children) {
    props.field.children = []
  }
}

const addChildField = () => {
  if (!props.field.children) {
    props.field.children = []
  }
  props.field.children.push({
    name: '',
    type: 'string',
    required: false,
    defaultValue: '',
    description: '',
    children: []
  })
}

const removeChildField = (index) => {
  props.field.children.splice(index, 1)
}
</script>

<style scoped>
.el-form-item {
  margin-bottom: 15px;
}
</style>
