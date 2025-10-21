"""
Менеджер миграций для безопасного обновления базы данных
Этот файл НЕ является миграцией, а содержит утилиты для управления миграциями
"""
import os
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class MigrationManager:
    """Менеджер миграций для безопасного обновления БД"""
    
    def __init__(self, db_path: str = "baz_car.db"):
        self.db_path = Path(db_path)
        self.migrations_table = "migrations_history"
        
    def create_migrations_table(self):
        """Создает таблицу для отслеживания выполненных миграций"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                details TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_executed_migrations(self) -> List[str]:
        """Получает список выполненных миграций"""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT migration_name FROM {self.migrations_table} WHERE success = TRUE ORDER BY executed_at")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Таблица миграций не существует
            return []
        finally:
            conn.close()
    
    def mark_migration_executed(self, migration_name: str, success: bool = True, details: str = ""):
        """Отмечает миграцию как выполненную"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"""
                INSERT OR REPLACE INTO {self.migrations_table} 
                (migration_name, success, details) 
                VALUES (?, ?, ?)
            """, (migration_name, success, details))
            
            conn.commit()
        finally:
            conn.close()
    
    def backup_database(self) -> str:
        """Создает резервную копию базы данных"""
        if not self.db_path.exists():
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.parent / f"{self.db_path.stem}_backup_{timestamp}.db"
        
        # Копируем файл базы данных
        import shutil
        shutil.copy2(self.db_path, backup_path)
        
        print(f"✅ Резервная копия создана: {backup_path}")
        return str(backup_path)
    
    def get_available_migrations(self) -> List[Dict[str, Any]]:
        """Получает список доступных миграций"""
        migrations_dir = Path("migrations")
        migrations = []
        
        if not migrations_dir.exists():
            return migrations
        
        for file_path in sorted(migrations_dir.glob("*.py")):
            if file_path.name.startswith("__") or file_path.name.startswith("_"):
                continue
                
            migration_name = file_path.stem
            migrations.append({
                "name": migration_name,
                "file": str(file_path),
                "description": self._get_migration_description(file_path)
            })
        
        return migrations
    
    def _get_migration_description(self, file_path: Path) -> str:
        """Получает описание миграции из комментариев в файле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Ищем описание в комментариях
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('#') and 'description' in line.lower():
                        return line.strip().replace('#', '').strip()
                return "Описание недоступно"
        except:
            return "Описание недоступно"
    
    def run_migration(self, migration_name: str) -> bool:
        """Выполняет конкретную миграцию"""
        migration_file = Path(f"migrations/{migration_name}.py")
        
        if not migration_file.exists():
            print(f"❌ Файл миграции не найден: {migration_file}")
            return False
        
        try:
            print(f"🔄 Выполнение миграции: {migration_name}")
            
            # Импортируем и выполняем миграцию
            import importlib.util
            spec = importlib.util.spec_from_file_location(migration_name, migration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Выполняем функцию миграции
            if hasattr(module, 'migrate'):
                result = module.migrate()
                if result:
                    self.mark_migration_executed(migration_name, True, "Миграция выполнена успешно")
                    print(f"✅ Миграция {migration_name} выполнена успешно")
                    return True
                else:
                    self.mark_migration_executed(migration_name, False, "Миграция завершилась с ошибкой")
                    print(f"❌ Миграция {migration_name} завершилась с ошибкой")
                    return False
            else:
                print(f"❌ Функция migrate() не найдена в {migration_name}")
                return False
                
        except Exception as e:
            self.mark_migration_executed(migration_name, False, f"Ошибка: {str(e)}")
            print(f"❌ Ошибка при выполнении миграции {migration_name}: {e}")
            return False
    
    def run_all_pending_migrations(self, create_backup: bool = True) -> bool:
        """Выполняет все ожидающие миграции"""
        print("🔧 Запуск автоматических миграций...")
        print("=" * 50)
        
        # Создаем таблицу миграций
        self.create_migrations_table()
        
        # Создаем резервную копию если нужно
        if create_backup and self.db_path.exists():
            self.backup_database()
        
        # Получаем выполненные и доступные миграции
        executed = self.get_executed_migrations()
        available = self.get_available_migrations()
        
        pending = [m for m in available if m["name"] not in executed]
        
        if not pending:
            print("✅ Все миграции уже выполнены")
            return True
        
        print(f"📋 Найдено {len(pending)} миграций для выполнения:")
        for migration in pending:
            print(f"   - {migration['name']}: {migration['description']}")
        
        print()
        
        # Выполняем миграции
        success_count = 0
        for migration in pending:
            if self.run_migration(migration["name"]):
                success_count += 1
            else:
                print(f"❌ Остановка выполнения миграций из-за ошибки в {migration['name']}")
                return False
        
        print(f"\n🎉 Успешно выполнено {success_count} из {len(pending)} миграций")
        return True
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Получает статус миграций"""
        executed = self.get_executed_migrations()
        available = self.get_available_migrations()
        pending = [m for m in available if m["name"] not in executed]
        
        return {
            "total_available": len(available),
            "executed": len(executed),
            "pending": len(pending),
            "executed_migrations": executed,
            "pending_migrations": [m["name"] for m in pending]
        }
