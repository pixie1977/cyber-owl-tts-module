#!/usr/bin/env python3
"""
HTTP-сервер на FastAPI для TTS с поддержкой POST, GET
"""

import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
# from prometheus_fastapi_instrumentator import Instrumentator

# Импорт TTS движка
from app.core.text_to_speech import TTS
from app.config.config import TTS_DOC_ROOT


app = FastAPI(title="TTS API Server")

# Подключаем статические файлы
print(f"TTS_DOC_ROOT={TTS_DOC_ROOT}")
app.mount("/static", StaticFiles(directory=TTS_DOC_ROOT), name="static")

# Инициализация TTS
tts_engine = TTS()

# Включение метрик Prometheus (на будущее)
# Instrumentator().instrument(core).expose(core)

# Модель для JSON-запроса
class TTSTextRequest(BaseModel):
    text: str


@app.get("/")
async def read_root():
    index_path = os.path.join(TTS_DOC_ROOT, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Cyber Owl TTS API"}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TTS"}


@app.post("/api/tts")
async def text_to_speech(text: str = Form(...)):
    """
    Обработка POST-запроса с формой (application/x-www-form-urlencoded)
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        tts_engine.text_to_speech(text_in=text)
        return JSONResponse(content={"status": "success", "text": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@app.post("/api/tts/json")
async def text_to_speech_json(request: TTSTextRequest):
    """
    Обработка JSON POST-запроса
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        tts_engine.text_to_speech(text_in=request.text)
        return {"status": "success", "text": request.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@app.get("/api/speak")
async def speak_get(text: str):
    """
    GET-эндпоинт для озвучки текста
    Пример: /api/speak?text=Привет
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    try:
        tts_engine.text_to_speech(text_in=text)
        return {"status": "success", "text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
