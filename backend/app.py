from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 检测是否有 GUI 环境
def has_gui_support():
    """检测系统是否支持 GUI"""
    try:
        # 尝试导入 tkinter
        import tkinter
        # 尝试创建一个隐藏窗口
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False

# 全局变量：是否支持 GUI
GUI_AVAILABLE = has_gui_support()

# 配置路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "images_dir": str(DATA_DIR / "images"),
    "annotations_dir": str(DATA_DIR / "annotations"),
    "auto_save": True,
    "json_indent": 2,
    "prompt_template": "<image> \n你是一个工业打印标签检测专家。\n只关注标签区域（金属凹陷处区域），金属凹陷处外的缺陷不予考虑，请按照以下缺陷类型分类检测标签质量：\n1. 缺失元素（文字、二维码等关键元素丢失）或过多元素（如打印本不应该有的元素）\n2. 偏移问题（标签位置偏移、字符偏移）\n3. 物理缺陷（气泡、皱褶、划痕、污渍、墨点,标签多打印，标签断裂、打印颠倒）\n4. 打印质量（字迹模糊、字迹黯淡、字符打印不完整、二维码打印质量、二维码打印不完整、打印字符错误等）\n5. 整体布局（元素排版问题）\n\n返回格式如下（JSON可以换行，便于阅读）：\n{\n  \"overall_status\": \"PASS\" 或 \"FAIL\",\n  \"defect_categories\": [\n    {\n      \"number\": 1,\n      \"category\": \"缺失元素\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 2,\n      \"category\": \"偏移问题\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 3,\n      \"category\": \"物理缺陷\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 4,\n      \"category\": \"打印质量\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 5,\n      \"category\": \"整体布局\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    }\n  ],\n  \"confidence_score\": 0.95,\n  \"processing_info\": {\n    \"stage\": \"defect_classification\",\n    \"template_matched\": true,\n    \"categories_checked\": [\"缺失元素\", \"偏移问题\", \"物理缺陷\", \"打印质量\", \"整体布局\"]\n  }\n}\n\n请只返回这个JSON格式的内容，JSON可以换行以便阅读。",
    "json_fields": [
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
}

# 加载配置
def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置
            return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG.copy()

# 保存配置
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 全局配置
app_config = load_config()
IMAGES_DIR = Path(app_config["images_dir"])
ANNOTATIONS_DIR = Path(app_config["annotations_dir"])

# 确保目录存在
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)

