from lupa.lua55 import LuaRuntime, LuaError
from alt import data
from ui.window import ShiftWindow
import requests
from data import version as versionshift
import platform
import time

_lua = None


def _safe_json(response):
    try:
        return response.json()
    except Exception:
        return None


def _to_lua(value):
    if _lua is None:
        return value
    if isinstance(value, dict):
        return _lua.table_from({k: _to_lua(v) for k, v in value.items()})
    if isinstance(value, list):
        return _lua.table_from([_to_lua(v) for v in value])
    return value


class post_request:
    def __init__(self, url="https://google.com/"):
        self.url: str = url
        self.headers = {
            "User-Agent": f"Shift/{versionshift}, Alt/{data.version}, {platform.system()}/{platform.release()}",
            "Alt_Created_By": "script/lua"
        }
        self.json = None
        self.data = None
        self.got_headers = None
        self.status_code = 0
        self.text = None
        self.got_json = None
        self.content = None

    def send(self):
        if not self.url.startswith("https://"):
            if self.url.startswith("http://") and not data.is_localfile and not data.requests_settings.get(
                    "http_allowed"):
                data.console_messages.append({
                    "type": "error",
                    "message": "http cannot use because this isn't localfile"
                })
                return
            else:
                data.console_messages.append({
                    "type": "error",
                    "message": "url hasn't written right"
                })
                return

        index = len(data.network_requests)

        data.network_requests.append({
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": time.time(),
            "status": 0,
            "method": "POST"
        })

        request: requests.Response = None

        try:
            request = requests.post(self.url, headers=self.headers, json=self.json, data=self.data)
        except Exception as e:
            data.console_messages.append({
                "type": "error",
                "message": e,
            })

            data.network_requests[index] = {
                "endpoint": self.url,
                "created_by": "script/lua",
                "when": data.network_requests[index]["when"],
                "status": -1,
                "method": "GET",
                "ping": (time.time() - data.network_requests[index]["when"]) * 1000,
                "text": e,
            }

            return

        data.network_requests[index] = {
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": data.network_requests[index]["when"],
            "status": request.status_code,
            "method": "GET",
            "ping": (time.time() - data.network_requests[index]["when"]) * 1000,
            "headers": request.headers,
            "json": _safe_json(request),
            "text": request.text,
            "content": request.content
        }

        self.status_code = request.status_code
        self.text = request.text
        self.got_json = _to_lua(_safe_json(request))
        self.content = request.content
        self.got_headers = request.headers

class get_request:
    def __init__(self, url="https://google.com/"):
        self.url: str = url
        self.headers = {
            "User-Agent": f"Shift/{versionshift}, Alt/{data.version}, {platform.system()}/{platform.release()}",
            "Alt_Created_By": "script/lua"
        }
        self.got_headers = None
        self.status_code = 0
        self.text = None
        self.json = None
        self.content = None

    def send(self):
        if not self.url.startswith("https://"):
            if self.url.startswith("http://") and not data.is_localfile and not data.requests_settings.get("http_allowed"):
                data.console_messages.append({
                    "type": "error",
                    "message": "http cannot use because this isn't localfile"
                })
                return
            else:
                data.console_messages.append({
                    "type": "error",
                    "message": "url hasn't written right"
                })
                return

        index = len(data.network_requests)

        data.network_requests.append({
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": time.time(),
            "status": 0,
            "method": "GET"
        })

        request: requests.Response = None

        try:
            request = requests.get(self.url, headers=self.headers)
        except Exception as e:
            data.console_messages.append({
                "type": "error",
                "message": e,
            })

            data.network_requests[index] = {
                "endpoint": self.url,
                "created_by": "script/lua",
                "when": data.network_requests[index]["when"],
                "status": -1,
                "method": "GET",
                "ping": (time.time() - data.network_requests[index]["when"]) * 1000,
                "text": e,
            }

            return

        data.network_requests[index] = {
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": data.network_requests[index]["when"],
            "status": request.status_code,
            "method": "GET",
            "ping": (time.time() - data.network_requests[index]["when"]) * 1000,
            "headers": request.headers,
            "json": _safe_json(request),
            "text": request.text,
            "content": request.content
        }

        self.status_code = request.status_code
        self.text = request.text
        self.json = _to_lua(_safe_json(request))
        self.content = request.content
        self.got_headers = request.headers


class Requests:
    def __init__(self, lua, window: ShiftWindow):
        global _lua
        _lua = lua
        self.lua: LuaRuntime = lua
        lua.globals()['requests'] = {
            "get": get_request,
            "post": post_request,
        }


