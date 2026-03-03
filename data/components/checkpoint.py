"""Checkpoint component for Super Mario Bros."""

from __future__ import annotations

import pygame as pg


class Checkpoint(pg.sprite.Sprite):
    """Invisible sprite used to add enemies, special boxes
    and trigger sliding down the flag pole"""

    def __init__(self, x: int, name: str, y: int = 0, width: int = 10, height: int = 600) -> None:
        super(Checkpoint, self).__init__()
        self.image = pg.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name
