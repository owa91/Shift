-- Ping-Pong: move the mouse up/down to control the left paddle.
-- Click to serve the ball. First to WIN_SCORE wins.

screen.set_scrolling_status(false, false, true)
drawer.fill_background("#0b0f1a")

local W, H = drawer.get_size_screen()

local WIN_SCORE = 7
local PADDLE_W, PADDLE_H, BALL, MARGIN = 14, 80, 14, 30
local AI_SPEED, BASE_SPEED, MAX_SPEED = 330, 380, 900
local DT = 1 / 60
local DASHES = 80

-- Visuals --------------------------------------------------------------
local dashes = {}
for i = 1, DASHES do
    local seg = drawer.rectangle(0, 0, 0, 0)
    seg.set_color("#2a3350")
    dashes[i] = seg
end

local left = drawer.rectangle(0, 0, 10, 10)
left.set_color("#4ade80")
local right = drawer.rectangle(0, 0, 10, 10)
right.set_color("#f87171")
local ball = drawer.rectangle(0, 0, 10, 10)
ball.set_color("#ffffff")

local score_l = drawer.text(0, 20, "0", 48, "Calibri", "Bold", "#4ade80", "center")
local score_r = drawer.text(0, 20, "0", 48, "Calibri", "Bold", "#f87171", "center")
local info = drawer.text(0, 0, "Click to serve", 28, "Calibri", "Regular", "#cbd5e1", "center")

-- State ----------------------------------------------------------------
local lp, rp = 0, 0
local ly, ry = 0, 0
local bx, by = 0, 0
local vx, vy = 0, 0
local speed = BASE_SPEED
local playing = false
local was_down = false

local function clamp(v, a, b)
    if v < a then return a end
    if v > b then return b end
    return v
end

-- Recompute all sizes/positions for the current window size.
-- Dynamic values (positions, velocities) are rescaled proportionally.
local function layout(newW, newH)
    local ow, oh = W, H
    local first = (ow == nil)
    W, H = newW, newH
    local sx, sy = W / (ow or W), H / (oh or H)
    local s = math.min(W / 1280, H / 700)
    s = clamp(s, 0.5, 2.5)

    PADDLE_W = math.max(8, 14 * s)
    PADDLE_H = math.max(50, H * 0.18)
    BALL = math.max(8, 14 * s)
    MARGIN = math.max(15, W * 0.03)
    BASE_SPEED, MAX_SPEED = 380 * (W / 1280), 900 * (W / 1280)
    AI_SPEED = 330 * (H / 700)

    ly, ry = ly * sy, ry * sy
    bx, by = bx * sx, by * sy
    vx, vy = vx * sx, vy * sy
    speed = speed * sx

    left.set_size(PADDLE_W, PADDLE_H)
    right.set_size(PADDLE_W, PADDLE_H)
    ball.set_size(BALL, BALL)

    local dash_h, gap = math.max(10, H * 0.025), math.max(10, H * 0.025)
    local step = dash_h + gap
    for i = 1, DASHES do
        local y = (i - 1) * step + gap / 2
        if y < H then
            dashes[i].set_size(math.max(2, 4 * s), math.min(dash_h, H - y))
            dashes[i].set_position(W / 2 - 2 * s, y)
        else
            dashes[i].set_size(0, 0)
        end
    end

    score_l.set_position(W / 2 - W * 0.06, 20)
    score_r.set_position(W / 2 + W * 0.06, 20)
    info.set_position(W / 2, H / 2 + 60)
end

local function reset_ball()
    bx, by = W / 2 - BALL / 2, H / 2 - BALL / 2
    vx, vy = 0, 0
end

local function serve(dir)
    reset_ball()
    speed = BASE_SPEED
    local angle = (math.random() - 0.5) * 0.9
    vx = math.cos(angle) * speed * dir
    vy = math.sin(angle) * speed
    playing = true
    info.set_text("")
end

local function bounce_off(paddle_y, dir)
    local rel = ((by + BALL / 2) - (paddle_y + PADDLE_H / 2)) / (PADDLE_H / 2)
    rel = clamp(rel, -1, 1)
    speed = math.min(MAX_SPEED, speed * 1.06)
    vx = math.cos(rel) * speed * dir
    vy = math.sin(rel) * speed
end

local function point_scored(left_won)
    playing = false
    if left_won then lp = lp + 1 else rp = rp + 1 end
    score_l.set_text(tostring(lp))
    score_r.set_text(tostring(rp))
    reset_ball()

    if lp >= WIN_SCORE or rp >= WIN_SCORE then
        info.set_text((lp > rp and "You win!" or "Computer wins!") .. "  Click to play again")
        lp, rp = 0, 0
        score_l.set_text("0")
        score_r.set_text("0")
    else
        info.set_text("Click to serve")
    end
end

-- initial layout
do
    local w0, h0 = W, H
    W, H = nil, nil
    ly, ry = h0 / 2 - 40, h0 / 2 - 40
    layout(w0, h0)
    ly, ry = H / 2 - PADDLE_H / 2, H / 2 - PADDLE_H / 2
    reset_ball()
end
-- Main loop ------------------------------------------------------------
while true do
    local nw, nh = drawer.get_size_screen()
    if nw ~= W or nh ~= H then layout(nw, nh) end

    local mx, my, down, inside = drawer.get_mouse()

    -- player paddle follows the mouse
    if inside then
        ly = clamp(my - PADDLE_H / 2, 0, H - PADDLE_H)
    end

    -- click to serve
    if down and not was_down and not playing then
        serve((lp + rp) % 2 == 0 and 1 or -1)
    end
    was_down = down

    if playing then
        bx = bx + vx * DT
        by = by + vy * DT

        -- walls
        if by <= 0 then by = 0; vy = math.abs(vy) end
        if by + BALL >= H then by = H - BALL; vy = -math.abs(vy) end

        -- left paddle
        local lx = MARGIN + PADDLE_W
        if vx < 0 and bx <= lx and bx + BALL >= MARGIN
           and by + BALL >= ly and by <= ly + PADDLE_H then
            bx = lx
            bounce_off(ly, 1)
        end

        -- right paddle
        local rx = W - MARGIN - PADDLE_W
        if vx > 0 and bx + BALL >= rx and bx <= rx + PADDLE_W
           and by + BALL >= ry and by <= ry + PADDLE_H then
            bx = rx - BALL
            bounce_off(ry, -1)
        end

        -- AI paddle: follows the ball (only when it comes towards it)
        local target = by + BALL / 2 - PADDLE_H / 2
        if vx < 0 then target = H / 2 - PADDLE_H / 2 end
        local diff = target - ry
        local step = AI_SPEED * DT
        if math.abs(diff) > step then
            ry = ry + (diff > 0 and step or -step)
        else
            ry = target
        end
        ry = clamp(ry, 0, H - PADDLE_H)

        -- scoring
        if bx + BALL < 0 then point_scored(false)
        elseif bx > W then point_scored(true) end
    else
        -- idle: AI paddle drifts to center
        ry = ry + (H / 2 - PADDLE_H / 2 - ry) * 0.1
    end

    left.set_position(MARGIN, ly)
    right.set_position(W - MARGIN - PADDLE_W, ry)
    ball.set_position(bx, by)

    sleep(DT)
end
