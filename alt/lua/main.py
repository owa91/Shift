from lupa.lua54 import LuaRuntime, LuaError
from alt.lua import drawer, cursor, screen, n_requests
from alt import data
from ui.window import ShiftWindow
import time
import traceback


class _PageStopped(Exception):
    pass


def load_script(lua_code, window: ShiftWindow, ctx=None):
    page_ctx = ctx if ctx is not None else data
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute('collectgarbage("generational")')

    drawer.Drawer(lua, window, page_ctx)
    cursor.Cursor(lua, window, page_ctx)
    screen.Screen(lua, window, page_ctx)
    n_requests.Requests(lua, window, page_ctx)

    def sleep(seconds):
        stop_event = getattr(page_ctx, "stop_event", None)
        if stop_event is not None:
            if stop_event.wait(timeout=max(0.0, float(seconds))):
                raise _PageStopped()
        else:
            time.sleep(seconds)
        drawer.run_events(page_ctx)

    lua.globals()["sleep"] = sleep

    try:
        lua.execute(lua_code)
    except _PageStopped:
        return
    except LuaError as e:
        if getattr(page_ctx, "stop_event", None) is not None and page_ctx.stop_event.is_set():
            return
        page_ctx.console_messages.append({
            "type": "error",
            "message": f"Error occurred when the page is initializing:\n{e}"
        })
        traceback.print_exc()