index_t = drawer.draw_text(0, 0, "QPMA LOX", 300, "Bastion", "Bold", "#FFFFFF", false, 1.0, "left")
index_u = drawer.draw_text(0, 400, "И урод", 100, "Calibri", "Italic", "#FFFFFF", false, 1.0, "left")


-- Вспомогательная функция для перевода HSL (цветового тона) в HEX
local function hsl_to_hex(h, s, l)
    local r, g, b
    if s == 0 then
        r, g, b = l, l, l
    else
        local function hue_to_rgb(p, q, t)
            if t < 0 then t = t + 1 end
            if t > 1 then t = t - 1 end
            if t < 1/6 then return p + (q - p) * 6 * t end
            if t < 1/2 then return q end
            if t < 2/3 then return p + (q - p) * (2/3 - t) * 6 end
            return p
        end
        local q = l < 0.5 and l * (1 + s) or l + s - l * s
        local p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    end
    return string.format("#%02X%02X%02X", math.floor(r * 255), math.floor(g * 255), math.floor(b * 255))
end

-- Основной цикл анимации
local hue = 0
while true do
    -- Получаем текущий радужный цвет (насыщенность 100%, яркость 50%)
    local rainbow_color = hsl_to_hex(hue, 1.0, 0.5)
    
    -- Перерисовываем текст
    drawer.redraw_text(index_t, {color = rainbow_color})
    
    -- Шаг изменения цвета (чем меньше число, тем плавнее перелив)
    hue = hue + 0.01
    if hue > 1 then hue = 0 end
    
    -- Маленькая задержка для плавности (0.02–0.05 сек = ~30-50 FPS)
    sleep(0.03) 
end

