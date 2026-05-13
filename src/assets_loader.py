from pathlib import Path

import pygame


ASSET_FILENAMES = {
    "player": "player.png",
    "monster": "monster.png",
    "firefly": "firefly.png",
    "wall": "wall.png",
    "floor": "floor.png",
    "exit_closed": "exit_closed.png",
    "exit_open": "exit_open.png",
}
MENU_BACKGROUND = "menu_background.png"
CHINESE_FONT_NAMES = [
    "microsoftyahei",
    "simhei",
    "simsun",
    "msyh",
    "nsimsun",
    "kaiti",
    "fangsong",
]


def asset_directory():
    return Path(__file__).resolve().parent.parent / "assets"


def create_placeholder_surface(name, tile_size):
    surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)

    if name == "floor":
        surface.fill((28, 35, 36))
        pygame.draw.rect(surface, (38, 48, 48), surface.get_rect(), 1)
    elif name == "wall":
        surface.fill((76, 84, 92))
        pygame.draw.rect(surface, (44, 50, 56), surface.get_rect(), 3)
        pygame.draw.line(surface, (98, 108, 116), (0, tile_size // 2), (tile_size, tile_size // 2), 2)
    elif name == "player":
        surface.fill((28, 35, 36))
        pygame.draw.circle(surface, (82, 176, 255), (tile_size // 2, tile_size // 2), tile_size // 3)
        pygame.draw.circle(surface, (226, 246, 255), (tile_size // 2, tile_size // 2), tile_size // 6)
    elif name == "monster":
        surface.fill((28, 35, 36))
        rect = pygame.Rect(tile_size // 5, tile_size // 5, tile_size * 3 // 5, tile_size * 3 // 5)
        pygame.draw.rect(surface, (205, 67, 67), rect, border_radius=6)
        pygame.draw.circle(surface, (30, 20, 20), (tile_size // 3, tile_size // 3), 4)
        pygame.draw.circle(surface, (30, 20, 20), (tile_size * 2 // 3, tile_size // 3), 4)
    elif name == "firefly":
        surface.fill((28, 35, 36))
        pygame.draw.circle(surface, (255, 222, 82), (tile_size // 2, tile_size // 2), tile_size // 5)
        pygame.draw.circle(surface, (255, 244, 173), (tile_size // 2, tile_size // 2), tile_size // 3, 2)
    elif name == "exit_closed":
        surface.fill((28, 35, 36))
        pygame.draw.rect(surface, (90, 65, 42), (10, 6, tile_size - 20, tile_size - 12))
        pygame.draw.rect(surface, (42, 30, 22), (16, 12, tile_size - 32, tile_size - 24))
    elif name == "exit_open":
        surface.fill((28, 35, 36))
        pygame.draw.rect(surface, (74, 160, 104), (10, 6, tile_size - 20, tile_size - 12))
        pygame.draw.rect(surface, (214, 255, 194), (18, 14, tile_size - 36, tile_size - 28), 2)

    return surface


def create_menu_background(size):
    width, height = size
    surface = pygame.Surface((width, height))

    for y in range(height):
        ratio = y / max(1, height - 1)
        color = (
            int(8 + 12 * ratio),
            int(14 + 20 * ratio),
            int(28 + 24 * ratio),
        )
        pygame.draw.line(surface, color, (0, y), (width, y))

    line_color = (42, 72, 82)
    for x in range(40, width, 96):
        pygame.draw.line(surface, line_color, (x, 120), (x, height - 80), 2)
    for y in range(140, height - 80, 76):
        pygame.draw.line(surface, line_color, (60, y), (width - 60, y), 2)

    firefly_colors = [(255, 226, 94), (160, 235, 180), (255, 247, 180)]
    points = [
        (width * 0.18, height * 0.24),
        (width * 0.78, height * 0.20),
        (width * 0.66, height * 0.70),
        (width * 0.30, height * 0.76),
        (width * 0.50, height * 0.42),
    ]
    for index, (x, y) in enumerate(points):
        color = firefly_colors[index % len(firefly_colors)]
        center = (int(x), int(y))
        pygame.draw.circle(surface, color, center, 4)
        pygame.draw.circle(surface, color, center, 18, 1)

    return surface


def ensure_placeholder_assets(tile_size):
    assets_dir = asset_directory()
    assets_dir.mkdir(exist_ok=True)

    for name, filename in ASSET_FILENAMES.items():
        path = assets_dir / filename
        if not path.exists():
            pygame.image.save(create_placeholder_surface(name, tile_size), path)


def ensure_menu_background(size):
    assets_dir = asset_directory()
    assets_dir.mkdir(exist_ok=True)
    path = assets_dir / MENU_BACKGROUND
    if not path.exists():
        pygame.image.save(create_menu_background(size), path)


def load_assets(tile_size):
    ensure_placeholder_assets(tile_size)
    assets_dir = asset_directory()
    assets = {}

    for name, filename in ASSET_FILENAMES.items():
        image = pygame.image.load(str(assets_dir / filename)).convert_alpha()
        assets[name] = pygame.transform.scale(image, (tile_size, tile_size))

    return assets


def load_menu_background(size):
    ensure_menu_background(size)
    path = asset_directory() / MENU_BACKGROUND
    image = pygame.image.load(str(path)).convert()
    return pygame.transform.scale(image, size)


def load_font(size):
    if not pygame.font.get_init():
        pygame.font.init()

    for font_name in CHINESE_FONT_NAMES:
        font_path = pygame.font.match_font(font_name)
        if font_path:
            return pygame.font.Font(font_path, size)

    print("未找到中文字体，中文可能无法正常显示")
    return pygame.font.Font(None, size)
