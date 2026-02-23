"""
Модуль для воспроизведения аудио через Pygame с поддержкой многопоточности.
"""

import io
import threading
import time

import numpy as np
import pygame
import pygame._sdl2.audio as sdl2_audio

from pygame import mixer
from scipy.io import wavfile

from app.config.config import TTS_SOUND_DEVICE_NAME


# Глобальные переменные
mutex = threading.Lock()

# Настройка параметров ПЕРЕД инициализацией
FREQUENCY = 48000
SIZE = -16  # 16-битный звук
CHANNELS = 2  # Стерео (PCM2902 — стерео-кодек)
BUFFER = 2048  # Размер буфера (увеличен для стабильности на Jetson)


def _initialize_mixer():
    """Инициализирует SDL и Pygame mixer с выбором аудиоустройства."""
    # Инициализируем SDL с аудио
    pygame.display.init()  # Требуется для корректной инициализации SDL
    pygame.init()

    names = sdl2_audio.get_audio_device_names(False)  # False = output devices

    if not names:
        print("⚠️  Не найдено ни одного аудиоустройства.")
        # Продолжаем с дефолтным устройством
        mixer.pre_init(FREQUENCY, SIZE, CHANNELS, BUFFER)
        mixer.init()
        print("✅ Mixer инициализирован с устройством по умолчанию.")
        return

    print(f"🎧 Доступные аудиоустройства: {names}")

    # Выбираем устройство: сначала по конфигу, иначе первое в списке
    device_name = TTS_SOUND_DEVICE_NAME or names[0]
    print(f"🔊 Используем устройство: {device_name}")

    mixer.quit()  # Закрываем предыдущий микшер
    mixer.pre_init(FREQUENCY, SIZE, CHANNELS, BUFFER)

    try:
        mixer.init(devicename=device_name)
        print(f"✅ Mixer инициализирован с устройством: {device_name}")
    except Exception as e:
        print(f"❌ Ошибка при инициализации с устройством '{device_name}': {e}")
        print("🔧 Пытаемся с дефолтным устройством...")
        mixer.init()
        print("✅ Mixer инициализирован с дефолтным устройством.")


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
        print(f"❌ Ошибка в play_sound: {e}")


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
        print(f"❌ Ошибка при воспроизведении: {e}")
    finally:
        mutex.release()
        print(f"🟢 {thread_name} освободил аудио")