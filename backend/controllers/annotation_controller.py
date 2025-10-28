"""
标注管理控制器
"""
from flask import Blueprint, request, jsonify

annotation_bp = Blueprint('annotations', __name__, url_prefix='/api')


class AnnotationController:
    """标注管理控制器类"""
    
    def __init__(self, annotation_service):
        self.annotation_service = annotation_service
    
    def get_annotation(self, image_name):
        """获取指定图片的标注数据"""
        try:
            data = self.annotation_service.get_annotation(image_name)
            return jsonify(data)
        except Exception as e:
            print(f"[错误] 获取标注失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    
    def save_annotation(self, image_name):
        """保存标注数据"""
        try:
            data = request.json
            self.annotation_service.save_annotation(image_name, data)
            return jsonify({"success": True, "message": "标注已保存"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def get_all_annotations(self):
        """获取所有标注数据"""
        try:
            annotations = self.annotation_service.get_all_annotations()
            return jsonify({"annotations": annotations})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
