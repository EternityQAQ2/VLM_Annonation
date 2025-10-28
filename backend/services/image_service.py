"""
图片管理服务
"""
import os
import imghdr
from pathlib import Path
from datetime import datetime
from PIL import Image
import hashlib


class ImageService:
    """图片管理服务类"""
    
    SUPPORTED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.mpo']
    THUMBNAIL_SIZE = (400, 400)  # 缩略图尺寸（提升质量）
    
    def __init__(self, images_dir, annotations_dir):
        self.images_dir = Path(images_dir)
        self.annotations_dir = Path(annotations_dir)
        # 缩略图目录
        self.thumbnails_dir = self.images_dir.parent / 'thumbnails'
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
    
    def get_all_images(self):
        """获取所有图片列表"""
        images = []
        
        for file in self.images_dir.iterdir():
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                # 验证是否为真正的图片文件
                is_valid_image = self._is_valid_image_file(file)
                
                if not is_valid_image:
                    print(f"[警告] 跳过无效图片文件: {file.name}")
                    continue
                
                # 检查是否有对应的标注文件
                annotation_file = self.annotations_dir / f"{file.stem}.json"
                
                images.append({
                    "name": file.name,
                    "path": str(file.relative_to(self.images_dir.parent)),
                    "annotated": annotation_file.exists(),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        
        # 按名称排序
        images.sort(key=lambda x: x['name'])
        return images
    
    def _is_valid_image_file(self, file_path):
        """检查文件是否为有效的图片"""
        try:
            # 使用 imghdr 检测真实的图片类型
            image_type = imghdr.what(file_path)
            if image_type is None:
                # 如果 imghdr 无法识别，检查文件大小
                # 太小的文件（<100字节）很可能不是真正的图片
                if file_path.stat().st_size < 100:
                    return False
            return image_type is not None or file_path.stat().st_size >= 100
        except Exception as e:
            print(f"[错误] 检查图片文件失败 {file_path.name}: {e}")
            return False
    
    def generate_thumbnail(self, image_path):
        """
        生成缩略图
        
        Args:
            image_path: 原始图片路径
            
        Returns:
            Path: 缩略图路径，失败返回 None
        """
        try:
            image_path = Path(image_path)
            
            # 缩略图文件名：使用原文件名
            thumbnail_path = self.thumbnails_dir / f"{image_path.stem}_thumb{image_path.suffix}"
            
            # 检查缩略图是否已存在且是最新的
            if thumbnail_path.exists():
                # 比较修改时间，如果缩略图比原图新，直接返回
                if thumbnail_path.stat().st_mtime >= image_path.stat().st_mtime:
                    return thumbnail_path
            
            # 生成新缩略图
            with Image.open(image_path) as img:
                # 转换RGBA到RGB（处理PNG透明背景）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 生成缩略图（保持宽高比）
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                
                # 保存为JPEG格式（提升质量）
                thumbnail_path = self.thumbnails_dir / f"{image_path.stem}_thumb.jpg"
                img.save(thumbnail_path, 'JPEG', quality=90, optimize=True)
                
                print(f"[信息] 已生成缩略图: {thumbnail_path.name}")
                return thumbnail_path
                
        except Exception as e:
            print(f"[错误] 生成缩略图失败 {image_path.name}: {e}")
            return None
    
    def get_thumbnail_path(self, filename):
        """
        获取缩略图路径，如果不存在则生成
        
        Args:
            filename: 原始图片文件名
            
        Returns:
            Path: 缩略图路径
        """
        image_path = self.images_dir / filename
        
        if not image_path.exists():
            raise FileNotFoundError(f"原始图片不存在: {filename}")
        
        # 缩略图统一使用 .jpg 格式
        # 从原文件名中提取basename（不含扩展名）
        basename = Path(filename).stem
        thumbnail_filename = f"{basename}_thumb.jpg"
        thumbnail_path = self.thumbnails_dir / thumbnail_filename
        
        # 如果缩略图不存在或过期，生成新的
        if not thumbnail_path.exists() or thumbnail_path.stat().st_mtime < image_path.stat().st_mtime:
            thumbnail_path = self.generate_thumbnail(image_path)
        
        # 如果生成失败，返回原图
        return thumbnail_path if thumbnail_path else image_path
    
    def get_image_path(self, filename):
        """获取图片的完整路径"""
        image_path = self.images_dir / filename
        
        if not image_path.exists():
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        return image_path
    
    def validate_image(self, filename):
        """验证图片文件是否有效"""
        file_path = self.images_dir / filename
        
        if not file_path.exists():
            return False, "文件不存在"
        
        if not file_path.is_file():
            return False, "不是一个文件"
        
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False, f"不支持的文件格式，支持的格式: {', '.join(self.SUPPORTED_EXTENSIONS)}"
        
        return True, "有效"
