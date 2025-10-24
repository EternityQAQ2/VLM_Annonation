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

# 配置路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
ANNOTATIONS_DIR = DATA_DIR / "annotations"

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
    """获取配置信息，包括缺陷类型"""
    return jsonify({
        "defect_categories": DEFECT_CATEGORIES,
        "status_options": ["PASS", "FAIL"]
    })


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
        return send_from_directory(IMAGES_DIR, filename)
    except Exception as e:
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
            return jsonify(get_default_annotation(image_name))
    except Exception as e:
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
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
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
    """导出完整数据集"""
    try:
        dataset = {
            "export_time": datetime.now().isoformat(),
            "data": []
        }
        
        for file in ANNOTATIONS_DIR.iterdir():
            if file.suffix == '.json':
                with open(file, 'r', encoding='utf-8') as f:
                    annotation = json.load(f)
                    dataset["data"].append({
                        "images": [annotation.get("image_path", "")],
                        "messages": [
                            {
                                "content": annotation.get("prompt", ""),
                                "role": "user"
                            },
                            {
                                "content": json.dumps(annotation.get("response", {}), ensure_ascii=False),
                                "role": "assistant"
                            }
                        ]
                    })
        
        return jsonify(dataset)
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
