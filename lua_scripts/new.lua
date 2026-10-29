-- Анимация "DVD-плеер": логотип летает по экрану и отскакивает от краёв.
drawer.fill_background("#000000")

local text      = "DVD"
local font_size = 80
local colors    = { "#FF3B30", "#FF9500", "#FFCC00", "#34C759", "#00C7BE", "#007AFF", "#AF52DE", "#FF2D55" }

-- Примерный размер текста (измерения текста в API пока нет)
local text_w = #text * font_size * 0.65
local text_h = font_size * 1.2

local x, y   = 100, 100
local vx, vy = 3, 2.5          -- скорость в пикселях за кадр
local color_i = 1

local logo = drawer.draw_text(x, y, text, font_size, "Calibri", "Bold", colors[color_i], false, 1.0, "left")

local function next_color()
    color_i = color_i % #colors + 1
    drawer.redraw_text(logo, { color = colors[color_i] })
end

while true do
    local screen_w, screen_h = drawer.get_size_screen()

    x = x + vx
    y = y + vy

    local bounced = false
    if x <= 0 then
        x = 0
        vx = math.abs(vx)
        bounced = true
    elseif x + text_w >= screen_w then
        x = math.max(0, screen_w - text_w)
        vx = -math.abs(vx)
        bounced = true
    end

    if y <= 0 then
        y = 0
        vy = math.abs(vy)
        bounced = true
    elseif y + text_h >= screen_h then
        y = math.max(0, screen_h - text_h)
        vy = -math.abs(vy)
        bounced = true
    end

    if bounced then next_color() end

    drawer.redraw_text(logo, { position = { x = x, y = y } })

    sleep(0.016) -- ~60 FPS
end
