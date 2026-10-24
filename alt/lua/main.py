from lupa import LuaRuntime, LuaError
from alt.lua import drawer
from alt.data import *
import time

lua = LuaRuntime(unpack_returned_tuples=True)

def load_script(lua_code):
    drawer.Drawer(lua)

    lua.globals()["sleep"] = time.sleep

    try:
        lua.execute(lua_code)
    except LuaError as e:
        console_messages.append({
            "type": "error",
            "message": f"Error occurred when the page is initializing:\n{e}"
        })
        print(e)