import io
import threading
import time

import sounddevice as sd
from pygame import mixer
from scipy.io import wavfile
import numpy as np

mutex = threading.Lock()
shared_resource = 0


def play_sound(audio, samplerate):
    global shared_resource
    print(f'{threading.current_thread().name} ожидает доступ к аудио')
    mutex.acquire()
    try:
        sd.play(audio, samplerate=samplerate)
        buffer = io.BytesIO()
        wavfile.write(buffer, rate=samplerate, data=(audio * 32767).numpy().astype(np.int16))
        buffer.seek(0)
        bytes = buffer.getvalue()
        play_sound_mixer(bytes)
    except Exception as e:
        print(e)
    mutex.release()
    print(f'{threading.current_thread().name} освободил аудио')

def play_sound_mixer(bytes):
    mutex.acquire()
    mixer.init()
    mixer.music.load(bytes)
    mixer.music.play()
    while mixer.music.get_busy():
        # Пауза, чтобы не загружать процессор
        time.sleep(1)
    time.sleep(1)
    mutex.release()