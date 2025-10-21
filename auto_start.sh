#!/bin/bash

# Автоматический запуск Baz Car API с исправлениями

echo "🚀 Автоматический запуск Baz Car API..."

# Останавливаем старый сервер
echo "🛑 Остановка старого сервера..."
pkill -f uvicorn || true
sleep 2

# Проверяем наличие Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Ошибка: python3 не установлен"
    exit 1
fi

echo "✅ Python3 найден: $(python3 --version)"

# Удаляем старое виртуальное окружение если есть
if [ -d "venv" ]; then
    echo "🗑️  Удаление старого виртуального окружения..."
    rm -rf venv
fi

# Создаем новое виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Проверяем, что виртуальное окружение создалось
if [ ! -d "venv" ]; then
    echo "❌ Ошибка: не удалось создать виртуальное окружение"
    echo "💡 Попробуйте установить: apt install python3.12-venv"
    exit 1
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

# Проверяем, что uvicorn установился
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "❌ Ошибка: uvicorn не установлен"
    exit 1
fi

# Применяем исправления CORS и cookies
echo "🔧 Применение исправлений..."
if [ -f "app/core/config_fixed.py" ]; then
    cp app/core/config_fixed.py app/core/config.py
    echo "✅ Настройки CORS обновлены"
fi

if [ -f "app/api/v1/endpoints/auth_fixed.py" ]; then
    cp app/api/v1/endpoints/auth_fixed.py app/api/v1/endpoints/auth.py
    echo "✅ Настройки cookies обновлены"
fi

# Удаляем временные файлы
rm -f app/core/config_fixed.py
rm -f app/api/v1/endpoints/auth_fixed.py

# Создаем директории
echo "📁 Создание директорий..."
mkdir -p uploads/temp
mkdir -p uploads/cars

# Проверяем права доступа
chmod 755 uploads
chmod 755 uploads/temp
chmod 755 uploads/cars

# Запускаем сервер на порту 8080
echo "✅ Запуск сервера на порту 8080..."
nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 > server.log 2>&1 &

# Сохраняем PID
SERVER_PID=$!
echo $SERVER_PID > server.pid

# Ждем немного и проверяем, что сервер запустился
sleep 3

if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Сервер успешно запущен!"
    echo "🌐 API доступен: http://91.229.8.235:8080/"
    echo "📚 Документация: http://91.229.8.235:8080/docs"
    echo "🔐 Авторизация: http://91.229.8.235:8080/api/v1/auth/login"
    echo "📋 Логи: tail -f server.log"
    echo "🛑 Остановка: kill $SERVER_PID"
    echo ""
    echo "🆔 PID сервера: $SERVER_PID"
else
    echo "❌ Ошибка: сервер не запустился. Проверьте логи: cat server.log"
    exit 1
fi
