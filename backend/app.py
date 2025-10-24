from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from tkinter import Tk, filedialog

app = Flask(__name__)
CORS(app)

# 配置路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "images_dir": str(DATA_DIR / "images"),
    "annotations_dir": str(DATA_DIR / "annotations"),
    "export_format": "vlm",  # vlm, standard, coco, yolo
    "auto_save": True,
    "json_indent": 2,
    "prompt_template": "<image> \n你是一个工业打印标签检测专家。\n只关注标签区域（金属凹陷处区域），金属凹陷处外的缺陷不予考虑，请按照以下缺陷类型分类检测标签质量：\n1. 缺失元素（文字、二维码等关键元素丢失）或过多元素（如打印本不应该有的元素）\n2. 偏移问题（标签位置偏移、字符偏移）\n3. 物理缺陷（气泡、皱褶、划痕、污渍、墨点,标签多打印，标签断裂、打印颠倒）\n4. 打印质量（字迹模糊、字迹黯淡、字符打印不完整、二维码打印质量、二维码打印不完整、打印字符错误等）\n5. 整体布局（元素排版问题）\n\n返回格式如下（JSON可以换行，便于阅读）：\n{\n  \"overall_status\": \"PASS\" 或 \"FAIL\",\n  \"defect_categories\": [\n    {\n      \"number\": 1,\n      \"category\": \"缺失元素\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 2,\n      \"category\": \"偏移问题\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 3,\n      \"category\": \"物理缺陷\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 4,\n      \"category\": \"打印质量\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    },\n    {\n      \"number\": 5,\n      \"category\": \"整体布局\",\n      \"compliance\": true/false,\n      \"result\": \"具体检测结果描述\",\n      \"details\": []\n    }\n  ],\n  \"confidence_score\": 0.95,\n  \"processing_info\": {\n    \"stage\": \"defect_classification\",\n    \"template_matched\": true,\n    \"categories_checked\": [\"缺失元素\", \"偏移问题\", \"物理缺陷\", \"打印质量\", \"整体布局\"]\n  }\n}\n\n请只返回这个JSON格式的内容，JSON可以换行以便阅读。",
    "json_schema": {
        "overall_status": {"type": "enum", "values": ["PASS", "FAIL"], "required": True},
        "defect_categories": {"type": "array", "required": True},
        "confidence_score": {"type": "number", "required": True},
        "processing_info": {"type": "object", "required": False}
    }
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
        "app_config": app_config
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
    """打开文件夹选择对话框"""
    try:
        data = request.json
        folder_type = data.get('folder_type', 'images')
        
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
            return jsonify({
                "success": True,
                "folder_path": selected_folder,
                "folder_type": folder_type
            })
        else:
            return jsonify({"success": False, "message": "未选择文件夹"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        print(f"[图片请求] 文件名: {filename}")
        print(f"[图片请求] 完整路径: {image_path}")
        print(f"[图片请求] 文件存在: {image_path.exists()}")
        
        if not image_path.exists():
            print(f"[错误] 文件不存在: {image_path}")
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
        
        print(f"[标注请求] 图片名: {image_name}")
        print(f"[标注请求] 基础名: {base_name}")
        print(f"[标注请求] 标注文件: {annotation_file}")
        print(f"[标注请求] 文件存在: {annotation_file.exists()}")
        
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[标注请求] 返回已存在的标注")
            return jsonify(data)
        else:
            # 返回默认的空标注
            default_data = get_default_annotation(image_name)
            print(f"[标注请求] 返回默认标注")
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


@app.route('/api/export', methods=['GET'])
def export_dataset():
    """导出完整数据集为 VLM 格式"""
    try:
        export_format = app_config.get("export_format", "vlm")
        prompt_template = app_config.get("prompt_template", "")
        json_indent = app_config.get("json_indent", 2)
        
        dataset = []
        
        for file in ANNOTATIONS_DIR.iterdir():
            if file.suffix == '.json':
                with open(file, 'r', encoding='utf-8') as f:
                    annotation = json.load(f)
                    
                    if export_format == "vlm":
                        # VLM 格式：包含 images 和 messages
                        # 从标注中提取图片路径
                        image_name = annotation.get("image_name", "")
                        relative_path = f"FINALPART/{image_name}"  # 可配置前缀
                        
                        # 构建 assistant 的回复（标注数据的 JSON）
                        response_data = {
                            "overall_status": annotation.get("overall_status", "PASS"),
                            "defect_categories": annotation.get("defect_categories", []),
                            "confidence_score": annotation.get("confidence_score", 0.95),
                            "processing_info": annotation.get("processing_info", {})
                        }
                        
                        vlm_item = {
                            "images": [relative_path],
                            "messages": [
                                {
                                    "content": prompt_template,
                                    "role": "user"
                                },
                                {
                                    "content": json.dumps(response_data, ensure_ascii=False, indent=json_indent),
                                    "role": "assistant"
                                }
                            ]
                        }
                        dataset.append(vlm_item)
                    else:
                        # 标准格式
                        dataset.append(annotation)
        
        return jsonify({
            "export_time": datetime.now().isoformat(),
            "format": export_format,
            "data": dataset,
            "total": len(dataset)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_default_annotation(image_name):
    """生成默认的空标注"""
    return {
        "image_name": image_name,
        "image_path": f"images/{image_name}",
        "overall_status": "PASS",
        "defect_categories": [
            {
                "number": cat["number"],
                "category": cat["category"],
                "compliance": True,
                "result": "",
                "details": []
            }
            for cat in DEFECT_CATEGORIES
        ],
        "confidence_score": 0.95,
        "processing_info": {
            "stage": "defect_classification",
            "template_matched": True,
            "categories_checked": [cat["category"] for cat in DEFECT_CATEGORIES]
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }


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
    app.run(debug=True, host='0.0.0.0', port=5000)
