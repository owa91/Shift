import threading
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from ui import window as w
from ui import loader
from alt import main as alt
from alt import data as alt_data

window: w.ShiftWindow = None
_app = None
tabs = []
_creating_internal = False
_bridge = None


class _FetchBridge(QObject):
    pageFetched = pyqtSignal(object, int, dict)


def _get_tab(index):
    for t in tabs:
        if t["index"] == index:
            return t
    return None


def _sync_ui_for_active_tab():
    if window is None:
        return
    cur = window.current_tab()
    active_tab = None
    for t in tabs:
        is_active = t["index"] == cur
        if t.get("ctx") is not None:
            t["ctx"].active = is_active
        if is_active:
            active_tab = t

    if active_tab is not None:
        window.set_url(active_tab["url"], force=True)
        can_back = active_tab["index_url"] > 0
        can_forward = active_tab["index_url"] < len(active_tab["last_urls"]) - 1
        window.set_nav_enabled(can_back, can_forward)
        window.set_loading(bool(active_tab.get("loading", False)))
    else:
        window.set_nav_enabled(False, False)


def _stop_tab_runtime(tab):
    timer = tab.get("timer")
    if timer is not None:
        timer.stop()
        tab["timer"] = None
    ctx = tab.get("ctx")
    if ctx is not None:
        ctx.stop()
        tab["ctx"] = None


def init(win, app=None):
    global window, _app, _bridge

    window = win
    _app = app
    _bridge = _FetchBridge(window)
    _bridge.pageFetched.connect(_on_page_fetched)

    window.tabCreated.connect(on_tab_created)
    window.tabClosed.connect(on_tab_closed)
    window.tabChanged.connect(on_tab_changed)
    window.navigateRequested.connect(on_navigate)
    window.backRequested.connect(on_back)
    window.forwardRequested.connect(on_forward)
    window.reloadRequested.connect(on_reload)


def on_tab_created(index):
    if _creating_internal:
        return
    if _get_tab(index) is not None:
        return
    url = "shift://new"
    tabs.append({
        "index": index,
        "url": url,
        "index_url": 0,
        "last_urls": [url],
        "load_id": 0,
        "loading": False,
        "ctx": None,
        "timer": None,
    })
    _sync_ui_for_active_tab()
    load(index, url, _app)


def on_tab_closed(index):
    for i, t in enumerate(tabs):
        if t["index"] == index:
            _stop_tab_runtime(t)
            tabs.pop(i)
            break
    for t in tabs:
        if t["index"] > index:
            t["index"] -= 1
            if t.get("ctx") is not None:
                t["ctx"].tab_index = t["index"]
    _sync_ui_for_active_tab()


def on_tab_changed(index):
    _sync_ui_for_active_tab()


def on_navigate(raw_url: str):
    if window is None:
        return
    tab = _get_tab(window.current_tab())
    if tab is None:
        return
    url = loader.normalize_url(raw_url)
    tab["last_urls"] = tab["last_urls"][:tab["index_url"] + 1]
    if not tab["last_urls"] or tab["last_urls"][-1] != url:
        tab["last_urls"].append(url)
        tab["index_url"] = len(tab["last_urls"]) - 1
    tab["url"] = url
    _sync_ui_for_active_tab()
    load(tab["index"], url, _app)


def on_back():
    if window is None:
        return
    tab = _get_tab(window.current_tab())
    if tab is None or tab["index_url"] <= 0:
        return
    tab["index_url"] -= 1
    tab["url"] = tab["last_urls"][tab["index_url"]]
    _sync_ui_for_active_tab()
    load(tab["index"], tab["url"], _app)


def on_forward():
    if window is None:
        return
    tab = _get_tab(window.current_tab())
    if tab is None or tab["index_url"] >= len(tab["last_urls"]) - 1:
        return
    tab["index_url"] += 1
    tab["url"] = tab["last_urls"][tab["index_url"]]
    _sync_ui_for_active_tab()
    load(tab["index"], tab["url"], _app)


def on_reload():
    if window is None:
        return
    tab = _get_tab(window.current_tab())
    if tab is None:
        return
    load(tab["index"], tab["url"], _app)


def _on_page_fetched(tab, load_id, result):
    if tab not in tabs or tab["load_id"] != load_id:
        return

    tab["loading"] = False
    final_url = result.get("final_url", tab["url"])
    tab["url"] = final_url
    if 0 <= tab["index_url"] < len(tab["last_urls"]):
        tab["last_urls"][tab["index_url"]] = final_url

    window.set_tab_title(tab["index"], result.get("title", loader.tab_title_for_url(final_url)))

    if window.current_tab() == tab["index"]:
        window.set_url(final_url, force=True)
        window.set_loading(False)

    _stop_tab_runtime(tab)

    ctx = alt_data.PageContext(is_local=result.get("is_localfile", False), tab_index=tab["index"])
    ctx.active = (window.current_tab() == tab["index"])
    vp = window.viewport(tab["index"])
    if vp is not None and hasattr(vp, "set_page_context"):
        vp.set_page_context(ctx)
    tab["ctx"] = ctx

    frames = alt.load(result.get("lua_code", ""), _app, window, tab["index"], ctx=ctx)

    timer = QTimer(window)

    def render_next_frame():
        if tab not in tabs or tab.get("ctx") is not ctx:
            timer.stop()
            return
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


def load(index, url: str, app=None):
    global _app
    if app is not None:
        _app = app

    tab = _get_tab(index)
    if tab is None:
        return

    norm_url = loader.normalize_url(url)
    tab["url"] = norm_url
    _stop_tab_runtime(tab)

    tab["load_id"] = tab.get("load_id", 0) + 1
    my_load_id = tab["load_id"]
    tab["loading"] = True

    window.set_tab_title(tab["index"], loader.tab_title_for_url(norm_url))
    if window.current_tab() == tab["index"]:
        window.set_url(norm_url, force=True)
        window.set_loading(True)

    def worker():
        result = loader.fetch_page(norm_url)
        if _bridge is not None:
            _bridge.pageFetched.emit(tab, my_load_id, result)

    threading.Thread(target=worker, daemon=True).start()


def new(url, show, app):
    global window, _app, _creating_internal
    if app is not None:
        _app = app

    norm_url = loader.normalize_url(url)
    title = loader.tab_title_for_url(norm_url)

    _creating_internal = True
    try:
        index = window.add_tab(title, select=show)
    finally:
        _creating_internal = False

    tabs.append({
        "index": index,
        "url": norm_url,
        "index_url": 0,
        "last_urls": [norm_url],
        "load_id": 0,
        "loading": False,
        "ctx": None,
        "timer": None,
    })

    if show:
        window.set_current_tab(index)
    _sync_ui_for_active_tab()
    load(index, norm_url, app)
