import os
import sys
from functools import lru_cache

import torch
from omegaconf import OmegaConf

from ..core.sound_device_provider import play_sound
# Абсолютные импорты
from ..config.config import TTS_USE_TORCH_MODEL_MANAGER_BOOL
from ..utils.utils import Utils


# --- Константы: голоса ---
SPEAKER_AIDAR = "aidar"
SPEAKER_BAYA = "baya"
SPEAKER_KSENIYA = "kseniya"
SPEAKER_XENIA = "xenia"
SPEAKER_RANDOM = "random"

# --- Константы: устройства ---
DEVICE_CPU = "cpu"
DEVICE_CUDA = "cuda"


log = Utils.create_logger(__name__)

# Пути к моделям
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
LOCAL_MODEL_PATH = os.path.join(CURRENT_DIRECTORY, "..", "models", "silero_model_ru.pt")


class TTS:
    is_busy = False

    def __init__(
        self,
        speaker: str = SPEAKER_KSENIYA,
        device: str = DEVICE_CPU,
        samplerate: int = 48000,
    ):
        self._speaker = speaker
        self._samplerate = samplerate
        self._device = torch.device(device)

        if TTS_USE_TORCH_MODEL_MANAGER_BOOL:
            try:
                torch.hub.download_url_to_file(
                    "https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml",
                    "latest_silero_models.yml",
                    progress=False,
                )
                models = OmegaConf.load("latest_silero_models.yml")
                model, _ = torch.hub.load(
                    repo_or_dir="snakers4/silero-models",
                    model="silero_tts",
                    language="ru",
                    speaker="v4_ru",
                )
            except Exception as e:
                log.error(f"Failed to load model via torch.hub: {e}")
                raise
        else:
            if not os.path.exists(LOCAL_MODEL_PATH):
                raise FileNotFoundError(f"Локальная модель не найдена: {LOCAL_MODEL_PATH}")
            log.info(f"Загружаем модель локально: {LOCAL_MODEL_PATH}")
            model = torch.package.PackageImporter(LOCAL_MODEL_PATH).load_pickle("tts_models", "model")
        model.to(self._device)
        self._model = model

    def text_to_speech(self, text_in: str) -> None:
        """Преобразует текст в речь и воспроизводит звук."""
        audio = self._generate_audio(text_in)
        play_sound(audio, self._samplerate)

    @lru_cache(maxsize=None)
    def _generate_audio(self, text_in: str):
        if "<speak>" in text_in:
            generated_audio =  self._model.apply_tts(
                ssml_text=text_in,
                speaker=self._speaker,
                sample_rate=self._samplerate,
            )
        else:
            generated_audio = self._model.apply_tts(
                text=text_in,
                speaker=self._speaker,
                sample_rate=self._samplerate,
            )
        return generated_audio

    def close(self) -> None:
        """Закрывает ресурсы (заглушка)."""
        pass


if __name__ == "__main__":
    text = """
    <speak>
      <p>
          Когда я просыпаюсь, <prosody rate="x-slow">я говорю довольно медленно</prosody>.
          Пот+ом я начинаю говорить своим обычным голосом,
          <prosody pitch="x-high"> а могу говорить тоном выше </prosody>,
          или <prosody pitch="x-low">наоборот, ниже</prosody>.
          Пот+ом, если повезет – <prosody rate="fast">я могу говорить и довольно быстро.</prosody>
          А еще я умею делать паузы любой длины, например, две секунды <break time="2000ms"/>.
      </p>
    </speak>
    """
    tts = TTS()
    tts.text_to_speech(text_in=text)