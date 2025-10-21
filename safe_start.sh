#!/bin/bash

# Безопасный запуск Baz Car API с автоматическими миграциями
# Этот скрипт гарантирует, что данные не будут потеряны при обновлении

echo "🚀 Безопасный запуск Baz Car API"
echo "================================"

# Останавливаем старый сервер если он запущен
echo "🛑 Проверка запущенных процессов..."
if [ -f "server.pid" ]; then
    OLD_PID=$(cat server.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "🛑 Останавливаем старый сервер (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    rm -f server.pid
fi

# Проверяем наличие Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Ошибка: python3 не установлен"
    exit 1
fi

echo "✅ Python3 найден: $(python3 --version)"

# Проверяем виртуальное окружение
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "⬆️  Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Создаем необходимые директории
echo "📁 Создание директорий..."
mkdir -p uploads/temp
mkdir -p uploads/cars
mkdir -p migrations

# Устанавливаем права доступа
chmod 755 uploads
chmod 755 uploads/temp
chmod 755 uploads/cars

# ВАЖНО: Выполняем автоматические миграции
echo ""
echo "🔧 Выполнение автоматических миграций..."
echo "   Это гарантирует, что данные не будут потеряны"
echo ""

./auto_migrate.sh

MIGRATION_EXIT_CODE=$?

if [ $MIGRATION_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "❌ Критическая ошибка: миграции не выполнены!"
    echo "   Сервер не будет запущен для защиты данных"
    echo "   Проверьте логи миграций выше"
    exit 1
fi

echo ""
echo "✅ Миграции выполнены успешно!"
echo ""

# Запускаем сервер
echo "🚀 Запуск сервера на порту 8080..."

# Определяем порт
PORT=${PORT:-8080}

# Запускаем сервер в фоне
nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port $PORT --reload > server.log 2>&1 &

# Сохраняем PID
SERVER_PID=$!
echo $SERVER_PID > server.pid

# Ждем запуска сервера
echo "⏳ Ожидание запуска сервера..."
sleep 3

# Проверяем, что сервер запустился
if ps -p $SERVER_PID > /dev/null; then
    echo ""
    echo "🎉 Сервер успешно запущен!"
    echo "================================"
    echo "🌐 API: http://localhost:$PORT/"
    echo "📚 Документация: http://localhost:$PORT/docs"
    echo "🔐 Авторизация: http://localhost:$PORT/api/v1/auth/login"
    echo "📋 Логи: tail -f server.log"
    echo "🛑 Остановка: kill $SERVER_PID"
    echo ""
    echo "🆔 PID сервера: $SERVER_PID"
    echo ""
    echo "✅ База данных обновлена безопасно"
    echo "✅ Все данные сохранены"
    echo "✅ Сервер готов к работе"
else
    echo ""
    echo "❌ Ошибка: сервер не запустился"
    echo "   Проверьте логи: cat server.log"
    exit 1
fi
