#!/usr/bin/env python3
"""
Toggle message preview truncation in carbonio-mails-ui.

OFF (патч) — письма всегда загружаются полностью, баннер не появляется.
ON  (дефолт) — предпросмотр обрезается до 250 KB, появляется кнопка «Загрузить сообщение».

Слетает при apt upgrade carbonio-mails-ui (новый хэш чанков).
После обновления пакета: запустить повторно, скрипт найдёт новый чанк автоматически.
"""

import glob
import sys

MAILS_UI_BASE = "/opt/zextras/web/iris/carbonio-mails-ui"

# Оригинальный код: preview-запрос с max=250000
MARKER_ON = "{msgId:t,max:25e4,shouldMarkAsRead:e}"
# Пропатченный код: без ограничения max (как loadFullMessage)
MARKER_OFF = "{msgId:t,shouldMarkAsRead:e}"


def find_chunk():
    chunks = glob.glob(f"{MAILS_UI_BASE}/*/5.*.chunk.js")
    chunks = [c for c in chunks if "/current/" not in c]
    for path in sorted(chunks):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if MARKER_ON in content or MARKER_OFF in content:
            return path, content
    return None, None


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    # Режим check (без интерактива)
    check_mode = len(sys.argv) > 1 and sys.argv[1] == "check"

    chunk_path, content = find_chunk()

    if chunk_path is None:
        print("ОШИБКА: чанк с функцией предпросмотра не найден.")
        print(f"Ищи вручную: grep -rl 'max:25e4,shouldMarkAsRead' {MAILS_UI_BASE}/")
        sys.exit(1)

    print(f"Файл: {chunk_path}")

    if MARKER_ON in content:
        state = "ON"
        print("Состояние: ВКЛЮЧЕНО — письма обрезаются до 250 KB при предпросмотре")
        action = "ОТКЛЮЧИТЬ усечение (письма всегда будут загружаться полностью)"
        old, new = MARKER_ON, MARKER_OFF
    else:
        state = "OFF"
        print("Состояние: ОТКЛЮЧЕНО — патч активен, письма загружаются полностью")
        action = "ВКЛЮЧИТЬ усечение (вернуть стандартное поведение)"
        old, new = MARKER_OFF, MARKER_ON

    if check_mode:
        sys.exit(0 if state == "OFF" else 1)

    print(f"\nДействие: {action}")
    print("Нажмите Enter для подтверждения, Ctrl+C для отмены: ", end="", flush=True)
    try:
        input()
    except KeyboardInterrupt:
        print("\nОтменено.")
        sys.exit(0)

    new_content = content.replace(old, new, 1)
    if new_content == content:
        print("ОШИБКА: замена не применилась (паттерн не найден точно).")
        sys.exit(1)

    write(chunk_path, new_content)

    if state == "ON":
        print("OK: усечение ОТКЛЮЧЕНО. Баннер «Загрузить сообщение» больше не появится.")
        print("    Все письма открываются полностью сразу.")
    else:
        print("OK: усечение ВКЛЮЧЕНО. Возвращено стандартное поведение Carbonio.")

    print("\nПерезагрузка страницы в браузере не нужна — изменения вступают сразу.")


if __name__ == "__main__":
    main()
