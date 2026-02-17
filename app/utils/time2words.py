# -- coding: utf-8 --
"""
time2words.py : перевод времени в русскую пропись
"""

from __future__ import annotations
import datetime as dt
from functools import lru_cache
from typing import Tuple, Union

# --- Словари -----------------------------------------------------------------
UNITS_M = {0: 'ноль', 1: 'один', 2: 'два', 3: 'три', 4: 'чет+ыре',
           5: 'пять', 6: 'шесть', 7: 'семь', 8: 'в+осемь', 9: 'д+евять'}
UNITS_F = {0: 'ноль', 1: 'одн+а', 2: 'две', 3: 'три', 4: 'чет+ыре',
           5: 'пять', 6: 'шесть', 7: 'семь', 8: 'в+осемь', 9: 'д+евять'}

TEENS = {10: 'д+есять', 11: 'од+иннадцать', 12: 'двен+адцать', 13: 'трин+адцать',
         14: 'чет+ырнадцать', 15: 'пятн+адцать', 16: 'шестн+адцать',
         17: 'семн+адцать', 18: 'восемн+адцать', 19: 'девятн+адцать'}

TENS = {20: 'дв+адцать', 30: 'три+дцать', 40: 'с+орок', 50: 'пятьдес+ят'}


# --- Вспомогательные функции -------------------------------------------------
@lru_cache(maxsize=None)
def number_to_words(n: int, feminine: bool = False) -> str:
    """0‥59 → слова c учётом рода."""
    if n < 0 or n >= 60:
        raise ValueError('n должно быть 0‥59')
    if n < 10:
        return (UNITS_F if feminine else UNITS_M)[n]
    if 10 <= n < 20:
        return TEENS[n]
    tens, units = divmod(n, 10)
    words = TENS[tens * 10]
    if units:
        words += ' ' + (UNITS_F if feminine else UNITS_M)[units]
    return words


def plural(word: str, n: int, with_charges: bool = True) -> str:
    """‘час’ | ‘минута’ с правильным окончанием."""
    groups = {}
    if with_charges:
        groups = {
            'час': ('час', 'час+а', 'час+ов'),
            'минута': ('мин+ута', 'мин+уты', 'мин+ут'),
            'секунда': ('сек+унда', 'сек+унды', 'сек+унд'),
        }
    else:
        groups = {
            'час': ('час', 'часа', 'часов'),
            'минута': ('минута', 'минуты', 'минут'),
            'секунда': ('секунда', 'секунды', 'секунд'),
        }
    if word not in groups:
        raise ValueError(f'неизвестное слово для склонения: {word}')
    one, few, many = groups[word]
    if 11 <= n % 100 <= 14:
        return many
    if n % 10 == 1:
        return one
    if 2 <= n % 10 <= 4:
        return few
    return many


def parse_time(
        time_: Union[str, Tuple[int, int, int], dt.time, dt.datetime]
) -> Tuple[int, int, int]:
    """
    Превращает разные типы входа в (h, m, s).
    Поддерживает 'HH:MM', 'HH:MM:SS', datetime, time, tuple.
    """
    if isinstance(time_, (dt.datetime, dt.time)):
        return time_.hour, time_.minute, time_.second
    if isinstance(time_, tuple):
        return (time_ + (0, 0, 0))[:3]  # дополним до 3 элементов
    if isinstance(time_, str):
        parts = list(map(int, time_.strip().split(':')))
        if len(parts) not in (2, 3):
            raise ValueError("Строка должна содержать 2 или 3 числа: HH:MM или HH:MM:SS")
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts)  # type: ignore
    raise TypeError('Неподдерживаемый тип входных данных')


# --- Главная функция --------------------------
def time_to_text(
        time_: Union[str, Tuple[int, int], dt.time, dt.datetime],
        style: str = 'formal'  # 'formal' | 'spoken'
) -> str:
    """
    Перевод времени в слова.
    style = 'formal'  ➜  «двенадцать часов пять минут»
    style = 'spoken'  ➜  «пять минут первого», «без четверти двенадцать»
    """
    h, m, s = parse_time(time_)
    if not (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59):
        raise ValueError('Время вне диапазона 00:00:00–23:59:59')

    # Особые случаи
    if h == 0 and m == 0 and s == 0:
        return 'п+олночь'
    if h == 12 and m == 0 and s == 0:
        return 'п+олдень'

    h = h % 12  # 0–11 часов для разговорного стиля
    if h == 0:
        h = 12  # 12:xx → "двенадцать"

    if style == 'spoken':
        # Разговорный стиль: «пять минут первого», «без пятнадцати восемь» и т.п.
        if m == 0:
            return f"{number_to_words(h)} {plural('час', h)}"
        elif m <= 30:
            if m == 30:
                return f"п+оловина {number_to_words(h + 1)}"
            elif m == 15:
                return f"чет+ырть {number_to_words(h + 1)}"
            else:
                minutes_word = number_to_words(m, feminine=True)
                minute_noun = plural('минута', m)
                next_hour = (h + 1) if h < 12 else 1
                return f"{minutes_word} {minute_noun} {number_to_words(next_hour)}"
        else:  # m > 30
            m_left = 60 - m
            if m_left == 15:
                next_hour = (h + 1) if h < 12 else 1
                return f"без чет+ырти {number_to_words(next_hour)}"
            elif m_left in [5, 10, 20, 25]:
                # Добавляем поддержку: без пяти, десяти, двадцати, двадцати пяти
                minutes_word = number_to_words(m_left, feminine=True)
                next_hour = (h + 1) if h < 12 else 1
                return f"без {minutes_word} {plural('минута', m_left)} {number_to_words(next_hour)}"
            else:
                minutes_word = number_to_words(m_left, feminine=True)
                minute_noun = plural('минута', m_left)
                next_hour = (h + 1) if h < 12 else 1
                return f"без {minutes_word} {minute_noun} {number_to_words(next_hour)}"
    else:
        # Деловой стиль
        parts = [number_to_words(h), plural('час', h)]
        if m == 0:
            parts.append('р+овно')
        else:
            parts.extend([
                number_to_words(m, feminine=True),
                plural('минута', m),
            ])
        return ' '.join(parts)


# --- Пример использования ----------------------------------------------------
if __name__ == '__main__':
    examples = ['00:00', '01:00', '01:05', '01:10', '01:20', '01:25', '01:30', '01:45', '01:50', '01:55', '17:40']
    print('— деловой стиль —')
    for t in examples:
        print(f'{t} -> {time_to_text(t, style="formal")}')

    print('\n— разговорный стиль —')
    for t in examples:
        print(f'{t} -> {time_to_text(t, style="spoken")}')