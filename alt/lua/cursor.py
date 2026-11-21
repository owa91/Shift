from lupa.lua54 import LuaRuntime, LuaError
from alt import data
from ui.window import ShiftWindow
import mouse

class Cursor:
    def __init__(self, lua, window: ShiftWindow, ctx=None):
        self.lua: LuaRuntime = lua
        self.window = window
        self.ctx = ctx if ctx is not None else data
        self._listeners = {}
        self.last_pos = []

        h1 = mouse.hook(self.on_move)
        h2 = mouse.on_click(self.on_click_left_button)
        h3 = mouse.on_right_click(self.on_click_right_button)
        if hasattr(self.ctx, "add_mouse_hook"):
            self.ctx.add_mouse_hook(h1)
            self.ctx.add_mouse_hook(h2)
            self.ctx.add_mouse_hook(h3)

        lua.globals()['cursor'] = {
            "get_position": self.get_position,
            "event": self.subscribe,
        }

    def subscribe(self, event_name, callback):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def trigger(self, event_name, *args):
        if not getattr(self.ctx, "active", True):
            return
        if event_name in self._listeners:
            for callback in list(self._listeners[event_name]):
                self.ctx.events.append((callback, args))

    def get_position(self):
        x, y = mouse.get_position()

        return x, y

    def on_move(self, _):
        x, y = mouse.get_position()

        if self.last_pos == [x, y]:
            return

        self.last_pos = [x, y]

        self.trigger("on_move", x, y)

    def on_click_left_button(self):
        self.trigger("on_click_left_button")

    def on_click_right_button(self):
        self.trigger("on_click_right_button")

