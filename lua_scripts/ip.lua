screen.set_scrolling_status(true, true, true)
drawer.fill_background("#0c1018")

local card = drawer.rectangle(0, 0, 10, 10)
card.set_color("#151b28")
card.set_corners(18, 18)

local badge = drawer.rectangle(0, 0, 10, 10)
badge.set_color("#1e2d4d")
badge.set_corners(8, 8)
local badge_txt = drawer.text(0, 0, "СЕТЕВАЯ ИНФОРМАЦИЯ", 12, "Calibri", "Bold", "#7aa2ff", "left")

local ip_title = drawer.text(0, 0, "Загрузка IP...", 38, "Calibri", "Bold", "#ffffff", "left")
local sub_txt = drawer.text(0, 0, "Определяем внешний адрес и провайдера...", 15, "Calibri", "Regular", "#94a3b8", "left")

local fields = {
    { key = "Страна", val = "—" },
    { key = "Регион", val = "—" },
    { key = "Город", val = "—" },
    { key = "Провайдер (ISP)", val = "—" },
    { key = "Организация", val = "—" },
    { key = "Часовой пояс", val = "—" },
    { key = "Координаты", val = "—" },
}

local row_bgs = {}
local row_keys = {}
local row_vals = {}
for i = 1, #fields do
    local bg = drawer.rectangle(0, 0, 10, 10)
    bg.set_color("#1b2233")
    bg.set_corners(10, 10)
    row_bgs[i] = bg
    row_keys[i] = drawer.text(0, 0, fields[i].key, 15, "Calibri", "Regular", "#8e9ab0", "left")
    row_vals[i] = drawer.text(0, 0, fields[i].val, 16, "Calibri", "Bold", "#e2e8f0", "right")
end

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
    local cw = math.min(720, math.max(460, w - 80))
    local cx = math.floor((w - cw) / 2)
    local top = 40
    local ch = 180 + #fields * 56

    card.set_position(cx, top)
    card.set_size(cw, ch)

    badge.set_position(cx + 28, top + 24)
    badge.set_size(176, 24)
    badge_txt.set_position(cx + 38, top + 29)

    btn_refresh.set_position(cx + cw - 148, top + 24)
    btn_refresh.set_size(120, 36)

    ip_title.set_position(cx + 28, top + 62)
    sub_txt.set_position(cx + 28, top + 114)

    local ry = top + 154
    for i = 1, #fields do
        row_bgs[i].set_position(cx + 28, ry)
        row_bgs[i].set_size(cw - 56, 46)
        row_keys[i].set_position(cx + 46, ry + 13)
        row_vals[i].set_position(cx + cw - 46, ry + 12)
        ry = ry + 56
    end
end

local function fetch_ip()
    sub_txt.set_text("Запрос к https://ipwho.is/...")
    local req = requests.get("https://ipwho.is/")
    req.send()
    if req.status_code ~= 200 or not req.json then
        ip_title.set_text("Нет соединения")
        sub_txt.set_text("Ошибка запроса: HTTP " .. tostring(req.status_code))
        return
    end
    local d = req.json
    ip_title.set_text(tostring(d.ip or "Неизвестно"))
    sub_txt.set_text("Тип: " .. tostring(d.type or "IPv4"))

    local conn = d.connection or {}
    local tz = d.timezone or {}
    row_vals[1].set_text(tostring(d.country or "—"))
    row_vals[2].set_text(tostring(d.region or "—"))
    row_vals[3].set_text(tostring(d.city or "—"))
    row_vals[4].set_text(tostring(conn.isp or "—"))
    row_vals[5].set_text(tostring(conn.org or "—"))
    row_vals[6].set_text(tostring(tz.id or "—"))
    row_vals[7].set_text(string.format("%.4f, %.4f", tonumber(d.latitude) or 0, tonumber(d.longitude) or 0))
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
        fetch_ip()
    end
    sleep(0.05)
end
