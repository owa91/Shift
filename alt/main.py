from alt.lua import main as lua
from alt.drawer import main as drawer
from alt.data import *
import time
import threading
from PyQt6.QtWidgets import QApplication



def load(lua_code, app: QApplication, window, tab_index):
    global fps

    console_messages.append({
        "type": "Info",
        "message": "Initializing the page"
    })

    threading.Thread(target=lua.load_script, args=(lua_code, window), daemon=True).start()

    while True:
        start_time = time.time()

        surface = drawer.draw(window, tab_index)

        yield surface

        elapsed = time.time() - start_time
        fps = 1 / elapsed if elapsed > 0 else 0