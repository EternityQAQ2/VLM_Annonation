"""
配置管理控制器
"""
from flask import Blueprint, request, jsonify

config_bp = Blueprint('config', __name__, url_prefix='/api')

# 缺陷类型配置（常量）
DEFECT_CATEGORIES = [
    {"number": 1, "category": "缺失元素", "description": "文字、二维码等关键元素丢失或过多元素"},
    {"number": 2, "category": "偏移问题", "description": "标签位置偏移、字符偏移"},
    {"number": 3, "category": "物理缺陷", "description": "气泡、皱褶、划痕、污渍、墨点等"},
    {"number": 4, "category": "打印质量", "description": "字迹模糊、字迹黯淡、字符打印不完整等"},
    {"number": 5, "category": "整体布局", "description": "元素排版问题"}
]


class ConfigController:
    """配置管理控制器类"""
    
    def __init__(self, config_manager, gui_available):
        self.config_manager = config_manager
        self.gui_available = gui_available
    
    def get_config(self):
        """获取配置信息"""
        return jsonify({
            "defect_categories": DEFECT_CATEGORIES,
            "status_options": ["PASS", "FAIL"],
            "app_config": self.config_manager.config,
            "gui_available": self.gui_available
        })
    
    def update_config(self, image_service, annotation_service):
        """更新应用配置"""
        try:
            new_config = request.json
            self.config_manager.update(new_config)
            
            # 重新初始化服务以使用新配置
            image_service.__init__(
                self.config_manager.images_dir,
                self.config_manager.annotations_dir
            )
            annotation_service.__init__(
                self.config_manager.annotations_dir,
                self.config_manager.config
            )
            
            return jsonify({"success": True, "config": self.config_manager.config})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