# 缺陷类型配置
DEFECT_CATEGORIES = [
    {"number": 1, "category": "缺失元素", "description": "文字、二维码等关键元素丢失或过多元素"},
    {"number": 2, "category": "偏移问题", "description": "标签位置偏移、字符偏移"},
    {"number": 3, "category": "物理缺陷", "description": "气泡、皱褶、划痕、污渍、墨点等"},
    {"number": 4, "category": "打印质量", "description": "字迹模糊、字迹黯淡、字符打印不完整等"},
    {"number": 5, "category": "整体布局", "description": "元素排版问题"}
]


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息，包括缺陷类型和应用配置"""
    return jsonify({
        "defect_categories": DEFECT_CATEGORIES,
        "status_options": ["PASS", "FAIL"],
        "app_config": app_config,
        "gui_available": GUI_AVAILABLE  # 告知前端是否支持 GUI
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新应用配置"""
    global app_config, IMAGES_DIR, ANNOTATIONS_DIR
    try:
        new_config = request.json
        app_config.update(new_config)
        save_config(app_config)
        
        # 更新路径
        IMAGES_DIR = Path(app_config["images_dir"])
        ANNOTATIONS_DIR = Path(app_config["annotations_dir"])
        
        # 确保目录存在
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
        
        return jsonify({"success": True, "config": app_config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/select-folder', methods=['POST'])
def select_folder():
    """选择文件夹 - 智能模式：GUI环境用对话框，容器环境用手动输入"""
    try:
        data = request.json
        folder_type = data.get('folder_type', 'images')
        folder_path = data.get('folder_path', '')
        use_dialog = data.get('use_dialog', True)  # 前端可以指定是否使用对话框
        
        # 模式 1: 使用文件对话框（如果支持 GUI 且前端要求）
        if GUI_AVAILABLE and use_dialog and not folder_path:
            try:
                from tkinter import Tk, filedialog
                
                # 创建隐藏的 Tk 窗口
                root = Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                # 打开文件夹选择对话框
                selected_folder = filedialog.askdirectory(
                    title=f"选择{'图片' if folder_type == 'images' else '标注'}文件夹"
                )
                
                root.destroy()
                
                if selected_folder:
                    folder_path = selected_folder
                else:
                    return jsonify({
                        "success": False, 
                        "message": "未选择文件夹",
                        "use_manual_input": False
                    }), 400
            except Exception as e:
                # GUI 模式失败，回退到手动输入
                return jsonify({
                    "success": False,
                    "message": f"无法打开文件选择对话框: {str(e)}",
                    "use_manual_input": True,
                    "gui_available": False
                }), 400
        
        # 模式 2: 手动输入路径验证
        if not folder_path:
            return jsonify({
                "success": False, 
                "message": "请提供文件夹路径",
                "use_manual_input": True
            }), 400
        
        # 验证路径是否存在
        path_obj = Path(folder_path)
        if not path_obj.exists():
            # 尝试创建目录
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                message = f"已创建目录: {folder_path}"
            except Exception as e:
                return jsonify({
                    "success": False, 
                    "message": f"路径不存在且无法创建: {folder_path}\n错误: {str(e)}",
                    "use_manual_input": not GUI_AVAILABLE
                }), 400
        elif not path_obj.is_dir():
            return jsonify({
                "success": False, 
                "message": f"路径不是一个有效的目录: {folder_path}",
                "use_manual_input": not GUI_AVAILABLE
            }), 400
        else:
            # 统计目录中的文件数
            file_count = len(list(path_obj.iterdir())) if path_obj.is_dir() else 0
            message = f"已验证路径: {folder_path} ({file_count} 个文件/目录)"
        
        return jsonify({
            "success": True,
            "folder_path": str(path_obj.absolute()),
            "folder_type": folder_type,
            "message": message,
            "method": "dialog" if (GUI_AVAILABLE and use_dialog) else "manual",
            "gui_available": GUI_AVAILABLE
        })
    except Exception as e:
        return jsonify({
            "error": f"设置路径失败: {str(e)}",
            "use_manual_input": not GUI_AVAILABLE,
            "gui_available": GUI_AVAILABLE
        }), 500


@app.route('/api/images', methods=['GET'])
def get_images():
    """获取所有图片列表"""
    try:
        images = []
        for file in IMAGES_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                # 检查是否有对应的标注文件
                annotation_file = ANNOTATIONS_DIR / f"{file.stem}.json"
                images.append({
                    "name": file.name,
                    "path": str(file.relative_to(DATA_DIR)),
                    "annotated": annotation_file.exists(),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        
        images.sort(key=lambda x: x['name'])
        return jsonify({"images": images})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    """提供图片文件"""
    try:
        image_path = IMAGES_DIR / filename
        
        if not image_path.exists():
            return jsonify({"error": f"文件不存在: {filename}"}), 404
            
        return send_from_directory(IMAGES_DIR, filename)
    except Exception as e:
        print(f"[错误] 图片服务异常: {str(e)}")
        return jsonify({"error": str(e)}), 404


@app.route('/api/annotations/<path:image_name>', methods=['GET'])
def get_annotation(image_name):
    """获取指定图片的标注数据"""
    try:
        # 移除扩展名，添加.json
        base_name = Path(image_name).stem
        annotation_file = ANNOTATIONS_DIR / f"{base_name}.json"
        
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        else:
            # 返回默认的空标注
            default_data = get_default_annotation(image_name)
            return jsonify(default_data)
    except Exception as e:
        print(f"[错误] 获取标注失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/annotations/<path:image_name>', methods=['POST'])
def save_annotation(image_name):
    """保存标注数据"""
    try:
        data = request.json
        base_name = Path(image_name).stem
        annotation_file = ANNOTATIONS_DIR / f"{base_name}.json"
        
        # 添加时间戳
        data['updated_at'] = datetime.now().isoformat()
        
        # 使用配置的缩进格式
        indent = app_config.get("json_indent", 2)
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        return jsonify({"success": True, "message": "标注已保存"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/annotations', methods=['GET'])
def get_all_annotations():
    """获取所有标注数据"""
    try:
        annotations = []
        for file in ANNOTATIONS_DIR.iterdir():
            if file.suffix == '.json':
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    annotations.append({
                        "image_name": file.stem,
                        "annotation": data
                    })
        return jsonify({"annotations": annotations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_default_annotation(image_name):
    """根据配置生成默认的空标注"""
    default_data = {
        "image_name": image_name,
        "image_path": f"images/{image_name}",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # 根据json_fields配置动态生成字段
    if 'json_fields' in app_config:
        for field_config in app_config['json_fields']:
            field_name = field_config['name']
            field_type = field_config['type']
            default_value = field_config.get('defaultValue', '')
            
            # 根据类型设置默认值
            if field_type == 'string':
                default_data[field_name] = default_value if default_value else ''
            elif field_type == 'number':
                default_data[field_name] = float(default_value) if default_value else 0
            elif field_type == 'boolean':
                default_data[field_name] = default_value == 'true' or default_value == True
            elif field_type == 'array':
                # 数组类型默认为空数组，由用户手动添加项
                default_data[field_name] = []
            elif field_type == 'object':
                # 递归生成对象字段
                default_data[field_name] = generate_default_object(field_config.get('children', []))
            else:
                default_data[field_name] = default_value
    
    return default_data

def generate_default_object(children_configs):
    """递归生成默认对象"""
    obj = {}
    for child_config in children_configs:
        field_name = child_config['name']
        field_type = child_config['type']
        default_value = child_config.get('defaultValue', '')
        
        if field_type == 'string':
            obj[field_name] = default_value if default_value else ''
        elif field_type == 'number':
            obj[field_name] = float(default_value) if default_value else 0
        elif field_type == 'boolean':
            obj[field_name] = default_value == 'true' or default_value == True
        elif field_type == 'array':
            obj[field_name] = []
        elif field_type == 'object':
            obj[field_name] = generate_default_object(child_config.get('children', []))
        else:
            obj[field_name] = default_value
    
    return obj


@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    """打开指定的文件夹"""
    try:
        data = request.json
        folder_type = data.get('folder_type', 'images')
        
        if folder_type == 'images':
            folder_path = IMAGES_DIR
        elif folder_type == 'annotations':
            folder_path = ANNOTATIONS_DIR
        else:
            folder_path = DATA_DIR
        
        # 确保文件夹存在
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # 根据操作系统打开文件夹
        system = platform.system()
        if system == 'Windows':
            os.startfile(folder_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', folder_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
        
        return jsonify({"success": True, "message": f"已打开文件夹: {folder_path}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print(f"Images directory: {IMAGES_DIR}")
    print(f"Annotations directory: {ANNOTATIONS_DIR}")
    print(f"GUI support: {'Available' if GUI_AVAILABLE else 'Not available (container mode)'}")
    app.run(debug=True, host='0.0.0.0', port=5000)
