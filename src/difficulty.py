DIFFICULTY_ORDER = ["Easy", "Normal", "Hard"]

DIFFICULTIES = {
    "Easy": {
        "monster_count": 1,
        "firefly_count": 1,
        "chase_probability": 0.15,
        "monster_move_interval_ms": 850,
        "monster_kill_score": 5,
        "bullet_cooldown_ms": 250,
        "max_bullets": 3,
        "bullet_move_interval_ms": 120,
    },
    "Normal": {
        "monster_count": 2,
        "firefly_count": 2,
        "chase_probability": 0.4,
        "monster_move_interval_ms": 700,
        "monster_kill_score": 10,
        "bullet_cooldown_ms": 250,
        "max_bullets": 3,
        "bullet_move_interval_ms": 120,
    },
    "Hard": {
        "monster_count": 3,
        "firefly_count": 3,
        "chase_probability": 0.75,
        "monster_move_interval_ms": 550,
        "monster_kill_score": 15,
        "bullet_cooldown_ms": 250,
        "max_bullets": 3,
        "bullet_move_interval_ms": 100,
    },
}

DEFAULT_DIFFICULTY = "Normal"


def get_difficulty(name):
    return DIFFICULTIES.get(name, DIFFICULTIES[DEFAULT_DIFFICULTY])


def next_difficulty(name, step):
    index = DIFFICULTY_ORDER.index(name) if name in DIFFICULTY_ORDER else 1
    return DIFFICULTY_ORDER[(index + step) % len(DIFFICULTY_ORDER)]
