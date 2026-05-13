TEXTS = {
    "title": "萤火虫迷宫 Firefly Maze",
    "main_menu": {
        "Start Game": "开始游戏",
        "Level Select": "选择关卡",
        "Difficulty": "难度选择",
        "Settings": "设置",
        "Quit": "退出游戏",
    },
    "difficulty": {
        "Easy": "简单",
        "Normal": "普通",
        "Hard": "困难",
    },
    "status": {
        "running": "进行中",
        "won": "胜利",
        "lost": "游戏失败",
        "quit": "已退出",
        "paused": "已暂停",
    },
    "level_status": {
        "completed": "已通关",
        "current": "当前关卡",
        "locked": "未解锁",
        "locked_hint": "请先通过前面的关卡",
    },
    "pause_menu": {
        "Resume": "继续游戏",
        "Restart Level": "重新开始本关",
        "Back to Main Menu": "返回主界面",
        "Quit": "退出游戏",
    },
    "settings": {
        "Toggle Music": "切换音乐静音",
        "Back": "返回",
        "music_on": "音乐：开启",
        "music_off": "音乐：静音",
        "note": "音乐文件：assets/bgm.mp3，默认音量 0.4，按 M 静音/恢复",
    },
    "hud": {
        "level": "关卡",
        "difficulty": "难度",
        "score": "得分",
        "fireflies": "萤火虫",
        "status": "状态",
    },
    "result": {
        "victory": "胜利",
        "defeat": "游戏失败",
        "quit": "已退出",
        "final_score": "最终得分",
        "all_completed": "全部关卡已完成",
    },
    "hints": {
        "menu": "↑/↓ 选择    Enter 确认    Esc 返回",
        "game": "移动：W/A/S/D 或方向键    空格：射击    M：静音/恢复音乐    Esc：暂停",
        "pause": "↑/↓ 选择    Enter 确认    Esc 返回游戏",
        "level_select": "Enter：进入已解锁关卡    Esc：返回",
        "end": "R：重新开始本关    Esc：返回主界面    M：静音/恢复音乐",
        "victory_next": "Enter：进入下一关    R：重新开始本关    Esc：返回主界面    M：静音/恢复音乐",
        "victory_done": "Enter：返回主界面    R：重新开始本关    Esc：返回主界面    M：静音/恢复音乐",
    },
    "messages": {
        "wall": "前方是墙，无法通过",
        "leave_maze": "不能离开迷宫",
        "monster": "你撞上了怪物",
        "firefly": "你收集到一只萤火虫",
        "exit_closed": "出口尚未开启，请先收集所有萤火虫",
        "exit_open": "出口已经开启",
        "hit_monster": "击中了怪物",
        "caught": "你被怪物抓住了",
        "escaped": "你逃出了迷宫",
        "quit": "你已退出本局",
    },
}


def t(section, key):
    return TEXTS[section][key]


def difficulty_label(name):
    return TEXTS["difficulty"].get(name, name)


def main_menu_label(item):
    return TEXTS["main_menu"].get(item, item)
