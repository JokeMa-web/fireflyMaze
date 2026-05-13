import pygame

from assets_loader import load_assets, load_font, load_menu_background
from audio import is_muted, start_background_music, stop_music, toggle_mute
from difficulty import DIFFICULTY_ORDER, get_difficulty
from game import (
    GAME_RUNNING,
    GAME_WON,
    create_game_state,
    handle_turn,
    quit_game,
    shoot_bullet,
    update_bullets,
    update_monsters,
)
from levels import LEVELS, get_level, max_level_number
from menu import (
    MAIN_MENU_ITEMS,
    PAUSE_MENU_ITEMS,
    SCREEN_DIFFICULTY,
    SCREEN_GAME,
    SCREEN_LEVEL_SELECT,
    SCREEN_MENU,
    SCREEN_PAUSE,
    SCREEN_SETTINGS,
    SETTINGS_ITEMS,
)
from render import (
    TILE_SIZE,
    draw_difficulty_menu,
    draw_game,
    draw_level_select,
    draw_main_menu,
    draw_pause_menu,
    draw_settings_menu,
    window_size,
)
from save_data import load_save_data, mark_level_completed, save_data as write_save_data, set_difficulty, set_last_level
from texts import TEXTS


KEY_TO_COMMAND = {
    pygame.K_w: "W",
    pygame.K_UP: "W",
    pygame.K_a: "A",
    pygame.K_LEFT: "A",
    pygame.K_s: "S",
    pygame.K_DOWN: "S",
    pygame.K_d: "D",
    pygame.K_RIGHT: "D",
}

SCANCODE_TO_COMMAND = {
    26: "W",
    4: "A",
    22: "S",
    7: "D",
}


def command_from_keydown(event):
    if event.key in KEY_TO_COMMAND:
        return KEY_TO_COMMAND[event.key]

    character = getattr(event, "unicode", "").lower()
    if character in ("w", "a", "s", "d"):
        return character.upper()

    scancode = getattr(event, "scancode", None)
    return SCANCODE_TO_COMMAND.get(scancode)


def start_level(level_number, difficulty_name):
    level = get_level(level_number)
    return create_game_state(
        level["map"],
        difficulty_name=difficulty_name,
        level_number=level["number"],
    )


def reset_level_runtime(now):
    return {
        "last_monster_move": now,
        "last_bullet_update": now,
        "last_shot_time": -9999,
        "completion_recorded": False,
        "all_completed": False,
    }


