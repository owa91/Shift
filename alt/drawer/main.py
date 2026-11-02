import skia
import time
from alt.data import *
import alt.data as data
from ui import window as w
from alt.drawer import cache, screen_set

style_map = {
    "Bold": skia.FontStyle.Bold(),
    "Italic": skia.FontStyle.Italic(),
    "BoldItalic": skia.FontStyle.BoldItalic(),
}


def draw_text(canvas: skia.Canvas, text, x, y, font, color=(255, 255, 255), alpha=1.0, outline=None, outline_w=0, align="left"):
    width = font.measureText(text)
    if align == "center":
        x -= width / 2
    elif align == "right":
        x -= width

    alpha_val = max(0.0, min(1.0, float(alpha)))
    use_layer = (alpha_val < 0.999) and outline and (outline_w > 0)

    if use_layer:
        metrics = font.getMetrics()
        pad = outline_w * 2 + 4
        rect = skia.Rect(x - pad, y + metrics.fAscent - pad, x + width + pad, y + metrics.fDescent + pad)
        canvas.saveLayerAlpha(rect, int(alpha_val * 255))

    if outline and outline_w > 0:
        stroke_color = skia.Color(*outline) if isinstance(outline, (tuple, list)) else skia.ColorBLACK
        stroke = skia.Paint(Color=stroke_color, AntiAlias=True)
        stroke.setStyle(skia.Paint.kStroke_Style)
        stroke.setStrokeWidth(outline_w * 2)
        stroke.setStrokeJoin(skia.Paint.kRound_Join)
        if not use_layer and alpha_val < 0.999:
            stroke.setAlphaf(alpha_val)
        canvas.drawString(text, x, y, font, stroke)

    if isinstance(color, (tuple, list)):
        fill_color = skia.Color(*color)
    elif isinstance(color, str) and color.startswith("#"):
        h = color.lstrip("#")
        fill_color = skia.Color(*(int(h[i:i + 2], 16) for i in (0, 2, 4)))
    else:
        fill_color = skia.ColorWHITE

    fill = skia.Paint(Color=fill_color, AntiAlias=True)
    if not use_layer and alpha_val < 0.999:
        fill.setAlphaf(alpha_val)
    canvas.drawString(text, x, y, font, fill)

    if use_layer:
        canvas.restore()

    global elements_lower_screen

    if y > canvas.imageInfo().height():
        if y+100 > elements_lower_screen:
            elements_lower_screen = y+100

def draw_button(canvas: skia.Canvas, x, y, width, height, corners, color, text, font, font_style, font_size, text_color, text_align="center"):
    rect = skia.Rect.MakeXYWH(x, y, width, height)
    paint = skia.Paint(
        AntiAlias=True,
        Color=skia.Color(*color)
    )

    canvas.drawRoundRect(rect, corners, corners, paint)

    style = style_map.get(font_style, skia.FontStyle.Normal())
    font = cache.get_skia_font(font, style, font_size)

    text_paint = skia.Paint(
        AntiAlias=True,
        Color=skia.Color(*text_color)
    )

    width_t = font.measureText(text)
    text_x = x
    text_y = rect.centerY() + (font.getSize() / 3)
    if text_align == "center":
        text_x = rect.centerX() - (width_t / 2)
    elif text_align == "right":
        text_x = rect.right() - width_t
    elif text_align == "left":
        text_x = x + 10

    canvas.drawString(text, text_x, text_y, font, text_paint)

    global elements_lower_screen

    if y > canvas.imageInfo().height():
        if y + width + 100 > elements_lower_screen:
            elements_lower_screen = y + width + 100


