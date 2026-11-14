-- Chess vs AI in Shift browser (new.lua)
-- Full chess rules: legal move validation (checks, pins, castling, en passant, promotion),
-- minimax with alpha-beta pruning and 3 difficulty levels, auto-sizing UI.

screen.set_scrolling_status(false, false, true)
drawer.fill_background("#16181f")

-- Constants & Piece Definitions
local WHITE, BLACK = 1, -1
local PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 1, 2, 3, 4, 5, 6

local PIECE_SYMBOLS = {
    [WHITE] = {
        [PAWN]   = "♟",
        [KNIGHT] = "♞",
        [BISHOP] = "♝",
        [ROOK]   = "♜",
        [QUEEN]  = "♛",
        [KING]   = "♚",
    },
    [BLACK] = {
        [PAWN]   = "♟",
        [KNIGHT] = "♞",
        [BISHOP] = "♝",
        [ROOK]   = "♜",
        [QUEEN]  = "♛",
        [KING]   = "♚",
    }
}

local PIECE_VALUES = {
    [PAWN] = 100,
    [KNIGHT] = 320,
    [BISHOP] = 330,
    [ROOK] = 500,
    [QUEEN] = 900,
    [KING] = 20000
}

-- Positional tables (from white's perspective, r=1..8 bottom-to-top)
local PST = {
    [PAWN] = {
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0
    },
    [KNIGHT] = {
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    },
    [BISHOP] = {
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    },
    [ROOK] = {
          0,  0,  0,  0,  0,  0,  0,  0,
          5, 10, 10, 10, 10, 10, 10,  5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
          0,  0,  0,  5,  5,  0,  0,  0
    },
    [QUEEN] = {
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    },
    [KING] = {
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20
    }
}

-- Game State representation
local game = {
    board = {},        -- 8x8 table: board[r][c] = { piece = PAWN..KING, color = WHITE|BLACK } or nil
    turn = WHITE,
    castling = {
        [WHITE] = { K = true, Q = true },
        [BLACK] = { K = true, Q = true }
    },
    ep = nil,          -- en passant target square: { r = ..., c = ... }
    game_over = false,
    status_text = "Ваш ход (Белые)",
    selected = nil,    -- { r = ..., c = ... }
    valid_moves = {},  -- list of { from_r, from_c, to_r, to_c, promo }
    last_move = nil,   -- { from_r, from_c, to_r, to_c }
    difficulty = 2,    -- 1: Новичок (глубина 1), 2: Любитель (глубина 2), 3: Мастер (глубина 3)
    ai_thinking = false,
    history = {}
}

local function copy_state(st)
    local nb = {}
    for r = 1, 8 do
        nb[r] = {}
        for c = 1, 8 do
            local p = st.board[r][c]
            if p then nb[r][c] = { piece = p.piece, color = p.color } else nb[r][c] = nil end
        end
    end
    return {
        board = nb,
        turn = st.turn,
        castling = {
            [WHITE] = { K = st.castling[WHITE].K, Q = st.castling[WHITE].Q },
            [BLACK] = { K = st.castling[BLACK].K, Q = st.castling[BLACK].Q }
        },
        ep = st.ep and { r = st.ep.r, c = st.ep.c } or nil
    }
end

local function init_board()
    game.board = {}
    for r = 1, 8 do
        game.board[r] = {}
        for c = 1, 8 do game.board[r][c] = nil end
    end

    local back = { ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK }
    for c = 1, 8 do
        game.board[1][c] = { piece = back[c], color = WHITE }
        game.board[2][c] = { piece = PAWN, color = WHITE }
        game.board[7][c] = { piece = PAWN, color = BLACK }
        game.board[8][c] = { piece = back[c], color = BLACK }
    end

    game.turn = WHITE
    game.castling = {
        [WHITE] = { K = true, Q = true },
        [BLACK] = { K = true, Q = true }
    }
    game.ep = nil
    game.game_over = false
    game.selected = nil
    game.valid_moves = {}
    game.last_move = nil
    game.ai_thinking = false
    game.status_text = "Ваш ход (Белые)"
end

-- Move Generation and Rules
local function is_square_attacked(b, r, c, by_color)
    -- Pawn attacks
    local p_dir = (by_color == WHITE) and -1 or 1 -- direction from attacker's pos
    local pr = r + p_dir
    if pr >= 1 and pr <= 8 then
        if c - 1 >= 1 then
            local p = b[pr][c - 1]
            if p and p.color == by_color and p.piece == PAWN then return true end
        end
        if c + 1 <= 8 then
            local p = b[pr][c + 1]
            if p and p.color == by_color and p.piece == PAWN then return true end
        end
    end

    -- Knight attacks
    local k_diffs = {
        {-2,-1},{-2,1},{-1,-2},{-1,2},
        {1,-2},{1,2},{2,-1},{2,1}
    }
    for _, d in ipairs(k_diffs) do
        local nr, nc = r + d[1], c + d[2]
        if nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 then
            local p = b[nr][nc]
            if p and p.color == by_color and p.piece == KNIGHT then return true end
        end
    end

    -- King attacks
    for dr = -1, 1 do
        for dc = -1, 1 do
            if dr ~= 0 or dc ~= 0 then
                local nr, nc = r + dr, c + dc
                if nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 then
                    local p = b[nr][nc]
                    if p and p.color == by_color and p.piece == KING then return true end
                end
            end
        end
    end

    -- Straight (Rook/Queen)
    local dirs = {{0,1},{0,-1},{1,0},{-1,0}}
    for _, d in ipairs(dirs) do
        local nr, nc = r + d[1], c + d[2]
        while nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 do
            local p = b[nr][nc]
            if p then
                if p.color == by_color and (p.piece == ROOK or p.piece == QUEEN) then return true end
                break
            end
            nr, nc = nr + d[1], nc + d[2]
        end
    end

    -- Diagonal (Bishop/Queen)
    local d_dirs = {{1,1},{1,-1},{-1,1},{-1,-1}}
    for _, d in ipairs(d_dirs) do
        local nr, nc = r + d[1], c + d[2]
        while nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 do
            local p = b[nr][nc]
            if p then
                if p.color == by_color and (p.piece == BISHOP or p.piece == QUEEN) then return true end
                break
            end
            nr, nc = nr + d[1], nc + d[2]
        end
    end

    return false
end

local function find_king(b, color)
    for r = 1, 8 do
        for c = 1, 8 do
            local p = b[r][c]
            if p and p.color == color and p.piece == KING then
                return r, c
            end
        end
    end
    return nil, nil
end

local function in_check(st, color)
    local kr, kc = find_king(st.board, color)
    if not kr then return false end
    return is_square_attacked(st.board, kr, kc, -color)
end

-- Apply move to state (mutates st)
local function apply_move(st, m)
    local p = st.board[m.from_r][m.from_c]
    local target = st.board[m.to_r][m.to_c]

    -- En passant capture
    if p.piece == PAWN and st.ep and m.to_r == st.ep.r and m.to_c == st.ep.c then
        st.board[m.from_r][m.to_c] = nil
    end

    -- Move piece
    st.board[m.to_r][m.to_c] = p
    st.board[m.from_r][m.from_c] = nil

    -- Pawn promotion
    if p.piece == PAWN and (m.to_r == 8 or m.to_r == 1) then
        p.piece = m.promo or QUEEN
    end

    -- Castling move (king jumped 2 squares)
    if p.piece == KING and math.abs(m.to_c - m.from_c) == 2 then
        if m.to_c == 7 then -- King side
            local rook = st.board[m.from_r][8]
            st.board[m.from_r][6] = rook
            st.board[m.from_r][8] = nil
        elseif m.to_c == 3 then -- Queen side
            local rook = st.board[m.from_r][1]
            st.board[m.from_r][4] = rook
            st.board[m.from_r][1] = nil
        end
    end

    -- Update castling rights
    if p.piece == KING then
        st.castling[p.color].K = false
        st.castling[p.color].Q = false
    elseif p.piece == ROOK then
        if m.from_r == 1 and m.from_c == 1 then st.castling[WHITE].Q = false end
        if m.from_r == 1 and m.from_c == 8 then st.castling[WHITE].K = false end
        if m.from_r == 8 and m.from_c == 1 then st.castling[BLACK].Q = false end
        if m.from_r == 8 and m.from_c == 8 then st.castling[BLACK].K = false end
    end
    if target and target.piece == ROOK then
        if m.to_r == 1 and m.to_c == 1 then st.castling[WHITE].Q = false end
        if m.to_r == 1 and m.to_c == 8 then st.castling[WHITE].K = false end
        if m.to_r == 8 and m.to_c == 1 then st.castling[BLACK].Q = false end
        if m.to_r == 8 and m.to_c == 8 then st.castling[BLACK].K = false end
    end

    -- Update en passant target
    if p.piece == PAWN and math.abs(m.to_r - m.from_r) == 2 then
        st.ep = { r = (m.from_r + m.to_r) // 2, c = m.from_c }
    else
        st.ep = nil
    end

    st.turn = -st.turn
end

local function generate_pseudo_moves(st, color)
    local moves = {}
    local b = st.board
    local fwd = (color == WHITE) and 1 or -1
    local start_row = (color == WHITE) and 2 or 7
    local promo_row = (color == WHITE) and 8 or 1

    for r = 1, 8 do
        for c = 1, 8 do
            local p = b[r][c]
            if p and p.color == color then
                if p.piece == PAWN then
                    -- 1 square forward
                    local nr = r + fwd
                    if nr >= 1 and nr <= 8 and not b[nr][c] then
                        if nr == promo_row then
                            for _, promo_p in ipairs({QUEEN, KNIGHT, ROOK, BISHOP}) do
                                moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = c, promo = promo_p }
                            end
                        else
                            moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = c }
                            -- 2 squares forward
                            if r == start_row and not b[r + 2 * fwd][c] then
                                moves[#moves+1] = { from_r = r, from_c = c, to_r = r + 2 * fwd, to_c = c }
                            end
                        end
                    end
                    -- Captures
                    for _, dc in ipairs({-1, 1}) do
                        local nc = c + dc
                        if nc >= 1 and nc <= 8 and nr >= 1 and nr <= 8 then
                            local dest = b[nr][nc]
                            if dest and dest.color == -color then
                                if nr == promo_row then
                                    for _, promo_p in ipairs({QUEEN, KNIGHT, ROOK, BISHOP}) do
                                        moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc, promo = promo_p }
                                    end
                                else
                                    moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc }
                                end
                            elseif st.ep and nr == st.ep.r and nc == st.ep.c then
                                moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc }
                            end
                        end
                    end
                elseif p.piece == KNIGHT then
                    local k_diffs = {{-2,-1},{-2,1},{-1,-2},{-1,2},{1,-2},{1,2},{2,-1},{2,1}}
                    for _, d in ipairs(k_diffs) do
                        local nr, nc = r + d[1], c + d[2]
                        if nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 then
                            local dest = b[nr][nc]
                            if not dest or dest.color == -color then
                                moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc }
                            end
                        end
                    end
                elseif p.piece == KING then
                    for dr = -1, 1 do
                        for dc = -1, 1 do
                            if dr ~= 0 or dc ~= 0 then
                                local nr, nc = r + dr, c + dc
                                if nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 then
                                    local dest = b[nr][nc]
                                    if not dest or dest.color == -color then
                                        moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc }
                                    end
                                end
                            end
                        end
                    end
                    -- Castling
                    local k_row = (color == WHITE) and 1 or 8
                    if r == k_row and c == 5 and not in_check(st, color) then
                        -- Kingside
                        if st.castling[color].K and not b[k_row][6] and not b[k_row][7] then
                            if not is_square_attacked(b, k_row, 6, -color) and not is_square_attacked(b, k_row, 7, -color) then
                                local rk = b[k_row][8]
                                if rk and rk.piece == ROOK and rk.color == color then
                                    moves[#moves+1] = { from_r = r, from_c = c, to_r = k_row, to_c = 7 }
                                end
                            end
                        end
                        -- Queenside
                        if st.castling[color].Q and not b[k_row][4] and not b[k_row][3] and not b[k_row][2] then
                            if not is_square_attacked(b, k_row, 4, -color) and not is_square_attacked(b, k_row, 3, -color) then
                                local rk = b[k_row][1]
                                if rk and rk.piece == ROOK and rk.color == color then
                                    moves[#moves+1] = { from_r = r, from_c = c, to_r = k_row, to_c = 3 }
                                end
                            end
                        end
                    end
                else
                    -- Sliding pieces: Bishop, Rook, Queen
                    local dirs = {}
                    if p.piece == BISHOP or p.piece == QUEEN then
                        table.insert(dirs, {1,1}); table.insert(dirs, {1,-1}); table.insert(dirs, {-1,1}); table.insert(dirs, {-1,-1})
                    end
                    if p.piece == ROOK or p.piece == QUEEN then
                        table.insert(dirs, {0,1}); table.insert(dirs, {0,-1}); table.insert(dirs, {1,0}); table.insert(dirs, {-1,0})
                    end
                    for _, d in ipairs(dirs) do
                        local nr, nc = r + d[1], c + d[2]
                        while nr >= 1 and nr <= 8 and nc >= 1 and nc <= 8 do
                            local dest = b[nr][nc]
                            if not dest then
                                moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc }
                            else
                                if dest.color == -color then
                                    moves[#moves+1] = { from_r = r, from_c = c, to_r = nr, to_c = nc }
                                end
                                break
                            end
                            nr, nc = nr + d[1], nc + d[2]
                        end
                    end
                end
            end
        end
    end
    return moves
end

local function generate_legal_moves(st, color)
    local pseudo = generate_pseudo_moves(st, color)
    local legal = {}
    for _, m in ipairs(pseudo) do
        local nxt = copy_state(st)
        apply_move(nxt, m)
        if not in_check(nxt, color) then
            legal[#legal+1] = m
        end
    end
    return legal
end

-- Evaluation & AI (Minimax + Alpha-Beta)
local function evaluate_board(b)
    local score = 0
    for r = 1, 8 do
        for c = 1, 8 do
            local p = b[r][c]
            if p then
                local val = PIECE_VALUES[p.piece]
                local pst_tbl = PST[p.piece]
                local pst_val = 0
                if pst_tbl then
                    local idx
                    if p.color == WHITE then
                        idx = (8 - r) * 8 + c
                    else
                        idx = (r - 1) * 8 + c
                    end
                    pst_val = pst_tbl[idx] or 0
                end
                local total = val + pst_val
                if p.color == WHITE then
                    score = score + total
                else
                    score = score - total
                end
            end
        end
    end
    return score
end

local function minimax(st, depth, alpha, beta, is_maximizing)
    if depth == 0 then
        return evaluate_board(st.board), nil
    end

    local color = is_maximizing and WHITE or BLACK
    local legal = generate_legal_moves(st, color)

    if #legal == 0 then
        if in_check(st, color) then
            -- Checkmate
            return is_maximizing and -100000 or 100000, nil
        else
            -- Stalemate
            return 0, nil
        end
    end

    -- Move ordering heuristic: prefer captures for earlier pruning
    table.sort(legal, function(a, b)
        local tA = st.board[a.to_r][a.to_c]
        local tB = st.board[b.to_r][b.to_c]
        local valA = tA and PIECE_VALUES[tA.piece] or 0
        local valB = tB and PIECE_VALUES[tB.piece] or 0
        return valA > valB
    end)

    local best_move = nil
    if is_maximizing then
        local max_eval = -999999
        for _, m in ipairs(legal) do
            local nxt = copy_state(st)
            apply_move(nxt, m)
            local eval = minimax(nxt, depth - 1, alpha, beta, false)
            if eval > max_eval then
                max_eval = eval
                best_move = m
            end
            if eval > alpha then alpha = eval end
            if beta <= alpha then break end
        end
        return max_eval, best_move
    else
        local min_eval = 999999
        for _, m in ipairs(legal) do
            local nxt = copy_state(st)
            apply_move(nxt, m)
            local eval = minimax(nxt, depth - 1, alpha, beta, true)
            if depth == 1 and game.difficulty == 1 then
                eval = eval + math.random(-35, 35)
            end
            if eval < min_eval then
                min_eval = eval
                best_move = m
            end
            if eval < beta then beta = eval end
            if beta <= alpha then break end
        end
        return min_eval, best_move
    end
end

-- Visual Elements Creation
local HIDE_Y = -2000
local needs_redraw = false

local ui = {
    squares = {},         -- [r][c] = rectangle
    highlights = {},      -- [r][c] = rectangle (moves / selection)
    hover_hl = nil,       -- rectangle for mouse hover
    check_hl = nil,       -- rectangle for king in check pulse
    flash_hl = nil,       -- rectangle for capture flash
    pieces = {},          -- [r][c] = text
    capture_fade = nil,   -- text for fading out captured piece
    anim_piece = nil,     -- text for sliding moving piece
    anim_piece2 = nil,    -- text for sliding castling rook
    border = nil,
    title = nil,
    status = nil,
    turn_badge = nil,
    turn_badge_text = nil,
    difficulty_label = nil,
    diff_buttons = {},
    btn_new_game = nil,
    ranks = {},           -- 1..8 rank texts
    files = {},           -- 1..8 file texts
    ai_status = nil
}

local function style_piece_text(txt, color)
    if color == WHITE then
        txt.set_color("#ffffff")
        txt.set_outline("#111111", 2)
    else
        txt.set_color("#18191c")
        txt.set_outline("#eeeeee", 2)
    end
end

local function create_ui()
    ui.border = drawer.rectangle(0, HIDE_Y, 10, 10)
    ui.border.set_color("#2a2e3d")

    for r = 1, 8 do
        ui.squares[r] = {}
        ui.highlights[r] = {}
        ui.pieces[r] = {}
        for c = 1, 8 do
            local sq = drawer.rectangle(0, HIDE_Y, 10, 10)
            local is_light = ((r + c) % 2 == 1)
            sq.set_color(is_light and "#ebd0a9" or "#9e6e44")
            ui.squares[r][c] = sq

            local hl = drawer.rectangle(0, HIDE_Y, 10, 10)
            hl.set_color("#ffff00")
            ui.highlights[r][c] = hl
        end
    end

    ui.hover_hl = drawer.rectangle(0, HIDE_Y, 10, 10)
    ui.hover_hl.set_color("#ffffff")
    ui.check_hl = drawer.rectangle(0, HIDE_Y, 10, 10)
    ui.check_hl.set_color("#ef4444")
    ui.flash_hl = drawer.rectangle(0, HIDE_Y, 10, 10)
    ui.flash_hl.set_color("#fbbf24")

    for r = 1, 8 do
        for c = 1, 8 do
            local p = drawer.text(0, HIDE_Y, "", 36, "Segoe UI Symbol", "Regular", "#ffffff", "center")
            ui.pieces[r][c] = p
        end
    end

    -- Top-layer animated pieces (drawn above static board pieces)
    ui.capture_fade = drawer.text(0, HIDE_Y, "", 36, "Segoe UI Symbol", "Regular", "#ffffff", "center")
    ui.anim_piece = drawer.text(0, HIDE_Y, "", 36, "Segoe UI Symbol", "Regular", "#ffffff", "center")
    ui.anim_piece2 = drawer.text(0, HIDE_Y, "", 36, "Segoe UI Symbol", "Regular", "#ffffff", "center")

    for i = 1, 8 do
        ui.ranks[i] = drawer.text(0, HIDE_Y, tostring(i), 16, "Calibri", "Bold", "#8e95a5", "center")
        local f_name = string.char(string.byte('a') + i - 1)
        ui.files[i] = drawer.text(0, HIDE_Y, f_name, 16, "Calibri", "Bold", "#8e95a5", "center")
    end

    ui.title = drawer.text(0, HIDE_Y, "Шахматы против ИИ", 30, "Calibri", "Bold", "#ffffff", "left")
    ui.status = drawer.text(0, HIDE_Y, "", 20, "Calibri", "Regular", "#cbd5e1", "left")
    ui.ai_status = drawer.text(0, HIDE_Y, "", 16, "Calibri", "Italic", "#93c5fd", "left")

    ui.turn_badge = drawer.rectangle(0, HIDE_Y, 10, 10)
    ui.turn_badge.set_color("#ffffff")
    ui.turn_badge_text = drawer.text(0, HIDE_Y, "Белые", 18, "Calibri", "Bold", "#000000", "center")

    ui.difficulty_label = drawer.text(0, HIDE_Y, "Уровень сложности:", 18, "Calibri", "Bold", "#cbd5e1", "left")

    local diff_names = { "Новичок", "Любитель", "Мастер" }
    for i = 1, 3 do
        local b = drawer.button(0, HIDE_Y, diff_names[i])
        b.set_font_style("Calibri", "Regular", 16)
        b.set_border_corner(6)
        b.event("on_left_click", function()
            if not game.ai_thinking then
                game.difficulty = i
                game.status_text = "Сложность: " .. diff_names[i]
                needs_redraw = true
            end
        end)
        ui.diff_buttons[i] = b
    end

    ui.btn_new_game = drawer.button(0, HIDE_Y, "Новая игра")
    ui.btn_new_game.set_color("#2563eb")
    ui.btn_new_game.set_text_color("#ffffff")
    ui.btn_new_game.set_font_style("Calibri", "Bold", 18)
    ui.btn_new_game.set_border_corner(8)
    ui.btn_new_game.event("on_selected", function() ui.btn_new_game.set_color("#3b82f6") end)
    ui.btn_new_game.event("on_deselected", function() ui.btn_new_game.set_color("#2563eb") end)
    ui.btn_new_game.event("on_left_click", function()
        if not game.ai_thinking then
            init_board()
            needs_redraw = true
        end
    end)
end

-- Layout & Auto-sizing
local W, H = 0, 0
local board_x, board_y, board_size, cell_size = 0, 0, 0, 0

local function layout(new_w, new_h)
    W, H = new_w, new_h
    local s = math.max(0.6, math.min(W / 1280, H / 760))

    local margin_y = math.max(20, H * 0.05)
    local avail_h = H - margin_y * 2
    local avail_w = W * 0.60
    local b_dim = math.min(avail_h, avail_w)
    cell_size = math.max(30, math.floor(b_dim / 8))
    board_size = cell_size * 8

    board_x = math.max(30, math.floor(W * 0.06))
    board_y = math.floor((H - board_size) / 2)

    local border_pad = math.max(4, math.floor(6 * s))
    ui.border.set_position(board_x - border_pad, board_y - border_pad)
    ui.border.set_size(board_size + border_pad * 2, board_size + border_pad * 2)

    local piece_font_size = math.floor(cell_size * 0.72)

    for r = 1, 8 do
        for c = 1, 8 do
            -- White pieces at bottom: row 1 is at y bottom
            local screen_row = 8 - r + 1
            local x = board_x + (c - 1) * cell_size
            local y = board_y + (screen_row - 1) * cell_size

            ui.squares[r][c].set_position(x, y)
            ui.squares[r][c].set_size(cell_size, cell_size)

            ui.highlights[r][c].set_size(cell_size, cell_size)
            ui.highlights[r][c].set_corners(0, 0)

            ui.pieces[r][c].set_font_style("Segoe UI Symbol", "Regular", piece_font_size)
        end
    end

    ui.capture_fade.set_font_style("Segoe UI Symbol", "Regular", piece_font_size)
    ui.anim_piece.set_font_style("Segoe UI Symbol", "Regular", piece_font_size)
    ui.anim_piece2.set_font_style("Segoe UI Symbol", "Regular", piece_font_size)

    -- Coordinate markers
    for i = 1, 8 do
        local screen_row = 8 - i + 1
        local ry = board_y + (screen_row - 1) * cell_size + cell_size * 0.35
        ui.ranks[i].set_font_style("Calibri", "Bold", math.max(12, math.floor(16 * s)))
        ui.ranks[i].set_position(board_x - border_pad - 12 * s, ry)

        local fx = board_x + (i - 1) * cell_size + cell_size * 0.5
        ui.files[i].set_font_style("Calibri", "Bold", math.max(12, math.floor(16 * s)))
        ui.files[i].set_position(fx, board_y + board_size + border_pad + 6 * s)
    end

    -- Sidebar UI on right side
    local side_x = board_x + board_size + math.max(30, math.floor(40 * s))
    local side_y = board_y

    ui.title.set_font_style("Calibri", "Bold", math.floor(28 * s))
    ui.title.set_position(side_x, side_y)

    local badge_w = math.floor(120 * s)
    local badge_h = math.floor(36 * s)
    ui.turn_badge.set_position(side_x, side_y + 45 * s)
    ui.turn_badge.set_size(badge_w, badge_h)
    ui.turn_badge.set_corners(math.floor(6 * s), math.floor(6 * s))

    ui.turn_badge_text.set_font_style("Calibri", "Bold", math.floor(18 * s))
    ui.turn_badge_text.set_position(side_x + badge_w / 2, side_y + 45 * s + badge_h * 0.18)

    ui.status.set_font_style("Calibri", "Regular", math.floor(20 * s))
    ui.status.set_position(side_x, side_y + 95 * s)

    ui.ai_status.set_font_style("Calibri", "Italic", math.floor(16 * s))
    ui.ai_status.set_position(side_x, side_y + 130 * s)

    -- Difficulty
    local diff_y = side_y + 175 * s
    ui.difficulty_label.set_font_style("Calibri", "Bold", math.floor(18 * s))
    ui.difficulty_label.set_position(side_x, diff_y)

    local btn_w = math.floor(95 * s)
    local btn_h = math.floor(38 * s)
    local btn_gap = math.floor(8 * s)
    for i = 1, 3 do
        local bx = side_x + (i - 1) * (btn_w + btn_gap)
        local by = diff_y + 30 * s
        ui.diff_buttons[i].set_position(bx, by)
        ui.diff_buttons[i].set_size(btn_w, btn_h)
        ui.diff_buttons[i].set_font_style("Calibri", "Regular", math.floor(16 * s))
    end

    -- New Game Button
    local ng_w = math.floor(200 * s)
    local ng_h = math.floor(48 * s)
    local ng_y = diff_y + 95 * s
    ui.btn_new_game.set_position(side_x, ng_y)
    ui.btn_new_game.set_size(ng_w, ng_h)
    ui.btn_new_game.set_font_style("Calibri", "Bold", math.floor(18 * s))
end

local anim_t = 0
local hover_rc = nil

local function cell_pos(r, c)
    local screen_row = 8 - r + 1
    return board_x + (c - 1) * cell_size, board_y + (screen_row - 1) * cell_size
end

local function piece_pos(r, c)
    local x, y = cell_pos(r, c)
    return x + cell_size * 0.5, y + cell_size * 0.12
end

local function update_idle_animations()
    local pulse = (math.sin(anim_t * 5.5) + 1) * 0.5 -- 0..1

    -- Pulse valid move dots
    for _, m in ipairs(game.valid_moves) do
        local hl = ui.highlights[m.to_r][m.to_c]
        local x, y = cell_pos(m.to_r, m.to_c)
        if game.board[m.to_r][m.to_c] then
            local pad = math.floor(cell_size * (0.04 + 0.03 * pulse))
            local sz = cell_size - pad * 2
            hl.set_position(x + pad, y + pad)
            hl.set_size(sz, sz)
            hl.set_corners(math.floor(sz * 0.25), math.floor(sz * 0.25))
            hl.set_color("#f87171")
        else
            local dot = math.floor(cell_size * (0.28 + 0.06 * pulse))
            local off = math.floor((cell_size - dot) / 2)
            hl.set_position(x + off, y + off)
            hl.set_size(dot, dot)
            hl.set_corners(dot, dot)
            hl.set_color("#34d399")
        end
    end

    -- Pulse king square when in check
    if in_check(game, game.turn) then
        local kr, kc = find_king(game.board, game.turn)
        if kr then
            local x, y = cell_pos(kr, kc)
            local pad = math.floor(cell_size * (0.03 * pulse))
            local sz = cell_size - pad * 2
            ui.check_hl.set_position(x + pad, y + pad)
            ui.check_hl.set_size(sz, sz)
            ui.check_hl.set_corners(math.floor(cell_size * 0.12), math.floor(cell_size * 0.12))
            ui.check_hl.set_color(pulse > 0.5 and "#ef4444" or "#dc2626")
        else
            ui.check_hl.set_position(0, HIDE_Y)
        end
    else
        ui.check_hl.set_position(0, HIDE_Y)
    end

    -- Hover highlight
    if hover_rc and not game.game_over and game.turn == WHITE and not game.ai_thinking then
        local r, c = hover_rc.r, hover_rc.c
        local is_valid = false
        for _, m in ipairs(game.valid_moves) do
            if m.to_r == r and m.to_c == c then is_valid = true; break end
        end
        local p = game.board[r][c]
        if is_valid or (p and p.color == WHITE) then
            local x, y = cell_pos(r, c)
            local pad = math.floor(cell_size * 0.06)
            local sz = cell_size - pad * 2
            ui.hover_hl.set_position(x + pad, y + pad)
            ui.hover_hl.set_size(sz, sz)
            ui.hover_hl.set_corners(math.floor(cell_size * 0.15), math.floor(cell_size * 0.15))
            ui.hover_hl.set_color(is_valid and "#a7f3d0" or "#93c5fd")
        else
            ui.hover_hl.set_position(0, HIDE_Y)
        end
    else
        ui.hover_hl.set_position(0, HIDE_Y)
    end
end

local function update_visuals()
    -- Board Pieces
    for r = 1, 8 do
        for c = 1, 8 do
            local p = game.board[r][c]
            local piece_txt = ui.pieces[r][c]
            if p then
                local sym = PIECE_SYMBOLS[p.color][p.piece] or ""
                piece_txt.set_text(sym)
                piece_txt.set_transparency(1)
                style_piece_text(piece_txt, p.color)

                local x, y = piece_pos(r, c)
                piece_txt.set_position(x, y)
            else
                piece_txt.set_position(0, HIDE_Y)
            end
        end
    end

    -- Highlight Squares
    for r = 1, 8 do
        for c = 1, 8 do
            local hl = ui.highlights[r][c]
            local x, y = cell_pos(r, c)

            local is_selected = (game.selected and game.selected.r == r and game.selected.c == c)
            local is_dest = false
            for _, m in ipairs(game.valid_moves) do
                if m.to_r == r and m.to_c == c then is_dest = true; break end
            end
            local is_last = (game.last_move and (
                (game.last_move.from_r == r and game.last_move.from_c == c) or
                (game.last_move.to_r == r and game.last_move.to_c == c)
            ))

            if is_selected then
                hl.set_position(x, y)
                hl.set_size(cell_size, cell_size)
                hl.set_corners(0, 0)
                hl.set_color("#60a5fa") -- Soft Blue
            elseif is_dest then
                -- Positioned & pulsed in update_idle_animations()
            elseif is_last then
                hl.set_position(x, y)
                hl.set_size(cell_size, cell_size)
                hl.set_corners(0, 0)
                hl.set_color("#c8b44c") -- Last Move Amber
            else
                hl.set_position(0, HIDE_Y)
            end
        end
    end

    update_idle_animations()

    -- Difficulty buttons active state
    for i = 1, 3 do
        local btn = ui.diff_buttons[i]
        if i == game.difficulty then
            btn.set_color("#3b82f6")
            btn.set_text_color("#ffffff")
        else
            btn.set_color("#2a2e3d")
            btn.set_text_color("#94a3b8")
        end
    end

    -- Turn badge
    if game.turn == WHITE then
        ui.turn_badge.set_color("#f1f5f9")
        ui.turn_badge_text.set_color("#0f172a")
        ui.turn_badge_text.set_text("Ход белых")
    else
        ui.turn_badge.set_color("#1e293b")
        ui.turn_badge_text.set_color("#f8fafc")
        ui.turn_badge_text.set_text("Ход чёрных")
    end

    ui.status.set_text(game.status_text)
    if in_check(game, game.turn) and not game.game_over then
        ui.ai_status.set_text("Внимание: ШАХ!")
        ui.ai_status.set_color("#ef4444")
    elseif game.ai_thinking then
        ui.ai_status.set_text("Компьютер думает...")
        ui.ai_status.set_color("#60a5fa")
    else
        ui.ai_status.set_text("")
    end
end

local function ease_out_cubic(t)
    local u = 1 - t
    return 1 - u * u * u
end

local function animate_move(m, moving_piece, captured_piece, rook_move)
    -- Hide destination static pieces while sliding
    ui.pieces[m.to_r][m.to_c].set_position(0, HIDE_Y)
    if rook_move then
        ui.pieces[rook_move.r][rook_move.to_c].set_position(0, HIDE_Y)
    end
    ui.hover_hl.set_position(0, HIDE_Y)

    -- Setup sliding main piece
    ui.anim_piece.set_text(PIECE_SYMBOLS[moving_piece.color][moving_piece.piece] or "")
    style_piece_text(ui.anim_piece, moving_piece.color)
    ui.anim_piece.set_transparency(1)

    -- Setup sliding castling rook if any
    if rook_move then
        ui.anim_piece2.set_text(PIECE_SYMBOLS[moving_piece.color][ROOK] or "")
        style_piece_text(ui.anim_piece2, moving_piece.color)
        ui.anim_piece2.set_transparency(1)
    else
        ui.anim_piece2.set_position(0, HIDE_Y)
    end

    -- Setup captured piece fade-out
    if captured_piece then
        ui.capture_fade.set_text(PIECE_SYMBOLS[captured_piece.color][captured_piece.piece] or "")
        style_piece_text(ui.capture_fade, captured_piece.color)
        local cx, cy = piece_pos(m.to_r, m.to_c)
        ui.capture_fade.set_position(cx, cy)
    else
        ui.capture_fade.set_position(0, HIDE_Y)
    end

    local frames = 13
    local is_knight = (moving_piece.piece == KNIGHT)
    for f = 1, frames do
        local cur_w, cur_h = drawer.get_size_screen()
        if cur_w ~= W or cur_h ~= H then
            layout(cur_w, cur_h)
        end

        local t = f / frames
        local e = ease_out_cubic(t)

        local fx, fy = piece_pos(m.from_r, m.from_c)
        local tx, ty = piece_pos(m.to_r, m.to_c)
        local lift = is_knight and (math.sin(t * math.pi) * cell_size * 0.28) or 0
        ui.anim_piece.set_position(fx + (tx - fx) * e, fy + (ty - fy) * e - lift)

        if rook_move then
            local rfx, rfy = piece_pos(rook_move.r, rook_move.from_c)
            local rtx, rty = piece_pos(rook_move.r, rook_move.to_c)
            ui.anim_piece2.set_position(rfx + (rtx - rfx) * e, rfy + (rty - rfy) * e)
        end

        if captured_piece then
            ui.capture_fade.set_transparency(math.max(0, 1 - t * 1.4))
            local fx_sq, fy_sq = cell_pos(m.to_r, m.to_c)
            local pad = math.floor(cell_size * (0.05 + 0.35 * e))
            local sz = math.max(2, cell_size - pad * 2)
            ui.flash_hl.set_position(fx_sq + pad, fy_sq + pad)
            ui.flash_hl.set_size(sz, sz)
            ui.flash_hl.set_corners(sz, sz)
            ui.flash_hl.set_color("#fbbf24")
        end

        sleep(0.016)
    end

    ui.anim_piece.set_position(0, HIDE_Y)
    ui.anim_piece2.set_position(0, HIDE_Y)
    ui.capture_fade.set_position(0, HIDE_Y)
    ui.flash_hl.set_position(0, HIDE_Y)
end

local function execute_animated_move(m)
    local p = game.board[m.from_r][m.from_c]
    local moving_piece = { piece = p.piece, color = p.color }
    local captured_piece = game.board[m.to_r][m.to_c]
    if not captured_piece and p.piece == PAWN and game.ep and m.to_r == game.ep.r and m.to_c == game.ep.c then
        captured_piece = game.board[m.from_r][m.to_c]
    end
    if captured_piece then
        captured_piece = { piece = captured_piece.piece, color = captured_piece.color }
    end

    local rook_move = nil
    if p.piece == KING and math.abs(m.to_c - m.from_c) == 2 then
        if m.to_c == 7 then
            rook_move = { r = m.from_r, from_c = 8, to_c = 6 }
        elseif m.to_c == 3 then
            rook_move = { r = m.from_r, from_c = 1, to_c = 4 }
        end
    end

    game.last_move = {
        from_r = m.from_r,
        from_c = m.from_c,
        to_r = m.to_r,
        to_c = m.to_c
    }
    apply_move(game, m)
    game.selected = nil
    game.valid_moves = {}
    update_visuals()
    animate_move(m, moving_piece, captured_piece, rook_move)
    update_visuals()
end

-- AI Turn Routine
local function do_ai_move()
    if game.game_over or game.turn ~= BLACK then return end

    game.ai_thinking = true
    update_visuals()
    sleep(0.05) -- allow frame update to show thinking

    -- Depth configuration based on difficulty
    local depth = 1
    if game.difficulty == 1 then depth = 1
    elseif game.difficulty == 2 then depth = 2
    elseif game.difficulty == 3 then depth = 3
    end

    local score, best_move = minimax(game, depth, -999999, 999999, false)

    if best_move then
        execute_animated_move(best_move)

        -- Check endgame after AI move
        local user_legal = generate_legal_moves(game, WHITE)
        if #user_legal == 0 then
            game.game_over = true
            if in_check(game, WHITE) then
                game.status_text = "Мат! Компьютер победил!"
            else
                game.status_text = "Пат! Ничья!"
            end
        else
            game.status_text = "Ваш ход (Белые)"
        end
    else
        -- No legal moves for AI
        game.game_over = true
        if in_check(game, BLACK) then
            game.status_text = "Мат! Вы победили!"
        else
            game.status_text = "Пат! Ничья!"
        end
    end

    game.ai_thinking = false
    update_visuals()
end

-- Mouse Click Handling
local function handle_board_click(mx, my)
    if game.game_over or game.turn ~= WHITE or game.ai_thinking then return end

    if mx < board_x or mx >= board_x + board_size or my < board_y or my >= board_y + board_size then
        -- Clicked outside board: deselect
        if game.selected then
            game.selected = nil
            game.valid_moves = {}
            update_visuals()
        end
        return
    end

    local col = math.floor((mx - board_x) / cell_size) + 1
    local screen_row = math.floor((my - board_y) / cell_size) + 1
    local row = 8 - screen_row + 1

    if col < 1 or col > 8 or row < 1 or row > 8 then return end

    -- Check if clicking on an already chosen destination
    local chosen_move = nil
    for _, m in ipairs(game.valid_moves) do
        if m.to_r == row and m.to_c == col then
            chosen_move = m
            break
        end
    end

    if chosen_move then
        -- Execute user move with animation
        execute_animated_move(chosen_move)

        -- Check if AI is in checkmate/stalemate
        local ai_legal = generate_legal_moves(game, BLACK)
        if #ai_legal == 0 then
            game.game_over = true
            if in_check(game, BLACK) then
                game.status_text = "Мат! Вы победили!"
            else
                game.status_text = "Пат! Ничья!"
            end
            update_visuals()
            return
        end

        game.status_text = "Ход компьютера..."
        update_visuals()

        -- Trigger AI move
        do_ai_move()
    else
        -- Check if selecting own piece
        local p = game.board[row][col]
        if p and p.color == WHITE then
            game.selected = { r = row, c = col }
            local all_legal = generate_legal_moves(game, WHITE)
            game.valid_moves = {}
            for _, m in ipairs(all_legal) do
                if m.from_r == row and m.from_c == col then
                    game.valid_moves[#game.valid_moves+1] = m
                end
            end
            update_visuals()
        else
            game.selected = nil
            game.valid_moves = {}
            update_visuals()
        end
    end
end

-- Initialization
create_ui()
init_board()

local init_w, init_h = drawer.get_size_screen()
layout(init_w, init_h)
update_visuals()

-- Main loop
local was_down = false
while true do
    local cur_w, cur_h = drawer.get_size_screen()
    if cur_w ~= W or cur_h ~= H then
        layout(cur_w, cur_h)
        needs_redraw = true
    end

    if needs_redraw then
        needs_redraw = false
        update_visuals()
    end

    local mx, my, down, inside = drawer.get_mouse()
    if inside and mx >= board_x and mx < board_x + board_size and my >= board_y and my < board_y + board_size then
        local hcol = math.floor((mx - board_x) / cell_size) + 1
        local hrow = 8 - (math.floor((my - board_y) / cell_size) + 1) + 1
        hover_rc = { r = hrow, c = hcol }
    else
        hover_rc = nil
    end

    if down and not was_down and inside then
        handle_board_click(mx, my)
    end
    was_down = down

    anim_t = anim_t + 0.016
    update_idle_animations()

    sleep(0.016)
end
