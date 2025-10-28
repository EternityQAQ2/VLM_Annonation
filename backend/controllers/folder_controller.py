"""
文件夹管理控制器
"""
from flask import Blueprint, request, jsonify

folder_bp = Blueprint('folders', __name__, url_prefix='/api')


class FolderController:
    """文件夹管理控制器类"""
    
    def __init__(self, folder_service, config_manager, system_helper):
        self.folder_service = folder_service
        self.config_manager = config_manager
        self.system_helper = system_helper
    
    def select_folder(self):
        """选择文件夹"""
        try:
            data = request.json
            folder_type = data.get('folder_type', 'images')
            folder_path = data.get('folder_path', '')
            use_dialog = data.get('use_dialog', True)
            
            result = self.folder_service.select_folder(folder_type, folder_path, use_dialog)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
        except Exception as e:
            return jsonify({
                "error": f"设置路径失败: {str(e)}",
                "use_manual_input": not self.folder_service.gui_available,
                "gui_available": self.folder_service.gui_available
            }), 500
    
    def open_folder(self):
        """打开指定的文件夹"""
        try:
            data = request.json
            folder_type = data.get('folder_type', 'images')
            
            if folder_type == 'images':
                folder_path = self.config_manager.images_dir
            elif folder_type == 'annotations':
                folder_path = self.config_manager.annotations_dir
            else:
                folder_path = self.config_manager.data_dir
            
            self.system_helper.open_folder(folder_path)
            
            return jsonify({"success": True, "message": f"已打开文件夹: {folder_path}"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
