"""
文件夹选择服务
"""
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.system_helper import SystemHelper


class FolderService:
    """文件夹选择和管理服务"""
    
    def __init__(self, gui_available=False):
        self.gui_available = gui_available
    
    def select_folder(self, folder_type='images', folder_path='', use_dialog=True):
        """
        选择文件夹 - 智能模式：GUI环境用对话框，容器环境用手动输入
        
        Args:
            folder_type: 文件夹类型 ('images' 或 'annotations')
            folder_path: 手动输入的路径（可选）
            use_dialog: 是否尝试使用对话框
        
        Returns:
            dict: 包含成功状态、路径和消息的字典
        """
        # 模式 1: 使用文件对话框（如果支持 GUI 且前端要求）
        if self.gui_available and use_dialog and not folder_path:
            try:
                title = f"选择{'图片' if folder_type == 'images' else '标注'}文件夹"
                selected_folder = SystemHelper.select_folder_dialog(title)
                
                if selected_folder:
                    folder_path = selected_folder
                else:
                    return {
                        "success": False,
                        "message": "未选择文件夹",
                        "use_manual_input": False
                    }
            except Exception as e:
                # GUI 模式失败，回退到手动输入
                return {
                    "success": False,
                    "message": str(e),
                    "use_manual_input": True,
                    "gui_available": False
                }
        
        # 模式 2: 手动输入路径验证
        if not folder_path:
            return {
                "success": False,
                "message": "请提供文件夹路径",
                "use_manual_input": True
            }
        
        # 验证并创建路径
        return self._validate_and_create_path(folder_path, folder_type)
    
    def _validate_and_create_path(self, folder_path, folder_type):
        """验证路径并在需要时创建"""
        path_obj = Path(folder_path)
        
        if not path_obj.exists():
            # 尝试创建目录
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                message = f"已创建目录: {folder_path}"
            except Exception as e:
                return {
                    "success": False,
                    "message": f"路径不存在且无法创建: {folder_path}\n错误: {str(e)}",
                    "use_manual_input": not self.gui_available
                }
        elif not path_obj.is_dir():
            return {
                "success": False,
                "message": f"路径不是一个有效的目录: {folder_path}",
                "use_manual_input": not self.gui_available
            }
        else:
            # 统计目录中的文件数
            file_count = len(list(path_obj.iterdir())) if path_obj.is_dir() else 0
            message = f"已验证路径: {folder_path} ({file_count} 个文件/目录)"
        
        return {
            "success": True,
            "folder_path": str(path_obj.absolute()),
            "folder_type": folder_type,
            "message": message,
            "method": "dialog" if self.gui_available else "manual",
            "gui_available": self.gui_available
        }
