import skia
from alt import data

def update_pos_y(canvas: skia.Canvas):
    max_scroll = max(0, getattr(data, "elements_lower_screen", 0))
    target_y = data.y_scroll_status.get("target_y", data.y_scroll_status.get("y", 0.0))
    target_y = max(-float(max_scroll), min(0.0, target_y))
    data.y_scroll_status["target_y"] = target_y
    cur_y = data.y_scroll_status.get("y", 0.0)
    diff = target_y - cur_y
    if abs(diff) > 0.5:
        cur_y += diff * 0.25
        data.y_scroll_status["y"] = cur_y
        data.y_scroll_status["scrolling"] = True
    else:
        data.y_scroll_status["y"] = target_y
        data.y_scroll_status["scrolling"] = False

    canvas.translate(0, data.y_scroll_status["y"])
