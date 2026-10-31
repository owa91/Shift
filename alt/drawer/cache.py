import skia

cache = {
    "fonts": {},
    "skia_fonts": {},
    "images": {}
}

def get_font(name, style):
    key = f"{name}_{style}"
    if key in cache["fonts"]:
        return cache["fonts"][key]
    tf = skia.Typeface.MakeFromName(name, style)
    cache["fonts"][key] = tf
    return tf

def get_skia_font(name, style, size):
    key = (name, str(style), float(size))
    if key in cache["skia_fonts"]:
        return cache["skia_fonts"][key]
    tf = get_font(name, style)
    f = skia.Font(tf, size)
    cache["skia_fonts"][key] = f
    return f
