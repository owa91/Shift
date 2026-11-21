screen.set_scrolling_status(true, true, true)
drawer.fill_background("#0e1118")

local title = drawer.text(0, 0, "Демо движка Alt", 32, "Calibri", "Bold", "#ffffff", "left")
local subtitle = drawer.text(0, 0, "Прокручивайте страницу колёсиком мыши и нажимайте кнопки", 15, "Calibri", "Regular", "#94a3b8", "left")

local counter = 0
local counter_card = drawer.rectangle(0, 0, 10, 10)
counter_card.set_color("#171c28")
counter_card.set_corners(14, 14)
local counter_txt = drawer.text(0, 0, "Счётчик нажатий: 0", 22, "Calibri", "Bold", "#e2e8f0", "left")

local btn_inc = drawer.button(0, 0, "+1")
btn_inc.set_color("#2563eb")
btn_inc.set_text_color("#ffffff")
btn_inc.set_font_style("Calibri", "Bold", 18)
btn_inc.set_border_corner(10)
btn_inc.event("on_selected", function() btn_inc.set_color("#3b82f6") end)
btn_inc.event("on_deselected", function() btn_inc.set_color("#2563eb") end)
btn_inc.event("on_left_click", function()
    counter = counter + 1
    counter_txt.set_text("Счётчик нажатий: " .. tostring(counter))
end)

local btn_reset = drawer.button(0, 0, "Сброс")
btn_reset.set_color("#2a3040")
btn_reset.set_text_color("#cbd5e1")
btn_reset.set_font_style("Calibri", "Regular", 16)
btn_reset.set_border_corner(10)
btn_reset.event("on_selected", function() btn_reset.set_color("#3a4256") end)
btn_reset.event("on_deselected", function() btn_reset.set_color("#2a3040") end)
btn_reset.event("on_left_click", function()
    counter = 0
    counter_txt.set_text("Счётчик нажатий: 0")
end)

local scroll_txt = drawer.text(0, 0, "Scroll Y: 0 px", 14, "Calibri", "Italic", "#6c8cff", "left")

local cards = {}
local card_titles = {}
local card_descs = {}
local items = {
    { "shift://new", "Домашняя страница Shift с природным фоном и логотипом" },
    { "shift://weather", "Погода в вашем городе по IP + прогноз на 5 дней" },
    { "shift://ip", "Информация о вашем IP-адресе, провайдере и геолокации" },
    { "shift://rates", "Актуальные курсы валют и криптовалют в реальном времени" },
    { "shift://chess", "Шахматы против ИИ (минимакс с альфа-бета отсечением)" },
    { "local://C:/shift.lua", "Запуск локальных Lua-скриптов прямо с диска" },
    { "https://...", "Загрузка удалённых страниц, поддерживающих движок Alt" },
}

for i = 1, #items do
    local c = drawer.rectangle(0, 0, 10, 10)
    c.set_color("#171c28")
    c.set_corners(14, 14)
    cards[i] = c
    card_titles[i] = drawer.text(0, 0, items[i][1], 18, "Calibri", "Bold", "#93c5fd", "left")
    card_descs[i] = drawer.text(0, 0, items[i][2], 15, "Calibri", "Regular", "#cbd5e1", "left")
end

local W, H = 0, 0
local function layout(w, h)
    W, H = w, h
    local cw = math.min(760, math.max(460, w - 80))
    local cx = math.floor((w - cw) / 2)
    local y = 36

    title.set_position(cx, y)
    subtitle.set_position(cx, y + 42)
    scroll_txt.set_position(cx, y + 70)

    y = y + 104
    counter_card.set_position(cx, y)
    counter_card.set_size(cw, 76)
    counter_txt.set_position(cx + 24, y + 24)
    btn_inc.set_position(cx + cw - 208, y + 18)
    btn_inc.set_size(86, 40)
    btn_reset.set_position(cx + cw - 110, y + 18)
    btn_reset.set_size(86, 40)

    y = y + 102
    for i = 1, #items do
        cards[i].set_position(cx, y)
        cards[i].set_size(cw, 92)
        card_titles[i].set_position(cx + 24, y + 18)
        card_descs[i].set_position(cx + 24, y + 48)
        y = y + 108
    end
end

local iw, ih = drawer.get_size_screen()
layout(iw, ih)

while true do
    local cw, ch = drawer.get_size_screen()
    if cw ~= W or ch ~= H then
        layout(cw, ch)
    end
    scroll_txt.set_text(string.format("Scroll Y: %.0f px", screen.get_scroll_y()))
    sleep(0.03)
end
