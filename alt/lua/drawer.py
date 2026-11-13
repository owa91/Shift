from lupa.lua55 import LuaRuntime, LuaError
from alt.data import  *
from alt.caching import image as caching_image
from ui.window import ShiftWindow
import mouse
from pathlib import Path
import random

def _rgb(color, *rest):
    if rest:
        return (color, *rest[:2])
    if isinstance(color, str) and color.startswith("#"):
        h = color.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    if hasattr(color, "values"):
        return list(color.values())
    return color

class button:
    def __init__(self, x=0, y=0, text="Hello world!"):
        self.x = x
        self.y = y
        self.text = text
        self.width = 150
        self.height = 50
        self.font = "Calibri"
        self.style = "Regular"
        self.size = 20
        self.border_corner = 10
        self.text_align = "center"
        self.index = len(drawer_tasks)

        self._listeners = {}
        self._hover = False

        mouse.hook(self.on_selected)
        mouse.on_click(self.on_left_click)
        mouse.on_right_click(self.on_right_click)

        drawer_tasks.append({
            "type": "button",
            "position": {"x": x, "y": y},
            "text": self.text,
            "color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "width": self.width,
            "height": self.height,
            "font": self.font,
            "font_style": self.style,
            "font_size": self.size,
            "border_corner": self.border_corner,
            "text_align": self.text_align,
        })

    def event(self, event_name, callback):
        self._listeners.setdefault(event_name, []).append(callback)

    def trigger(self, event_name, *args):
        for callback in list(self._listeners.get(event_name, [])):
            events.append((callback, args))

    def _over(self):
        if self.x < -500 or self.y < -500:
            return False
        m = mouse_state
        if not m["inside"]:
            return False
        scroll_y = y_scroll_status.get("y", 0)
        return bool(self.x <= m["x"] < self.x + self.width
                    and (self.y + scroll_y) <= m["y"] < (self.y + scroll_y) + self.height)

    def set_color(self, color="#ffffff", *rest):
        drawer_tasks[self.index]["color"] = _rgb(color, *rest)

    def set_text_color(self, color="#ffffff", *rest):
        drawer_tasks[self.index]["text_color"] = _rgb(color, *rest)

    def set_position(self, x=0, y=0):
        self.x, self.y = x, y
        drawer_tasks[self.index]["position"] = {"x": x, "y": y}

    def set_size(self, width, height):
        if width is None or height is None:
            console_messages.append({
                "type": "error",
                "message": "width and height cannot be None",
            })
            return

        self.width, self.height = width, height
        drawer_tasks[self.index]["width"] = width
        drawer_tasks[self.index]["height"] = height

    def set_font_style(self, font, style, size):
        if font is None or style is None or size is None:
            console_messages.append({
                "type": "error",
                "message": "font, style, size cannot be None",
            })
            return

        self.font, self.style, self.size = font, style, size
        drawer_tasks[self.index]["font"] = font
        drawer_tasks[self.index]["font_style"] = style
        drawer_tasks[self.index]["font_size"] = size

    def auto_font_size(self, margin):
        width, height = self.width, self.height

        font_size = ((width+height)/2)-margin

        text_max_size = 0

        for line in self.text.splitlines():
            if len(line) > text_max_size:
                text_max_size = len(line)

        font_size = font_size-(width-text_max_size)

        self.size = font_size

        drawer_tasks[self.index]["font_size"] = font_size

    def set_text(self, text):
        if text is None:
            console_messages.append({
                "type": "error",
                "message": "text cannot be None",
            })
            return

        self.text = text
        drawer_tasks[self.index]["text"] = self.text

    def set_border_corner(self, val):
        if val is None:
            console_messages.append({
                "type": "error",
                "message": "border corner cannot be None",
            })
            return

        self.border_corner = val
        drawer_tasks[self.index]["border_corner"] = self.border_corner

    def set_text_align(self, val):
        if val is None:
            console_messages.append({
                "type": "error",
                "message": "text align cannot be None",
            })
            return

        self.text_align = val
        drawer_tasks[self.index]["text_align"] = self.text_align

    def on_selected(self, _event):
        over = self._over()
        if over != self._hover:
            self._hover = over
            self.trigger("on_selected" if over else "on_deselected")

    def on_left_click(self):
        if self._over():
            self.trigger("on_left_click")

    def on_right_click(self):
        if self._over():
            self.trigger("on_right_click")


class text:
    def __init__(self, x=0, y=0, text="", font_size=14, font="Calibri", font_style="Regular", color="#ffffff", align="left"):
        self.task = {
            "index": -1,
            "type": "text",
            "position": {"x": x, "y": y},
            "text": text,
            "font": {"font": font, "size": font_size, "style": font_style},
            "outline": None,
            "transparency": 1,
            "align": align,
            "color": _rgb(color),
        }
        drawer_tasks.append(self.task)

    def set_text(self, value):
        self.task["text"] = value

    def set_color(self, color="#ffffff", *rest):
        self.task["color"] = _rgb(color, *rest)

    def set_position(self, x=0, y=0):
        self.task["position"] = {"x": x, "y": y}

    def set_font_style(self, font, style, size):
        self.task["font"] = {"font": font, "size": size, "style": style}

    def set_align(self, align):
        self.task["align"] = align

    def set_transparency(self, value):
        self.task["transparency"] = value

    def set_outline(self, color, weight):
        self.task["outline"] = {"color": _rgb(color), "weight": weight}

    def remove(self):
        if self.task in drawer_tasks:
            drawer_tasks.remove(self.task)

