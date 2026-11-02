import time
from lupa import LuaRuntime, LuaError
from alt import data
from ui.window import ShiftWindow
from pynput import mouse
import platform
import math

class Screen:
    def __init__(self, lua, window: ShiftWindow):
        self.lua: LuaRuntime = lua
        self.window = window
        self._listeners = []
        self.scrolling_enabled = True
        self.show_status = True
        self.automatic = True
        self.ymax = None

        listener = mouse.Listener(on_scroll=self.scroll)
        listener.daemon = True
        listener.start()
        self.listener = listener

        lua.globals()['screen'] = {
            "scrolling_enabled": self.scrolling_enabled,
            "set_scrolling_status": self.set_scrolling_status,
            "get_scroll_y": lambda: data.y_scroll_status.get("y", 0.0),
        }

    def set_scrolling_status(self, enabled=True, show_status=True, automatic=True, YMax=None): #YMax - set to maximum scrolling by y-axis
        if automatic and YMax is not None:
            data.console_messages.append({
                "type": "error",
                "message": "automatic cannot be true when ymax isn't nil"
            })
            return

        self.scrolling_enabled, self.show_status, self.automatic, self.ymax = enabled, show_status, automatic, YMax

        data.y_scrolling = {"enabled": self.scrolling_enabled, "show_status": self.show_status, "automatic": self.automatic, "ymax": self.ymax}

    def scroll(self, x, y, dx, dy):
        if dy != 0 and self.scrolling_enabled and data.y_scrolling.get("enabled", True):
            lines = 3

            if platform.system() == "Windows":
                try:
                    import ctypes
                    scroll_lines = ctypes.c_uint()
                    ctypes.windll.user32.SystemParametersInfoW(0x0068, 0, ctypes.byref(scroll_lines), 0)
                    lines = scroll_lines.value
                except Exception:
                    lines = 3

            to_pixels = lines * (dy * 33)

            max_scroll = max(0, getattr(data, "elements_lower_screen", 0))
            cur_target = data.y_scroll_status.get("target_y", data.y_scroll_status.get("y", 0.0))

            if max_scroll <= 0 and cur_target >= 0:
                return

            target_y = max(-float(max_scroll), min(0.0, cur_target + to_pixels))
            data.y_scroll_status["target_y"] = target_y
