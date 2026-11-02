-- ============================================================================
-- ROBLOX HOMEPAGE & DISCOVER LANDING (Shift / Alt Engine)
-- С поддержкой скроллинга и расширенной структурой страницы
-- ============================================================================

drawer.fill_background("#0E1015")

-- ────────────────────────── БАЗА ДАННЫХ ИГР ROBLOX (9 ПЛЕЙСОВ) ──────────────────────────
local games = {
    -- Секция 1: Топ тренды
    {
        id = 1,
        title = "Blox Fruits ⚔️",
        category = "rpg",
        trending = true,
        tag = "ТОП-1 ТРЕНД",
        tag_color = "#E2252B",
        online_str = "🟢 482K онлайн",
        rating_str = "⭐ 95%",
        visits = "36.8 млрд",
        creator = "Gamer Robot Inc",
        genre = "Экшен / RPG",
        desc = "Найди легендарные фрукты, овладей волей и стань сильнейшим мечником!"
    },
    {
        id = 2,
        title = "Brookhaven 🏡RP",
        category = "rp",
        trending = true,
        tag = "ХИТ РОЛЕВЫХ",
        tag_color = "#8E44AD",
        online_str = "🟢 394K онлайн",
        rating_str = "⭐ 91%",
        visits = "51.2 млрд",
        creator = "Wolfpaq",
        genre = "Город / RP",
        desc = "Покупай виллы, катайся на спорткарах, заводи друзей и живи в удовольствие."
    },
    {
        id = 3,
        title = "Adopt Me! 🐾",
        category = "rp",
        trending = false,
        tag = "СЕМЕЙНЫЙ",
        tag_color = "#E67E22",
        online_str = "🟢 215K онлайн",
        rating_str = "⭐ 93%",
        visits = "38.5 млрд",
        creator = "DreamCraft",
        genre = "Питомцы / RP",
        desc = "Выращивай редких питомцев, строй дом мечты и торгуйся с игроками."
    },
    -- Секция 2: Экшен, Паркур и Хорроры (ниже экрана)
    {
        id = 4,
        title = "Tower of Hell ⏱️",
        category = "parkour",
        trending = false,
        tag = "ХАРДКОР",
        tag_color = "#D32F2F",
        online_str = "🟢 98K онлайн",
        rating_str = "⭐ 89%",
        visits = "23.4 млрд",
        creator = "YXEmpire",
        genre = "Паркур / Obby",
        desc = "Никаких чекпоинтов! 6 случайных уровней башни и таймер на выживание."
    },
    {
        id = 5,
        title = "Doors 👁️",
        category = "horror",
        trending = true,
        tag = "ХОРРОР ГОДА",
        tag_color = "#34495E",
        online_str = "🟢 145K онлайн",
        rating_str = "⭐ 96%",
        visits = "6.2 млрд",
        creator = "LSPLASH",
        genre = "Хоррор / Квест",
        desc = "100 дверей таинственного отеля. Слушай монстров и прячься в шкафу!"
    },
    {
        id = 6,
        title = "Blade Ball ⚡",
        category = "rpg",
        trending = true,
        tag = "КИБЕРСПОРТ",
        tag_color = "#1976D2",
        online_str = "🟢 178K онлайн",
        rating_str = "⭐ 94%",
        visits = "4.9 млрд",
        creator = "Wiggity.",
        genre = "Экшен / Арена",
        desc = "Отражай летящий смертельный мяч на скорости и используй суперспособности."
    },
    -- Секция 3: Новые хиты и Рекомендации (глубоко ниже экрана)
    {
        id = 7,
        title = "Pet Simulator 99! 💎",
        category = "rp",
        trending = true,
        tag = "НОВИНКА",
        tag_color = "#00B0FF",
        online_str = "🟢 130K онлайн",
        rating_str = "⭐ 92%",
        visits = "14.1 млрд",
        creator = "BIG Games",
        genre = "Симулятор / Квест",
        desc = "Открывай яйца, собирай огромных питомцев и торгуй алмазами по всему миру!"
    },
    {
        id = 8,
        title = "Murder Mystery 2 🔪",
        category = "horror",
        trending = false,
        tag = "ДЕТЕКТИВ",
        tag_color = "#C2185B",
        online_str = "🟢 110K онлайн",
        rating_str = "⭐ 90%",
        visits = "19.8 млрд",
        creator = "Nikilis",
        genre = "Выживание",
        desc = "Невинные, шериф и убийца. Раскрой тайну или устрани всех до единого!"
    },
    {
        id = 9,
        title = "Arsenal 🎯",
        category = "rpg",
        trending = false,
        tag = "ШУТЕР",
        tag_color = "#00796B",
        online_str = "🟢 75K онлайн",
        rating_str = "⭐ 94%",
        visits = "5.8 млрд",
        creator = "ROLVe Community",
        genre = "Шутер / Арена",
        desc = "Динамичный аркадный шутер с сотнями видов оружия, скинами и быстрыми матчами."
    }
}

local categories = {
    { id = "all", label = "🔥 Все плейсы" },
    { id = "trending", label = "⚡ В тренде" },
    { id = "rpg", label = "⚔️ Экшен & RPG" },
    { id = "rp", label = "🏡 Симуляторы & RP" },
    { id = "parkour", label = "🏃 Паркур / Obby" },
    { id = "horror", label = "👁️ Хорроры" }
}

local robux_bundles = {
    { robux = 400, price = "449 ₽", bonus = "Базовый" },
    { robux = 800, price = "899 ₽", bonus = "Хит продаж ⭐" },
    { robux = 1700, price = "1 790 ₽", bonus = "+10% Бонус" },
    { robux = 4500, price = "4 490 ₽", bonus = "+20% Бонус" }
}

