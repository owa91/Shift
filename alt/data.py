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