#!/usr/bin/env python3
"""
Generate Mario-style background images programmatically.
Creates pixel-art style backgrounds without external assets.
"""

import pygame as pg
import os

# Initialize pygame
pg.init()

# Mario color palette
COLORS = {
    'sky_blue': (107, 140, 255),
    'sky_dark': (64, 64, 128),
    'cloud_white': (255, 255, 255),
    'cloud_shadow': (200, 200, 255),
    'hill_green': (0, 180, 0),
    'hill_dark': (0, 100, 0),
    'bush_green': (34, 139, 34),
    'ground_brown': (139, 69, 19),
    'brick_red': (178, 34, 34),
    'pipe_green': (0, 200, 0),
    'pipe_dark': (0, 100, 0),
    'castle_grey': (128, 128, 128),
    'castle_dark': (64, 64, 64),
    'star_yellow': (255, 215, 0),
    'night_blue': (10, 10, 50),
    'sunset_orange': (255, 140, 0),
    'sunset_pink': (255, 105, 180),
}


def draw_cloud(surface, x, y, size=1, color=COLORS['cloud_white']):
    """Draw a pixel-art cloud"""
    cloud_pixels = [
        (0, 2, 3, 3),
        (1, 1, 5, 2),
        (2, 0, 4, 1),
        (3, 1, 4, 2),
        (4, 2, 3, 2),
        (5, 3, 2, 1),
    ]
    for px, py, w, h in cloud_pixels:
        rect = pg.Rect(
            (x + px * 8 * size),
            (y + py * 8 * size),
            8 * size * w,
            8 * size * h
        )
        pg.draw.rect(surface, color, rect)


def draw_hill(surface, x, y, size=1, color=COLORS['hill_green']):
    """Draw a pixel-art hill"""
    points = [
        (x, y),
        (x + 100 * size, y - 80 * size),
        (x + 200 * size, y),
    ]
    pg.draw.polygon(surface, color, points)
    # Add details
    for i in range(3):
        detail_y = y - 20 * size - (i * 15 * size)
        detail_width = 150 * size - (i * 40 * size)
        if detail_width > 0:
            pg.draw.line(
                surface,
                COLORS['hill_dark'],
                (x + 25 * size + i * 10 * size, detail_y),
                (x + 25 * size + detail_width, detail_y),
                3
            )


def draw_bush(surface, x, y, size=1):
    """Draw a pixel-art bush"""
    bush_circles = [
        (x + 15 * size, y, 20 * size),
        (x + 35 * size, y - 5 * size, 25 * size),
        (x + 55 * size, y, 20 * size),
    ]
    for cx, cy, r in bush_circles:
        pg.draw.circle(surface, COLORS['bush_green'], (int(cx), int(cy)), int(r))


def draw_mushroom_platform(surface, x, y):
    """Draw a mushroom platform like in SMB3"""
    # Stem
    pg.draw.rect(surface, (255, 200, 100), (x + 40, y, 40, 60))
    # Cap
    pg.draw.ellipse(surface, COLORS['brick_red'], (x, y - 30, 120, 50))
    # Spots
    pg.draw.circle(surface, COLORS['cloud_white'], (x + 30, y - 15), 10)
    pg.draw.circle(surface, COLORS['cloud_white'], (x + 90, y - 15), 10)
    pg.draw.circle(surface, COLORS['cloud_white'], (x + 60, y - 25), 8)


