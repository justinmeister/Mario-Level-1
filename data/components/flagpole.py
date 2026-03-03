"""Flagpole component for Super Mario Bros."""

from __future__ import annotations

from typing import Any, List

import pygame as pg

from data import constants as c
from .. import setup
from ..tools import sprite_utils


class Flag(pg.sprite.Sprite):
    """Flag on top of the flag pole at the end of the level"""

    rect: pg.Rect

    def __init__(self, x: int, y: int) -> None:
        super(Flag, self).__init__()
        self.sprite_sheet = setup.GFX["item_objects"]
        self.frames: List[pg.Surface] = []
        self.setup_images()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.right = x
        self.rect.y = y
        self.state = c.TOP_OF_POLE
        self.y_vel: float = 0

    def setup_images(self) -> None:
        """Sets up a list of image frames"""
        self.frames = []
        self.frames.append(self.get_image(128, 32, 16, 16))

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.BRICK_SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, *args: Any) -> None:
        """Updates behavior"""
        self.handle_state()

    def handle_state(self) -> None:
        """Determines behavior based on state"""
        if self.state == c.TOP_OF_POLE:
            self.image = self.frames[0]
        elif self.state == c.SLIDE_DOWN:
            self.sliding_down()
        elif self.state == c.BOTTOM_OF_POLE:
            self.image = self.frames[0]

    def sliding_down(self) -> None:
        """State when Mario reaches flag pole"""
        self.y_vel = 5
        self.rect.y += self.y_vel

        if self.rect.bottom >= 485:
            self.state = c.BOTTOM_OF_POLE


class Pole(pg.sprite.Sprite):
    """Pole that the flag is on top of"""

    rect: pg.Rect

    def __init__(self, x: int, y: int) -> None:
        super(Pole, self).__init__()
        self.sprite_sheet = setup.GFX["tile_set"]
        self.frames: List[pg.Surface] = []
        self.setup_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def setup_frames(self) -> None:
        """Create the frame list"""
        self.frames = []
        self.frames.append(self.get_image(263, 144, 2, 16))

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.BRICK_SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, *args: Any) -> None:
        """Placeholder for update, since there is nothing to update"""
        pass


class Finial(pg.sprite.Sprite):
    """The top of the flag pole"""

    def __init__(self, x: int, y: int) -> None:
        super(Finial, self).__init__()
        self.sprite_sheet = setup.GFX["tile_set"]
        self.frames: List[pg.Surface] = []
        self.setup_frames()
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def setup_frames(self) -> None:
        """Creates the self.frames list"""
        self.frames = []
        self.frames.append(self.get_image(228, 120, 8, 8))

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, *args: Any) -> None:
        pass
