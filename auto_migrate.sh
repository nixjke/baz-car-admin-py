#!/bin/bash

# Автоматические миграции для Baz Car API
# Этот скрипт безопасно обновляет базу данных без потери данных

echo "🔧 Автоматические миграции Baz Car API"
echo "======================================"

# Проверяем, активирована ли виртуальная среда
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Активируем виртуальную среду..."
    source venv/bin/activate
fi

# Проверяем наличие Python
if ! command -v python &> /dev/null; then
    echo "❌ Ошибка: Python не найден"
    exit 1
fi

echo "✅ Python найден: $(python --version)"

# Запускаем миграции
echo "🔄 Запуск автоматических миграций..."
python -c "
from migrations._migration_manager import MigrationManager
import sys

manager = MigrationManager()

# Показываем статус миграций
status = manager.get_migration_status()
print(f'📊 Статус миграций:')
print(f'   Всего доступно: {status[\"total_available\"]}')
print(f'   Выполнено: {status[\"executed\"]}')
print(f'   Ожидает: {status[\"pending\"]}')

if status['pending'] > 0:
    print(f'   Ожидающие миграции: {status[\"pending_migrations\"]}')
    print()

# Выполняем миграции
success = manager.run_all_pending_migrations(create_backup=True)

if success:
    print('🎉 Все миграции выполнены успешно!')
    sys.exit(0)
else:
    print('❌ Ошибка при выполнении миграций!')
    sys.exit(1)
"

MIGRATION_EXIT_CODE=$?

if [ $MIGRATION_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Миграции завершены успешно!"
    echo "   База данных обновлена без потери данных"
    echo "   Резервная копия создана автоматически"
else
    echo ""
    echo "❌ Ошибка при выполнении миграций!"
    echo "   Проверьте логи выше для деталей"
    echo "   Резервная копия создана для восстановления"
    exit 1
fi
