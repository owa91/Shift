from lupa import LuaRuntime, LuaError
from alt.data import  *
from ui.window import ShiftWindow
import mouse

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

        # Хуки библиотеки mouse вызываются из её потока: сами они Lua не трогают,
        # а только кладут события в очередь (см. trigger / run_events).
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
        """Подписка на событие: on_selected, on_deselected, on_left_click, on_right_click."""
        self._listeners.setdefault(event_name, []).append(callback)

    def trigger(self, event_name, *args):
        """Вызывается из потока хука мыши: не запускает Lua сразу (дедлок с циклом скрипта),
        а ставит обработчики в очередь. Выполняет их run_events() из Lua-потока (внутри sleep)."""
        for callback in list(self._listeners.get(event_name, [])):
            events.append((callback, args))

    def _over(self):
        """Курсор над кнопкой? Координаты берём из Qt (относительно страницы), а не экранные."""
        m = mouse_state
        return bool(m["inside"]
                    and self.x <= m["x"] < self.x + self.width
                    and self.y <= m["y"] < self.y + self.height)

    def set_color(self, color="#ffffff"):
        if isinstance(color, str) and color.startswith("#"):
            h = color.lstrip("#")
            color = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        elif hasattr(color, "values"):
            color = list(color.values())


        drawer_tasks[self.index]["color"] = color

    def set_text_color(self, color="#ffffff"):
        if isinstance(color, str) and color.startswith("#"):
            h = color.lstrip("#")
            color = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        elif hasattr(color, "values"):
            color = list(color.values())

        drawer_tasks[self.index]["text_color"] = color

    def set_position(self, x, y):
        if x is None:
            x = self.x

        if y is None:
            y = self.y

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
        """Хук любого события мыши: сообщает о входе курсора на кнопку и выходе с неё."""
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


def run_events():
    """Выполняет накопленные события (обработчики из Lua). Вызывать только из Lua-потока."""
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
            "draw_text": self.draw_text,
            "button": button,
            "redraw_text": self.redraw_text,
            "paste_image": self.paste_image,
            "fill_background": self.fill_background,
            "get_size_screen": self.get_size_screen,
            "get_mouse": self.get_mouse,
        }

    def get_mouse(self):
        m = mouse_state
        return m["x"], m["y"], m["down"], m["inside"]

    def get_size_screen(self):
        size = self.window.get_canvas_size()

        return size.width, size.height

    def redraw_text(self, index, to_change):
        task = None
        to_change = dict(to_change)

        for ftask in drawer_tasks:
            if ftask["type"] == "text" and ftask["index"] == index:
                task = ftask

        if task is None:
            console_messages.append({
                "type": "error",
                "message": f"The text with index {index} doesn't exist"
            })
            return

        for name, value in to_change.items():
            if task.get(name) is None:
                console_messages.append({
                    "type": "warn",
                    "message": f"Cannot find a value with name {name} in the text with index {index}"
                })
                continue

            if name == "color":
                if isinstance(value, str) and value.startswith("#"):
                    h = value.lstrip("#")
                    value = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
                elif hasattr(value, "values"):
                    value = list(value.values())
            elif name == "position" and hasattr(value, "keys"):
                value = {"x": value["x"], "y": value["y"]}

            task[name] = value

        return self.texts

    def draw_text(self, x, y, text, font_size=14, font="Calibri", font_style="Regular", color="#ffffff", outline=False, transparency=1, align="left"):
        try:
            outline = dict(outline) if outline and not isinstance(outline, bool) else None
            if isinstance(color, str) and color.startswith("#"):
                h = color.lstrip("#")
                color = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            elif hasattr(color, "values"):
                color = list(color.values())

            self.texts += 1

            drawer_tasks.append({
                "index": self.texts,
                "type": "text",
                "position": {"x": x, "y": y},
                "text": text,
                "font": {"font": font, "size": font_size, "style": font_style},
                "outline": outline,
                "transparency": transparency,
                "align": align,
                "color": color
            })

            return self.texts
        except Exception as e:
            console_messages.append({
                "type": "error",
                "message": e
            })

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

    def paste_image(self):
        pass