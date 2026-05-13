import os
import random

from difficulty import DEFAULT_DIFFICULTY, get_difficulty
from texts import TEXTS


WALL = "#"
FLOOR = "."
PLAYER = "P"
FIREFLY = "F"
MONSTER = "M"
EXIT = "E"
DEFAULT_PATROL_RADIUS = 3
FIREFLY_SCORE = 10
DEFAULT_BULLET_DIRECTION = "D"

DIRECTIONS = {
    "W": (-1, 0),
    "A": (0, -1),
    "S": (1, 0),
    "D": (0, 1),
}

GAME_RUNNING = "running"
GAME_WON = "won"
GAME_LOST = "lost"
GAME_QUIT = "quit"


def create_monster(position, patrol_radius):
    return {
        "position": position,
        "spawn_position": position,
        "patrol_radius": patrol_radius,
    }


def manhattan_distance(first, second):
    first_row, first_col = first
    second_row, second_col = second
    return abs(first_row - second_row) + abs(first_col - second_col)


def monster_positions(state):
    return {monster["position"] for monster in state["monsters"]}


def is_in_bounds(state, position):
    row, col = position
    return 0 <= row < len(state["grid"]) and 0 <= col < len(state["grid"][row])


def is_wall(state, position):
    if not is_in_bounds(state, position):
        return True
    row, col = position
    return state["grid"][row][col] == WALL


def is_exit(state, position):
    return position == state["exit"]


def create_game_state(
    map_rows,
    patrol_radius=DEFAULT_PATROL_RADIUS,
    difficulty_name=DEFAULT_DIFFICULTY,
    level_number=1,
):
    grid = []
    player = None
    monsters = []
    fireflies = set()
    exit_pos = None

    for row_index, row in enumerate(map_rows):
        grid_row = []
        for col_index, char in enumerate(row):
            pos = (row_index, col_index)
            if char == PLAYER:
                player = pos
                grid_row.append(FLOOR)
            elif char == MONSTER:
                monsters.append(create_monster(pos, patrol_radius))
                grid_row.append(FLOOR)
            elif char == FIREFLY:
                fireflies.add(pos)
                grid_row.append(FLOOR)
            elif char == EXIT:
                exit_pos = pos
                grid_row.append(EXIT)
            else:
                grid_row.append(char)
        grid.append(grid_row)

    if player is None:
        raise ValueError("Map must contain one player marked with P.")
    if exit_pos is None:
        raise ValueError("Map must contain one exit marked with E.")

    state = {
        "grid": grid,
        "player": player,
        "monsters": monsters,
        "fireflies": fireflies,
        "total_fireflies": len(fireflies),
        "exit": exit_pos,
        "steps": 0,
        "score": 0,
        "status": GAME_RUNNING,
        "message": "",
        "last_direction": DEFAULT_BULLET_DIRECTION,
        "bullets": [],
        "difficulty": difficulty_name,
        "level_number": level_number,
    }
    apply_difficulty_counts(state, get_difficulty(difficulty_name), patrol_radius)
    return state


def random_empty_positions(state, count, avoid_positions, min_player_distance=4, min_firefly_distance=0):
    candidates = []
    player = state["player"]
    occupied = set(avoid_positions)

    for row_index, row in enumerate(state["grid"]):
        for col_index, tile in enumerate(row):
            pos = (row_index, col_index)
            if tile == WALL or pos in occupied or pos == state["exit"]:
                continue
            if manhattan_distance(pos, player) < min_player_distance:
                continue
            if manhattan_distance(pos, state["exit"]) < 2:
                continue
            if min_firefly_distance and any(
                manhattan_distance(pos, firefly) < min_firefly_distance
                for firefly in state["fireflies"]
            ):
                continue
            candidates.append(pos)

    random.shuffle(candidates)
    return candidates[:count]


def apply_difficulty_counts(state, difficulty_config, patrol_radius):
    if len(state["fireflies"]) < difficulty_config["firefly_count"]:
        avoid = monster_positions(state) | state["fireflies"] | {state["player"], state["exit"]}
        needed = difficulty_config["firefly_count"] - len(state["fireflies"])
        for pos in random_empty_positions(state, needed, avoid, 3):
            state["fireflies"].add(pos)

    if len(state["monsters"]) < difficulty_config["monster_count"]:
        avoid = monster_positions(state) | state["fireflies"] | {state["player"], state["exit"]}
        needed = difficulty_config["monster_count"] - len(state["monsters"])
        for pos in random_empty_positions(state, needed, avoid, 4, 2):
            state["monsters"].append(create_monster(pos, patrol_radius))

    state["total_fireflies"] = len(state["fireflies"])


def draw_map(state):
    visible = [row[:] for row in state["grid"]]

    for row, col in state["fireflies"]:
        visible[row][col] = FIREFLY
    for row, col in monster_positions(state):
        visible[row][col] = MONSTER

    player_row, player_col = state["player"]
    visible[player_row][player_col] = PLAYER

    print("\n".join("".join(row) for row in visible))
    print(f"Steps: {state['steps']}")
    print(f"Score: {state['score']}")
    print(f"Fireflies remaining: {len(state['fireflies'])}")
    if state["message"]:
        print(state["message"])


