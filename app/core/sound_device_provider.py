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
shared_resource = 0

# Настройка параметров ПЕРЕД инициализацией
FREQUENCY = 44100
SIZE = -16  # 16-битный звук
CHANNELS = 2  # Стерео (PCM2902 — стерео-кодек)
BUFFER = 2048  # Размер буфера (увеличен для стабильности на Jetson)
AUDIO_OUTPUT = False

def _initialize_mixer():
    names = sdl2_audio.get_audio_device_names(AUDIO_OUTPUT)

    print(f"Available audio devices: {names}")

    # Select the desired device name (e.g., the first one in the list, or a specific name like 'HDMI 0')
    if names:
        # You may need to change the index based on your specific setup
        device_name = names[0]
        print(f"Selected device: {device_name}")
    else:
        raise RuntimeError("No audio devices found!")

    # Quit the current mixer (optional, but good practice if already initialized via pygame.init())
    mixer.quit()

    # Initialize the mixer with the specific device name
    try:
        mixer.pre_init(FREQUENCY, SIZE, CHANNELS, BUFFER)
        mixer.init(devicename=device_name)
        print(f"Mixer initialized with device: {device_name}")
    except pygame.error as e:
        print(f"Failed to initialize mixer with device {device_name}: {e}")
        # Handle error (e.g., fall back to default init)
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