-- ────────────────────────── СОСТОЯНИЕ ПРИЛОЖЕНИЯ ──────────────────────────
local current_cat = "all"
local user_robux = 1250
local is_launcher_open = false
local is_robux_open = false
local is_info_open = false
local selected_game = games[1]
local is_favorited = false

local toast_msg = ""
local toast_time = 0

local function show_toast(msg)
    toast_msg = msg
    toast_time = 180 -- ~3 секунды при 60fps
end

local function format_robux(val)
    return string.format("%d", val):reverse():gsub("(%d%d%d)", "%1 "):reverse():gsub("^ ", "")
end

-- ────────────────────────── 1. ШАПКА (HEADER) ──────────────────────────
local header_bg = drawer.button(0, 0, "")
header_bg:set_color("#141720")
header_bg:set_border_corner(0)

local header_border = drawer.button(0, 0, "")
header_border:set_color("#222736")
header_border:set_border_corner(0)

local logo_icon = drawer.button(0, 0, "■")
logo_icon:set_color("#E2252B")
logo_icon:set_text_color("#FFFFFF")
logo_icon:set_font_style("Calibri", "Bold", 17)
logo_icon:set_border_corner(6)

local logo_text = drawer.text(0, 0, "ROBLOX", 21, "Calibri", "Bold", "#FFFFFF", "left")

local nav_btn_discover = drawer.button(0, 0, "Плейсы")
nav_btn_discover:set_color("#232838")
nav_btn_discover:set_text_color("#FFFFFF")
nav_btn_discover:set_font_style("Calibri", "Bold", 13)
nav_btn_discover:set_border_corner(8)

local nav_btn_market = drawer.button(0, 0, "Маркет")
nav_btn_market:set_color("#181B26")
nav_btn_market:set_text_color("#9AA3B8")
nav_btn_market:set_font_style("Calibri", "Bold", 13)
nav_btn_market:set_border_corner(8)

local nav_btn_create = drawer.button(0, 0, "Создать")
nav_btn_create:set_color("#181B26")
nav_btn_create:set_text_color("#9AA3B8")
nav_btn_create:set_font_style("Calibri", "Bold", 13)
nav_btn_create:set_border_corner(8)

local search_bar = drawer.button(0, 0, "🔍 Поиск плейсов, миров и создателей...")
search_bar:set_color("#1C202C")
search_bar:set_text_color("#656E82")
search_bar:set_font_style("Calibri", "Regular", 12)
search_bar:set_border_corner(8)
search_bar:set_text_align("left")

local header_robux_btn = drawer.button(0, 0, "⏣ " .. format_robux(user_robux) .. " R$")
header_robux_btn:set_color("#1F2535")
header_robux_btn:set_text_color("#00C896")
header_robux_btn:set_font_style("Calibri", "Bold", 13)
header_robux_btn:set_border_corner(8)

local profile_btn = drawer.button(0, 0, "👤 Noob_2026")
profile_btn:set_color("#232838")
profile_btn:set_text_color("#FFFFFF")
profile_btn:set_font_style("Calibri", "Bold", 13)
profile_btn:set_border_corner(8)

-- ────────────────────────── 2. HERO-СЕКЦИЯ ──────────────────────────
local hero_bg = drawer.button(0, 0, "")
hero_bg:set_color("#171A24")
hero_bg:set_border_corner(14)

local hero_accent = drawer.button(0, 0, "")
hero_accent:set_color("#E2252B")
hero_accent:set_border_corner(3)

local hero_badge = drawer.button(0, 0, "🔥 ВООБРАЖЕНИЮ НЕТ ПРЕДЕЛОВ")
hero_badge:set_color("#291E24")
hero_badge:set_text_color("#FF6B6B")
hero_badge:set_font_style("Calibri", "Bold", 11)
hero_badge:set_border_corner(6)

local hero_title = drawer.text(0, 0, "Добро пожаловать в метавселенную Roblox", 24, "Calibri", "Bold", "#FFFFFF", "left")
local hero_desc = drawer.text(0, 0, "Исследуй миллионы захватывающих 3D-миров, играй с друзьями и воплощай любые идеи.", 13, "Calibri", "Regular", "#8F99AD", "left")

local hero_play_btn = drawer.button(0, 0, "▶ Быстрая игра")
hero_play_btn:set_color("#00B06F")
hero_play_btn:set_text_color("#FFFFFF")
hero_play_btn:set_font_style("Calibri", "Bold", 14)
hero_play_btn:set_border_corner(10)

local hero_robux_btn = drawer.button(0, 0, "⏣ Пополнить Robux")
hero_robux_btn:set_color("#232838")
hero_robux_btn:set_text_color("#00A2FF")
hero_robux_btn:set_font_style("Calibri", "Bold", 14)
hero_robux_btn:set_border_corner(10)

local hero_stat1 = drawer.button(0, 0, "👥 70M+ в день")
hero_stat1:set_color("#1E222E")
hero_stat1:set_text_color("#A3ADBF")
hero_stat1:set_font_style("Calibri", "Regular", 12)
hero_stat1:set_border_corner(6)

local hero_stat2 = drawer.button(0, 0, "🎮 5.5M+ миров")
hero_stat2:set_color("#1E222E")
hero_stat2:set_text_color("#A3ADBF")
hero_stat2:set_font_style("Calibri", "Regular", 12)
hero_stat2:set_border_corner(6)

local hero_stat3 = drawer.button(0, 0, "📱 ПК • Телефон • VR")
hero_stat3:set_color("#1E222E")
hero_stat3:set_text_color("#A3ADBF")
hero_stat3:set_font_style("Calibri", "Regular", 12)
hero_stat3:set_border_corner(6)

