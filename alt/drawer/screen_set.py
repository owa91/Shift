import skia
from alt.data import *

def update_pos_y(canvas: skia.Canvas):
    target_y = y_scroll_status.get("target_y", y_scroll_status.get("y", 0.0))
    cur_y = y_scroll_status.get("y", 0.0)
    diff = target_y - cur_y
    if abs(diff) > 0.5:
        cur_y += diff * 0.25
        y_scroll_status["y"] = cur_y
    else:
        y_scroll_status["y"] = target_y

    canvas.translate(0, y_scroll_status["y"])
