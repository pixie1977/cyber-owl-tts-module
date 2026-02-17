from typing import Optional

#!/usr/bin/python3
import datetime
import json
import locale
import logging
import os
import sys

from fuzzywuzzy import fuzz
from .time2words import time_to_text

logging.basicConfig()

class Utils:

    @staticmethod
    def get_root_dir():
        return os.path.abspath(os.path.dirname(__file__))

    # конфигурация логгера
    @staticmethod
    def create_logger(name: str) -> logging.Logger:
        log = logging.getLogger(__name__)
        log.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        log.addHandler(stdout_handler)

        file_path = os.path.join(Utils.get_root_dir(), 'sowa_logs.log')
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)

        return log

    # загрузка справочника для реакции крылом
    @staticmethod
    def bad_words_load(file_path):
        words = []
        print('Загружаем справочник слов...')
        with open(file_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                words.append(line.replace('\n', ''))
        print(words)
        return set(words)

    # загрузка справочника для реакции звуком
    @staticmethod
    def audio_reactions_load(file_path):
        print('Загружаем справочник аудио реакций...')
        with open(file_path, 'r', encoding='utf-8') as fJson:
            data = json.load(fJson)
        return data['items']

    # проверка наличия списка новых слов в другом списке слов
    @staticmethod
    def compare_lists(input_words, expected):
        result = False
        set_input_words = set(input_words)
        set_expected = set(expected)
        if set_expected.intersection(set_input_words):
            result = True
        return result

    # выделяет слова, которые есть в новом потоке и нет в старом
    @staticmethod
    def exclude_words(command, last_command):
        list_command = set(command)
        list_last_command = set(last_command)
        return list_command.difference(list_last_command)

    # проверка команд
    @staticmethod
    def check_command(command, last_commands):
        result = list()
        # проверяем, что в строке больше 1 символа
        if command and len(command.replace(' ', '')) > 1:
            list_command = command.split(' ')
            list_last_commands = list(last_commands)
            # удаляем из списка новых слов слова предыдущего списка
            result = list(Utils.exclude_words(list_command, list_last_commands))
        return result

    @staticmethod
    def time_as_words():
        """
        Возвращает текущее время словами на русском языке.
        """
        try:
            locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        except locale.Error:
            print("Не удалось установить локаль 'ru_RU.UTF-8'. Время будет выведено в стандартном формате.")

        return time_to_text(datetime.datetime.now())

    @staticmethod
    def fuzzy_find_fw(keyword: str,
                      phrase: str,
                      threshold: int = 80):
        """
        Поиск приблизительных вхождений keyword в phrase с помощью fuzzywuzzy.
        threshold – минимальный процент сходства (0–100), по умолчанию 80 %.
        Возвращает список кортежей (позиция, фрагмент, score).
        """
        kw = keyword.lower()
        text = phrase.lower()
        k = len(kw)
        hits = []

        if k == 0 or k > len(text):
            return hits

        for i in range(len(text) - k + 1):
            window = text[i:i + k]
            score = fuzz.ratio(kw, window)  # 100 – полное совпадение
            if score >= threshold:
                hits.append((i,
                             phrase[i:i + k],  # оригинальный регистр
                             score))
        return hits

    # ---------------- пример ----------------
    if __name__ == '__main__':
        phrase = 'Сегодня потрясающая погода, поедем гулять у пагоды?'
        keyword = 'пагода'
        res = fuzzy_find_fw(keyword, phrase, threshold=70)

        if res:
            print('Найдено (порог 70 %):')
            for pos, frag, sc in res:
                print(f'  "{frag}" (позиция {pos}, сходство {sc}%)')
        else:
            print('Совпадений не найдено.')

def str_to_bool(value: Optional[str], default: bool = False) -> bool:
    """Преобразует строку в булево значение."""
    if not value:
        return default
    return value.lower() in ("true", "1", "yes", "on", "enable")