#!/bin/bash
set -e

echo "🚀 Запуск Cyber Owl TTS сервера..."

# Проверка и активация виртуального окружения
VENV_DIR="./venv"
PYTHON="$VENV_DIR/bin/python"

if [ ! -d "$VENV_DIR" ]; then
    echo "📁 Создаём виртуальное окружение..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Виртуальное окружение найдено."
fi

# Активация venv
source "$VENV_DIR/bin/activate"

# Установка зависимостей, если требуется
if [ ! -f "$VENV_DIR/.requirements_installed" ] || [ "requirements.txt" -nt "$VENV_DIR/.requirements_installed" ]; then
    echo "📦 Устанавливаем зависимости из requirements.txt..."
    pip install --no-cache-dir -r requirements.txt
    touch "$VENV_DIR/.requirements_installed"
else
    echo "✅ Зависимости уже установлены."
fi

# Проверка модели
MODEL_PATH="./app/models/silero_model_ru.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Ошибка: модель не найдена по пути $MODEL_PATH"
    echo "👉 Скачайте silero_model_ru.pt и поместите в папку app/models/"
    exit 1
fi
echo "✅ Модель найдена: $MODEL_PATH"

# Экспорт переменных окружения (если не заданы)
export PYTHONPATH="./app:$PYTHONPATH"
export TTS_HOST=${TTS_HOST:-"0.0.0.0"}
export TTS_PORT=${TTS_PORT:-8081}
export TTS_LOG_LEVEL=${TTS_LOG_LEVEL:-"info"}

echo "📦 Версия Python: $(python --version 2>&1)"
echo "🌍 API будет доступен на http://$TTS_HOST:$TTS_PORT"

# Проверка PulseAudio (опционально)
if command -v pactl &> /dev/null; then
    echo "🔊 PulseAudio: доступен"
    pactl info | grep 'Server Name\|Library'
else
    echo "🔊 PulseAudio: не установлен (работает без аудио-переадресации)"
fi

# Запуск приложения
echo "▶️ Запуск app.main..."
exec python -m app.main