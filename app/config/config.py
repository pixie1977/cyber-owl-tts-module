import os
from distutils.util import strtobool
from dotenv import load_dotenv


CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

TTS_PORT = os.getenv("TTS_PORT")
if not TTS_PORT:
    raise ValueError("Не задан TTS_PORT в .env")
TTS_PORT = int(TTS_PORT)

TTS_HOST = os.getenv("TTS_HOST")
if not TTS_HOST:
    raise ValueError("Не задан TTS_HOST в .env")

TTS_LOG_LEVEL = os.getenv("TTS_LOG_LEVEL")
if not TTS_LOG_LEVEL:
    raise ValueError("Не задан TTS_LOG_LEVEL в .env")

TTS_DOC_ROOT = os.getenv("TTS_DOC_ROOT")
if not TTS_DOC_ROOT:
    TTS_DOC_ROOT = os.path.join(CURRENT_DIRECTORY, "..", "content")

TTS_USE_TORCH_MODEL_MANAGER_STR = os.getenv("TTS_USE_TORCH_MODEL_MANAGER")
if not TTS_USE_TORCH_MODEL_MANAGER_STR:
    raise ValueError("Не задан TTS_USE_TORCH_MODEL_MANAGER в .env")
TTS_USE_TORCH_MODEL_MANAGER_BOOL = strtobool(TTS_USE_TORCH_MODEL_MANAGER_STR)
