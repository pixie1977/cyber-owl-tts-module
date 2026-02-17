"""
Запуск FastAPI-сервера для TTS-модуля.
"""

from app.core.httpd import app
from app.config.config import TTS_HOST, TTS_PORT, TTS_LOG_LEVEL


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=TTS_HOST,
        port=TTS_PORT,
        log_level=TTS_LOG_LEVEL,
    )