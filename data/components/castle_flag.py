"""Castle flag component for Super Mario Bros."""

from __future__ import annotations

from typing import Any

import pygame as pg

from .. import constants as c
from .. import setup
from ..tools import sprite_utils


class Flag(pg.sprite.Sprite):
    """Flag on the castle"""

    rect: pg.Rect

    def __init__(self, x: int, y: int) -> None:
        """Initialize object"""
        super(Flag, self).__init__()
        self.sprite_sheet = setup.GFX["item_objects"]
        self.image = self.get_image(129, 2, 14, 14)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.state = "rising"
        self.y_vel: float = -2
        self.target_height = y

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, *args: Any) -> None:
        """Updates flag position"""
        if self.state == "rising":
            self.rising()
        elif self.state == "resting":
            self.resting()

    def rising(self) -> None:
        """State when flag is rising to be on the castle"""
        self.rect.y += self.y_vel
        if self.rect.bottom <= self.target_height:
            self.state = "resting"

    def resting(self) -> None:
        """State when the flag is stationary doing nothing"""
        pass
