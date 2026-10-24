from ui import window as w
from ui import tabs

window : w.ShiftWindow = None

def start(app):
    global window

    window = w.create_window()

    tabs.init(window)

    tabs.new("shift://new", True, app)

    window.show()