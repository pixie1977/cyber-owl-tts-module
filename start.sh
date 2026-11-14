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

echo "📦 Версия Python: $(python --version 2>&1)"
echo "🌍 API будет доступен на http://$TTS_HOST:$TTS_PORT"

# Запуск PulseAudio (если не запущен)
if command -v pactl &> /dev/null; then
    echo "🔊 Настройка PulseAudio..."
    if ! pactl info &> /dev/null 2>&1; then
        echo "⚡ Запуск PulseAudio..."
        export PULSE_RUNTIME_PATH="/tmp/pulse"
        mkdir -p "$PULSE_RUNTIME_PATH"
        pulseaudio --kill 2>/dev/null || true
        # Пытаемся запустить PulseAudio с разными опциями
        if [ "$(whoami)" = "root" ]; then
            export PULSE_SYSTEM=1
            pulseaudio --start --system --exit-idle-time=-1 --disallow-exit 2>/dev/null || \
            pulseaudio --start --exit-idle-time=-1 --disallow-exit 2>/dev/null || true
        else
            pulseaudio --start --exit-idle-time=-1 --disallow-exit 2>/dev/null || true
        fi
        sleep 1
        if pactl info &> /dev/null 2>&1; then
            echo "✅ PulseAudio запущен"
        else
            echo "⚠️ PulseAudio не запустился — попробуем ALSA напрямую"
        fi
    else
        echo "✅ PulseAudio уже запущен"
    fi
else
    echo "🔊 PulseAudio: не установлен (работает без аудио-переадресации)"
fi

# Запуск приложения
echo "▶️ Запуск app.main..."
exec python -m app.main