def draw_not_animated_image(canvas: skia.Canvas, x, y, width, height, bytes_data, random_id):
    image =  None
    if random_id in cache.cache["images"]:
        image = cache.cache["images"][random_id]
    else:
        data = skia.Data.MakeWithoutCopy(bytes_data)
        image = skia.Image.MakeFromEncoded(data)

        cache.cache["images"][random_id] = image

    sampling = skia.SamplingOptions(skia.FilterMode.kLinear)

    dest_rect = skia.Rect(float(x), float(y), float(x + width), float(y + height))

    canvas.drawImageRect(image, dest_rect, sampling, None)

    global elements_lower_screen

    if y > canvas.imageInfo().height():
        if y + width + 100 > elements_lower_screen:
            elements_lower_screen = y + width + 100


def draw(window: w.ShiftWindow, tab_index):
    if window is None:
        return None

    canvas = window.get_canvas(tab_index)
    if canvas is None:
        return None

    color = None

    for task in drawer_tasks:
        if task["type"] == "fill_background":
            color = task["color"]
            break

    if color is None:
        canvas.clear(skia.Color(11, 12, 15, 255))
    elif isinstance(color, (tuple, list)):
        canvas.clear(skia.Color(*color))
    elif isinstance(color, str) and color.startswith("#"):
        h = color.lstrip("#")
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        canvas.clear(skia.Color(*rgb))
    else:
        canvas.clear(skia.Color(11, 12, 15, 255))

    canvas_h = canvas.getLocalClipBounds().height()
    max_y = 0
    for task in drawer_tasks:
        pos = task.get("position")
        if pos:
            ty = pos.get("y", 0)
            th = task.get("height", 0)
            if 0 <= ty < 10000 and ty + th > max_y:
                max_y = ty + th
        elif "y" in task:
            ty = task.get("y", 0)
            th = task.get("height", 0)
            if 0 <= ty < 10000 and ty + th > max_y:
                max_y = ty + th

    if max_y > canvas_h:
        data.elements_lower_screen = int(max_y - canvas_h + 80)
    else:
        data.elements_lower_screen = 0

    screen_set.update_pos_y(canvas)
    cur_scroll_y = data.y_scroll_status.get("y", 0.0)

    for task in drawer_tasks:
        pos = task.get("position")
        if pos:
            ty = pos.get("y", 0)
            th = task.get("height", 150)
        else:
            ty = task.get("y", 0)
            th = task.get("height", 150)

        # Skip off-screen elements (culling)
        if ty < -500:
            continue
        if ty + cur_scroll_y + th < -150 or ty + cur_scroll_y > canvas_h + 150:
            continue
        if task["type"] == "text":
            try:
                style = style_map.get(task["font"]["style"], skia.FontStyle.Normal())
                font = cache.get_skia_font(task["font"]["font"], style, task["font"]["size"])

                outline = task.get("outline") or {}
                draw_text(
                    canvas,
                    task["text"],
                    task["position"]["x"],
                    task["position"]["y"] - font.getMetrics().fAscent,
                    font,
                    task["color"],
                    task["transparency"],
                    outline.get("color"),
                    outline.get("weight", 0),
                    task.get("align", "left"),
                )
            except Exception as e:
                console_messages.append({
                    "type": "warn",
                    "message": e,
                })
        elif task["type"] == "button":
            try:
                draw_button(
                    canvas,
                    task["position"]["x"],
                    task["position"]["y"],
                    task["width"],
                    task["height"],
                    task["border_corner"],
                    task["color"],
                    task["text"],
                    task["font"],
                    task["font_style"],
                    task["font_size"],
                    task["text_color"],
                    task["text_align"],
                )
            except Exception as e:
                console_messages.append({
                    "type": "warn",
                    "message": e,
                })
        elif task["type"] == "image":
            try:
                draw_not_animated_image(
                    canvas,
                    task["x"],
                    task["y"],
                    task["width"],
                    task["height"],
                    task["bytes"],
                    task["random_index"]
                )
            except Exception as e:
                console_messages.append({
                    "type": "warn",
                    "message": e,
                })
                print(e)

    window.render_done(tab_index)
    return True
