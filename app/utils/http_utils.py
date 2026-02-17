"""
HTTP-утилиты: генерация ответов, MIME-типы, безопасное объединение путей.
"""

import mimetypes
import os
from datetime import datetime

# Настройка дополнительных MIME-типов
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/gif', '.gif')
mimetypes.add_type('application/x-shockwave-flash', '.swf')

# HTTP-статусы
STATUS_LINES = {
    200: "HTTP/1.1 200 OK",
    404: "HTTP/1.1 404 Not Found",
    403: "HTTP/1.1 403 Forbidden",
    405: "HTTP/1.1 405 Method Not Allowed",
    500: "HTTP/1.1 500 Internal Server Error",
}


def get_content_type(filepath):
    """Возвращает Content-Type по расширению файла."""
    mime, _ = mimetypes.guess_type(filepath)
    return mime or 'application/octet-stream'


def build_response(status, headers=None, body=b""):
    """
    Собирает HTTP-ответ.

    :param status: HTTP-статус (200, 404 и т.д.)
    :param headers: словарь дополнительных заголовков
    :param body: тело ответа (bytes)
    :return: полный HTTP-ответ (bytes)
    """
    response_line = STATUS_LINES.get(status, STATUS_LINES[500])
    response = [response_line]

    if headers is None:
        headers = {}

    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    headers.setdefault("Date", now)
    headers.setdefault("Server", "mini-http/0.1")
    headers.setdefault("Connection", "close")

    if status == 200 and body:
        headers.setdefault("Content-Length", str(len(body)))
    else:
        headers["Content-Length"] = "0"

    for key, value in headers.items():
        response.append(f"{key}: {value}")
    response.append("")  # пустая строка — разделитель заголовков и тела

    header_block = "\r\n".join(response).encode('utf-8')
    return header_block + b"\r\n" + body


def safe_join(root, path):
    """
    Безопасно объединяет root и путь из URL, предотвращая path traversal.

    :param root: корневая директория (DOCUMENT_ROOT)
    :param path: путь из URL
    :return: нормализованный путь или None, если вне root
    """
    root = os.path.abspath(root)
    target = os.path.abspath(os.path.join(root, path.lstrip("/")))
    if not target.startswith(root):
        return None
    return target