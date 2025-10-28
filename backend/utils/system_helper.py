"""
系统工具模块
"""
import os
import subprocess
import platform
from pathlib import Path


class SystemHelper:
    """系统相关的辅助工具类"""
    
    @staticmethod
    def has_gui_support():
        """检测系统是否支持 GUI"""
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            root.destroy()
            return True
        except Exception:
            return False
    
    @staticmethod
    def open_folder(folder_path):
        """根据操作系统打开文件夹"""
        folder_path = Path(folder_path)
        
        # 确保文件夹存在
        folder_path.mkdir(parents=True, exist_ok=True)
        
        system = platform.system()
        if system == 'Windows':
            os.startfile(folder_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', folder_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
    
    @staticmethod
    def select_folder_dialog(title="选择文件夹"):
        """打开文件夹选择对话框"""
        try:
            from tkinter import Tk, filedialog
            
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            selected_folder = filedialog.askdirectory(title=title)
            
            root.destroy()
            
            return selected_folder if selected_folder else None
        except Exception as e:
            raise Exception(f"无法打开文件选择对话框: {str(e)}")
