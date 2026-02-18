"""
Модуль для воспроизведения аудио через Pygame с поддержкой многопоточности.
"""

import io
import threading
import time

import numpy as np
from pygame import mixer
from scipy.io import wavfile

from app.config.config import TTS_SOUND_DEVICE_NAME


# Глобальные переменные
mutex = threading.Lock()
shared_resource = 0

# Настройка параметров ПЕРЕД инициализацией
FREQUENCY = 44100
SIZE = -16  # 16-битный звук
CHANNELS = 2  # Стерео (PCM2902 — стерео-кодек)
BUFFER = 2048  # Размер буфера (увеличен для стабильности на Jetson)


def _initialize_mixer():
    """Инициализирует Pygame mixer с заданными параметрами."""
    try:
        print(f"TTS_SOUND_DEVICE_NAME={TTS_SOUND_DEVICE_NAME}")
        mixer.pre_init(FREQUENCY, SIZE, CHANNELS, BUFFER)
        if TTS_SOUND_DEVICE_NAME:
            mixer.init(devicename=TTS_SOUND_DEVICE_NAME)
        else:
            mixer.init()
        print(f"Mixer initialized at {FREQUENCY}Hz")
    except Exception as e:
        print(f"Failed to init mixer: {e}")
        raise


# Инициализация при импорте
_initialize_mixer()


def play_sound(audio, samplerate):
    """
    Преобразует аудио в .wav и передаёт на воспроизведение.

    :param audio: Аудиоданные (Tensor)
    :param samplerate: Частота дискретизации
    """
    try:
        buffer = io.BytesIO()
        wav_data = (audio * 32767).numpy().astype(np.int16)
        wavfile.write(buffer, rate=FREQUENCY, data=wav_data)
        buffer.seek(0)
        play_sound_mixer(buffer)
    except Exception as e:
        print(f"Error in play_sound: {e}")


def play_sound_mixer(audio_bytes):
    """
    Воспроизводит аудио из байтового потока.

    :param audio_bytes: Байтовый поток .wav
    """
    thread_name = threading.current_thread().name
    mutex.acquire()
    try:
        mixer.music.load(audio_bytes)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)  # Небольшая пауза, чтобы не загружать CPU
    except Exception as e:
        print(f"Error playing sound: {e}")
    finally:
        mutex.release()
        print(f"{thread_name} освободил аудио")