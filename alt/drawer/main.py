import skia
import time
from alt.data import *
from ui import window as w
from alt.drawer import cache

style_map = {
    "Bold": skia.FontStyle.Bold(),
    "Italic": skia.FontStyle.Italic(),
    "BoldItalic": skia.FontStyle.BoldItalic(),
}


def draw_text(canvas, text, x, y, font, color=(255, 255, 255), alpha=1.0, outline=None, outline_w=0, align="left"):
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

    for task in drawer_tasks:
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

    window.render_done(tab_index)
    return True
