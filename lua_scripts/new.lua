drawer.fill_background("#0B0C0F")

local W, H = 220, 56
local IDLE, HOVER, DISABLED = "#6C8CFF", "#FF8C42", "#3A3F4B"
local DOT_COLORS = { "#FFFFFF", "#FF3B30", "#34C759", "#007AFF", "#FFCC00", "#AF52DE" }

local function lerp(a, b, t)
    local out = "#"
    for i = 2, 6, 2 do
        local x, y = tonumber(a:sub(i, i + 1), 16), tonumber(b:sub(i, i + 1), 16)
        out = out .. string.format("%02X", math.floor(x + (y - x) * t + 0.5))
    end
    return out
end

local btn = drawer.button(0, 0, "Нажми меня")
btn:set_size(W, H)
btn:set_font_style("Calibri", "Bold", 22)
btn:set_border_corner(14)
btn:set_color(IDLE)
btn:set_text_color("#FFFFFF")

local hovered, disabled, t = false, false, 0

btn:event("on_selected", function() hovered = true end)
btn:event("on_deselected", function() hovered = false end)
btn:event("on_left_click", function()
    disabled, hovered = true, false
    btn:set_text("Заблокировано")
    btn:set_color(DISABLED)
    btn:set_text_color("#7A8090")
end)

local dot = drawer.draw_text(-1000, -1000, "●", 120, "Calibri", "Regular", DOT_COLORS[1], false, 1.0, "center")
local dot_i, was_down = 1, false

while true do
    local sw, sh = drawer.get_size_screen()
    local mx, my, down, inside = drawer.get_mouse()

    btn:set_position((sw - W) / 2, (sh - H) / 2)

    if not disabled then
        t = math.max(0, math.min(1, t + (hovered and 0.12 or -0.12)))
        btn:set_color(lerp(IDLE, HOVER, t))
    end

    local props = {}
    if inside then props.position = { x = mx, y = my - 80 } end
    if down and not was_down then
        dot_i = dot_i % #DOT_COLORS + 1
        props.color = DOT_COLORS[dot_i]
    end
    was_down = down
    drawer.redraw_text(dot, props)

    sleep(0.016)
end
