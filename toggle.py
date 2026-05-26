#!/usr/bin/env python3
"""
Toggle message preview truncation in carbonio-mails-ui.

OFF (patch) — messages always load in full, banner never appears.
ON  (default) — preview is truncated at 250 KB, "Load message" button appears.

Reapply after apt upgrade carbonio-mails-ui — the script finds the new chunk automatically.
"""

import glob
import os
import sys

MAILS_UI_BASE = "/opt/zextras/web/iris/carbonio-mails-ui"

# Original code: preview request with max=250000
MARKER_ON = "{msgId:t,max:25e4,shouldMarkAsRead:e}"
# Patched code: no max limit (same as loadFullMessage)
MARKER_OFF = "{msgId:t,shouldMarkAsRead:e}"


def is_russian():
    for var in ("LANG", "LC_ALL", "LC_MESSAGES"):
        if os.environ.get(var, "").lower().startswith("ru"):
            return True
    return False


def msgs():
    if is_russian():
        return {
            "not_found":  "ОШИБКА: чанк с функцией предпросмотра не найден.",
            "hint":       f"Ищи вручную: grep -rl 'max:25e4,shouldMarkAsRead' {MAILS_UI_BASE}/",
            "file":       "Файл",
            "state_on":   "Состояние: ВКЛЮЧЕНО — письма обрезаются до 250 KB при предпросмотре",
            "state_off":  "Состояние: ОТКЛЮЧЕНО — патч активен, письма загружаются полностью",
            "action_on":  "ОТКЛЮЧИТЬ усечение (письма всегда будут загружаться полностью)",
            "action_off": "ВКЛЮЧИТЬ усечение (вернуть стандартное поведение)",
            "action":     "Действие",
            "prompt":     "Нажмите Enter для подтверждения, Ctrl+C для отмены: ",
            "cancelled":  "Отменено.",
            "err_patch":  "ОШИБКА: замена не применилась (паттерн не найден точно).",
            "ok_off":     "OK: усечение ОТКЛЮЧЕНО. Баннер «Загрузить сообщение» больше не появится.\n    Все письма открываются полностью сразу.",
            "ok_on":      "OK: усечение ВКЛЮЧЕНО. Возвращено стандартное поведение Carbonio.",
            "reload":     "Перезагрузка страницы в браузере не нужна — изменения вступают сразу.",
        }
    else:
        return {
            "not_found":  "ERROR: preview chunk not found.",
            "hint":       f"Search manually: grep -rl 'max:25e4,shouldMarkAsRead' {MAILS_UI_BASE}/",
            "file":       "File",
            "state_on":   "State: ENABLED — messages are truncated at 250 KB on preview",
            "state_off":  "State: DISABLED — patch is active, messages always load in full",
            "action_on":  "DISABLE truncation (messages will always load in full)",
            "action_off": "ENABLE truncation (restore default behavior)",
            "action":     "Action",
            "prompt":     "Press Enter to confirm, Ctrl+C to cancel: ",
            "cancelled":  "Cancelled.",
            "err_patch":  "ERROR: replacement failed (pattern not found).",
            "ok_off":     'OK: truncation DISABLED. The "Load message" banner will no longer appear.\n    All messages open in full immediately.',
            "ok_on":      "OK: truncation ENABLED. Default Carbonio behavior restored.",
            "reload":     "No browser page reload needed — changes take effect immediately.",
        }


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
    check_mode = len(sys.argv) > 1 and sys.argv[1] == "check"
    m = msgs()

    chunk_path, content = find_chunk()

    if chunk_path is None:
        print(m["not_found"])
        print(m["hint"])
        sys.exit(1)

    print(f"{m['file']}: {chunk_path}")

    if MARKER_ON in content:
        state = "ON"
        print(m["state_on"])
        action = m["action_on"]
        old, new = MARKER_ON, MARKER_OFF
    else:
        state = "OFF"
        print(m["state_off"])
        action = m["action_off"]
        old, new = MARKER_OFF, MARKER_ON

    if check_mode:
        sys.exit(0 if state == "OFF" else 1)

    print(f"\n{m['action']}: {action}")
    print(m["prompt"], end="", flush=True)
    try:
        input()
    except KeyboardInterrupt:
        print(f"\n{m['cancelled']}")
        sys.exit(0)

    new_content = content.replace(old, new, 1)
    if new_content == content:
        print(m["err_patch"])
        sys.exit(1)

    write(chunk_path, new_content)
    print(m["ok_off"] if state == "ON" else m["ok_on"])
    print(f"\n{m['reload']}")


if __name__ == "__main__":
    main()
