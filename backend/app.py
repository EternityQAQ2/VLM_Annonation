"""
VLM Annotation Tool - 后端服务
重构版本 - 标准MVC架构
"""
from flask import Flask
from flask_cors import CORS

# 导入配置和工具
from config import Config
from utils import SystemHelper

# 导入服务层
from services import ImageService, AnnotationService, FolderService

# 导入控制器
from controllers import (
    ConfigController,
    ImageController,
    AnnotationController,
    FolderController
)


def create_app():
    """应用工厂函数"""
    # 初始化 Flask 应用
    app = Flask(__name__)
    CORS(app)
    
    # 初始化配置和系统检测
    config_manager = Config()
    gui_available = SystemHelper.has_gui_support()
    
    # 初始化服务层
    image_service = ImageService(
        config_manager.images_dir,
        config_manager.annotations_dir
    )
    annotation_service = AnnotationService(
        config_manager.annotations_dir,
        config_manager.config
    )
    folder_service = FolderService(gui_available)
    
    # 初始化控制器
    config_controller = ConfigController(config_manager, gui_available)
    image_controller = ImageController(image_service)
    annotation_controller = AnnotationController(annotation_service)
    folder_controller = FolderController(folder_service, config_manager, SystemHelper)
    
    # ============= 注册路由 =============
    
    # 配置相关路由
    @app.route('/api/config', methods=['GET'])
    def get_config():
        return config_controller.get_config()
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        return config_controller.update_config(image_service, annotation_service)
    
    # 文件夹相关路由
    @app.route('/api/select-folder', methods=['POST'])
    def select_folder():
        return folder_controller.select_folder()
    
    @app.route('/api/open-folder', methods=['POST'])
    def open_folder():
        return folder_controller.open_folder()
    
    # 图片相关路由
    @app.route('/api/images', methods=['GET'])
    def get_images():
        return image_controller.get_images()
    
    @app.route('/api/images/<path:filename>', methods=['GET'])
    def serve_image(filename):
        return image_controller.serve_image(filename)
    
    @app.route('/api/thumbnails/<path:filename>', methods=['GET'])
    def serve_thumbnail(filename):
        return image_controller.serve_thumbnail(filename)
    
    # 标注相关路由
    @app.route('/api/annotations/<path:image_name>', methods=['GET'])
    def get_annotation(image_name):
        return annotation_controller.get_annotation(image_name)
    
    @app.route('/api/annotations/<path:image_name>', methods=['POST'])
    def save_annotation(image_name):
        return annotation_controller.save_annotation(image_name)
    
    @app.route('/api/annotations', methods=['GET'])
    def get_all_annotations():
        return annotation_controller.get_all_annotations()
    
    # 存储配置管理器供其他地方使用
    app.config_manager = config_manager
    app.gui_available = gui_available
    
    return app


# ============= 应用入口 =============

if __name__ == '__main__':
    app = create_app()
    
    print("=" * 60)
    print("VLM Annotation Tool - Backend Server")
    print("=" * 60)
    print(f"Images directory: {app.config_manager.images_dir}")
    print(f"Annotations directory: {app.config_manager.annotations_dir}")
    print(f"GUI support: {'Available' if app.gui_available else 'Not available (container mode)'}")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
