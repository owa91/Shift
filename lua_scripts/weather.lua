screen.set_scrolling_status(true, true, true)
drawer.fill_background("#0b0f19")

local WMO = {
    [0] = "Ясно",
    [1] = "Преимущественно ясно",
    [2] = "Переменная облачность",
    [3] = "Пасмурно",
    [45] = "Туман",
    [48] = "Изморозь",
    [51] = "Лёгкая морось",
    [53] = "Умеренная морось",
    [55] = "Сильная морось",
    [61] = "Небольшой дождь",
    [63] = "Умеренный дождь",
    [65] = "Сильный дождь",
    [66] = "Ледяной дождь",
    [67] = "Сильный ледяной дождь",
    [71] = "Небольшой снег",
    [73] = "Умеренный снег",
    [75] = "Сильный снег",
    [77] = "Снежные зёрна",
    [80] = "Ливень",
    [81] = "Сильный ливень",
    [82] = "Очень сильный ливень",
    [85] = "Снегопад",
    [86] = "Сильный снегопад",
    [95] = "Гроза",
    [96] = "Гроза с градом",
    [99] = "Сильная гроза с градом",
}

local function wmo_text(code)
    return WMO[code] or ("Код погоды: " .. tostring(code))
end

local hero_card = drawer.rectangle(0, 0, 10, 10)
hero_card.set_color("#141b2d")
hero_card.set_corners(18, 18)

local badge = drawer.rectangle(0, 0, 10, 10)
badge.set_color("#1f2d4a")
badge.set_corners(8, 8)
local badge_txt = drawer.text(0, 0, "ПОГОДА ПО IP", 12, "Calibri", "Bold", "#7aa2ff", "left")

local city_txt = drawer.text(0, 0, "Определяем местоположение...", 30, "Calibri", "Bold", "#f1f5f9", "left")
local sub_txt = drawer.text(0, 0, "Запрос данных по IP и Open-Meteo...", 15, "Calibri", "Regular", "#94a3b8", "left")

local temp_txt = drawer.text(0, 0, "--°", 68, "Calibri", "Bold", "#ffffff", "right")
local desc_txt = drawer.text(0, 0, "", 18, "Calibri", "Regular", "#cbd5e1", "right")

local metric_cards = {}
local metric_labels = {}
local metric_values = {}
local metric_names = { "Ощущается", "Влажность", "Ветер", "Координаты" }
for i = 1, 4 do
    local c = drawer.rectangle(0, 0, 10, 10)
    c.set_color("#1a2338")
    c.set_corners(12, 12)
    metric_cards[i] = c
    metric_labels[i] = drawer.text(0, 0, metric_names[i], 13, "Calibri", "Regular", "#7c8aa6", "left")
    metric_values[i] = drawer.text(0, 0, "—", 20, "Calibri", "Bold", "#e2e8f0", "left")
end

local forecast_title = drawer.text(0, 0, "Прогноз на 5 дней", 20, "Calibri", "Bold", "#e2e8f0", "left")

local day_cards = {}
local day_dates = {}
local day_descs = {}
local day_temps = {}
for i = 1, 5 do
    local c = drawer.rectangle(0, 0, 10, 10)
    c.set_color("#141b2d")
    c.set_corners(14, 14)
    day_cards[i] = c
    day_dates[i] = drawer.text(0, 0, "—", 15, "Calibri", "Bold", "#93c5fd", "left")
    day_descs[i] = drawer.text(0, 0, "", 14, "Calibri", "Regular", "#94a3b8", "left")
    day_temps[i] = drawer.text(0, 0, "--° / --°", 18, "Calibri", "Bold", "#f8fafc", "right")
end

local status_txt = drawer.text(0, 0, "", 13, "Calibri", "Italic", "#64748b", "left")

local refresh_needed = true
local btn_refresh = drawer.button(0, 0, "Обновить")
btn_refresh.set_color("#3b82f6")
btn_refresh.set_text_color("#ffffff")
btn_refresh.set_font_style("Calibri", "Bold", 15)
btn_refresh.set_border_corner(10)
btn_refresh.event("on_selected", function() btn_refresh.set_color("#60a5fa") end)
btn_refresh.event("on_deselected", function() btn_refresh.set_color("#3b82f6") end)
btn_refresh.event("on_left_click", function() refresh_needed = true end)