def draw_castle(surface, x, y, size=1):
    """Draw a pixel-art castle"""
    # Main tower
    pg.draw.rect(surface, COLORS['castle_grey'], (x, y - 100 * size, 60 * size, 100 * size))
    pg.draw.rect(surface, COLORS['castle_dark'], (x + 5 * size, y - 95 * size, 50 * size, 90 * size))

    # Side towers
    pg.draw.rect(surface, COLORS['castle_grey'], (x - 40 * size, y - 60 * size, 30 * size, 60 * size))
    pg.draw.rect(surface, COLORS['castle_grey'], (x + 70 * size, y - 60 * size, 30 * size, 60 * size))

    # Tower tops
    pg.draw.rect(surface, COLORS['castle_dark'], (x - 40 * size, y - 80 * size, 30 * size, 20 * size))
    pg.draw.rect(surface, COLORS['castle_dark'], (x, y - 120 * size, 60 * size, 20 * size))
    pg.draw.rect(surface, COLORS['castle_dark'], (x + 70 * size, y - 80 * size, 30 * size, 20 * size))

    # Door
    pg.draw.ellipse(surface, COLORS['castle_dark'], (x + 15 * size, y - 30 * size, 30 * size, 30 * size))

    # Windows
    pg.draw.rect(surface, COLORS['star_yellow'], (x + 20 * size, y - 70 * size, 8 * size, 12 * size))
    pg.draw.rect(surface, COLORS['star_yellow'], (x + 32 * size, y - 70 * size, 8 * size, 12 * size))


def draw_pipe(surface, x, y, height=2):
    """Draw a green pipe"""
    pipe_width = 60
    pipe_height = 80 * height

    # Main pipe body
    pg.draw.rect(surface, COLORS['pipe_green'], (x, y, pipe_width, pipe_height))
    pg.draw.rect(surface, COLORS['pipe_dark'], (x + 5, y, 10, pipe_height))
    pg.draw.rect(surface, COLORS['pipe_dark'], (x + 45, y, 10, pipe_height))

    # Pipe top
    pg.draw.rect(surface, COLORS['pipe_green'], (x - 5, y, pipe_width + 10, 30))
    pg.draw.rect(surface, COLORS['pipe_dark'], (x, y, 10, 30))
    pg.draw.rect(surface, (0, 255, 0), (x + 50, y, 5, 30))


def draw_star(surface, x, y, size=20):
    """Draw a star"""
    points = []
    for i in range(5):
        angle = i * 72 - 90
        outer_x = x + size * pg.math.Vector2(1, 0).rotate(angle).x
        outer_y = y + size * pg.math.Vector2(1, 0).rotate(angle).y
        points.append((outer_x, outer_y))

        angle = i * 72 - 90 + 36
        inner_x = x + (size * 0.4) * pg.math.Vector2(1, 0).rotate(angle).x
        inner_y = y + (size * 0.4) * pg.math.Vector2(1, 0).rotate(angle).y
        points.append((inner_x, inner_y))

    pg.draw.polygon(surface, COLORS['star_yellow'], points)


def generate_sky_background(width=800, height=600):
    """Generate a classic sky background with clouds"""
    surface = pg.Surface((width, height))
    surface.fill(COLORS['sky_blue'])

    # Draw clouds
    cloud_positions = [(50, 80), (200, 120), (400, 60), (600, 100), (750, 80)]
    for x, y in cloud_positions:
        draw_cloud(surface, x, y, size=2)

    # Draw hills in background
    draw_hill(surface, 50, height - 100, size=2)
    draw_hill(surface, 300, height - 80, size=2)
    draw_hill(surface, 550, height - 120, size=2)

    # Draw bushes
    draw_bush(surface, 100, height - 50)
    draw_bush(surface, 400, height - 50)
    draw_bush(surface, 650, height - 50)

    return surface


def generate_night_background(width=800, height=600):
    """Generate a night sky background"""
    surface = pg.Surface((width, height))

    # Gradient sky
    for y in range(height):
        ratio = y / height
        r = int(COLORS['night_blue'][0] * (1 - ratio * 0.5))
        g = int(COLORS['night_blue'][1] * (1 - ratio * 0.5))
        b = int(COLORS['night_blue'][2] + ratio * 30)
        pg.draw.line(surface, (r, g, b), (0, y), (width, y))

    # Draw stars
    import random
    random.seed(42)  # Fixed seed for consistency
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height // 2)
        draw_star(surface, x, y, size=random.randint(5, 15))

    # Draw moon
    pg.draw.circle(surface, COLORS['cloud_white'], (width - 100, 80), 40)
    pg.draw.circle(surface, COLORS['night_blue'], (width - 90, 75), 35)

    # Draw castle silhouette
    draw_castle(surface, 100, height - 150, size=1.5)

    return surface


