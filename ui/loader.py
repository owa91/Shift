import platform
import re
import socket
from pathlib import Path
from urllib.parse import urlparse
import requests
from alt import data as alt_data
from data import version as versionshift


def _lua_str(s: str) -> str:
    return (
        '"'
        + str(s)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "")
        .replace("\n", "\\n")
        + '"'
    )


def normalize_url(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return "shift://new"
    low = s.lower()
    if low.startswith("shift://"):
        return "shift://" + s[len("shift://"):]
    if low.startswith("local://"):
        return "local://" + s[len("local://"):]
    if low.startswith("https://"):
        return "https://" + s[len("https://"):]
    if low.startswith("http://"):
        return "http://" + s[len("http://"):]
    if "://" in s:
        return s
    if re.match(r"^[a-zA-Z]:[\\/]", s):
        return "local://" + s
    return "https://" + s


def tab_title_for_url(url: str) -> str:
    low = url.lower()
    if low in ("shift://new", "shift://new.lua"):
        return "Новая вкладка"
    if low.startswith("shift://"):
        return url
    if low.startswith("local://"):
        p = url[len("local://"):].lstrip("/")
        if len(p) >= 2 and p[1] == ":":
            return Path(p).name or url
        return Path(url[len("local://"):]).name or url
    parsed = urlparse(url)
    return parsed.netloc or url


def _wrap_text(text: str, max_chars: int = 64) -> list[str]:
    lines = []
    for paragraph in str(text).splitlines():
        words = paragraph.split(" ")
        cur = ""
        for w in words:
            if not cur:
                cur = w
            elif len(cur) + 1 + len(w) <= max_chars:
                cur += " " + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines or [""]


def build_error_page(code: str, title: str, description: str, details: str = "", url: str = "") -> str:
    desc_lines = _wrap_text(description, 62)
    det_lines = _wrap_text(details, 70) if details else []
    url_line = url if len(url) <= 72 else url[:69] + "..."

    desc_lua = ", ".join(_lua_str(line) for line in desc_lines)
    det_lua = ", ".join(_lua_str(line) for line in det_lines)

    return f"""
screen.set_scrolling_status(false, false, true)
drawer.fill_background("#0f1115")

local card = drawer.rectangle(0, 0, 10, 10)
card.set_color("#1a1d24")
card.set_corners(14, 14)

local badge = drawer.rectangle(0, 0, 10, 10)
badge.set_color("#e5484d")
badge.set_corners(6, 6)

local badge_txt = drawer.text(0, 0, {_lua_str(code)}, 13, "Calibri", "Bold", "#ffffff", "left")
local title_txt = drawer.text(0, 0, {_lua_str(title)}, 28, "Calibri", "Bold", "#e6e8ee", "left")

local desc_lines = {{ {desc_lua} }}
local desc_objs = {{}}
for i = 1, #desc_lines do
    desc_objs[i] = drawer.text(0, 0, desc_lines[i], 17, "Calibri", "Regular", "#a8b0c0", "left")
end

local det_lines = {{ {det_lua} }}
local det_objs = {{}}
for i = 1, #det_lines do
    det_objs[i] = drawer.text(0, 0, det_lines[i], 14, "Calibri", "Italic", "#788092", "left")
end

local url_txt = drawer.text(0, 0, {_lua_str(url_line)}, 13, "Calibri", "Regular", "#6c8cff", "left")

local W, H = 0, 0
local function layout(w, h)
    W, H = w, h
    local cw = math.min(680, math.max(360, w - 80))
    local ch = 165 + #desc_objs * 24 + (#det_objs > 0 and (#det_objs * 20 + 16) or 0)
    local cx = math.floor((w - cw) / 2)
    local cy = math.floor((h - ch) / 2)

    card.set_position(cx, cy)
    card.set_size(cw, ch)

    local pad = 32
    badge.set_position(cx + pad, cy + pad)
    badge.set_size(math.min(cw - pad * 2, math.max(90, #{_lua_str(code)} * 9 + 22)), 26)
    badge_txt.set_position(cx + pad + 11, cy + pad + 5)

    title_txt.set_position(cx + pad, cy + pad + 42)

    local y = cy + pad + 88
    for i = 1, #desc_objs do
        desc_objs[i].set_position(cx + pad, y)
        y = y + 24
    end

    if #det_objs > 0 then
        y = y + 12
        for i = 1, #det_objs do
            det_objs[i].set_position(cx + pad, y)
            y = y + 20
        end
    end

    url_txt.set_position(cx + pad, cy + ch - 34)
end

local iw, ih = drawer.get_size_screen()
layout(iw, ih)

while true do
    local cw, ch = drawer.get_size_screen()
    if cw ~= W or ch ~= H then
        layout(cw, ch)
    end
    sleep(0.05)
end
"""


def _is_dns_error(exc: Exception) -> bool:
    cur = exc
    seen = set()
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        if isinstance(cur, socket.gaierror):
            return True
        name = type(cur).__name__
        msg = str(cur).lower()
        if "nameresolutionerror" in name.lower():
            return True
        if any(
            k in msg
            for k in (
                "failed to resolve",
                "getaddrinfo failed",
                "name or service not known",
                "nodename nor servname",
                "temporary failure in name resolution",
                "no such host",
            )
        ):
            return True
        cur = getattr(cur, "__cause__", None) or getattr(cur, "__context__", None)
        if cur is None and getattr(exc, "args", None):
            for arg in exc.args:
                if isinstance(arg, Exception) and id(arg) not in seen:
                    cur = arg
                    break
    return False


def _response_supports_alt(resp: requests.Response) -> tuple[bool, str]:
    headers = resp.headers
    content_type = headers.get("Content-Type", "").lower()

    alt_header = None
    for key in ("Alt-Engine", "Alt-Support", "X-Alt-Engine", "X-Alt-Support", "Alt", "Shift-Alt", "Alt-Version"):
        val = headers.get(key)
        if val is not None:
            alt_header = val.strip().lower()
            break

    if alt_header in ("false", "no", "0", "unsupported", "none"):
        return False, f"Сервер явно указал отсутствие поддержки Alt ({alt_header})."

    is_lua_ct = any(tok in content_type for tok in ("lua", "alt-script", "application/alt"))
    parsed_path = urlparse(resp.url).path.lower()
    is_lua_ext = parsed_path.endswith(".lua")
    body_head = resp.text.lstrip()[:64].lower()
    looks_html = body_head.startswith(("<!doctype", "<html", "<head", "<body", "<?xml"))
    is_html_ct = ("text/html" in content_type) or ("xhtml" in content_type)

    if (is_html_ct or looks_html) and not alt_header and not is_lua_ct:
        ct_label = content_type.split(";")[0] if content_type else "text/html"
        return False, f"Получен формат {ct_label} вместо скрипта Alt."

    if alt_header or is_lua_ct:
        return True, ""

    if is_lua_ext and (not content_type or "text/plain" in content_type or "application/octet-stream" in content_type):
        return True, ""

    ct_label = content_type.split(";")[0] if content_type else "не указан"
    return False, f"Content-Type: {ct_label}. Отсутствуют заголовки поддержки Alt."


def fetch_page(raw_url: str) -> dict:
    url = normalize_url(raw_url)
    low = url.lower()

    if low.startswith("shift://"):
        rel = url[len("shift://"):].strip("/\\")
        if not rel:
            rel = "new"
        if not rel.lower().endswith(".lua"):
            rel += ".lua"

        folder = Path("lua_scripts").resolve()
        candidate = (folder / rel).resolve()
        target = None
        try:
            candidate.relative_to(folder)
            if candidate.is_file():
                target = candidate
        except ValueError:
            target = None

        if target is None:
            found = next(folder.rglob(Path(rel).name), None)
            if found is not None and found.is_file():
                target = found

        if target is not None:
            try:
                code = target.read_text(encoding="utf-8")
                return {
                    "ok": True,
                    "lua_code": code,
                    "is_localfile": True,
                    "title": tab_title_for_url(url),
                    "final_url": url,
                }
            except Exception as e:
                return {
                    "ok": False,
                    "lua_code": build_error_page(
                        "SHIFT_READ_ERROR",
                        "Не удалось прочитать скрипт Shift",
                        "Произошла ошибка при чтении встроенного скрипта.",
                        str(e),
                        url,
                    ),
                    "is_localfile": True,
                    "title": "Ошибка",
                    "final_url": url,
                }

        return {
            "ok": False,
            "lua_code": build_error_page(
                "SHIFT_NOT_FOUND",
                "Скрипт Shift не найден",
                f"Не удалось найти встроенный скрипт по адресу {url}.",
                "Проверьте наличие файла в папке lua_scripts.",
                url,
            ),
            "is_localfile": True,
            "title": "Не найдено",
            "final_url": url,
        }

    if low.startswith("local://"):
        raw_path = url[len("local://"):]
        if raw_path.startswith("/") and len(raw_path) >= 3 and raw_path[2] == ":":
            raw_path = raw_path[1:]
        path = Path(raw_path)

        if not path.exists() or not path.is_file():
            return {
                "ok": False,
                "lua_code": build_error_page(
                    "LOCAL_NOT_FOUND",
                    "Локальный файл не найден",
                    f"Файл по пути {path} не существует.",
                    "Проверьте правильность пути к файлу.",
                    url,
                ),
                "is_localfile": True,
                "title": "Файл не найден",
                "final_url": url,
            }

        if path.suffix.lower() != ".lua":
            return {
                "ok": False,
                "lua_code": build_error_page(
                    "UNSUPPORTED_FILE",
                    "Неподдерживаемый тип файла",
                    "Shift может открывать только локальные Lua-скрипты (.lua).",
                    f"Выбранный файл: {path.name}",
                    url,
                ),
                "is_localfile": True,
                "title": "Ошибка файла",
                "final_url": url,
            }

        try:
            code = path.read_text(encoding="utf-8")
            return {
                "ok": True,
                "lua_code": code,
                "is_localfile": True,
                "title": path.name,
                "final_url": url,
            }
        except PermissionError:
            return {
                "ok": False,
                "lua_code": build_error_page(
                    "LOCAL_ACCESS_DENIED",
                    "Нет доступа к файлу",
                    f"Недостаточно прав для чтения файла {path}.",
                    "",
                    url,
                ),
                "is_localfile": True,
                "title": "Нет доступа",
                "final_url": url,
            }
        except Exception as e:
            return {
                "ok": False,
                "lua_code": build_error_page(
                    "LOCAL_READ_ERROR",
                    "Ошибка чтения файла",
                    "Не удалось прочитать локальный скрипт.",
                    str(e),
                    url,
                ),
                "is_localfile": True,
                "title": "Ошибка файла",
                "final_url": url,
            }

    if low.startswith("http://"):
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_INSECURE_HTTP",
                "Небезопасное соединение (HTTP)",
                "Соединение по протоколу HTTP не защищено. Shift требует HTTPS для загрузки страниц из интернета.",
                "Попробуйте заменить http:// на https:// в адресной строке.",
                url,
            ),
            "is_localfile": False,
            "title": "Небезопасное соединение",
            "final_url": url,
        }

    if not low.startswith("https://"):
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_UNSUPPORTED_PROTOCOL",
                "Неподдерживаемый протокол",
                "Браузер Shift поддерживает только протоколы https://, local:// и shift://.",
                f"Указанный адрес: {url}",
                url,
            ),
            "is_localfile": False,
            "title": "Ошибка адреса",
            "final_url": url,
        }

    parsed = urlparse(url)
    if not parsed.netloc:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_INVALID_URL",
                "Некорректный адрес сайта",
                "Указан неверный URL. Проверьте правильность написания адреса.",
                "",
                url,
            ),
            "is_localfile": False,
            "title": "Некорректный URL",
            "final_url": url,
        }

    headers = {
        "User-Agent": f"Shift/{versionshift}, Alt/{alt_data.version}, {platform.system()}/{platform.release()}",
        "Accept": "application/alt-lua, text/x-lua, application/x-lua, text/plain",
        "Alt_Type-Script": "Global",
        "Alt_Created_By": "Shift.Browser",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    except requests.exceptions.SSLError as e:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_SSL_PROTOCOL_ERROR",
                "Ошибка защищённого соединения (SSL)",
                f"Не удалось проверить сертификат безопасности для {parsed.netloc}.",
                str(e),
                url,
            ),
            "is_localfile": False,
            "title": "Ошибка SSL",
            "final_url": url,
        }
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_CONNECTION_TIMED_OUT",
                "Превышено время ожидания",
                f"Сервер {parsed.netloc} не ответил вовремя.",
                "Проверьте подключение к интернету или попробуйте перезагрузить страницу.",
                url,
            ),
            "is_localfile": False,
            "title": "Таймаут",
            "final_url": url,
        }
    except requests.exceptions.TooManyRedirects:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_TOO_MANY_REDIRECTS",
                "Слишком много перенаправлений",
                f"Сайт {parsed.netloc} выполнил слишком много переадресаций.",
                "",
                url,
            ),
            "is_localfile": False,
            "title": "Ошибка редиректа",
            "final_url": url,
        }
    except requests.exceptions.ConnectionError as e:
        if _is_dns_error(e):
            return {
                "ok": False,
                "lua_code": build_error_page(
                    "ERR_NAME_NOT_RESOLVED",
                    "Ошибка DNS - сайт не найден",
                    f"Не удалось найти IP-адрес сервера {parsed.netloc}.",
                    "Проверьте правильность доменного имени, DNS-записи или подключение к сети.",
                    url,
                ),
                "is_localfile": False,
                "title": "Ошибка DNS",
                "final_url": url,
            }
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_CONNECTION_FAILED",
                "Не удалось подключиться к сайту",
                f"Сервер {parsed.netloc} недоступен или отклонил соединение.",
                str(e),
                url,
            ),
            "is_localfile": False,
            "title": "Нет подключения",
            "final_url": url,
        }
    except requests.exceptions.RequestException as e:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_NETWORK",
                "Сетевая ошибка",
                f"Не удалось загрузить страницу {parsed.netloc}.",
                str(e),
                url,
            ),
            "is_localfile": False,
            "title": "Ошибка сети",
            "final_url": url,
        }

    final_url = resp.url or url
    host = urlparse(final_url).netloc or parsed.netloc

    if resp.status_code == 404:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "HTTP 404",
                "Страница не найдена",
                f"Запрошенная страница на {host} не существует (ошибка 404).",
                "",
                final_url,
            ),
            "is_localfile": False,
            "title": "404 - Не найдено",
            "final_url": final_url,
        }

    if resp.status_code == 403:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "HTTP 403",
                "Доступ запрещён",
                f"Сервер {host} запретил доступ к этой странице (ошибка 403).",
                "",
                final_url,
            ),
            "is_localfile": False,
            "title": "403 - Доступ запрещён",
            "final_url": final_url,
        }

    if resp.status_code != 200:
        return {
            "ok": False,
            "lua_code": build_error_page(
                f"HTTP {resp.status_code}",
                f"Ошибка сервера ({resp.status_code})",
                f"Сервер {host} вернул статус {resp.status_code} {resp.reason or ''}.",
                "",
                final_url,
            ),
            "is_localfile": False,
            "title": f"Ошибка {resp.status_code}",
            "final_url": final_url,
        }

    supported, reason = _response_supports_alt(resp)
    if not supported:
        return {
            "ok": False,
            "lua_code": build_error_page(
                "ERR_ALT_NOT_SUPPORTED",
                "Страница не поддерживает Alt",
                f"Сайт {host} не поддерживает движок Alt браузера Shift.",
                reason,
                final_url,
            ),
            "is_localfile": False,
            "title": "Alt не поддерживается",
            "final_url": final_url,
        }

    return {
        "ok": True,
        "lua_code": resp.text,
        "is_localfile": False,
        "title": host,
        "final_url": final_url,
    }
