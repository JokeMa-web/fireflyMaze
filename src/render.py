import pygame

from difficulty import DIFFICULTY_ORDER
from game import EXIT, FLOOR, GAME_LOST, GAME_QUIT, GAME_RUNNING, GAME_WON, WALL, monster_positions
from levels import LEVELS
from texts import TEXTS, difficulty_label, main_menu_label


TILE_SIZE = 48
HUD_HEIGHT = 112
BACKGROUND = (16, 20, 22)
HUD_BACKGROUND = (22, 28, 30)
TEXT = (232, 238, 230)
MUTED_TEXT = (166, 178, 170)
LOCKED_TEXT = (92, 96, 96)
WIN_TEXT = (142, 232, 164)
LOSE_TEXT = (255, 132, 132)


def map_size(state):
    rows = len(state["grid"])
    cols = max(len(row) for row in state["grid"])
    return cols * TILE_SIZE, rows * TILE_SIZE


def window_size(state):
    map_width, map_height = map_size(state)
    return map_width, map_height + HUD_HEIGHT


def status_label(state):
    return TEXTS["status"].get(state["status"], state["status"])


def draw_wrapped_centered_text(screen, font, text, y, color=TEXT, max_width=None, line_height=None):
    max_width = max_width or screen.get_width() - 48
    line_height = line_height or font.get_linesize()
    words = list(text)
    lines = []
    current = ""

    for char in words:
        test = current + char
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)

    for index, line in enumerate(lines):
        surface = font.render(line, True, color)
        screen.blit(surface, surface.get_rect(center=(screen.get_width() // 2, y + index * line_height)))


def draw_centered_text(screen, font, text, y, color=TEXT):
    draw_wrapped_centered_text(screen, font, text, y, color)


def draw_centered_lines(screen, font, lines, y, color=TEXT, line_gap=6, max_width=None):
    line_height = font.get_linesize() + line_gap
    for index, line in enumerate(lines):
        draw_wrapped_centered_text(
            screen,
            font,
            line,
            y + index * line_height,
            color,
            max_width=max_width,
            line_height=line_height,
        )


def split_hint_parts(text):
    return [part.strip() for part in text.split("    ") if part.strip()]


def paired_hint_lines(text):
    parts = split_hint_parts(text)
    return ["    ".join(parts[index:index + 2]) for index in range(0, len(parts), 2)]


def draw_menu_background(screen, background=None):
    if background is not None:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BACKGROUND)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 142))
    screen.blit(overlay, (0, 0))


def draw_hud(screen, state, font, small_font, width, map_height):
    hud_rect = pygame.Rect(0, map_height, width, HUD_HEIGHT)
    pygame.draw.rect(screen, HUD_BACKGROUND, hud_rect)

    labels = TEXTS["hud"]
    info = (
        f"{labels['level']}：{state['level_number']}    "
        f"{labels['difficulty']}：{difficulty_label(state['difficulty'])}    "
        f"{labels['score']}：{state['score']}    "
        f"{labels['fireflies']}：{len(state['fireflies'])}    "
        f"{labels['status']}：{status_label(state)}"
    )
    draw_wrapped_centered_text(screen, small_font, info, map_height + 14, TEXT, width - 36)

    if state["status"] == GAME_RUNNING:
        hint_lines = paired_hint_lines(TEXTS["hints"]["game"])
    else:
        score_line = f"{state['message']}  {TEXTS['result']['final_score']}：{state['score']}"
        hint_lines = [score_line] + paired_hint_lines(TEXTS["hints"]["end"])
    draw_centered_lines(screen, small_font, hint_lines[:2], map_height + 48, MUTED_TEXT, line_gap=2, max_width=width - 36)


