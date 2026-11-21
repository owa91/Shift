import threading
import mouse

console_messages = []
drawer_tasks = []
events = []
version = 1
y_scrolling = {"enabled": True, "show_status": True, "automatic": True, "ymax": None}
y_scroll_status = {"y": 0, "scrolling": False}
elements_lower_screen = 0
mouse_state = {"x": 0, "y": 0, "down": False, "inside": False}
fps = 0
network_requests = []
is_localfile = False


cachingservice_settings = {
    "http_allowed": False, # When parameter "http_allowed" is True, then CachingService allows http protocol
}

requests_settings = {
    "http_allowed": True, # When parameter "http_allowed" is True, then requests allows http protocol
}


class PageContext:
    def __init__(self, is_local=False, tab_index=None):
        self.console_messages = []
        self.drawer_tasks = []
        self.events = []
        self.version = version
        self.y_scrolling = {"enabled": True, "show_status": True, "automatic": True, "ymax": None}
        self.y_scroll_status = {"y": 0.0, "target_y": 0.0, "scrolling": False}
        self.elements_lower_screen = 0
        self.mouse_state = {"x": 0, "y": 0, "down": False, "inside": False, "wheel": 0.0}
        self.fps = 0
        self.network_requests = []
        self.is_localfile = is_local
        self.cachingservice_settings = cachingservice_settings
        self.requests_settings = requests_settings
        self.tab_index = tab_index
        self.active = True
        self.stop_event = threading.Event()
        self._mouse_hooks = []

    def add_mouse_hook(self, hook):
        if hook is not None:
            self._mouse_hooks.append(hook)

    def stop(self):
        self.active = False
        self.stop_event.set()
        for hook in self._mouse_hooks:
            try:
                mouse.unhook(hook)
            except Exception:
                pass
        self._mouse_hooks.clear()
        self.events.clear()