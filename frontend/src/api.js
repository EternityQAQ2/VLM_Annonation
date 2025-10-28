import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:9011/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 获取配置
  getConfig() {
    return api.get('/config')
  },
  
  // 更新配置
  updateConfig(config) {
    return api.post('/config', config)
  },
  
  // 选择文件夹
  selectFolder(folderType, folderPath = '', useDialog = true) {
    return api.post('/select-folder', { 
      folder_type: folderType,
      folder_path: folderPath,
      use_dialog: useDialog
    })
  },
  
  // 获取图片列表
  getImages() {
    return api.get('/images')
  },
  
  // 获取图片URL
  getImageUrl(filename) {
    // 直接使用后端端口
    return `http://localhost:9011/api/images/${encodeURIComponent(filename)}`
  },
  
  // 获取缩略图URL
  getThumbnailUrl(filename) {
    // 直接使用后端端口
    return `http://localhost:9011/api/thumbnails/${encodeURIComponent(filename)}`
  },
  
  // 获取标注数据
  getAnnotation(imageName) {
    return api.get(`/annotations/${imageName}`)
  },
  
  // 保存标注数据
  saveAnnotation(imageName, data) {
    return api.post(`/annotations/${imageName}`, data)
  },
  
  // 获取所有标注
  getAllAnnotations() {
    return api.get('/annotations')
  },
  
  // 打开文件夹
  openFolder(folderType) {
    return api.post('/open-folder', { folder_type: folderType })
  }
}
