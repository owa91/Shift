import skia
from alt import data

def update_pos_y(canvas: skia.Canvas, ctx=None):
    page_ctx = ctx if ctx is not None else data
    max_scroll = max(0, getattr(page_ctx, "elements_lower_screen", 0))
    target_y = page_ctx.y_scroll_status.get("target_y", page_ctx.y_scroll_status.get("y", 0.0))
    target_y = max(-float(max_scroll), min(0.0, target_y))
    page_ctx.y_scroll_status["target_y"] = target_y
    cur_y = page_ctx.y_scroll_status.get("y", 0.0)
    diff = target_y - cur_y
    if abs(diff) > 0.5:
        cur_y += diff * 0.25
        page_ctx.y_scroll_status["y"] = cur_y
        page_ctx.y_scroll_status["scrolling"] = True
    else:
        page_ctx.y_scroll_status["y"] = target_y
        page_ctx.y_scroll_status["scrolling"] = False

    canvas.translate(0, page_ctx.y_scroll_status["y"])
