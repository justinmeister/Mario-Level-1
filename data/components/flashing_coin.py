"""Flashing coin component for Super Mario Bros."""

from __future__ import annotations

from typing import List

import pygame as pg

from data import constants as c
from .. import setup
from ..tools import sprite_utils


class Coin(pg.sprite.Sprite):
    """Flashing coin next to coin total info"""

    def __init__(self, x: int, y: int) -> None:
        super(Coin, self).__init__()
        self.sprite_sheet = setup.GFX["item_objects"]
        self.frames: List[pg.Surface] = []
        self.create_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer: float = 0
        self.first_half = True
        self.frame_index: int = 0

    def create_frames(self) -> None:
        """Extract coin images from sprite sheet and assign them to a list"""
        self.frames = []
        self.frame_index = 0

        self.frames.append(self.get_image(1, 160, 5, 8))
        self.frames.append(self.get_image(9, 160, 5, 8))
        self.frames.append(self.get_image(17, 160, 5, 8))

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.BRICK_SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, current_time: float) -> None:
        """Animates flashing coin"""
        if self.first_half:
            if self.frame_index == 0:
                if (current_time - self.timer) > 375:
                    self.frame_index += 1
                    self.timer = current_time
            elif self.frame_index < 2:
                if (current_time - self.timer) > 125:
                    self.frame_index += 1
                    self.timer = current_time
            elif self.frame_index == 2:
                if (current_time - self.timer) > 125:
                    self.frame_index -= 1
                    self.first_half = False
                    self.timer = current_time
        else:
            if self.frame_index == 1:
                if (current_time - self.timer) > 125:
                    self.frame_index -= 1
                    self.first_half = True
                    self.timer = current_time

        self.image = self.frames[self.frame_index]
