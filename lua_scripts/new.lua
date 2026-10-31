drawer.fill_background("#0D0F15")

-- ────────────────────────── ДАННЫЕ МАГАЗИНА ──────────────────────────
local products = {
    {
        id = 1,
        name = "Shift Mech Pro",
        tag = "КЛАВИАТУРА",
        desc = "Кастомная механика, смазанные свитчи, Hot-Swap, RGB",
        price_num = 12990,
        price_str = "12 990 ₽"
    },
    {
        id = 2,
        name = "Glide Ultralight",
        tag = "МЫШЬ",
        desc = "49 г, сенсор PixArt 3395, 4000 Гц, оптические клики",
        price_num = 7490,
        price_str = "7 490 ₽"
    },
    {
        id = 3,
        name = "AeroPad Deskmat",
        tag = "АКСЕССУАР",
        desc = "Жаккардовый ковёр 900x400 мм с влагозащитой и прошивкой",
        price_num = 2490,
        price_str = "2 490 ₽"
    }
}

local cart_items = {}
local is_cart_open = false

-- ────────────────────────── ОСНОВНЫЕ ВИДЖЕТЫ ──────────────────────────
-- Шапка
local header_bg = drawer.button(0, 0, "")
header_bg:set_color("#151822")
header_bg:set_border_corner(0)

local brand_title = drawer.text(0, 0, "⚡ SHIFT STORE", 20, "Calibri", "Bold", "#6C8CFF", "left")

local cart_btn = drawer.button(0, 0, "🛒 Корзина (0)")
cart_btn:set_color("#222736")
cart_btn:set_text_color("#FFFFFF")
cart_btn:set_font_style("Calibri", "Bold", 14)
cart_btn:set_border_corner(8)

-- Заголовок страницы
local hero_title = drawer.text(0, 0, "Флагманские аксессуары Shift", 26, "Calibri", "Bold", "#FFFFFF", "center")
local hero_sub = drawer.text(0, 0, "Топовые девайсы для максимальной продуктивности и побед", 14, "Calibri", "Regular", "#868E9E", "center")

-- Карточки товаров
local cards = {}
for i, item in ipairs(products) do
    local card_bg = drawer.button(0, 0, "")
    card_bg:set_color("#181B26")
    card_bg:set_border_corner(14)

    local tag_txt = drawer.text(0, 0, item.tag, 11, "Calibri", "Bold", "#6C8CFF", "left")
    local name_txt = drawer.text(0, 0, item.name, 19, "Calibri", "Bold", "#FFFFFF", "left")
    local desc_txt = drawer.text(0, 0, item.desc, 12, "Calibri", "Regular", "#868E9E", "left")
    local price_txt = drawer.text(0, 0, item.price_str, 18, "Calibri", "Bold", "#34C759", "left")

    local buy_btn = drawer.button(0, 0, "Купить")
    buy_btn:set_color("#6C8CFF")
    buy_btn:set_text_color("#FFFFFF")
    buy_btn:set_font_style("Calibri", "Bold", 14)
    buy_btn:set_border_corner(10)

    cards[i] = {
        bg = card_bg,
        tag = tag_txt,
        name = name_txt,
        desc = desc_txt,
        price = price_txt,
        buy = buy_btn,
        in_cart = false
    }
end

-- ────────────────────────── ОКНО КОРЗИНЫ ──────────────────────────
local cart_overlay = drawer.button(-2000, -2000, "")
cart_overlay:set_color("#000000")
cart_overlay:set_border_corner(0)

local cart_modal = drawer.button(-2000, -2000, "")
cart_modal:set_color("#181B26")
cart_modal:set_border_corner(16)

local cart_title = drawer.text(-2000, -2000, "Корзина покупок", 22, "Calibri", "Bold", "#FFFFFF", "left")

