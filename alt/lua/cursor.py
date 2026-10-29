from lupa import LuaRuntime, LuaError
from alt.data import  *
from ui.window import ShiftWindow
import mouse

class Cursor:
    def __init__(self, lua, window: ShiftWindow):
        self.lua: LuaRuntime = lua
        self.window = window
        self._listeners = []
        self.last_pos = []

        mouse.hook(self.on_move)
        mouse.on_click(self.on_click_left_button)
        mouse.on_right_click(self.on_click_right_button)

        lua.globals()['cursor'] = {
            "get_position": self.get_position,
            "event": self.subscribe,
        }

    def subscribe(self, event_name, callback):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def trigger(self, event_name, *args):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args)

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

