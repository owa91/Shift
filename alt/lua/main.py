from lupa import LuaRuntime, LuaError
from alt.lua import drawer, cursor, screen, n_requests
from alt.data import *
from ui.window import ShiftWindow
import time
import traceback

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('collectgarbage("generational")')

def load_script(lua_code, window: ShiftWindow):
    drawer.Drawer(lua, window)
    cursor.Cursor(lua, window)
    screen.Screen(lua, window)
    n_requests.Requests(lua, window)

    def sleep(seconds):
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
        traceback.print_exc()