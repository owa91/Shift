screen.set_scrolling_status(true, true, true)
drawer.fill_background("#0b0e16")

local title = drawer.text(0, 0, "Курсы валют и криптовалют", 30, "Calibri", "Bold", "#f8fafc", "left")
local subtitle = drawer.text(0, 0, "Данные в реальном времени (CoinGecko + ExchangeRate)", 15, "Calibri", "Regular", "#8e9ab0", "left")

local refresh_needed = true
local btn_refresh = drawer.button(0, 0, "Обновить")
btn_refresh.set_color("#3b82f6")
btn_refresh.set_text_color("#ffffff")
btn_refresh.set_font_style("Calibri", "Bold", 15)
btn_refresh.set_border_corner(10)
btn_refresh.event("on_selected", function() btn_refresh.set_color("#60a5fa") end)
btn_refresh.event("on_deselected", function() btn_refresh.set_color("#3b82f6") end)
btn_refresh.event("on_left_click", function() refresh_needed = true end)

local crypto_items = {
    { id = "bitcoin", name = "Bitcoin", sym = "BTC" },
    { id = "ethereum", name = "Ethereum", sym = "ETH" },
    { id = "the-open-network", name = "Toncoin", sym = "TON" },
    { id = "solana", name = "Solana", sym = "SOL" },
}

local c_cards, c_names, c_prices, c_changes = {}, {}, {}, {}
for i = 1, #crypto_items do
    local bg = drawer.rectangle(0, 0, 10, 10)
    bg.set_color("#141a29")
    bg.set_corners(14, 14)
    c_cards[i] = bg
    c_names[i] = drawer.text(0, 0, crypto_items[i].name .. " (" .. crypto_items[i].sym .. ")", 18, "Calibri", "Bold", "#f1f5f9", "left")
    c_prices[i] = drawer.text(0, 0, "$—", 24, "Calibri", "Bold", "#ffffff", "left")
    c_changes[i] = drawer.text(0, 0, "24ч: —", 14, "Calibri", "Regular", "#94a3b8", "left")
end

local fiat_title = drawer.text(0, 0, "Фиатные валюты к RUB", 20, "Calibri", "Bold", "#e2e8f0", "left")
local fiat_items = {
    { code = "USD", name = "Доллар США (USD)" },
    { code = "EUR", name = "Евро (EUR)" },
    { code = "CNY", name = "Китайский юань (CNY)" },
}

local f_cards, f_names, f_vals = {}, {}, {}
for i = 1, #fiat_items do
    local bg = drawer.rectangle(0, 0, 10, 10)
    bg.set_color("#141a29")
    bg.set_corners(14, 14)
    f_cards[i] = bg
    f_names[i] = drawer.text(0, 0, fiat_items[i].name, 16, "Calibri", "Regular", "#cbd5e1", "left")
    f_vals[i] = drawer.text(0, 0, "— ₽", 20, "Calibri", "Bold", "#93c5fd", "right")
end

local status_txt = drawer.text(0, 0, "", 13, "Calibri", "Italic", "#64748b", "left")

local W, H = 0, 0
local function layout(w, h)
    W, H = w, h
    local cw = math.min(800, math.max(500, w - 80))
    local cx = math.floor((w - cw) / 2)
    local top = 36

    title.set_position(cx, top)
    subtitle.set_position(cx, top + 40)
    btn_refresh.set_position(cx + cw - 130, top + 6)
    btn_refresh.set_size(130, 38)

    local gap = 16
    local card_w = math.floor((cw - gap) / 2)
    local cy = top + 84
    for i = 1, #crypto_items do
        local col = (i - 1) % 2
        local row = math.floor((i - 1) / 2)
        local x = cx + col * (card_w + gap)
        local y = cy + row * 124
        c_cards[i].set_position(x, y)
        c_cards[i].set_size(card_w, 108)
        c_names[i].set_position(x + 20, y + 16)
        c_prices[i].set_position(x + 20, y + 46)
        c_changes[i].set_position(x + 20, y + 78)
    end

    local fy = cy + 266
    fiat_title.set_position(cx, fy)
    fy = fy + 40
    for i = 1, #fiat_items do
        f_cards[i].set_position(cx, fy)
        f_cards[i].set_size(cw, 56)
        f_names[i].set_position(cx + 22, fy + 17)
        f_vals[i].set_position(cx + cw - 22, fy + 16)
        fy = fy + 66
    end

    status_txt.set_position(cx, fy + 8)
end

local function fetch_rates()
    status_txt.set_text("Загрузка курсов...")

    local cg = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,the-open-network,solana&vs_currencies=usd&include_24hr_change=true")
    cg.send()
    if cg.status_code == 200 and cg.json then
        for i, item in ipairs(crypto_items) do
            local entry = cg.json[item.id]
            if entry and entry.usd then
                c_prices[i].set_text(string.format("$%.2f", tonumber(entry.usd)))
                local chg = tonumber(entry.usd_24h_change) or 0
                c_changes[i].set_text(string.format("24ч: %+.2f%%", chg))
                c_changes[i].set_color(chg >= 0 and "#34d399" or "#f87171")
            end
        end
    end

    local fx = requests.get("https://open.er-api.com/v6/latest/RUB")
    fx.send()
    if fx.status_code == 200 and fx.json and fx.json.rates then
        local rates = fx.json.rates
        for i, item in ipairs(fiat_items) do
            local r = tonumber(rates[item.code])
            if r and r > 0 then
                f_vals[i].set_text(string.format("%.2f ₽", 1 / r))
            end
        end
    end

    status_txt.set_text("Обновлено")
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
        fetch_rates()
    end
    sleep(0.05)
end
