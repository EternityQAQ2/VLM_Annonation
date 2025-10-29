"""
图片管理控制器
"""
from flask import Blueprint, request, jsonify, send_from_directory

image_bp = Blueprint('images', __name__, url_prefix='/api')


class ImageController:
    """图片管理控制器类"""
    
    def __init__(self, image_service):
        self.image_service = image_service
    
    def get_images(self):
        """获取所有图片列表"""
        try:
            images = self.image_service.get_all_images()
            return jsonify({"images": images})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def serve_image(self, filename):
        """提供图片文件"""
        try:
            image_path = self.image_service.get_image_path(filename)
            return send_from_directory(image_path.parent, image_path.name)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            print(f"[错误] 图片服务异常: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def serve_thumbnail(self, filename):
        """提供缩略图"""
        try:
            thumbnail_path = self.image_service.get_thumbnail_path(filename)
            return send_from_directory(thumbnail_path.parent, thumbnail_path.name)
        except FileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            print(f"[错误] 缩略图服务异常: {str(e)}")
            # 如果缩略图失败，尝试返回原图
            try:
                image_path = self.image_service.get_image_path(filename)
                return send_from_directory(image_path.parent, image_path.name)
            except:
                return jsonify({"error": str(e)}), 500
    
    def delete_image(self, filename):
        """删除图片及相关文件"""
        try:
            success, message = self.image_service.delete_image(filename)
            if success:
                return jsonify({"success": True, "message": message})
            else:
                return jsonify({"success": False, "error": message}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
