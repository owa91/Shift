from alt.lua import main as lua
from alt.drawer import main as drawer
from alt import data
import time
import threading
from PyQt6.QtWidgets import QApplication



def load(lua_code, app: QApplication, window, tab_index, ctx=None):
    page_ctx = ctx if ctx is not None else data
    page_ctx.console_messages.append({
        "type": "Info",
        "message": "Initializing the page"
    })

    threading.Thread(target=lua.load_script, args=(lua_code, window, page_ctx), daemon=True).start()

    while True:
        if getattr(page_ctx, "stop_event", None) is not None and page_ctx.stop_event.is_set():
            break

        start_time = time.time()

        cur_index = getattr(page_ctx, "tab_index", tab_index)
        if cur_index is None:
            cur_index = tab_index

        surface = drawer.draw(window, cur_index, page_ctx)

        yield surface

        elapsed = time.time() - start_time
        page_ctx.fps = 1 / elapsed if elapsed > 0 else 0