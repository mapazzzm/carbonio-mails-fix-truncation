# carbonio-mails-fix-truncation

[<sup>ru</sup> Русский](#русский) | [<sup>en</sup> English](#english)

---

## Русский

### Проблема

При открытии письма carbonio-mails-ui отправляет `GetMsgRequest` с параметром `max=250000` (250 KB). Если суммарный HTML/текст тела превышает этот лимит, сервер обрезает содержимое и возвращает `truncated=1`. UI показывает баннер:

> *Это сообщение было обрезано из-за длины* — **Загрузить сообщение**

Письма, которые стабильно вызывают усечение:

- **Письма из Outlook с вложениями** — HTML-тело раздуто Word-стилями и XML-неймспейсами Microsoft даже при двух строчках текста
- **Цепочки пересылок** (`FW: FW: FW:`) — накопленный quoted HTML каждой итерации
- **HTML-отчёты** из ERP/CRM-систем с большими таблицами
- Длинные **рассылки/newsletters**

### Решение

Патч убирает параметр `max` из preview-запроса. Без `max` сервер возвращает письмо целиком — точно так же, как кнопка «Загрузить сообщение».

Изменение в `5.*.chunk.js` (carbonio-mails-ui):

```
# ДО (оригинал):
{msgId:t,max:25e4,shouldMarkAsRead:e}

# ПОСЛЕ (патч):
{msgId:t,shouldMarkAsRead:e}
```

### Использование

```bash
python3 toggle.py
```

Скрипт определяет текущее состояние и предлагает переключить:

```
Файл: /opt/zextras/web/iris/carbonio-mails-ui/[hash]/5.*.chunk.js
Состояние: ВКЛЮЧЕНО — письма обрезаются до 250 KB при предпросмотре

Действие: ОТКЛЮЧИТЬ усечение (письма всегда будут загружаться полностью)
Нажмите Enter для подтверждения, Ctrl+C для отмены:
OK: усечение ОТКЛЮЧЕНО. Баннер «Загрузить сообщение» больше не появится.
```

Если патч уже применён — предложит вернуть оригинальное поведение.

#### Режим проверки (без интерактива)

```bash
python3 toggle.py check
# exit=0 — патч активен (усечение отключено)
# exit=1 — патч не активен (оригинальное поведение)
```

Удобно для автоматической проверки в скриптах и чеклистах после `apt upgrade`.

### После `apt upgrade carbonio-mails-ui`

При обновлении пакета `carbonio-mails-ui` хэш директории с чанками меняется. Скрипт автоматически находит новый чанк по содержимому — просто запустить повторно:

```bash
python3 toggle.py
```

Если скрипт не находит чанк (изменилось имя файла `5.*.chunk.js`):

```bash
grep -rl 'max:25e4,shouldMarkAsRead' /opt/zextras/web/iris/carbonio-mails-ui/
```

### Совместимость

Проверено на **Carbonio CE 26.3.2** (Ubuntu 22.04 / 24.04).

Перезапуск сервисов не требуется — изменения вступают в силу при следующей загрузке страницы в браузере.

### Как это работает

В carbonio-mails-ui две функции для загрузки письма:

| Функция | Вызов | `max` |
|---------|-------|-------|
| `vT` / `p` | Автоматически при открытии | `250000` |
| `MA` / `m` | Кнопка «Загрузить сообщение» | не передаётся |

Параметр `max` в `GetMsgRequest` (SOAP API Zimbra) ограничивает суммарный объём текстового контента всех body-частей MIME, возвращаемых сервером. При превышении сервер ставит `truncated=1` — UI читает этот флаг и показывает баннер.

Патч приводит preview-запрос к тому же поведению, что и кнопка «Загрузить сообщение».

---

## English

### Problem

When opening an email, carbonio-mails-ui sends a `GetMsgRequest` with `max=250000` (250 KB). If the total HTML/text body exceeds this limit, the server truncates the content and returns `truncated=1`. The UI then shows a banner:

> *This message has been truncated due to its length* — **Load message**

Emails that reliably trigger truncation:

- **Outlook emails with attachments** — HTML body is bloated with Word styles and Microsoft XML namespaces even for two lines of text
- **Forwarded chains** (`FW: FW: FW:`) — accumulated quoted HTML from each iteration
- **HTML reports** from ERP/CRM systems with large tables
- Long **newsletters**

### Solution

The patch removes the `max` parameter from the preview request. Without `max`, the server returns the full message — exactly as the "Load message" button does.

Change in `5.*.chunk.js` (carbonio-mails-ui):

```
# Before (original):
{msgId:t,max:25e4,shouldMarkAsRead:e}

# After (patched):
{msgId:t,shouldMarkAsRead:e}
```

### Usage

```bash
python3 toggle.py
```

The script detects the current state and offers to toggle:

```
File: /opt/zextras/web/iris/carbonio-mails-ui/[hash]/5.*.chunk.js
State: ENABLED — messages are truncated at 250 KB on preview

Action: DISABLE truncation (messages will always load in full)
Press Enter to confirm, Ctrl+C to cancel:
OK: truncation DISABLED. The "Load message" banner will no longer appear.
```

If the patch is already applied, it will offer to restore the default behavior.

#### Check mode (non-interactive)

```bash
python3 toggle.py check
# exit=0 — patch is active (truncation disabled)
# exit=1 — patch is not active (default behavior)
```

Useful for automated checks in post-upgrade scripts.

### After `apt upgrade carbonio-mails-ui`

When the `carbonio-mails-ui` package is updated, the chunk directory hash changes. The script automatically finds the new chunk by content — just run it again:

```bash
python3 toggle.py
```

If the script can't find the chunk (the filename `5.*.chunk.js` changed):

```bash
grep -rl 'max:25e4,shouldMarkAsRead' /opt/zextras/web/iris/carbonio-mails-ui/
```

### Compatibility

Tested on **Carbonio CE 26.3.2** (Ubuntu 22.04 / 24.04).

No service restart required — changes take effect on the next browser page reload.

### How it works

carbonio-mails-ui has two functions for fetching a message:

| Function | Triggered by | `max` |
|----------|-------------|-------|
| `vT` / `p` | Automatically on open | `250000` |
| `MA` / `m` | "Load message" button | not sent |

The `max` parameter in `GetMsgRequest` (Zimbra SOAP API) limits the total text content of all returned MIME body parts. When exceeded, the server sets `truncated=1` on the truncated part — the UI reads this flag and shows the banner.

The patch brings the preview request in line with the "Load message" behavior.