-- ────────────────────────── 3. ВКЛАДКИ КАТЕГОРИЙ ──────────────────────────
local cat_buttons = {}
for i, c in ipairs(categories) do
    local btn = drawer.button(0, 0, c.label)
    btn:set_font_style("Calibri", "Bold", 13)
    btn:set_border_corner(8)
    if c.id == current_cat then
        btn:set_color("#E2252B")
        btn:set_text_color("#FFFFFF")
    else
        btn:set_color("#1A1D27")
        btn:set_text_color("#8F99AD")
    end
    cat_buttons[i] = { btn = btn, id = c.id }
end

-- ────────────────────────── 4. СЕКЦИИ И КАРТОЧКИ ИГР (9 КАРТОЧЕК) ──────────────────────────
local sec1_title = drawer.text(0, 0, "🔥 В тренде прямо сейчас", 18, "Calibri", "Bold", "#FFFFFF", "left")
local sec2_title = drawer.text(0, 0, "⚡ Экшен, Паркур и Хорроры", 18, "Calibri", "Bold", "#FFFFFF", "left")
local sec3_title = drawer.text(0, 0, "🌟 Новые хиты и Рекомендации", 18, "Calibri", "Bold", "#FFFFFF", "left")

local card_widgets = {}
for i = 1, #games do
    local g = games[i]

    local bg = drawer.button(0, 0, "")
    bg:set_color("#181B26")
    bg:set_border_corner(12)

    local tag_badge = drawer.button(0, 0, g.tag)
    tag_badge:set_color(g.tag_color)
    tag_badge:set_text_color("#FFFFFF")
    tag_badge:set_font_style("Calibri", "Bold", 10)
    tag_badge:set_border_corner(4)

    local title_txt = drawer.text(0, 0, g.title, 16, "Calibri", "Bold", "#FFFFFF", "left")
    local online_txt = drawer.text(0, 0, g.online_str, 12, "Calibri", "Bold", "#00C896", "left")
    local rating_txt = drawer.text(0, 0, g.rating_str, 12, "Calibri", "Bold", "#FFB800", "right")
    local desc_txt = drawer.text(0, 0, g.desc, 12, "Calibri", "Regular", "#7E889D", "left")

    local play_btn = drawer.button(0, 0, "▶ Играть")
    play_btn:set_color("#00B06F")
    play_btn:set_text_color("#FFFFFF")
    play_btn:set_font_style("Calibri", "Bold", 13)
    play_btn:set_border_corner(8)

    local info_btn = drawer.button(0, 0, "ℹ Инфо")
    info_btn:set_color("#232838")
    info_btn:set_text_color("#9AA3B8")
    info_btn:set_font_style("Calibri", "Bold", 13)
    info_btn:set_border_corner(8)

    card_widgets[i] = {
        game = g,
        bg = bg,
        tag = tag_badge,
        title = title_txt,
        online = online_txt,
        rating = rating_txt,
        desc = desc_txt,
        play = play_btn,
        info = info_btn
    }
end

-- ────────────────────────── 5. СЕКЦИЯ МАГАЗИНА ROBUX НА СТРАНИЦЕ ──────────────────────────
local robux_sec_title = drawer.text(0, 0, "⏣ Официальный магазин Robux", 18, "Calibri", "Bold", "#FFFFFF", "left")
local robux_sec_sub = drawer.text(0, 0, "Покупай скины, экипировку, анимации и пропуска в любимых плейсах", 12, "Calibri", "Regular", "#8F99AD", "left")

local robux_page_cards = {}
for i, b in ipairs(robux_bundles) do
    local card_bg = drawer.button(0, 0, "")
    card_bg:set_color("#181B26")
    card_bg:set_border_corner(12)

    local r_badge = drawer.button(0, 0, b.bonus)
    r_badge:set_color(i == 2 and "#E2252B" or "#232838")
    r_badge:set_text_color(i == 2 and "#FFFFFF" or "#FFB800")
    r_badge:set_font_style("Calibri", "Bold", 10)
    r_badge:set_border_corner(4)

    local r_val = drawer.text(0, 0, b.robux .. " R$", 18, "Calibri", "Bold", "#00A2FF", "center")

    local r_btn = drawer.button(0, 0, b.price)
    r_btn:set_color("#00B06F")
    r_btn:set_text_color("#FFFFFF")
    r_btn:set_font_style("Calibri", "Bold", 13)
    r_btn:set_border_corner(8)

    robux_page_cards[i] = {
        data = b,
        bg = card_bg,
        badge = r_badge,
        val = r_val,
        btn = r_btn
    }
end

-- ────────────────────────── 6. СЕКЦИЯ ПРЕИМУЩЕСТВ ПЛАТФОРМЫ ──────────────────────────
local feat_sec_title = drawer.text(0, 0, "Почему миллионы игроков выбирают Roblox?", 18, "Calibri", "Bold", "#FFFFFF", "left")

local features_data = {
    { title = "🚀 Творчество без границ", text = "Создавай собственные миры в бесплатном редакторе Roblox Studio и делись ими со всей планетой." },
    { title = "🎮 Играй где угодно", text = "Полная кроссплатформенность: ПК, смартфоны, планшеты, консоли и VR работают в единой сети." },
    { title = "🛡️ Безопасность и защита", text = "Продвинутая модерация контента, родительский контроль и надежная защита игрового профиля." }
}

local feat_widgets = {}
for i, f in ipairs(features_data) do
    local f_bg = drawer.button(0, 0, "")
    f_bg:set_color("#181B26")
    f_bg:set_border_corner(12)

    local f_title = drawer.text(0, 0, f.title, 15, "Calibri", "Bold", "#FFFFFF", "left")
    local f_text = drawer.text(0, 0, f.text, 12, "Calibri", "Regular", "#8F99AD", "left")

    feat_widgets[i] = {
        bg = f_bg,
        title = f_title,
        text = f_text
    }
end

-- ────────────────────────── 7. ПОДВАЛ (FOOTER) ──────────────────────────
local footer_line = drawer.button(0, 0, "")
footer_line:set_color("#232838")
footer_line:set_border_corner(0)

