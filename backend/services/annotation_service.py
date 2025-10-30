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
    
    def get_annotation_summary(self, image_name):
        """
        获取标注摘要信息
        动态提取所有顶级字段，统一处理数组展示
        
        Args:
            image_name: 图片文件名
            
        Returns:
            dict: 摘要信息
        """
        try:
            annotation = self.get_annotation(image_name)
            
            # 基础摘要信息
            summary = {
                "image_path": annotation.get("image_path", f"images/{image_name}"),
                "fields": {}  # 存储所有顶级字段
            }
            
            # 获取配置的字段列表
            json_fields = self.config.get('json_fields', [])
            field_names = {field['name'] for field in json_fields}
            
            # 遍历所有顶级字段（排除内部字段）
            exclude_fields = {'image_name', 'image_path', 'created_at', 'updated_at'}
            
            for key, value in annotation.items():
                if key not in exclude_fields and key in field_names:
                    # 获取字段配置
                    field_config = next((f for f in json_fields if f['name'] == key), None)
                    
                    # 获取描述，如果为空则使用字段名
                    description = key  # 默认使用字段名
                    if field_config:
                        config_desc = field_config.get('description', '')
                        if config_desc and config_desc.strip():  # 确保不是空字符串
                            description = config_desc
                    
                    field_type = field_config['type'] if field_config else type(value).__name__
                    
                    # 统一处理数组类型 - 提取详细信息
                    if field_type == 'array' and isinstance(value, list):
                        # 提取数组项的详细信息
                        array_items = []
                        for idx, item in enumerate(value):
                            if isinstance(item, dict):
                                # 字典项：提取所有键值对
                                array_items.append({
                                    "index": idx + 1,
                                    "data": item
                                })
                            else:
                                # 基本类型项：直接存储
                                array_items.append({
                                    "index": idx + 1,
                                    "data": item
                                })
                        
                        summary["fields"][key] = {
                            "value": value,
                            "type": field_type,
                            "description": description,
                            "array_items": array_items,  # 新增：数组详细信息
                            "children_config": field_config.get('children', []) if field_config else []  # 子字段配置
                        }
                    else:
                        # 非数组类型：保持原样
                        summary["fields"][key] = {
                            "value": value,
                            "type": field_type,
                            "description": description
                        }
            
            return summary
            
        except Exception as e:
            print(f"[错误] 获取标注摘要失败 {image_name}: {e}")
            return {
                "image_path": f"images/{image_name}",
                "fields": {}
            }
