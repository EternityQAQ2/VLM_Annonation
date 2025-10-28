"""
标注管理服务
"""
import json
from pathlib import Path
from datetime import datetime


class AnnotationService:
    """标注管理服务类"""
    
    def __init__(self, annotations_dir, config):
        self.annotations_dir = Path(annotations_dir)
        self.config = config
    
    def get_annotation(self, image_name):
        """获取指定图片的标注数据"""
        base_name = Path(image_name).stem
        annotation_file = self.annotations_dir / f"{base_name}.json"
        
        if annotation_file.exists():
            with open(annotation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 返回默认的空标注
            return self._generate_default_annotation(image_name)
    
    def save_annotation(self, image_name, data):
        """保存标注数据"""
        base_name = Path(image_name).stem
        annotation_file = self.annotations_dir / f"{base_name}.json"
        
        # 添加时间戳
        data['updated_at'] = datetime.now().isoformat()
        
        # 使用配置的缩进格式
        indent = self.config.get("json_indent", 2)
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        return True
    
    def get_all_annotations(self):
        """获取所有标注数据"""
        annotations = []
        
        for file in self.annotations_dir.iterdir():
            if file.suffix == '.json':
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    annotations.append({
                        "image_name": file.stem,
                        "annotation": data
                    })
        
        return annotations
    
    def _generate_default_annotation(self, image_name):
        """根据配置生成默认的空标注"""
        default_data = {
            "image_name": image_name,
            "image_path": f"images/{image_name}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 根据json_fields配置动态生成字段
        json_fields = self.config.get('json_fields', [])
        
        for field_config in json_fields:
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
                default_data[field_name] = []
            elif field_type == 'object':
                default_data[field_name] = self._generate_default_object(field_config.get('children', []))
            else:
                default_data[field_name] = default_value
        
        return default_data
    
    def _generate_default_object(self, children_configs):
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
                obj[field_name] = self._generate_default_object(child_config.get('children', []))
            else:
                obj[field_name] = default_value
        
        return obj
