from lupa import LuaRuntime, LuaError
from alt.lua import drawer
from alt.data import *
from ui.window import ShiftWindow
import time

lua = LuaRuntime(unpack_returned_tuples=True)

def load_script(lua_code, window: ShiftWindow):
    drawer.Drawer(lua, window)

    def sleep(seconds):
        # пауза + выполнение событий (клики и т.п.) в Lua-потоке
        time.sleep(seconds)
        drawer.run_events()

    lua.globals()["sleep"] = sleep

    try:
        lua.execute(lua_code)
    except LuaError as e:
        console_messages.append({
            "type": "error",
            "message": f"Error occurred when the page is initializing:\n{e}"
        })
        print(e)