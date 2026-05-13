import json
from pathlib import Path

from difficulty import DEFAULT_DIFFICULTY, DIFFICULTY_ORDER


SAVE_PATH = Path(__file__).resolve().parent.parent / "save_data.json"
DEFAULT_MAX_LEVEL = 5


def default_save_data():
    return {
        "difficulty": DEFAULT_DIFFICULTY,
        "progress": {
            name: {
                "unlocked_levels": [1],
                "completed_levels": [],
                "highest_unlocked_level": 1,
                "current_level": 1,
                "last_level": 1,
            }
            for name in DIFFICULTY_ORDER
        },
    }


def normalize_save_data(data):
    default = default_save_data()
    if not isinstance(data, dict):
        return default

    difficulty = data.get("difficulty", DEFAULT_DIFFICULTY)
    if difficulty not in DIFFICULTY_ORDER:
        difficulty = DEFAULT_DIFFICULTY

    progress = default["progress"]
    raw_progress = data.get("progress", {})
    if isinstance(raw_progress, dict):
        for difficulty_name in DIFFICULTY_ORDER:
            raw_entry = raw_progress.get(difficulty_name, {})
            if not isinstance(raw_entry, dict):
                continue

            completed = raw_entry.get("completed_levels", [])
            if not isinstance(completed, list):
                completed = []
            completed = sorted({
                level for level in completed
                if isinstance(level, int) and 1 <= level <= DEFAULT_MAX_LEVEL
            })

            unlocked = raw_entry.get("unlocked_levels", [1])
            if not isinstance(unlocked, list):
                unlocked = [1]
            unlocked = sorted({
                level for level in unlocked
                if isinstance(level, int) and 1 <= level <= DEFAULT_MAX_LEVEL
            })

            candidates = [1]
            for key in ("current_level", "highest_unlocked_level", "last_level"):
                value = raw_entry.get(key)
                if isinstance(value, int):
                    candidates.append(value)
            if unlocked:
                candidates.append(max(unlocked))
            if completed:
                candidates.append(min(DEFAULT_MAX_LEVEL, max(completed) + 1))

            current_level = max(1, min(DEFAULT_MAX_LEVEL, max(candidates)))
            if DEFAULT_MAX_LEVEL in completed:
                completed_levels = list(range(1, DEFAULT_MAX_LEVEL + 1))
                current_level = DEFAULT_MAX_LEVEL
            else:
                completed_levels = list(range(1, current_level))

            unlocked_levels = list(range(1, current_level + 1))
            progress[difficulty_name] = {
                "unlocked_levels": unlocked_levels,
                "completed_levels": completed_levels,
                "highest_unlocked_level": current_level,
                "current_level": current_level,
                "last_level": current_level,
            }

    return {
        "difficulty": difficulty,
        "progress": progress,
    }


def load_save_data():
    if not SAVE_PATH.exists():
        data = default_save_data()
        save_data(data)
        return data

    try:
        with SAVE_PATH.open("r", encoding="utf-8") as file:
            return normalize_save_data(json.load(file))
    except (OSError, json.JSONDecodeError):
        data = default_save_data()
        save_data(data)
        return data


def save_data(data):
    SAVE_PATH.write_text(json.dumps(normalize_save_data(data), indent=2), encoding="utf-8")


def get_progress(data, difficulty):
    return data["progress"][difficulty]


def set_difficulty(data, difficulty):
    data["difficulty"] = difficulty
    save_data(data)


def set_last_level(data, difficulty, level_number):
    progress = get_progress(data, difficulty)
    current_level = progress["current_level"]
    if level_number == current_level:
        progress["last_level"] = current_level
        save_data(data)


def mark_level_completed(data, difficulty, level_number, max_level):
    progress = get_progress(data, difficulty)
    current_level = progress["current_level"]
    if level_number != current_level:
        save_data(data)
        return

    if level_number < max_level:
        next_level = level_number + 1
        progress["current_level"] = next_level
        progress["last_level"] = next_level
        progress["highest_unlocked_level"] = next_level
        progress["unlocked_levels"] = list(range(1, next_level + 1))
        progress["completed_levels"] = list(range(1, next_level))
    else:
        progress["current_level"] = max_level
        progress["last_level"] = max_level
        progress["highest_unlocked_level"] = max_level
        progress["unlocked_levels"] = list(range(1, max_level + 1))
        progress["completed_levels"] = list(range(1, max_level + 1))
    save_data(data)