def move_player(state, command):
    direction = DIRECTIONS.get(command.upper())
    if direction is None:
        state["message"] = TEXTS["messages"]["leave_maze"]
        return False

    row_delta, col_delta = direction
    row, col = state["player"]
    new_pos = (row + row_delta, col + col_delta)

    if is_wall(state, new_pos):
        state["message"] = TEXTS["messages"]["wall"]
        return False

    state["player"] = new_pos
    state["last_direction"] = command.upper()
    state["steps"] += 1

    if new_pos in monster_positions(state):
        state["message"] = TEXTS["messages"]["monster"]
        return True

    if new_pos in state["fireflies"]:
        state["fireflies"].remove(new_pos)
        state["score"] = max(0, state["score"] + FIREFLY_SCORE)
        state["message"] = TEXTS["messages"]["firefly"]
    elif new_pos == state["exit"] and state["fireflies"]:
        state["message"] = TEXTS["messages"]["exit_closed"]
    elif not state["fireflies"]:
        state["message"] = TEXTS["messages"]["exit_open"]
    else:
        state["message"] = ""

    return True


def shoot_bullet(state, difficulty_config):
    if state["status"] != GAME_RUNNING:
        return False
    if len(state["bullets"]) >= difficulty_config["max_bullets"]:
        return False

    direction = state.get("last_direction", DEFAULT_BULLET_DIRECTION)
    row_delta, col_delta = DIRECTIONS[direction]
    row, col = state["player"]
    bullet_pos = (row + row_delta, col + col_delta)

    if is_wall(state, bullet_pos) or is_exit(state, bullet_pos):
        return False

    if remove_monster_at(state, bullet_pos, difficulty_config):
        update_game_status(state)
        return True

    state["bullets"].append({
        "position": bullet_pos,
        "direction": direction,
    })
    return True


def remove_monster_at(state, position, difficulty_config):
    for index, monster in enumerate(state["monsters"]):
        if monster["position"] == position:
            del state["monsters"][index]
            state["score"] = max(0, state["score"] + difficulty_config["monster_kill_score"])
            state["message"] = TEXTS["messages"]["hit_monster"]
            return True
    return False


def update_bullets(state, difficulty_config):
    if state["status"] != GAME_RUNNING:
        return False

    moved_bullets = []
    for bullet in state["bullets"]:
        row_delta, col_delta = DIRECTIONS[bullet["direction"]]
        row, col = bullet["position"]
        next_pos = (row + row_delta, col + col_delta)

        if is_wall(state, next_pos) or is_exit(state, next_pos):
            continue
        if remove_monster_at(state, next_pos, difficulty_config):
            continue

        moved_bullets.append({
            "position": next_pos,
            "direction": bullet["direction"],
        })

    state["bullets"] = moved_bullets
    update_game_status(state)
    return True


def update_game_status(state):
    if check_lose(state):
        state["status"] = GAME_LOST
        state["message"] = TEXTS["messages"]["caught"]
    elif check_win(state):
        state["status"] = GAME_WON
        state["message"] = TEXTS["messages"]["escaped"]
    return state["status"]


def handle_turn(state, command):
    if state["status"] != GAME_RUNNING:
        return False

    moved = move_player(state, command)
    if not moved:
        return False

    update_game_status(state)
    return True


def update_monsters(state, difficulty_config=None):
    if state["status"] != GAME_RUNNING:
        return False

    move_monsters(state, difficulty_config or get_difficulty(state["difficulty"]))
    update_game_status(state)
    return True


def quit_game(state):
    state["status"] = GAME_QUIT
    state["message"] = TEXTS["messages"]["quit"]


def legal_monster_moves(state, monster, occupied, current_positions):
    current_pos = monster["position"]
    row, col = current_pos
    candidates = []
    for row_delta, col_delta in [(0, 0)] + list(DIRECTIONS.values()):
        next_pos = (row + row_delta, col + col_delta)
        if (
            not is_wall(state, next_pos)
            and next_pos not in occupied
            and (next_pos == current_pos or next_pos not in current_positions)
            and manhattan_distance(next_pos, monster["spawn_position"]) <= monster["patrol_radius"]
        ):
            candidates.append(next_pos)
    return candidates


def chase_candidates(monster, player, candidates):
    current_distance = manhattan_distance(monster["position"], player)
    better = [
        pos for pos in candidates
        if pos != monster["position"] and manhattan_distance(pos, player) < current_distance
    ]
    if not better:
        return []
    best_distance = min(manhattan_distance(pos, player) for pos in better)
    return [pos for pos in better if manhattan_distance(pos, player) == best_distance]


def move_monsters(state, difficulty_config=None):
    difficulty_config = difficulty_config or get_difficulty(state["difficulty"])
    occupied = set()
    moved_monsters = []
    current_positions = monster_positions(state)

    for monster in state["monsters"]:
        candidates = legal_monster_moves(state, monster, occupied, current_positions)
        chase_options = chase_candidates(monster, state["player"], candidates)
        if chase_options and random.random() < difficulty_config["chase_probability"]:
            new_pos = random.choice(chase_options)
        else:
            new_pos = random.choice(candidates)

        moved_monster = monster.copy()
        moved_monster["position"] = new_pos
        moved_monsters.append(moved_monster)
        occupied.add(new_pos)

    state["monsters"] = moved_monsters


def check_win(state):
    return not state["fireflies"] and state["player"] == state["exit"]


def check_lose(state):
    return state["player"] in monster_positions(state)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def finish_game(state, message, result):
    print(message)
    print(f"Final score: {state['score']}")
    return result


def main_loop(map_rows, patrol_radius=DEFAULT_PATROL_RADIUS):
    state = create_game_state(map_rows, patrol_radius)

    while True:
        clear_screen()
        draw_map(state)

        if check_lose(state):
            state["status"] = GAME_LOST
            return finish_game(state, TEXTS["result"]["defeat"], False)
        if check_win(state):
            state["status"] = GAME_WON
            return finish_game(state, TEXTS["result"]["victory"], True)

        command = input("移动（W/A/S/D，Q 退出）：").strip().upper()
        if command == "Q":
            quit_game(state)
            return finish_game(state, TEXTS["result"]["quit"], False)

        handle_turn(state, command)
