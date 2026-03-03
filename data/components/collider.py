"""Collider component for Super Mario Bros."""

from __future__ import annotations

from typing import Optional

import pygame as pg


class Collider(pg.sprite.Sprite):
    """Invisible sprites placed overtop background parts
    that can be collided with (pipes, steps, ground, etc."""

    def __init__(self, x: int, y: int, width: int, height: int, name: str = "collider") -> None:
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.state: Optional[str] = None
        self.name = name
