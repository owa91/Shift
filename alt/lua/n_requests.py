from lupa.lua54 import LuaRuntime, LuaError
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


def _to_lua(value, lua_rt=None):
    rt = lua_rt or _lua
    if rt is None:
        return value
    if isinstance(value, dict):
        return rt.table_from({k: _to_lua(v, rt) for k, v in value.items()})
    if isinstance(value, list):
        return rt.table_from([_to_lua(v, rt) for v in value])
    return value


def _from_lua(value):
    if value is None or isinstance(value, (str, bytes, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {k: _from_lua(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_from_lua(v) for v in value]
    if hasattr(value, "items"):
        items = list(value.items())
        if items and all(isinstance(k, int) for k, _ in items):
            keys = sorted(k for k, _ in items)
            if keys == list(range(1, len(keys) + 1)):
                return [_from_lua(value[k]) for k in keys]
        return {k: _from_lua(v) for k, v in items}
    return value


class post_request:
    def __init__(self, url="https://google.com/", lua_rt=None, ctx=None):
        self._lua = lua_rt
        self.ctx = ctx if ctx is not None else data
        self.url: str = url
        self.headers = {
            "User-Agent": f"Shift/{versionshift}, Alt/{self.ctx.version}, {platform.system()}/{platform.release()}",
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
            if self.url.startswith("http://"):
                if not self.ctx.is_localfile and not self.ctx.requests_settings.get("http_allowed"):
                    self.ctx.console_messages.append({
                        "type": "error",
                        "message": "http cannot use because this isn't localfile"
                    })
                    return
            else:
                self.ctx.console_messages.append({
                    "type": "error",
                    "message": "url hasn't written right"
                })
                return

        index = len(self.ctx.network_requests)

        self.ctx.network_requests.append({
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": time.time(),
            "status": 0,
            "method": "POST"
        })

        request: requests.Response = None

        try:
            request = requests.post(
                self.url,
                headers=_from_lua(self.headers),
                json=_from_lua(self.json),
                data=_from_lua(self.data)
            )
        except Exception as e:
            self.ctx.console_messages.append({
                "type": "error",
                "message": str(e),
            })

            self.ctx.network_requests[index] = {
                "endpoint": self.url,
                "created_by": "script/lua",
                "when": self.ctx.network_requests[index]["when"],
                "status": -1,
                "method": "POST",
                "ping": (time.time() - self.ctx.network_requests[index]["when"]) * 1000,
                "text": str(e),
            }

            return

        parsed_json = _safe_json(request)
        self.ctx.network_requests[index] = {
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": self.ctx.network_requests[index]["when"],
            "status": request.status_code,
            "method": "POST",
            "ping": (time.time() - self.ctx.network_requests[index]["when"]) * 1000,
            "headers": request.headers,
            "json": parsed_json,
            "text": request.text,
            "content": request.content
        }

        self.status_code = request.status_code
        self.text = request.text
        self.got_json = _to_lua(parsed_json, self._lua)
        self.content = request.content
        self.got_headers = request.headers

class get_request:
    def __init__(self, url="https://google.com/", lua_rt=None, ctx=None):
        self._lua = lua_rt
        self.ctx = ctx if ctx is not None else data
        self.url: str = url
        self.headers = {
            "User-Agent": f"Shift/{versionshift}, Alt/{self.ctx.version}, {platform.system()}/{platform.release()}",
            "Alt_Created_By": "script/lua"
        }
        self.got_headers = None
        self.status_code = 0
        self.text = None
        self.json = None
        self.content = None

    def send(self):
        if not self.url.startswith("https://"):
            if self.url.startswith("http://"):
                if not self.ctx.is_localfile and not self.ctx.requests_settings.get("http_allowed"):
                    self.ctx.console_messages.append({
                        "type": "error",
                        "message": "http cannot use because this isn't localfile"
                    })
                    return
            else:
                self.ctx.console_messages.append({
                    "type": "error",
                    "message": "url hasn't written right"
                })
                return

        index = len(self.ctx.network_requests)

        self.ctx.network_requests.append({
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": time.time(),
            "status": 0,
            "method": "GET"
        })

        request: requests.Response = None

        try:
            request = requests.get(self.url, headers=_from_lua(self.headers))
        except Exception as e:
            self.ctx.console_messages.append({
                "type": "error",
                "message": str(e),
            })

            self.ctx.network_requests[index] = {
                "endpoint": self.url,
                "created_by": "script/lua",
                "when": self.ctx.network_requests[index]["when"],
                "status": -1,
                "method": "GET",
                "ping": (time.time() - self.ctx.network_requests[index]["when"]) * 1000,
                "text": str(e),
            }

            return

        parsed_json = _safe_json(request)
        self.ctx.network_requests[index] = {
            "endpoint": self.url,
            "created_by": "script/lua",
            "when": self.ctx.network_requests[index]["when"],
            "status": request.status_code,
            "method": "GET",
            "ping": (time.time() - self.ctx.network_requests[index]["when"]) * 1000,
            "headers": request.headers,
            "json": parsed_json,
            "text": request.text,
            "content": request.content
        }

        self.status_code = request.status_code
        self.text = request.text
        self.json = _to_lua(parsed_json, self._lua)
        self.content = request.content
        self.got_headers = request.headers


class Requests:
    def __init__(self, lua, window: ShiftWindow, ctx=None):
        global _lua
        _lua = lua
        self.lua: LuaRuntime = lua
        self.ctx = ctx if ctx is not None else data
        lua.globals()['requests'] = {
            "get": lambda url="https://google.com/": get_request(url, lua, self.ctx),
            "post": lambda url="https://google.com/": post_request(url, lua, self.ctx),
        }


