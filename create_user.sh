#!/bin/bash

# Скрипт для создания пользователей
# Использование: ./create_user.sh <username> [password]

echo "🔐 Baz Car Admin - Создание пользователя"
echo "========================================"

# Проверяем, активирована ли виртуальная среда
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Активируем виртуальную среду..."
    source venv/bin/activate
fi

# Запускаем Python скрипт
python create_user.py "$@"