local footer_links_txt = drawer.text(0, 0, "О Roblox  •  Вакансии  •  Для разработчиков  •  Условия использования  •  Конфиденциальность  •  Поддержка", 12, "Calibri", "Regular", "#6C768A", "center")
local footer_copy_txt = drawer.text(0, 0, "© 2026 Roblox Corporation. Все товарные знаки являются собственностью их владельцев. Платформа Shift.", 11, "Calibri", "Regular", "#4E5666", "center")

-- ────────────────────────── ПЛАВАЮЩИЙ TOAST ──────────────────────────
local toast_bg = drawer.button(-3000, -3000, "")
toast_bg:set_color("#162920")
toast_bg:set_border_corner(10)

local toast_txt = drawer.text(-3000, -3000, "", 14, "Calibri", "Bold", "#00E58F", "center")

-- ────────────────────────── МОДАЛЬНОЕ ОКНО 1: ЛАУНЧЕР ИГРЫ ──────────────────────────
local modal_overlay = drawer.button(-3000, -3000, "")
modal_overlay:set_color("#0A0C11")
modal_overlay:set_border_corner(0)

local launch_box = drawer.button(-3000, -3000, "")
launch_box:set_color("#171A24")
launch_box:set_border_corner(16)

local launch_header_bar = drawer.button(-3000, -3000, "")
launch_header_bar:set_color("#202433")
launch_header_bar:set_border_corner(16)

local launch_title = drawer.text(-3000, -3000, "Запуск Roblox", 22, "Calibri", "Bold", "#FFFFFF", "left")
local launch_sub = drawer.text(-3000, -3000, "", 14, "Calibri", "Regular", "#8F99AD", "left")

local launch_close = drawer.button(-3000, -3000, "✕")
launch_close:set_color("#272D3E")
launch_close:set_text_color("#FFFFFF")
launch_close:set_font_style("Calibri", "Bold", 16)
launch_close:set_border_corner(8)

local launch_banner = drawer.button(-3000, -3000, "🟢 Сервер: Европа-1 • Пинг: 24 ms • Мест: 19/20")
launch_banner:set_color("#1A2522")
launch_banner:set_text_color("#00E58F")
launch_banner:set_font_style("Calibri", "Bold", 13)
launch_banner:set_border_corner(8)

local launch_info1 = drawer.button(-3000, -3000, "")
launch_info1:set_color("#1F2331")
launch_info1:set_text_color("#A2ACBF")
launch_info1:set_font_style("Calibri", "Regular", 12)
launch_info1:set_border_corner(8)

local launch_info2 = drawer.button(-3000, -3000, "")
launch_info2:set_color("#1F2331")
launch_info2:set_text_color("#A2ACBF")
launch_info2:set_font_style("Calibri", "Regular", 12)
launch_info2:set_border_corner(8)

local launch_status = drawer.text(-3000, -3000, "Клиент Roblox готов к старту. Нажмите для запуска:", 13, "Calibri", "Regular", "#8F99AD", "center")

local launch_start_btn = drawer.button(-3000, -3000, "▶ Присоединиться к серверу")
launch_start_btn:set_color("#00B06F")
launch_start_btn:set_text_color("#FFFFFF")
launch_start_btn:set_font_style("Calibri", "Bold", 15)
launch_start_btn:set_border_corner(10)

local launch_fav_btn = drawer.button(-3000, -3000, "⭐ В избранное")
launch_fav_btn:set_color("#242A3A")
launch_fav_btn:set_text_color("#FFB800")
launch_fav_btn:set_font_style("Calibri", "Bold", 14)
launch_fav_btn:set_border_corner(10)

-- ────────────────────────── МОДАЛЬНОЕ ОКНО 2: МАГАЗИН ROBUX ──────────────────────────
local robux_box = drawer.button(-3000, -3000, "")
robux_box:set_color("#171A24")
robux_box:set_border_corner(16)

local robux_title = drawer.text(-3000, -3000, "Магазин Robux ⏣", 22, "Calibri", "Bold", "#FFFFFF", "left")
local robux_balance_txt = drawer.text(-3000, -3000, "Баланс: " .. format_robux(user_robux) .. " R$", 15, "Calibri", "Bold", "#00C896", "left")

local robux_close = drawer.button(-3000, -3000, "✕")
robux_close:set_color("#272D3E")
robux_close:set_text_color("#FFFFFF")
robux_close:set_font_style("Calibri", "Bold", 16)
robux_close:set_border_corner(8)

local robux_bundle_widgets = {}
for i, b in ipairs(robux_bundles) do
    local card = drawer.button(-3000, -3000, "")
    card:set_color("#1F2331")
    card:set_border_corner(10)

    local amount = drawer.text(-3000, -3000, b.robux .. " R$", 17, "Calibri", "Bold", "#00A2FF", "left")
    local tag = drawer.text(-3000, -3000, b.bonus, 12, "Calibri", "Bold", "#FFB800", "left")

    local buy = drawer.button(-3000, -3000, b.price)
    buy:set_color("#00B06F")
    buy:set_text_color("#FFFFFF")
    buy:set_font_style("Calibri", "Bold", 13)
    buy:set_border_corner(8)

    robux_bundle_widgets[i] = {
        data = b,
        card = card,
        amount = amount,
        tag = tag,
        buy = buy
    }
end

-- ────────────────────────── МОДАЛЬНОЕ ОКНО 3: ИНФО О ПЛЕЙСЕ ──────────────────────────
local info_box = drawer.button(-3000, -3000, "")
info_box:set_color("#171A24")
info_box:set_border_corner(16)

local info_title = drawer.text(-3000, -3000, "Информация о плейсе", 22, "Calibri", "Bold", "#FFFFFF", "left")
local info_close = drawer.button(-3000, -3000, "✕")
info_close:set_color("#272D3E")
info_close:set_text_color("#FFFFFF")
info_close:set_font_style("Calibri", "Bold", 16)
info_close:set_border_corner(8)