class image:
    def __init__(self, x=0, y=0, source=""):
        self.x = x
        self.y = y
        self.source = source
        self.width, self.height = 100, 100
        self.index = len(drawer_tasks)
        self.mapping = 1
        self.loaded = False
        self.bytes = None
        self.random_index = random.randint(1, 1000000)

        with Path("images/not-loaded.jpg").open("rb") as f:
            self.bytes = f.read()


        drawer_tasks.append({
            "type": "image",
            "x": self.x,
            "y": self.y,
            "loaded": self.loaded,
            "bytes": self.bytes,
            "width": self.width,
            "height": self.height,
            "mapping": self.mapping,
            "random_index": self.random_index
        })

    def set_position(self, x=0, y=0):
        self.x = x
        self.y = y

        drawer_tasks[self.index]["x"], drawer_tasks[self.index]["y"] = self.x, self.y

    def set_size(self, width=100, height=100):
        self.width, self.height = width, height
        drawer_tasks[self.index]["width"], drawer_tasks[self.index]["height"] = width, height

    def type_mapping(self, val=0):
        """
        0 - stretch
        1 - scale
        """

        if val < 0 or val > 1:
            console_messages.append({
                "type": "error",
                "message": "value must be between 0 and 1",
            })
            return

        self.mapping = val
        drawer_tasks[self.index]["mapping"] = val

    def change_source(self, source=""):
        self.source = source
        drawer_tasks[self.index]["source"] = source

    def load(self):
        with Path("images/loading.jpg").open("rb") as f:
            self.bytes = f.read()
            self.random_index = random.randint(1, 1000000)
            drawer_tasks[self.index]["random_index"] = self.random_index
            drawer_tasks[self.index]["bytes"] = self.bytes

        status, val = 0, None

        try:
            status, val = caching_image.load_not_animated_and_cache(self.source, is_localfile, self.random_index)
        except Exception as e:
            print(e)
            val = e

        if status == 0:
            print(val)
            console_messages.append({
                "type": "error",
                "message": f"cannot load image. Cause: {val}",
            })

            with Path("images/error-image.jpg").open("rb") as f:
                self.bytes = f.read()
                self.random_index = random.randint(1, 1000000)
                drawer_tasks[self.index]["random_index"] = self.random_index
                drawer_tasks[self.index]["bytes"] = self.bytes
            return

        self.loaded, self.bytes = True, val
        self.random_index = random.randint(1, 1000000)
        drawer_tasks[self.index]["random_index"] = self.random_index
        drawer_tasks[self.index]["bytes"] = self.bytes
        drawer_tasks[self.index]["loaded"] = self.loaded

class rectangle:
    def __init__(self, x=0, y=0, height=100, width=100):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.corners_x = 0
        self.corners_y = 0
        self.color = _rgb("#ffffff")

        self.index = len(drawer_tasks)

        drawer_tasks.append({
            "type": "rectangle",
            "x": self.x,
            "y": self.y,
            "height": self.height,
            "width": self.width,
            "corners_x": self.corners_x,
            "corners_y": self.corners_y,
            "color": self.color
        })

    def set_position(self, x=0, y=0):
        self.x = x
        self.y = y

        drawer_tasks[self.index]["x"], drawer_tasks[self.index]["y"] = self.x, self.y

    def set_size(self, width=100, height=100):
        self.width, self.height = width, height
        drawer_tasks[self.index]["width"], drawer_tasks[self.index]["height"] = width, height

    def set_corners(self, rx=0, ry=0):
        self.corners_x = rx
        self.corners_y = ry

        drawer_tasks[self.index]["self.corners_x"], drawer_tasks[self.index]["self.corners_y"] = self.corners_x, self.corners_y

    def set_color(self, color="#ffffff", *rest):
        drawer_tasks[self.index]["color"] = _rgb(color, *rest)

def run_events():
    while events:
        callback, args = events.pop(0)
        try:
            callback(*args)
        except Exception as e:
            console_messages.append({
                "type": "error",
                "message": f"Error in event handler: {e}"
            })


class Drawer:
    def __init__(self, lua, window: ShiftWindow):
        self.lua: LuaRuntime = lua
        self.texts = 0
        self.window = window

        lua.globals()['drawer'] = {
            "button": button,
            "text": text,
            "image": image,
            "rectangle": rectangle,
            "fill_background": self.fill_background,
            "get_size_screen": self.get_size_screen,
            "get_mouse": self.get_mouse,
            "get_wheel": self.get_wheel,
        }

    def get_wheel(self):
        # wheel notches accumulated since the last call (positive = away from user)
        v = mouse_state.get("wheel", 0.0)
        mouse_state["wheel"] = 0.0
        return v

    def get_mouse(self):
        m = mouse_state
        return m["x"], m["y"], m["down"], m["inside"]

    def get_size_screen(self):
        try:
            size = self.window.get_canvas_size()
            if not size or size.width is None or size.height is None:
                return 1280, 700
            return size.width, size.height
        except Exception:
            return 1280, 700

    def fill_background(self, color):
        if isinstance(color, str) and color.startswith("#"):
            h = color.lstrip("#")
            color = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        elif hasattr(color, "values"):
            color = list(color.values())

        found_task = False
        for task in drawer_tasks:
            if task["type"] == "fill_background":
                task["color"] = color
                found_task = True
                break

        if not found_task:
            drawer_tasks.append({
                "type": "fill_background",
                "color": color
            })

        return True