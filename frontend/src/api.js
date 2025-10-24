import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
  
  // 获取图片列表
  getImages() {
    return api.get('/images')
  },
  
  // 获取图片URL
  getImageUrl(filename) {
    return `/api/images/${filename}`
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
  
  // 导出数据集
  exportDataset() {
    return api.get('/export')
  },
  
  // 打开文件夹
  openFolder(folderType) {
    return api.post('/open-folder', { folder_type: folderType })
  }
}