def generate_sunset_background(width=800, height=600):
    """Generate a sunset background"""
    surface = pg.Surface((width, height))

    # Gradient sunset sky
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            r = int(COLORS['sunset_orange'][0] * (1 - ratio))
            g = int(COLORS['sunset_orange'][1] * (1 - ratio * 1.5))
            b = int(COLORS['sunset_pink'][2] * ratio * 2)
        else:
            r = int(COLORS['sunset_pink'][0] * (1 - (ratio - 0.5) * 2))
            g = int(COLORS['sunset_pink'][1] * 0.5)
            b = int(COLORS['sunset_pink'][2] * 0.8)
        pg.draw.line(surface, (r, g, b), (0, y), (width, y))

    # Draw sun
    pg.draw.circle(surface, COLORS['star_yellow'], (width // 2, height - 100), 60)

    # Draw clouds
    cloud_positions = [(100, 150), (300, 100), (550, 180), (700, 120)]
    for x, y in cloud_positions:
        draw_cloud(surface, x, y, size=3, color=COLORS['sunset_pink'])

    # Draw mushroom platforms
    draw_mushroom_platform(surface, 150, height - 200)
    draw_mushroom_platform(surface, 500, height - 280)

    return surface


def generate_underground_background(width=800, height=600):
    """Generate an underground/cave background"""
    surface = pg.Surface((width, height))
    surface.fill((50, 30, 10))

    # Draw brick pattern
    brick_width = 80
    brick_height = 40
    for y in range(0, height, brick_height):
        offset = (y // brick_height) % 2 * (brick_width // 2)
        for x in range(-brick_width, width + brick_width, brick_width):
            brick_rect = pg.Rect(x + offset, y, brick_width - 2, brick_height - 2)
            pg.draw.rect(surface, COLORS['brick_red'], brick_rect)
            pg.draw.rect(surface, (100, 20, 20), brick_rect, 2)

    # Draw some pipes
    draw_pipe(surface, 150, height - 200, height=2)
    draw_pipe(surface, 550, height - 280, height=3)

    return surface


def generate_castle_background(width=800, height=600):
    """Generate a castle interior background"""
    surface = pg.Surface((width, height))
    surface.fill(COLORS['castle_dark'])

    # Draw stone pattern
    stone_width = 100
    stone_height = 60
    for y in range(0, height, stone_height):
        offset = (y // stone_height) % 2 * (stone_width // 2)
        for x in range(-stone_width, width + stone_width, stone_width):
            stone_rect = pg.Rect(x + offset, y, stone_width - 4, stone_height - 4)
            pg.draw.rect(surface, COLORS['castle_grey'], stone_rect)
            pg.draw.rect(surface, (40, 40, 40), stone_rect, 3)

    # Draw torches
    for x in [100, 700]:
        pg.draw.rect(surface, (100, 80, 40), (x, 200, 20, 60))
        pg.draw.circle(surface, COLORS['star_yellow'], (x + 10, 200), 15)
        pg.draw.circle(surface, COLORS['sunset_orange'], (x + 10, 200), 10)

    return surface


def save_background(surface, filename):
    """Save background to file"""
    os.makedirs('img', exist_ok=True)
    pg.image.save(surface, os.path.join('img', filename))
    print(f"Saved: img/{filename}")


def main():
    """Generate all backgrounds"""
    print("Generating Mario-style backgrounds...")

    backgrounds = [
        ('sky_background.png', generate_sky_background),
        ('night_background.png', generate_night_background),
        ('sunset_background.png', generate_sunset_background),
        ('underground_background.png', generate_underground_background),
        ('castle_background.png', generate_castle_background),
    ]

    for filename, generator in backgrounds:
        print(f"Generating {filename}...")
        surface = generator()
        save_background(surface, filename)

    print("\nDone! Backgrounds saved to img/ folder")
    print("\nTo use in game, add to resources/graphics/:")
    print("  - sky_background.png -> Classic sky level")
    print("  - night_background.png -> Night level")
    print("  - sunset_background.png -> Sunset level")
    print("  - underground_background.png -> Underground level")
    print("  - castle_background.png -> Castle level")


if __name__ == '__main__':
    main()
