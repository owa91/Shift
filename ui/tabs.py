from ui import window as w
from alt import main as alt
from PyQt6.QtCore import QTimer
from pathlib import Path
import threading

window: w.ShiftWindow = None
tabs = []

def init(w):
    global window

    window = w
    window.tabClosed.connect(on_tab_closed)


def on_tab_closed(index):
    for i, t in enumerate(tabs):
        if t["index"] == index:
            if "timer" in t:
                t["timer"].stop()
            tabs.pop(i)
            break


def load(index, url: str, app):
    global window

    tab = None
    for stab in tabs:
        if index == stab["index"]:
            tab = stab
            break

    lua_code = ""
    if url.startswith("shift://"):
        folder = Path("lua_scripts")
        file = next(folder.rglob(url[len("shift://"):]+".lua"), None)
        if file is not None:
            lua_code = file.read_text(encoding="utf-8")
        else:
            lua_code = f'drawer.draw_text(0, 0, "Не удалось найти файл по пути {url}", 20, "Calibri", "Italic", "#FFFFFF", false, 1.0, "left")'

    frames = alt.load(lua_code, app, window, tab["index"])

    timer = QTimer(window)

    def render_next_frame():
        try:
            frame = next(frames)
            if frame is not None and frame is not True:
                window.set_image(frame, tab["index"])
        except StopIteration:
            timer.stop()
        except Exception as e:
            print("Error in render_next_frame:", e)

    timer.timeout.connect(render_next_frame)
    tab["timer"] = timer
    timer.start(16)


def new(url, show, app):
    global window

    index = window.add_tab(url)
    if show:
        window.set_current_tab(index)

    tabs.append({
        "index": index,
        "url": url,
        "index_url": 0,
        "last_urls": [url],
    })

    load(index, url, app)


