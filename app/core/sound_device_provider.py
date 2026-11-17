"""
Модуль для воспроизведения аудио через Pygame с поддержкой многопоточности.
"""

import io
import os
import threading
import time

import numpy as np
import pygame
import pygame._sdl2.audio as sdl2_audio

from pygame import mixer
from scipy.io import wavfile

from app.config.config import TTS_SOUND_DEVICE_NAME
from app.core.logger import get_logger


log = get_logger(__name__)

# Глобальные переменные
mutex = threading.Lock()
_is_playing = False

# Настройка параметров ПЕРЕД инициализацией
FREQUENCY = 44100
SIZE = -16  # 16-битный звук
CHANNELS = 2  # Стерео (Необходимо для совместимости с plughw:0,0)
BUFFER = 2048  # Размер буфера (увеличен для стабильности на Jetson)


def _initialize_mixer():
    """Инициализирует SDL и Pygame mixer с выбором аудиоустройства."""
    # НАСТРОЙКА ALSA: Принудительно связываем SDL с ALSA плагином plughw
    os.environ["SDL_AUDIODRIVER"] = "alsa"
    os.environ["AUDIODEV"] = "plughw:0,0"
    
    # Fallback для XDG_RUNTIME_DIR при запуске от root
    if not os.environ.get("XDG_RUNTIME_DIR"):
        xdg_dir = f"/run/user/{os.getuid()}"
        if not os.path.exists(xdg_dir):
            os.makedirs(xdg_dir, exist_ok=True)
        os.environ["XDG_RUNTIME_DIR"] = xdg_dir
    if not os.environ.get("PULSE_RUNTIME_PATH"):
        pulse_dir = f"{os.environ['XDG_RUNTIME_DIR']}/pulse"
        os.makedirs(pulse_dir, exist_ok=True)
        os.environ["PULSE_RUNTIME_PATH"] = pulse_dir

    pygame.display.init()  # Требуется для корректной инициализации SDL
    pygame.init()

    names = sdl2_audio.get_audio_device_names(False)  # False = output devices

    # Ищем устройство, в имени которого есть ReSpeaker или ArrayUAC10
    target_device = None
    for name in names:
        device_str = name.decode('utf-8') if isinstance(name, bytes) else name
        print(f"🔊 Найдено устройство SDL2: {device_str}")
        if "ArrayUAC10" in device_str or "ReSpeaker" in device_str:
            target_device = device_str
            break

    device_name = TTS_SOUND_DEVICE_NAME or target_device or (names[0] if names else None)    
    print(f"🔊 Целевое устройство вывода: {device_name}")

    mixer.quit()  # Закрываем предыдущий микшер
    mixer.pre_init(FREQUENCY, SIZE, CHANNELS, BUFFER)

    try:
        # ИСПРАВЛЕНО: Явно передаем имя найденного устройства в devicename
        mixer.init(devicename=device_name)
        print(f"✅ Mixer успешно привязан к ReSpeaker: {device_name}")
    except Exception as e:
        print(f"❌ Ошибка при инициализации с устройством '{device_name}': {e}")
        print("🔧 Пытаемся с дефолтным устройством и переменными ALSA...")
        try:
            mixer.init()
            print("✅ Mixer инициализирован через системный default (plughw).")
        except Exception as default_e:
            if "AUDIODEV" in os.environ: del os.environ["AUDIODEV"]
            mixer.init()
            print(f"✅ Mixer инициализирован в чистом дефолтном режиме: {default_e}")


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
        
        # Конвертируем тензор в float32 numpy массив
        audio_data = audio.numpy() if hasattr(audio, 'numpy') else np.array(audio)
        
        # Нормализуем звук в int16
        wav_data = (audio_data * 32767).astype(np.int16)
        
        # ИСПРАВЛЕНО: Дублируем моно-поток Silero в стерео-массив (2 канала),
        # чтобы он соответствовал CHANNELS = 2 в конфигурации микшера.
        if wav_data.ndim == 1:
            wav_data = np.vstack((wav_data, wav_data)).T
        
        # Записываем WAV с правильным стерео-массивом
        wavfile.write(buffer, rate=FREQUENCY, data=wav_data)
        buffer.seek(0)
        
        play_sound_mixer(buffer)
    except Exception as e:
        print(f"❌ Ошибка в play_sound: {e}")


def stop_sound():
    """Мгновенно останавливает текущее воспроизведение."""
    global _is_playing
    try:
        # Проверяем, инициализирован ли микшер
        if not mixer.get_init()[0]:
            log.warning("Микшер не инициализирован, не можем остановить")
            return
        
        with mutex:
            mixer.music.stop()
            _is_playing = False
        log.info("Аудиовоспроизведение остановлено")
    except Exception as e:
        log.warning(f"Ошибка при остановке аудио: {e}")


def play_sound_mixer(audio_bytes):
    """
    Воспроизводит аудио из байтового потока.

    :param audio_bytes: Байтовый поток .wav
    """
    global _is_playing
    thread_name = threading.current_thread().name
    mutex.acquire()
    try:
        _is_playing = True
        mixer.music.load(audio_bytes)
        mixer.music.play()
        timeout = 0
        while mixer.music.get_busy() and timeout < 3000:
            time.sleep(0.05)
            timeout += 50
        _is_playing = False
    except Exception as e:
        print(f"❌ Ошибка при воспроизведении: {e}")
    finally:
        mutex.release()
        log.info(f"🟢 {thread_name} освободил аудио")