local cart_close_btn = drawer.button(-2000, -2000, "✕")
cart_close_btn:set_color("#2A2F40")
cart_close_btn:set_text_color("#FFFFFF")
cart_close_btn:set_font_style("Calibri", "Bold", 16)
cart_close_btn:set_border_corner(8)

local cart_empty_msg = drawer.text(-2000, -2000, "Ваша корзина пока пуста :(", 15, "Calibri", "Regular", "#868E9E", "center")

local cart_row_widgets = {}
for i = 1, 3 do
    cart_row_widgets[i] = {
        bg = drawer.button(-2000, -2000, ""),
        title = drawer.text(-2000, -2000, "", 14, "Calibri", "Bold", "#FFFFFF", "left"),
        price = drawer.text(-2000, -2000, "", 14, "Calibri", "Bold", "#34C759", "right")
    }
    cart_row_widgets[i].bg:set_color("#202433")
    cart_row_widgets[i].bg:set_border_corner(8)
end

local cart_total_txt = drawer.text(-2000, -2000, "Итого: 0 ₽", 18, "Calibri", "Bold", "#FFFFFF", "left")

local cart_checkout_btn = drawer.button(-2000, -2000, "Оформить заказ")
cart_checkout_btn:set_color("#34C759")
cart_checkout_btn:set_text_color("#FFFFFF")
cart_checkout_btn:set_font_style("Calibri", "Bold", 15)
cart_checkout_btn:set_border_corner(10)

-- ────────────────────────── ЛОГИКА И ИВЕНТЫ ──────────────────────────
local function update_cart_badge()
    local count = 0
    local total = 0
    for id, qty in pairs(cart_items) do
        count = count + qty
        for _, p in ipairs(products) do
            if p.id == id then
                total = total + p.price_num * qty
            end
        end
    end
    cart_btn:set_text("🛒 Корзина (" .. count .. ")")
    cart_total_txt:set_text("Итого: " .. string.format("%d", total):reverse():gsub("(%d%d%d)", "%1 "):reverse():gsub("^ ", "") .. " ₽")
end

-- Клик по кнопке корзины в шапке
cart_btn:event("on_left_click", function()
    is_cart_open = not is_cart_open
end)

cart_close_btn:event("on_left_click", function()
    is_cart_open = false
end)

cart_checkout_btn:event("on_left_click", function()
    cart_checkout_btn:set_text("Заказ оформлен! 🎉")
    cart_checkout_btn:set_color("#2A3042")
end)

-- Ивенты карточек товаров
for i, item in ipairs(products) do
    local c = cards[i]
    c.buy:event("on_left_click", function()
        c.in_cart = not c.in_cart
        if c.in_cart then
            cart_items[item.id] = 1
            c.buy:set_text("В корзине ✓")
            c.buy:set_color("#2A3042")
            c.buy:set_text_color("#7A8299")
        else
            cart_items[item.id] = nil
            c.buy:set_text("Купить")
            c.buy:set_color("#6C8CFF")
            c.buy:set_text_color("#FFFFFF")
        end
        update_cart_badge()
    end)
end

-- ────────────────────────── ГЛАВНЫЙ ЦИКЛ РЕСАЙЗА ──────────────────────────
local last_sw, last_sh = -1, -1
local last_cart_state = false