local info_game_name = drawer.text(-3000, -3000, "", 18, "Calibri", "Bold", "#00A2FF", "left")
local info_game_author = drawer.text(-3000, -3000, "", 13, "Calibri", "Regular", "#8F99AD", "left")
local info_game_desc = drawer.text(-3000, -3000, "", 13, "Calibri", "Regular", "#CBD4E3", "left")
local info_game_stats = drawer.text(-3000, -3000, "", 13, "Calibri", "Bold", "#00C896", "left")

local info_ok_btn = drawer.button(-3000, -3000, "Понятно")
info_ok_btn:set_color("#2A3144")
info_ok_btn:set_text_color("#FFFFFF")
info_ok_btn:set_font_style("Calibri", "Bold", 14)
info_ok_btn:set_border_corner(10)

-- ────────────────────────── ОБРАБОТЧИКИ СОБЫТИЙ ──────────────────────────

local function add_robux(amount)
    user_robux = user_robux + amount
    header_robux_btn:set_text("⏣ " .. format_robux(user_robux) .. " R$")
    robux_balance_txt:set_text("Баланс: " .. format_robux(user_robux) .. " R$")
    show_toast("+" .. amount .. " R$ зачислено на ваш баланс!")
end

-- Клик по Robux в шапке / Hero
header_robux_btn:event("on_left_click", function()
    is_robux_open = true
    is_launcher_open = false
    is_info_open = false
end)

hero_robux_btn:event("on_left_click", function()
    is_robux_open = true
    is_launcher_open = false
    is_info_open = false
end)

robux_close:event("on_left_click", function()
    is_robux_open = false
end)

-- Покупка Robux в модалке
for i, bw in ipairs(robux_bundle_widgets) do
    bw.buy:event("on_left_click", function()
        add_robux(bw.data.robux)
    end)
    bw.buy:event("on_selected", function()
        bw.buy:set_color("#00C97F")
    end)
    bw.buy:event("on_deselected", function()
        bw.buy:set_color("#00B06F")
    end)
end

-- Покупка Robux на самой странице
for i, rpc in ipairs(robux_page_cards) do
    rpc.btn:event("on_left_click", function()
        add_robux(rpc.data.robux)
    end)
    rpc.btn:event("on_selected", function()
        rpc.btn:set_color("#00C97F")
    end)
    rpc.btn:event("on_deselected", function()
        rpc.btn:set_color("#00B06F")
    end)
end

-- Клик по вкладкам категорий
for i, cb in ipairs(cat_buttons) do
    cb.btn:event("on_left_click", function()
        current_cat = cb.id
        for _, other in ipairs(cat_buttons) do
            if other.id == current_cat then
                other.btn:set_color("#E2252B")
                other.btn:set_text_color("#FFFFFF")
            else
                other.btn:set_color("#1A1D27")
                other.btn:set_text_color("#8F99AD")
            end
        end
    end)
end

-- Быстрая игра из Hero
hero_play_btn:event("on_left_click", function()
    selected_game = games[1]
    is_launcher_open = true
    is_robux_open = false
    is_info_open = false
    is_favorited = false
    launch_fav_btn:set_text("⭐ В избранное")
end)

hero_play_btn:event("on_selected", function()
    hero_play_btn:set_color("#00C97F")
end)
hero_play_btn:event("on_deselected", function()
    hero_play_btn:set_color("#00B06F")
end)

header_robux_btn:event("on_selected", function()
    header_robux_btn:set_color("#2B3349")
end)
header_robux_btn:event("on_deselected", function()
    header_robux_btn:set_color("#1F2535")
end)

-- Карточки игр: клики и ховеры
for i, cw in ipairs(card_widgets) do
    cw.bg:event("on_selected", function()
        cw.bg:set_color("#212534")
    end)
    cw.bg:event("on_deselected", function()
        cw.bg:set_color("#181B26")
    end)

    cw.play:event("on_selected", function()
        cw.play:set_color("#00C97F")
    end)
    cw.play:event("on_deselected", function()
        cw.play:set_color("#00B06F")
    end)

    cw.info:event("on_selected", function()
        cw.info:set_color("#2D354A")
    end)
    cw.info:event("on_deselected", function()
        cw.info:set_color("#232838")
    end)

    cw.play:event("on_left_click", function()
        selected_game = cw.game
        is_launcher_open = true
        is_robux_open = false
        is_info_open = false
        is_favorited = false
        launch_fav_btn:set_text("⭐ В избранное")
    end)

    cw.info:event("on_left_click", function()
        selected_game = cw.game
        is_info_open = true
        is_launcher_open = false
        is_robux_open = false
    end)
end

-- Модалка запуска
launch_close:event("on_left_click", function()
    is_launcher_open = false
end)

launch_start_btn:event("on_left_click", function()
    launch_start_btn:set_text("Запуск клиента...")
    launch_start_btn:set_color("#232838")
    show_toast("🚀 Подключение к " .. selected_game.title .. "...")
end)

launch_fav_btn:event("on_left_click", function()
    is_favorited = not is_favorited
    if is_favorited then
        launch_fav_btn:set_text("★ В избранном")
        launch_fav_btn:set_color("#38321F")
        show_toast("Плейс добавлен в избранное!")
    else
        launch_fav_btn:set_text("⭐ В избранное")
        launch_fav_btn:set_color("#242A3A")
        show_toast("Удалено из избранного.")
    end
end)

-- Модалка инфо
info_close:event("on_left_click", function()
    is_info_open = false
end)

info_ok_btn:event("on_left_click", function()
    is_info_open = false
end)

-- Поиск и профиль
search_bar:event("on_left_click", function()
    show_toast("Введите название игры в строке поиска")
end)

profile_btn:event("on_left_click", function()
    show_toast("Профиль: Noob_2026 (Premium игрок)")
end)

