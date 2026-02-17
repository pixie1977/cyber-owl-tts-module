# Используем официальный образ Python 3.10 (слабая версия для минимального размера)
FROM python:3.10-slim

# Устанавливаем метаданные
LABEL maintainer="you@example.com"
LABEL description="TTS server with Silero for Russian using FastAPI"

# Устанавливаем рабочую директорию
WORKDIR /app

# Системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libportaudio2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Делаем start.sh исполняемым
RUN chmod +x /app/start.sh

# Экспорт переменных окружения по умолчанию
ENV TTS_HOST=0.0.0.0
ENV TTS_PORT=8081
ENV TTS_LOG_LEVEL=info
ENV TTS_DOC_ROOT=/app/src/content
ENV TTS_USE_TORCH_MODEL_MANAGER=false

# Открываем порт
EXPOSE $TTS_PORT

# Точка входа
CMD ["/app/start.sh"]