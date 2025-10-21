"""
Сервис для работы с файлами
"""
import os
import shutil
import uuid
from typing import List, Optional
from fastapi import UploadFile

from app.core.config import settings


class StorageService:
    """Сервис для работы с файлами"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.temp_upload_dir = settings.TEMP_UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        
        # Создаем директории если их нет
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.temp_upload_dir, exist_ok=True)
    
    def _generate_filename(self, original_filename: str) -> str:
        """Генерация уникального имени файла"""
        file_extension = os.path.splitext(original_filename)[1]
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    def _get_public_path(self, file_path: str) -> str:
        """Получение публичного пути к файлу"""
        return f"/uploads/{os.path.relpath(file_path, self.upload_dir)}"
    
    def save_file(self, car_id: int, file: UploadFile) -> str:
        """Сохранение файла для конкретного автомобиля"""
        # Проверяем размер файла
        if file.size and file.size > self.max_file_size:
            raise ValueError("Файл слишком большой")
        
        # Создаем директорию для автомобиля
        car_dir = os.path.join(self.upload_dir, str(car_id))
        os.makedirs(car_dir, exist_ok=True)
        
        # Генерируем имя файла
        filename = self._generate_filename(file.filename)
        file_path = os.path.join(car_dir, filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return self._get_public_path(file_path)
    
    def save_temp_file(self, file: UploadFile) -> str:
        """Сохранение временного файла"""
        # Проверяем размер файла
        if file.size and file.size > self.max_file_size:
            raise ValueError("Файл слишком большой")
        
        # Генерируем имя файла
        filename = self._generate_filename(file.filename)
        file_path = os.path.join(self.temp_upload_dir, filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return self._get_public_path(file_path)
    
    def move_temp_to_car(self, car_id: int, temp_paths: List[str]) -> List[str]:
        """Перемещение временных файлов к автомобилю"""
        car_dir = os.path.join(self.upload_dir, str(car_id))
        os.makedirs(car_dir, exist_ok=True)
        
        moved_paths = []
        for temp_path in temp_paths:
            # Получаем относительный путь от /uploads
            relative_path = temp_path.replace("/uploads/", "")
            temp_file_path = os.path.join(self.upload_dir, relative_path)
            
            if os.path.exists(temp_file_path):
                # Генерируем новое имя файла
                filename = self._generate_filename(os.path.basename(temp_file_path))
                new_file_path = os.path.join(car_dir, filename)
                
                # Перемещаем файл
                shutil.move(temp_file_path, new_file_path)
                moved_paths.append(self._get_public_path(new_file_path))
        
        return moved_paths
    
    def delete_by_public_paths(self, public_paths: List[str]) -> int:
        """Удаление файлов по публичным путям"""
        deleted_count = 0
        for public_path in public_paths:
            # Получаем относительный путь от /uploads
            relative_path = public_path.replace("/uploads/", "")
            file_path = os.path.join(self.upload_dir, relative_path)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
        
        return deleted_count
    
    def cleanup_temp_files(self) -> int:
        """Очистка временных файлов"""
        deleted_count = 0
        if os.path.exists(self.temp_upload_dir):
            for filename in os.listdir(self.temp_upload_dir):
                file_path = os.path.join(self.temp_upload_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1
        
        return deleted_count