local W, H = 0, 0
local function layout(w, h)
    W, H = w, h
    local cw = math.min(820, math.max(520, w - 80))
    local cx = math.floor((w - cw) / 2)
    local top = 36

    hero_card.set_position(cx, top)
    hero_card.set_size(cw, 260)

    badge.set_position(cx + 28, top + 24)
    badge.set_size(124, 24)
    badge_txt.set_position(cx + 38, top + 29)

    city_txt.set_position(cx + 28, top + 60)
    sub_txt.set_position(cx + 28, top + 102)

    temp_txt.set_position(cx + cw - 28, top + 34)
    desc_txt.set_position(cx + cw - 28, top + 114)

    local gap = 14
    local mw = math.floor((cw - 56 - gap * 3) / 4)
    local my = top + 152
    for i = 1, 4 do
        local mx = cx + 28 + (i - 1) * (mw + gap)
        metric_cards[i].set_position(mx, my)
        metric_cards[i].set_size(mw, 82)
        metric_labels[i].set_position(mx + 14, my + 14)
        metric_values[i].set_position(mx + 14, my + 40)
    end

    local fy = top + 286
    forecast_title.set_position(cx, fy)
    btn_refresh.set_position(cx + cw - 130, fy - 6)
    btn_refresh.set_size(130, 36)

    local dy = fy + 44
    for i = 1, 5 do
        day_cards[i].set_position(cx, dy)
        day_cards[i].set_size(cw, 58)
        day_dates[i].set_position(cx + 22, dy + 18)
        day_descs[i].set_position(cx + 170, dy + 19)
        day_temps[i].set_position(cx + cw - 22, dy + 17)
        dy = dy + 68
    end

    status_txt.set_position(cx, dy + 8)
end

local function fetch_weather()
    status_txt.set_text("Загрузка данных...")
    local ip_req = requests.get("https://ipwho.is/")
    ip_req.send()

    if ip_req.status_code ~= 200 or not ip_req.json then
        city_txt.set_text("Не удалось определить город")
        sub_txt.set_text("Проверьте подключение к интернету")
        status_txt.set_text("Ошибка ipwho.is: HTTP " .. tostring(ip_req.status_code))
        return
    end

    local geo = ip_req.json
    if geo.success == false then
        city_txt.set_text("Ошибка геолокации")
        sub_txt.set_text(tostring(geo.message or "Неизвестная ошибка"))
        return
    end

    local city = tostring(geo.city or "Неизвестно")
    local country = tostring(geo.country or "")
    local lat = tonumber(geo.latitude)
    local lon = tonumber(geo.longitude)
    local ip = tostring(geo.ip or "")

    city_txt.set_text(city .. (country ~= "" and (", " .. country) or ""))
    sub_txt.set_text("IP: " .. ip)
    metric_values[4].set_text(string.format("%.2f, %.2f", lat or 0, lon or 0))

    if not lat or not lon then
        status_txt.set_text("Координаты не получены")
        return
    end

    local url = string.format(
        "https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto&forecast_days=5",
        lat, lon
    )
    local w_req = requests.get(url)
    w_req.send()

    if w_req.status_code ~= 200 or not w_req.json or not w_req.json.current then
        status_txt.set_text("Ошибка Open-Meteo: HTTP " .. tostring(w_req.status_code))
        return
    end

    local cur = w_req.json.current
    local t = tonumber(cur.temperature_2m) or 0
    local app = tonumber(cur.apparent_temperature) or 0
    local hum = tonumber(cur.relative_humidity_2m) or 0
    local wind = tonumber(cur.wind_speed_10m) or 0
    local code = tonumber(cur.weather_code) or 0

    temp_txt.set_text(string.format("%+.0f°C", t))
    desc_txt.set_text(wmo_text(code))
    metric_values[1].set_text(string.format("%+.0f°C", app))
    metric_values[2].set_text(string.format("%d%%", hum))
    metric_values[3].set_text(string.format("%.1f км/ч", wind))

    local daily = w_req.json.daily
    if daily and daily.time then
        for i = 1, 5 do
            local dt = daily.time[i]
            local tmax = tonumber(daily.temperature_2m_max and daily.temperature_2m_max[i])
            local tmin = tonumber(daily.temperature_2m_min and daily.temperature_2m_min[i])
            local dcode = tonumber(daily.weather_code and daily.weather_code[i]) or 0
            if dt then
                day_dates[i].set_text(tostring(dt))
                day_descs[i].set_text(wmo_text(dcode))
                if tmax and tmin then
                    day_temps[i].set_text(string.format("%+.0f° / %+.0f°", tmax, tmin))
                end
            end
        end
    end

    status_txt.set_text("Обновлено • Источник: ipwho.is + Open-Meteo")
end

local iw, ih = drawer.get_size_screen()
layout(iw, ih)

while true do
    local cw, ch = drawer.get_size_screen()
    if cw ~= W or ch ~= H then
        layout(cw, ch)
    end
    if refresh_needed then
        refresh_needed = false
        fetch_weather()
    end
    sleep(0.05)
end