def main():
    pygame.init()
    pygame.display.set_caption("Firefly Maze")
    start_background_music()

    data = load_save_data()
    difficulty = data["difficulty"]
    progress = data["progress"][difficulty]
    state = start_level(progress["current_level"], difficulty)

    screen = pygame.display.set_mode(window_size(state))
    font = load_font(34)
    small_font = load_font(24)
    assets = load_assets(TILE_SIZE)
    menu_background = load_menu_background(screen.get_size())
    clock = pygame.time.Clock()

    screen_name = SCREEN_MENU
    menu_index = 0
    difficulty_index = DIFFICULTY_ORDER.index(difficulty)
    level_index = 0
    settings_index = 0
    pause_index = 0
    level_hint = ""
    last_monster_move = pygame.time.get_ticks()
    last_bullet_update = pygame.time.get_ticks()
    last_shot_time = -9999
    completion_recorded = False
    all_completed = False
    running = True

    while running:
        config = get_difficulty(difficulty)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if screen_name == SCREEN_MENU:
                    if event.key == pygame.K_UP:
                        menu_index = (menu_index - 1) % len(MAIN_MENU_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        menu_index = (menu_index + 1) % len(MAIN_MENU_ITEMS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        item = MAIN_MENU_ITEMS[menu_index]
                        if item == "Start Game":
                            progress = data["progress"][difficulty]
                            state = start_level(progress["current_level"], difficulty)
                            screen = pygame.display.set_mode(window_size(state))
                            menu_background = load_menu_background(screen.get_size())
                            last_monster_move = now
                            last_bullet_update = now
                            last_shot_time = -9999
                            completion_recorded = False
                            all_completed = False
                            screen_name = SCREEN_GAME
                        elif item == "Level Select":
                            level_index = 0
                            screen_name = SCREEN_LEVEL_SELECT
                        elif item == "Difficulty":
                            difficulty_index = DIFFICULTY_ORDER.index(difficulty)
                            screen_name = SCREEN_DIFFICULTY
                        elif item == "Settings":
                            settings_index = 0
                            screen_name = SCREEN_SETTINGS
                        elif item == "Quit":
                            running = False
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False

                elif screen_name == SCREEN_DIFFICULTY:
                    item_count = len(DIFFICULTY_ORDER) + 1
                    if event.key == pygame.K_UP:
                        difficulty_index = (difficulty_index - 1) % item_count
                    elif event.key == pygame.K_DOWN:
                        difficulty_index = (difficulty_index + 1) % item_count
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if difficulty_index < len(DIFFICULTY_ORDER):
                            difficulty = DIFFICULTY_ORDER[difficulty_index]
                            set_difficulty(data, difficulty)
                            data = load_save_data()
                        else:
                            screen_name = SCREEN_MENU
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        screen_name = SCREEN_MENU

                elif screen_name == SCREEN_LEVEL_SELECT:
                    if event.key == pygame.K_UP:
                        level_index = (level_index - 1) % len(LEVELS)
                    elif event.key == pygame.K_DOWN:
                        level_index = (level_index + 1) % len(LEVELS)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        level_number = LEVELS[level_index]["number"]
                        current_level = data["progress"][difficulty]["current_level"]
                        if level_number <= current_level:
                            set_last_level(data, difficulty, level_number)
                            data = load_save_data()
                            state = start_level(level_number, difficulty)
                            screen = pygame.display.set_mode(window_size(state))
                            menu_background = load_menu_background(screen.get_size())
                            last_monster_move = now
                            last_bullet_update = now
                            last_shot_time = -9999
                            completion_recorded = False
                            all_completed = False
                            screen_name = SCREEN_GAME
                            level_hint = ""
                        else:
                            level_hint = TEXTS["level_status"]["locked_hint"]
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        level_hint = ""
                        screen_name = SCREEN_MENU

                elif screen_name == SCREEN_SETTINGS:
                    if event.key == pygame.K_UP:
                        settings_index = (settings_index - 1) % len(SETTINGS_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        settings_index = (settings_index + 1) % len(SETTINGS_ITEMS)
                    elif event.key == pygame.K_m:
                        toggle_mute()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if SETTINGS_ITEMS[settings_index] == "Toggle Music":
                            toggle_mute()
                        else:
                            screen_name = SCREEN_MENU
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        screen_name = SCREEN_MENU

                elif screen_name == SCREEN_GAME:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and state["status"] == GAME_WON:
                        if all_completed:
                            screen_name = SCREEN_MENU
                        else:
                            progress = data["progress"][difficulty]
                            state = start_level(progress["current_level"], difficulty)
                            screen = pygame.display.set_mode(window_size(state))
                            menu_background = load_menu_background(screen.get_size())
                            runtime = reset_level_runtime(now)
                            last_monster_move = runtime["last_monster_move"]
                            last_bullet_update = runtime["last_bullet_update"]
                            last_shot_time = runtime["last_shot_time"]
                            completion_recorded = runtime["completion_recorded"]
                            all_completed = runtime["all_completed"]
                    elif event.key == pygame.K_r and state["status"] != GAME_RUNNING:
                        state = start_level(state["level_number"], difficulty)
                        screen = pygame.display.set_mode(window_size(state))
                        menu_background = load_menu_background(screen.get_size())
                        last_monster_move = now
                        last_bullet_update = now
                        last_shot_time = -9999
                        completion_recorded = False
                        all_completed = False
                    elif event.key == pygame.K_m:
                        toggle_mute()
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        if state["status"] == GAME_RUNNING:
                            pause_index = 0
                            screen_name = SCREEN_PAUSE
                        else:
                            set_last_level(data, difficulty, state["level_number"])
                            data = load_save_data()
                            screen_name = SCREEN_MENU
                    elif event.key == pygame.K_SPACE:
                        if now - last_shot_time >= config["bullet_cooldown_ms"]:
                            if shoot_bullet(state, config):
                                last_shot_time = now
                    else:
                        command = command_from_keydown(event)
                        if command is not None:
                            handle_turn(state, command)

                elif screen_name == SCREEN_PAUSE:
                    if event.key == pygame.K_UP:
                        pause_index = (pause_index - 1) % len(PAUSE_MENU_ITEMS)
                    elif event.key == pygame.K_DOWN:
                        pause_index = (pause_index + 1) % len(PAUSE_MENU_ITEMS)
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        screen_name = SCREEN_GAME
                    elif event.key == pygame.K_m:
                        toggle_mute()
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        item = PAUSE_MENU_ITEMS[pause_index]
                        if item == "Resume":
                            screen_name = SCREEN_GAME
                            last_monster_move = now
                            last_bullet_update = now
                        elif item == "Restart Level":
                            state = start_level(state["level_number"], difficulty)
                            screen = pygame.display.set_mode(window_size(state))
                            menu_background = load_menu_background(screen.get_size())
                            last_monster_move = now
                            last_bullet_update = now
                            last_shot_time = -9999
                            completion_recorded = False
                            all_completed = False
                            screen_name = SCREEN_GAME
                        elif item == "Back to Main Menu":
                            set_last_level(data, difficulty, state["level_number"])
                            data = load_save_data()
                            screen_name = SCREEN_MENU
                        elif item == "Quit":
                            running = False

        if screen_name == SCREEN_GAME and state["status"] == GAME_RUNNING:
            if now - last_monster_move >= config["monster_move_interval_ms"]:
                update_monsters(state, config)
                last_monster_move = now
            if now - last_bullet_update >= config["bullet_move_interval_ms"]:
                update_bullets(state, config)
                last_bullet_update = now

        if screen_name == SCREEN_GAME and state["status"] == GAME_WON and not completion_recorded:
            mark_level_completed(data, difficulty, state["level_number"], max_level_number())
            data = load_save_data()
            all_completed = max_level_number() in data["progress"][difficulty]["completed_levels"]
            completion_recorded = True

        if screen_name == SCREEN_MENU:
            draw_main_menu(screen, font, small_font, MAIN_MENU_ITEMS, menu_index, difficulty, menu_background)
        elif screen_name == SCREEN_DIFFICULTY:
            draw_difficulty_menu(screen, font, small_font, difficulty_index, difficulty, menu_background)
        elif screen_name == SCREEN_LEVEL_SELECT:
            draw_level_select(screen, font, small_font, level_index, data, difficulty, level_hint, menu_background)
        elif screen_name == SCREEN_SETTINGS:
            draw_settings_menu(screen, font, small_font, SETTINGS_ITEMS, settings_index, is_muted(), menu_background)
        elif screen_name == SCREEN_GAME:
            draw_game(screen, state, assets, font, small_font, all_completed)
        elif screen_name == SCREEN_PAUSE:
            draw_game(screen, state, assets, font, small_font, all_completed)
            draw_pause_menu(screen, font, small_font, PAUSE_MENU_ITEMS, pause_index)

        pygame.display.flip()
        clock.tick(60)

    write_save_data(data)
    stop_music()
    pygame.quit()


if __name__ == "__main__":
    main()
