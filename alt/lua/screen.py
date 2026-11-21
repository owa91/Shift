from lupa.lua54 import LuaRuntime, LuaError
from alt import data
from ui.window import ShiftWindow

class Screen:
    def __init__(self, lua, window: ShiftWindow, ctx=None):
        self.lua: LuaRuntime = lua
        self.window = window
        self.ctx = ctx if ctx is not None else data
        self._listeners = []
        self.scrolling_enabled = True
        self.show_status = True
        self.automatic = True
        self.ymax = None

        lua.globals()['screen'] = {
            "scrolling_enabled": self.scrolling_enabled,
            "set_scrolling_status": self.set_scrolling_status,
            "get_scroll_y": lambda: self.ctx.y_scroll_status.get("y", 0.0),
        }

    def set_scrolling_status(self, enabled=True, show_status=True, automatic=True, YMax=None): #YMax - set to maximum scrolling by y-axis
        if automatic and YMax is not None:
            self.ctx.console_messages.append({
                "type": "error",
                "message": "automatic cannot be true when ymax isn't nil"
            })
            return

        self.scrolling_enabled, self.show_status, self.automatic, self.ymax = enabled, show_status, automatic, YMax
        self.lua.globals()['screen']['scrolling_enabled'] = self.scrolling_enabled

        self.ctx.y_scrolling = {"enabled": self.scrolling_enabled, "show_status": self.show_status, "automatic": self.automatic, "ymax": self.ymax}
