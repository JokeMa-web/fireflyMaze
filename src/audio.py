from pathlib import Path

import pygame


DEFAULT_VOLUME = 0.4
_music_loaded = False
_muted = False


def music_path():
    return Path(__file__).resolve().parent.parent / "assets" / "bgm.mp3"


def start_background_music(volume=DEFAULT_VOLUME):
    global _music_loaded, _muted

    path = music_path()
    if not path.exists():
        print(f"未找到背景音乐文件：{path}")
        return False

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except pygame.error as error:
        print(f"背景音乐启动失败：{error}")
        _music_loaded = False
        return False

    _music_loaded = True
    _muted = False
    return True


def toggle_mute(volume=DEFAULT_VOLUME):
    global _muted

    if not _music_loaded:
        return False

    _muted = not _muted
    pygame.mixer.music.set_volume(0.0 if _muted else volume)
    return _muted


def is_muted():
    return _muted


def stop_music():
    if not _music_loaded:
        return

    try:
        pygame.mixer.music.stop()
    except pygame.error as error:
        print(f"背景音乐停止失败：{error}")
