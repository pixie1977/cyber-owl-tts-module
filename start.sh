#!/bin/bash
set -e

echo "🚀 Запуск Cyber Owl TTS сервера..."
echo "📦 Версия Python: $(python --version 2>&1)"
echo "🌍 API будет доступен на http://$TTS_HOST:$TTS_PORT"
echo "📁 Документ-рут: $TTS_DOC_ROOT"

# Проверка наличия модели
if [ ! -f "./app/models/silero_model_ru.pt" ]; then
    echo "❌ Ошибка: модель не найдена в ./app/models/silero_model_ru.pt"
    echo "👉 Убедитесь, что вы скопировали модель в папку models/"
    exit 1
fi

echo "✅ Модель найдена: silero_model_ru.pt"

# Устанавливаем PYTHONPATH, чтобы Python нашёл пакет `app`
export PYTHONPATH="/app"

echo "🔊 Проверка аудио..."
pactl info || echo "PulseAudio недоступен (возможно, в контейнере)"

# Запуск основного приложения
exec python -m app.main