def draw_end_overlay(screen, state, font, small_font, all_completed=False):
    if state["status"] == GAME_RUNNING:
        return

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    width, height = screen.get_size()
    if state["status"] == GAME_WON:
        title = TEXTS["result"]["all_completed"] if all_completed else TEXTS["result"]["victory"]
        color = WIN_TEXT
    elif state["status"] == GAME_QUIT:
        title = TEXTS["result"]["quit"]
        color = MUTED_TEXT
    else:
        title = TEXTS["result"]["defeat"]
        color = LOSE_TEXT

    title_surface = font.render(title, True, color)
    score_surface = small_font.render(f"{TEXTS['result']['final_score']}：{state['score']}", True, TEXT)
    if state["status"] == GAME_WON and all_completed:
        help_text = TEXTS["hints"]["victory_done"]
    elif state["status"] == GAME_WON:
        help_text = TEXTS["hints"]["victory_next"]
    else:
        help_text = TEXTS["hints"]["end"]
    help_lines = paired_hint_lines(help_text)

    screen.blit(title_surface, title_surface.get_rect(center=(width // 2, height // 2 - 34)))
    screen.blit(score_surface, score_surface.get_rect(center=(width // 2, height // 2 + 6)))
    draw_centered_lines(screen, small_font, help_lines, height // 2 + 40, MUTED_TEXT, line_gap=4, max_width=width - 48)


def draw_game(screen, state, assets, font, small_font, all_completed=False):
    screen.fill(BACKGROUND)

    for row_index, row in enumerate(state["grid"]):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            screen.blit(assets["floor"], (x, y))
            if tile == WALL:
                screen.blit(assets["wall"], (x, y))
            elif tile == EXIT:
                exit_asset = "exit_open" if not state["fireflies"] else "exit_closed"
                screen.blit(assets[exit_asset], (x, y))
            elif tile != FLOOR:
                screen.blit(assets["floor"], (x, y))

    for row, col in state["fireflies"]:
        screen.blit(assets["firefly"], (col * TILE_SIZE, row * TILE_SIZE))

    for row, col in monster_positions(state):
        screen.blit(assets["monster"], (col * TILE_SIZE, row * TILE_SIZE))

    for bullet in state["bullets"]:
        row, col = bullet["position"]
        center = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
        pygame.draw.circle(screen, (255, 244, 160), center, 7)
        pygame.draw.circle(screen, (255, 196, 64), center, 7, 2)

    player_row, player_col = state["player"]
    screen.blit(assets["player"], (player_col * TILE_SIZE, player_row * TILE_SIZE))

    width, height = screen.get_size()
    map_height = height - HUD_HEIGHT
    draw_hud(screen, state, font, small_font, width, map_height)
    draw_end_overlay(screen, state, font, small_font, all_completed)


def draw_menu_screen(screen, font, small_font, title, items, selected_index, subtitle=None, background=None):
    draw_menu_background(screen, background)
    draw_centered_text(screen, font, title, 88)
    if subtitle:
        draw_centered_text(screen, small_font, subtitle, 130, MUTED_TEXT)

    start_y = 190
    for index, item in enumerate(items):
        color = TEXT if index == selected_index else MUTED_TEXT
        prefix = ">" if index == selected_index else " "
        draw_centered_text(screen, font, f"{prefix} {item}", start_y + index * 46, color)

    draw_centered_lines(screen, small_font, paired_hint_lines(TEXTS["hints"]["menu"]), screen.get_height() - 58, MUTED_TEXT)


def draw_main_menu(screen, font, small_font, items, selected_index, difficulty, background=None):
    draw_menu_screen(
        screen,
        font,
        small_font,
        TEXTS["title"],
        [main_menu_label(item) for item in items],
        selected_index,
        f"{TEXTS['hud']['difficulty']}：{difficulty_label(difficulty)}",
        background,
    )


def draw_difficulty_menu(screen, font, small_font, selected_index, current_difficulty, background=None):
    items = []
    for name in DIFFICULTY_ORDER:
        marker = "（当前）" if name == current_difficulty else ""
        items.append(f"{difficulty_label(name)}{marker}")
    items.append("返回")
    draw_menu_screen(
        screen,
        font,
        small_font,
        TEXTS["main_menu"]["Difficulty"],
        items,
        selected_index,
        f"当前难度：{difficulty_label(current_difficulty)}",
        background,
    )


def draw_settings_menu(screen, font, small_font, items, selected_index, music_muted=False, background=None):
    labels = TEXTS["settings"]
    visible_items = [labels.get(item, item) for item in items]
    music_text = labels["music_off"] if music_muted else labels["music_on"]
    draw_menu_screen(
        screen,
        font,
        small_font,
        TEXTS["main_menu"]["Settings"],
        visible_items,
        selected_index,
        f"{music_text}    {labels['note']}",
        background,
    )


def draw_pause_menu(screen, font, small_font, items, selected_index):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 176))
    screen.blit(overlay, (0, 0))
    draw_centered_text(screen, font, "游戏暂停", 110)
    start_y = 190
    for index, item in enumerate(items):
        color = TEXT if index == selected_index else MUTED_TEXT
        label = TEXTS["pause_menu"].get(item, item)
        prefix = ">" if index == selected_index else " "
        draw_centered_text(screen, font, f"{prefix} {label}", start_y + index * 46, color)
    draw_centered_lines(screen, small_font, paired_hint_lines(TEXTS["hints"]["pause"]), screen.get_height() - 58, MUTED_TEXT)


def draw_level_select(screen, font, small_font, selected_index, save_data, difficulty, hint="", background=None):
    draw_menu_background(screen, background)
    draw_centered_text(screen, font, TEXTS["main_menu"]["Level Select"], 84)
    draw_centered_text(screen, small_font, f"难度：{difficulty_label(difficulty)}", 124, MUTED_TEXT)

    progress = save_data["progress"][difficulty]
    completed = set(progress.get("completed_levels", []))
    current = progress["current_level"]
    all_completed = LEVELS[-1]["number"] in completed

    start_y = 178
    for index, level in enumerate(LEVELS):
        number = level["number"]
        if all_completed or number < current:
            status = TEXTS["level_status"]["completed"]
            color = MUTED_TEXT
        elif number == current:
            status = TEXTS["level_status"]["current"]
            color = TEXT
        else:
            status = TEXTS["level_status"]["locked"]
            color = LOCKED_TEXT

        prefix = ">" if index == selected_index else " "
        label = f"{prefix} 第 {number} 关：{level['name']}    {status}"
        draw_centered_text(screen, font, label, start_y + index * 42, color if index != selected_index else TEXT)

    if hint:
        draw_centered_text(screen, small_font, hint, screen.get_height() - 76, LOSE_TEXT)
    draw_centered_lines(screen, small_font, paired_hint_lines(TEXTS["hints"]["level_select"]), screen.get_height() - 58, MUTED_TEXT)
