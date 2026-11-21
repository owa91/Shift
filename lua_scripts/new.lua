screen.set_scrolling_status(false, false, true)
drawer.fill_background("#090d14")

local bg = drawer.image(0, 0, "local://images/nature_bg.jpg")
bg.load()

local dim = drawer.rectangle(0, 0, 10, 10)
dim.set_color(6, 10, 16, 155)

local icon = drawer.image(0, 0, "local://images/icon.ico")
icon.load()

local brand = drawer.text(0, 0, "Shift", 64, "Calibri", "Bold", "#ffffff", "left")
brand.set_outline("#090d14", 2)

local hint = drawer.text(0, 0, "shift://weather   •   shift://ip   •   shift://rates   •   shift://chess   •   shift://demo", 14, "Calibri", "Regular", "#cbd5e1", "center")
hint.set_transparency(0.75)

local BG_RATIO = 16 / 9
local W, H = 0, 0

local function layout(w, h)
    W, H = w, h

    local win_ratio = w / math.max(1, h)
    local bw, bh, bx, by
    if win_ratio > BG_RATIO then
        bw = w
        bh = math.ceil(w / BG_RATIO)
        bx = 0
        by = math.floor((h - bh) / 2)
    else
        bh = h
        bw = math.ceil(h * BG_RATIO)
        bx = math.floor((w - bw) / 2)
        by = 0
    end
    bg.set_position(bx, by)
    bg.set_size(bw, bh)

    dim.set_position(0, 0)
    dim.set_size(w, h)

    local s = math.max(0.7, math.min(w / 1280, h / 760))
    local icon_size = math.floor(84 * s)
    local font_size = math.floor(68 * s)
    local gap = math.floor(20 * s)
    local text_w = math.floor(font_size * 2.1)
    local total_w = icon_size + gap + text_w

    local start_x = math.floor((w - total_w) / 2)
    local center_y = math.floor(h / 2)

    icon.set_position(start_x, math.floor(center_y - icon_size / 2))
    icon.set_size(icon_size, icon_size)

    brand.set_font_style("Calibri", "Bold", font_size)
    brand.set_position(start_x + icon_size + gap, math.floor(center_y - font_size * 0.52))

    hint.set_font_style("Calibri", "Regular", math.max(12, math.floor(14 * s)))
    hint.set_position(math.floor(w / 2), h - math.floor(42 * s))
end

local iw, ih = drawer.get_size_screen()
layout(iw, ih)

while true do
    local cw, ch = drawer.get_size_screen()
    if cw ~= W or ch ~= H then
        layout(cw, ch)
    end
    sleep(0.05)
end
