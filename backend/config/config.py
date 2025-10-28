"""
配置管理模块
"""
import json
from pathlib import Path
from datetime import datetime


class Config:
    """应用配置管理类"""
    
    def __init__(self, config_file='config.json'):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.config_file = self.base_dir / config_file
        
        # 默认配置
        self.default_config = {
            "images_dir": str(self.data_dir / "images"),
            "annotations_dir": str(self.data_dir / "annotations"),
            "auto_save": True,
            "json_indent": 2,
            "prompt_template": self._get_default_prompt_template(),
            "json_fields": self._get_default_json_fields()
        }
        
        # 加载配置
        self.config = self.load()
        
        # 初始化目录
        self.init_directories()
    
    def _get_default_prompt_template(self):
        """获取默认的提示词模板"""
        return """<image> 
你是一个工业打印标签检测专家。
只关注标签区域（金属凹陷处区域），金属凹陷处外的缺陷不予考虑，请按照以下缺陷类型分类检测标签质量：
1. 缺失元素（文字、二维码等关键元素丢失）或过多元素（如打印本不应该有的元素）
2. 偏移问题（标签位置偏移、字符偏移）
3. 物理缺陷（气泡、皱褶、划痕、污渍、墨点,标签多打印，标签断裂、打印颠倒）
4. 打印质量（字迹模糊、字迹黯淡、字符打印不完整、二维码打印质量、二维码打印不完整、打印字符错误等）
5. 整体布局（元素排版问题）

返回格式如下（JSON可以换行，便于阅读）：
{
  "overall_status": "PASS" 或 "FAIL",
  "defect_categories": [
    {
      "number": 1,
      "category": "缺失元素",
      "compliance": true/false,
      "result": "具体检测结果描述",
      "details": []
    },
    {
      "number": 2,
      "category": "偏移问题",
      "compliance": true/false,
      "result": "具体检测结果描述",
      "details": []
    },
    {
      "number": 3,
      "category": "物理缺陷",
      "compliance": true/false,
      "result": "具体检测结果描述",
      "details": []
    },
    {
      "number": 4,
      "category": "打印质量",
      "compliance": true/false,
      "result": "具体检测结果描述",
      "details": []
    },
    {
      "number": 5,
      "category": "整体布局",
      "compliance": true/false,
      "result": "具体检测结果描述",
      "details": []
    }
  ],
  "confidence_score": 0.95,
  "processing_info": {
    "stage": "defect_classification",
    "template_matched": true,
    "categories_checked": ["缺失元素", "偏移问题", "物理缺陷", "打印质量", "整体布局"]
  }
}

请只返回这个JSON格式的内容，JSON可以换行以便阅读。"""
    
    def _get_default_json_fields(self):
        """获取默认的JSON字段配置"""
        return [
            {
                "name": "overall_status",
                "type": "string",
                "required": True,
                "defaultValue": "PASS",
                "description": "整体检测状态",
                "children": []
            },
            {
                "name": "defect_categories",
                "type": "array",
                "required": True,
                "defaultValue": "",
                "description": "缺陷分类列表",
                "children": [
                    {"name": "number", "type": "number", "required": True, "defaultValue": "", "description": "序号", "children": []},
                    {"name": "category", "type": "string", "required": True, "defaultValue": "", "description": "分类名称", "children": []},
                    {"name": "compliance", "type": "boolean", "required": True, "defaultValue": "true", "description": "是否合规", "children": []},
                    {"name": "result", "type": "string", "required": False, "defaultValue": "", "description": "检测结果", "children": []},
                    {"name": "details", "type": "array", "required": False, "defaultValue": "", "description": "详细信息", "children": []}
                ]
            },
            {
                "name": "confidence_score",
                "type": "number",
                "required": True,
                "defaultValue": "0.95",
                "description": "置信度分数",
                "children": []
            },
            {
                "name": "processing_info",
                "type": "object",
                "required": False,
                "defaultValue": "",
                "description": "处理信息",
                "children": []
            }
        ]
    
    def load(self):
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                return {**self.default_config, **config}
        return self.default_config.copy()
    
    def save(self, config=None):
        """保存配置文件"""
        if config:
            self.config = config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def update(self, new_config):
        """更新配置"""
        self.config.update(new_config)
        self.save()
        self.init_directories()
    
    def init_directories(self):
        """初始化必要的目录"""
        images_dir = Path(self.config["images_dir"])
        annotations_dir = Path(self.config["annotations_dir"])
        
        images_dir.mkdir(parents=True, exist_ok=True)
        annotations_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key, default=None):
        """获取配置项"""
        return self.config.get(key, default)
    
    @property
    def images_dir(self):
        """图片目录路径"""
        return Path(self.config["images_dir"])
    
    @property
    def annotations_dir(self):
        """标注目录路径"""
        return Path(self.config["annotations_dir"])
