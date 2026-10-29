-- Тестовая страница: кнопка с событиями и "точка", следящая за мышью.
drawer.fill_background("#0B0C0F")

-- ───────────── Вспомогательное ─────────────
local function hex_to_rgb(hex)
    return tonumber(hex:sub(2, 3), 16), tonumber(hex:sub(4, 5), 16), tonumber(hex:sub(6, 7), 16)
end

-- Плавная смесь двух цветов: t = 0 -> a, t = 1 -> b
local function lerp_color(a, b, t)
    local ar, ag, ab = hex_to_rgb(a)
    local br, bg, bb = hex_to_rgb(b)
    return string.format("#%02X%02X%02X",
        math.floor(ar + (br - ar) * t + 0.5),
        math.floor(ag + (bg - ag) * t + 0.5),
        math.floor(ab + (bb - ab) * t + 0.5))
end

-- ───────────── Кнопка ─────────────
local BTN_W, BTN_H = 220, 56
local COLOR_IDLE     = "#6C8CFF"
local COLOR_HOVER    = "#FF8C42"
local COLOR_DISABLED = "#3A3F4B"

local btn = drawer.button(0, 0, "Нажми меня")
btn:set_size(BTN_W, BTN_H)
btn:set_font_style("Calibri", "Bold", 22)
btn:set_border_corner(14)
btn:set_color(COLOR_IDLE)
btn:set_text_color("#FFFFFF")
btn:set_text_align("center")

local hover_t = 0          -- 0..1, прогресс анимации наведения
local HOVER_SPEED = 0.12   -- шаг анимации за кадр
local hovered = false
local btn_disabled = false

-- События кнопки (выполняются в этом же потоке, внутри sleep)
btn:event("on_selected", function() hovered = true end)
btn:event("on_deselected", function() hovered = false end)
btn:event("on_left_click", function()
    if btn_disabled then return end
    btn_disabled = true
    hovered = false
    btn:set_text("Заблокировано")
    btn:set_color(COLOR_DISABLED)
    btn:set_text_color("#7A8090")
end)

-- ───────────── Точка (большой символ ●) ─────────────
local DOT_SIZE = 120
local DOT_Y_OFFSET = DOT_SIZE * 0.67   -- центр глифа ● по вертикали (Calibri)
local DOT_COLORS = { "#FFFFFF", "#FF3B30", "#34C759", "#007AFF", "#FFCC00", "#AF52DE" }
local dot_i = 1

local dot = drawer.draw_text(-1000, -1000, "●", DOT_SIZE, "Calibri", "Regular", DOT_COLORS[dot_i], false, 1.0, "center")

-- ───────────── Главный цикл ─────────────
local btn_x, btn_y = 0, 0
local was_down = false

while true do
    local screen_w, screen_h = drawer.get_size_screen()
    local mx, my, down, inside = drawer.get_mouse()

    -- кнопка по центру экрана
    local nx, ny = (screen_w - BTN_W) / 2, (screen_h - BTN_H) / 2
    if nx ~= btn_x or ny ~= btn_y then
        btn_x, btn_y = nx, ny
        btn:set_position(btn_x, btn_y)
    end

    -- плавное наведение (пока кнопка не заблокирована)
    if not btn_disabled then
        local target = hovered and 1 or 0
        if hover_t < target then hover_t = math.min(target, hover_t + HOVER_SPEED)
        elseif hover_t > target then hover_t = math.max(target, hover_t - HOVER_SPEED) end
        btn:set_color(lerp_color(COLOR_IDLE, COLOR_HOVER, hover_t))
    end

    -- точка следует за курсором, при нажатии меняет цвет
    local pressed = down and not was_down
    was_down = down

    local props = {}
    if inside then
        props.position = { x = mx, y = my - DOT_Y_OFFSET }
    end
    if pressed then
        dot_i = dot_i % #DOT_COLORS + 1
        props.color = DOT_COLORS[dot_i]
    end
    if props.position or props.color then
        drawer.redraw_text(dot, props)
    end

    sleep(0.016) -- ~60 FPS, заодно выполняет события кнопки
end