-- ────────────────────────── ГЛАВНЫЙ ЦИКЛ РЕНДЕРИНГА И РЕСАЙЗА ──────────────────────────
local last_sw, last_sh = -1, -1
local last_cat = ""
local last_launcher = false
local last_robux = false
local last_info = false
local last_sel_id = -1
local last_toast = ""
local last_scroll_y = -999999

while true do
    local sw, sh = drawer.get_size_screen()
    if not sw or not sh then
        sw, sh = 1280, 720
    end

    if toast_time > 0 then
        toast_time = toast_time - 1
        if toast_time == 0 then
            toast_msg = ""
        end
    end

    local cur_scroll = 0
    if screen and screen.get_scroll_y then
        cur_scroll = screen.get_scroll_y() or 0
    end

    local page_layout_needed = (sw ~= last_sw) or (sh ~= last_sh) or (current_cat ~= last_cat)
    local any_modal_active = is_launcher_open or is_robux_open or is_info_open or (toast_msg ~= "")
    local modal_state_changed = (is_launcher_open ~= last_launcher) or (is_robux_open ~= last_robux)
                             or (is_info_open ~= last_info) or (selected_game.id ~= last_sel_id)
                             or (toast_msg ~= last_toast)
    local scroll_moved = any_modal_active and (math.abs(cur_scroll - last_scroll_y) > 0.5)

    if page_layout_needed then
        last_sw, last_sh = sw, sh
        last_cat = current_cat

        -- 1. ШАПКА (HEADER)
        local h_h = 56
        header_bg:set_position(0, 0)
        header_bg:set_size(sw, h_h)

        header_border:set_position(0, h_h - 1)
        header_border:set_size(sw, 1)

        logo_icon:set_position(24, 13)
        logo_icon:set_size(30, 30)

        logo_text:set_position(62, 17)

        nav_btn_discover:set_position(170, 12)
        nav_btn_discover:set_size(75, 32)

        nav_btn_market:set_position(252, 12)
        nav_btn_market:set_size(75, 32)

        nav_btn_create:set_position(334, 12)
        nav_btn_create:set_size(75, 32)

        local profile_w = 120
        local robux_w = 135
        local right_x = sw - 24

        profile_btn:set_size(profile_w, 34)
        profile_btn:set_position(right_x - profile_w, 11)

        header_robux_btn:set_size(robux_w, 34)
        header_robux_btn:set_position(right_x - profile_w - robux_w - 12, 11)

        local search_x = 425
        local search_w = math.max(120, (right_x - profile_w - robux_w - 24) - search_x)
        if search_w > 150 then
            search_bar:set_position(search_x, 11)
            search_bar:set_size(search_w, 34)
        else
            search_bar:set_position(-3000, -3000)
        end

        -- 2. ГЕРОЙ-СЕКЦИЯ (HERO)
        local pad_x = math.max(20, sw * 0.03)
        local hero_y = h_h + 16
        local hero_w = sw - pad_x * 2
        local hero_h = 135

        hero_bg:set_position(pad_x, hero_y)
        hero_bg:set_size(hero_w, hero_h)

        hero_accent:set_position(pad_x, hero_y)
        hero_accent:set_size(5, hero_h)

        hero_badge:set_position(pad_x + 22, hero_y + 16)
        hero_badge:set_size(210, 24)

        hero_title:set_position(pad_x + 22, hero_y + 46)
        hero_desc:set_position(pad_x + 22, hero_y + 76)

        local hero_btn_w = math.min(170, hero_w * 0.22)
        local hero_btn_x = pad_x + hero_w - hero_btn_w - 20
        hero_play_btn:set_size(hero_btn_w, 38)
        hero_play_btn:set_position(hero_btn_x, hero_y + 24)

        hero_robux_btn:set_size(hero_btn_w, 36)
        hero_robux_btn:set_position(hero_btn_x, hero_y + 70)

        hero_stat1:set_position(pad_x + 22, hero_y + 102)
        hero_stat1:set_size(125, 22)

        hero_stat2:set_position(pad_x + 155, hero_y + 102)
        hero_stat2:set_size(125, 22)

        hero_stat3:set_position(pad_x + 288, hero_y + 102)
        hero_stat3:set_size(150, 22)

        -- 3. ВКЛАДКИ КАТЕГОРИЙ
        local tab_y = hero_y + hero_h + 18
        local cur_tab_x = pad_x
        local tab_gap = 10
        for _, cb in ipairs(cat_buttons) do
            local tab_w = 125
            cb.btn:set_position(cur_tab_x, tab_y)
            cb.btn:set_size(tab_w, 32)
            cur_tab_x = cur_tab_x + tab_w + tab_gap
        end

        -- 4. СЕТКА КАРТОЧЕК ИГР (3 СЕКЦИИ ПО 3 КАРТОЧКИ)
        local cols = 3
        local gap_x = 16
        local card_w = (hero_w - (cols - 1) * gap_x) / cols
        local card_h = 165

        -- Секция 1: Топ тренды
        local sec1_y = tab_y + 44
        sec1_title:set_position(pad_x, sec1_y)
        local row1_y = sec1_y + 28

        -- Секция 2: Экшен & Хорроры (начинается вокруг 620-700px, переходя за нижнюю границу)
        local sec2_y = row1_y + card_h + 24
        sec2_title:set_position(pad_x, sec2_y)
        local row2_y = sec2_y + 28

        -- Секция 3: Новые хиты (начинается на ~900px, глубоко ниже экрана)
        local sec3_y = row2_y + card_h + 24
        sec3_title:set_position(pad_x, sec3_y)
        local row3_y = sec3_y + 28

        local row_starts = { row1_y, row2_y, row3_y }

        for i, cw in ipairs(card_widgets) do
            local is_visible = false
            if current_cat == "all" then
                is_visible = true
            elseif current_cat == "trending" and cw.game.trending then
                is_visible = true
            elseif cw.game.category == current_cat then
                is_visible = true
            end

            if is_visible then
                local row_idx = math.floor((i - 1) / cols) + 1
                local col_idx = (i - 1) % cols

                local cx = pad_x + col_idx * (card_w + gap_x)
                local cy = row_starts[row_idx] or (row3_y + (row_idx - 3) * (card_h + 24))

                cw.bg:set_position(cx, cy)
                cw.bg:set_size(card_w, card_h)

                local in_pad = 16
                cw.tag:set_position(cx + in_pad, cy + 14)
                cw.tag:set_size(105, 20)

                cw.title:set_position(cx + in_pad, cy + 40)
                cw.online:set_position(cx + in_pad, cy + 64)
                cw.rating:set_position(cx + card_w - in_pad, cy + 64)

                cw.desc:set_position(cx + in_pad, cy + 86)

                local btn_h = 32
                local btn_play_w = math.max(85, card_w * 0.42)
                local btn_info_w = math.max(70, card_w * 0.32)
                local btn_y = cy + card_h - btn_h - 12

                cw.play:set_size(btn_play_w, btn_h)
                cw.play:set_position(cx + in_pad, btn_y)

                cw.info:set_size(btn_info_w, btn_h)
                cw.info:set_position(cx + in_pad + btn_play_w + 10, btn_y)
            else
                cw.bg:set_position(-3000, -3000)
                cw.tag:set_position(-3000, -3000)
                cw.title:set_position(-3000, -3000)
                cw.online:set_position(-3000, -3000)
                cw.rating:set_position(-3000, -3000)
                cw.desc:set_position(-3000, -3000)
                cw.play:set_position(-3000, -3000)
                cw.info:set_position(-3000, -3000)
            end
        end

        -- 5. СЕКЦИЯ МАГАЗИНА ROBUX НА СТРАНИЦЕ (на ~1150px)
        local robux_sec_y = row3_y + card_h + 30
        robux_sec_title:set_position(pad_x, robux_sec_y)
        robux_sec_sub:set_position(pad_x, robux_sec_y + 24)

        local r_cards_y = robux_sec_y + 48
        local r_cols = 4
        local r_gap = 14
        local r_card_w = (hero_w - (r_cols - 1) * r_gap) / r_cols
        local r_card_h = 105

        for i, rpc in ipairs(robux_page_cards) do
            local rcx = pad_x + (i - 1) * (r_card_w + r_gap)
            local rcy = r_cards_y

            rpc.bg:set_position(rcx, rcy)
            rpc.bg:set_size(r_card_w, r_card_h)

            rpc.badge:set_position(rcx + (r_card_w - 90) / 2, rcy + 10)
            rpc.badge:set_size(90, 18)

            rpc.val:set_position(rcx + r_card_w / 2, rcy + 36)

            local buy_w = math.max(100, r_card_w - 28)
            rpc.btn:set_position(rcx + (r_card_w - buy_w) / 2, rcy + r_card_h - 36)
            rpc.btn:set_size(buy_w, 28)
        end

        -- 6. СЕКЦИЯ ПРЕИМУЩЕСТВ ПЛАТФОРМЫ (на ~1320px)
        local feat_sec_y = r_cards_y + r_card_h + 30
        feat_sec_title:set_position(pad_x, feat_sec_y)

        local feat_cards_y = feat_sec_y + 28
        local f_cols = 3
        local f_gap = 16
        local f_card_w = (hero_w - (f_cols - 1) * f_gap) / f_cols
        local f_card_h = 80

        for i, fw in ipairs(feat_widgets) do
            local fcx = pad_x + (i - 1) * (f_card_w + f_gap)
            local fcy = feat_cards_y

            fw.bg:set_position(fcx, fcy)
            fw.bg:set_size(f_card_w, f_card_h)

            fw.title:set_position(fcx + 16, fcy + 14)
            fw.text:set_position(fcx + 16, fcy + 38)
        end

        -- 7. ПОДВАЛ (FOOTER) (на ~1460px)
        local footer_y = feat_cards_y + f_card_h + 35
        footer_line:set_position(pad_x, footer_y)
        footer_line:set_size(hero_w, 1)

        footer_links_txt:set_position(sw / 2, footer_y + 16)
        footer_copy_txt:set_position(sw / 2, footer_y + 38)
    end

    if modal_state_changed or scroll_moved or page_layout_needed then
        last_launcher = is_launcher_open
        last_robux = is_robux_open
        last_info = is_info_open
        last_sel_id = selected_game.id
        last_toast = toast_msg
        last_scroll_y = cur_scroll

        -- 8. МОДАЛЬНОЕ ОКНО 1: ЛАУНЧЕР ИГРЫ (компенсирует скролл, оставаясь по центру экрана)
        if is_launcher_open then
            modal_overlay:set_position(0, -cur_scroll)
            modal_overlay:set_size(sw, sh)

            local mw = math.min(520, sw * 0.92)
            local mh = math.min(420, sh * 0.88)
            local mx = (sw - mw) / 2
            local my = (sh - mh) / 2 - cur_scroll

            launch_box:set_position(mx, my)
            launch_box:set_size(mw, mh)

            launch_header_bar:set_position(mx, my)
            launch_header_bar:set_size(mw, 65)

            launch_title:set_position(mx + 24, my + 14)
            launch_sub:set_text("Плейс: " .. selected_game.title .. " • " .. selected_game.genre)
            launch_sub:set_position(mx + 24, my + 40)

            launch_close:set_position(mx + mw - 44, my + 14)
            launch_close:set_size(32, 32)

            launch_banner:set_position(mx + 24, my + 82)
            launch_banner:set_size(mw - 48, 36)

            local info_w = (mw - 48 - 12) / 2
            launch_info1:set_text("👑 " .. selected_game.creator)
            launch_info1:set_position(mx + 24, my + 128)
            launch_info1:set_size(info_w, 36)

            launch_info2:set_text("👁️ " .. selected_game.visits .. " посещений")
            launch_info2:set_position(mx + 24 + info_w + 12, my + 128)
            launch_info2:set_size(info_w, 36)

            launch_status:set_position(mx + mw / 2, my + 185)

            launch_start_btn:set_position(mx + 24, my + mh - 120)
            launch_start_btn:set_size(mw - 48, 46)
            launch_start_btn:set_text("▶ Запустить плейс в Roblox")
            launch_start_btn:set_color("#00B06F")

            launch_fav_btn:set_position(mx + 24, my + mh - 64)
            launch_fav_btn:set_size(mw - 48, 38)
        else
            launch_box:set_position(-3000, -3000)
            launch_header_bar:set_position(-3000, -3000)
            launch_title:set_position(-3000, -3000)
            launch_sub:set_position(-3000, -3000)
            launch_close:set_position(-3000, -3000)
            launch_banner:set_position(-3000, -3000)
            launch_info1:set_position(-3000, -3000)
            launch_info2:set_position(-3000, -3000)
            launch_status:set_position(-3000, -3000)
            launch_start_btn:set_position(-3000, -3000)
            launch_fav_btn:set_position(-3000, -3000)
        end

        -- 9. МОДАЛЬНОЕ ОКНО 2: МАГАЗИН ROBUX
        if is_robux_open then
            modal_overlay:set_position(0, -cur_scroll)
            modal_overlay:set_size(sw, sh)

            local mw = math.min(540, sw * 0.92)
            local mh = math.min(440, sh * 0.88)
            local mx = (sw - mw) / 2
            local my = (sh - mh) / 2 - cur_scroll

            robux_box:set_position(mx, my)
            robux_box:set_size(mw, mh)

            robux_title:set_position(mx + 24, my + 18)
            robux_balance_txt:set_position(mx + 24, my + 44)

            robux_close:set_position(mx + mw - 44, my + 14)
            robux_close:set_size(32, 32)

            local bundle_y = my + 78
            local bundle_h = 56
            local gap = 12

            for i, bw in ipairs(robux_bundle_widgets) do
                local cy = bundle_y + (i - 1) * (bundle_h + gap)

                bw.card:set_position(mx + 24, cy)
                bw.card:set_size(mw - 48, bundle_h)

                bw.amount:set_position(mx + 40, cy + 12)
                bw.tag:set_position(mx + 40, cy + 32)

                local btn_w = 110
                local btn_h = 36
                bw.buy:set_position(mx + mw - 48 - btn_w - 12, cy + (bundle_h - btn_h) / 2)
                bw.buy:set_size(btn_w, btn_h)
            end
        else
            robux_box:set_position(-3000, -3000)
            robux_title:set_position(-3000, -3000)
            robux_balance_txt:set_position(-3000, -3000)
            robux_close:set_position(-3000, -3000)
            for _, bw in ipairs(robux_bundle_widgets) do
                bw.card:set_position(-3000, -3000)
                bw.amount:set_position(-3000, -3000)
                bw.tag:set_position(-3000, -3000)
                bw.buy:set_position(-3000, -3000)
            end
        end

        -- 10. МОДАЛЬНОЕ ОКНО 3: ИНФО О ПЛЕЙСЕ
        if is_info_open then
            modal_overlay:set_position(0, -cur_scroll)
            modal_overlay:set_size(sw, sh)

            local mw = math.min(500, sw * 0.9)
            local mh = math.min(360, sh * 0.8)
            local mx = (sw - mw) / 2
            local my = (sh - mh) / 2 - cur_scroll

            info_box:set_position(mx, my)
            info_box:set_size(mw, mh)

            info_title:set_position(mx + 24, my + 18)
            info_close:set_position(mx + mw - 44, my + 14)
            info_close:set_size(32, 32)

            info_game_name:set_text(selected_game.title)
            info_game_name:set_position(mx + 24, my + 60)

            info_game_author:set_text("Создатель: " .. selected_game.creator .. "  |  Жанр: " .. selected_game.genre)
            info_game_author:set_position(mx + 24, my + 90)

            info_game_desc:set_text("Описание: " .. selected_game.desc)
            info_game_desc:set_position(mx + 24, my + 120)

            info_game_stats:set_text("Всего визитов: " .. selected_game.visits .. "  •  " .. selected_game.online_str)
            info_game_stats:set_position(mx + 24, my + 155)

            info_ok_btn:set_position(mx + 24, my + mh - 55)
            info_ok_btn:set_size(mw - 48, 40)
        else
            info_box:set_position(-3000, -3000)
            info_title:set_position(-3000, -3000)
            info_close:set_position(-3000, -3000)
            info_game_name:set_position(-3000, -3000)
            info_game_author:set_position(-3000, -3000)
            info_game_desc:set_position(-3000, -3000)
            info_game_stats:set_position(-3000, -3000)
            info_ok_btn:set_position(-3000, -3000)
        end

        -- Оверлей
        if not is_launcher_open and not is_robux_open and not is_info_open then
            modal_overlay:set_position(-3000, -3000)
        end

        -- 11. ТОСТ-УВЕДОМЛЕНИЕ
        if toast_msg ~= "" then
            local tw = math.min(380, sw * 0.8)
            local th = 40
            local tx = (sw - tw) / 2
            local ty = sh - th - 20 - cur_scroll

            toast_bg:set_position(tx, ty)
            toast_bg:set_size(tw, th)

            toast_txt:set_text(toast_msg)
            toast_txt:set_position(tx + tw / 2, ty + 12)
        else
            toast_bg:set_position(-3000, -3000)
            toast_txt:set_position(-3000, -3000)
        end
    end

    sleep(0.016)
end