while true do
    local sw, sh = drawer.get_size_screen()
    if not sw or not sh then
        sw, sh = 1280, 700
    end

    -- Если окно изменило размер ИЛИ изменилось состояние открытия корзины
    if sw ~= last_sw or sh ~= last_sh or is_cart_open ~= last_cart_state then
        last_sw, last_sh = sw, sh
        last_cart_state = is_cart_open

        -- 1. Шапка
        local h_h = 64
        header_bg:set_position(0, 0)
        header_bg:set_size(sw, h_h)

        brand_title:set_position(28, 22)

        local cart_w, cart_h = 150, 38
        cart_btn:set_size(cart_w, cart_h)
        cart_btn:set_position(sw - cart_w - 28, (h_h - cart_h) / 2)

        -- 2. Hero-секция
        hero_title:set_position(sw / 2, h_h + 36)
        hero_sub:set_position(sw / 2, h_h + 70)

        -- 3. Сетка карточек
        local pad_x = math.max(24, sw * 0.05)
        local content_y = h_h + 115
        local avail_w = sw - pad_x * 2
        local gap = math.max(16, sw * 0.02)
        local card_w = (avail_w - gap * 2) / 3
        local card_h = math.max(220, math.min(320, sh - content_y - 28))

        for i, c in ipairs(cards) do
            local cx = pad_x + (i - 1) * (card_w + gap)
            local cy = content_y

            c.bg:set_position(cx, cy)
            c.bg:set_size(card_w, card_h)

            local in_pad = math.max(14, card_w * 0.07)
            c.tag:set_position(cx + in_pad, cy + 22)
            c.name:set_position(cx + in_pad, cy + 48)
            c.desc:set_position(cx + in_pad, cy + 76)

            local btn_w = math.max(105, card_w * 0.42)
            local btn_h = 40
            local bottom_y = cy + card_h - btn_h - in_pad

            c.price:set_position(cx + in_pad, bottom_y + 11)
            c.buy:set_size(btn_w, btn_h)
            c.buy:set_position(cx + card_w - btn_w - in_pad, bottom_y)
        end

        -- 4. Отрисовка модалки Корзины
        if is_cart_open then
            cart_overlay:set_position(0, 0)
            cart_overlay:set_size(sw, sh)

            local modal_w = math.min(480, sw * 0.9)
            local modal_h = math.min(520, sh * 0.85)
            local mx = (sw - modal_w) / 2
            local my = (sh - modal_h) / 2

            cart_modal:set_position(mx, my)
            cart_modal:set_size(modal_w, modal_h)

            cart_title:set_position(mx + 28, my + 24)

            cart_close_btn:set_size(34, 34)
            cart_close_btn:set_position(mx + modal_w - 34 - 24, my + 18)

            local row_y = my + 75
            local active_rows = 0

            for i, p in ipairs(products) do
                local w = cart_row_widgets[i]
                if cart_items[p.id] then
                    active_rows = active_rows + 1
                    local r_h = 44
                    w.bg:set_position(mx + 24, row_y)
                    w.bg:set_size(modal_w - 48, r_h)

                    w.title:set_text(p.name)
                    w.title:set_position(mx + 38, row_y + 14)

                    w.price:set_text(p.price_str)
                    w.price:set_position(mx + modal_w - 40, row_y + 14)

                    row_y = row_y + r_h + 10
                else
                    w.bg:set_position(-2000, -2000)
                    w.title:set_position(-2000, -2000)
                    w.price:set_position(-2000, -2000)
                end
            end

            if active_rows == 0 then
                cart_empty_msg:set_position(mx + modal_w / 2, my + 150)
            else
                cart_empty_msg:set_position(-2000, -2000)
            end

            cart_total_txt:set_position(mx + 28, my + modal_h - 90)

            cart_checkout_btn:set_size(modal_w - 56, 44)
            cart_checkout_btn:set_position(mx + 28, my + modal_h - 60)
            cart_checkout_btn:set_text(active_rows > 0 and "Оформить заказ" or "Корзина пуста")
        else
            -- Прячем корзину за экран
            cart_overlay:set_position(-3000, -3000)
            cart_modal:set_position(-3000, -3000)
            cart_title:set_position(-3000, -3000)
            cart_close_btn:set_position(-3000, -3000)
            cart_empty_msg:set_position(-3000, -3000)
            cart_total_txt:set_position(-3000, -3000)
            cart_checkout_btn:set_position(-3000, -3000)
            for i = 1, 3 do
                local w = cart_row_widgets[i]
                w.bg:set_position(-3000, -3000)
                w.title:set_position(-3000, -3000)
                w.price:set_position(-3000, -3000)
            end
        end
    end

    sleep(0.016)
end
