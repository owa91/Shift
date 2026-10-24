from lupa import LuaRuntime, LuaError
from alt.data import  *

class Drawer:
    def __init__(self, lua):
        self.lua: LuaRuntime = lua
        self.texts = 0

        lua.globals()['drawer'] = {
            "draw_text": self.draw_text,
            "redraw_text": self.redraw_text,
            "draw_button": self.draw_button,
            "paste_image": self.paste_image,
            "fill_background": self.fill_background,
            "get_size_screen": self.get_size_screen,
        }

    def get_size_screen(self):
        return

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

    def draw_button(self):
        pass

    def paste_image(self):
        pass