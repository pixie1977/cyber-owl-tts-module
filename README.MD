# Cyber Owl TTS Module

Модуль озвучки текста для киберсовы.
Вынесен отдельно для реализации микросервисной архитектуры.
Реализовано на основе Silero TTS.


## Установка
$pip install .
--- или ---
$pip install -e .

## Запуск
$python -m main

## Конфигурация
Создайте `.env` по образу и подобию .env_example

### Создайте виртуальное окружение в папке venv.
$python -m venv venv

### Активация
- win:
./venv/Scripts/activate.bat
- linux:
$source venv/bin/activate

### Установка зависимостей (если нужно) 
## Для работы с pytorch необходимо установить версию python 3.8, а также библиотеки для CUDA 
$pip install -r requirements.txt

## Теперь качаем модель
# Для русского языка:
wget https://models.silero.ai/models/tts/ru/v4_ru.pt -O silero_model_ru.pt

# Или для английского:
wget https://models.silero.ai/models/tts/en/v3_en.pt -O silero_model_en.pt

# Скачанную модель положить в папку models

---

### Примеры GET и POST запросов к FastAPI-серверу из файла src/app/httpd.py (host/port могут быть иными)

✅ 1. GET-запросы
🔹 Озвучить текст (через /api/speak)
curl "http://localhost:8081/api/speak?text=Привет%2C%20я%20говорю%20по-русски"

📝 Текст должен быть URL-encoded: пробелы → %20, запятые → %2C и т.д.

🔹 Проверка состояния
curl "http://localhost:8081/health"
Ответ: 
{"status":"ok","service":"TTS"}

🔹 Главная страница (если есть index.html)
curl http://localhost:8081/


✅ 2. POST-запросы
🔹 Форма: application/x-www-form-urlencoded (/api/tts)
curl -X POST http://localhost:8081/api/tts -d "text=Здравствуйте, как у вас дела?"
     
-d автоматически устанавливает тип application/x-www-form-urlencoded.

🔹 JSON: application/json (/api/tts/json)      
 curl -X POST http://localhost:8081/api/tts/json \
     -H "Content-Type: application/json" \
     -d '{"text": "Это тест озвучки через JSON."}'

Обязательно указать заголовок -H "Content-Type: application/json".

✅ 3. Пример с Python (requests)
Если протестировать из скрипта:

import requests

BASE_URL = "http://localhost:8081"

# GET-запрос
response = requests.get(f"{BASE_URL}/api/speak", params={"text": "Привет от Python!"})
print(response.json())

# POST (форма)
response = requests.post(f"{BASE_URL}/api/tts", data={"text": "POST форма работает!"})
print(response.json())

# POST (JSON)
response = requests.post(f"{BASE_URL}/api/tts/json", json={"text": "JSON тоже работает!"})
print(response.json())

✅ 4. Документация API (в браузере)
После запуска сервера открыть:
http://localhost:8081/
На странице будет форма ввода текста для озвучки.

✅ 5. Документация API (в браузере)
После запуска сервера открыть:


## Swagger (интерактивная документация, host/port могут быть иными):
http://localhost:8081/docs

## ReDoc:
http://localhost:8081/redoc

---
# Создание Docker контейнера
docker build -t cyber-owl-tts .

# Развертывание docker контейнера
docker run -p 8081:8081 \
  -e TTS_PORT=8081 \
  -e TTS_LOG_LEVEL=info \
  --name tts-server \
  cyber-owl-tts


curl -X POST http://localhost:8081/api/tts -d "text=Здравствуйте, как у вас дела?"
