"""Coins found in boxes and bricks."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import pygame as pg

from .. import constants as c
from .. import setup
from ..tools import sprite_utils
from . import score

if TYPE_CHECKING:
    pass


class Coin(pg.sprite.Sprite):
    """Coins found in boxes and bricks"""

    def __init__(self, x: int, y: int, score_group: List[Any]) -> None:
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX["item_objects"]
        self.frames: List[pg.Surface] = []
        self.frame_index: int = 0
        self.animation_timer: float = 0
        self.state: str = c.SPIN
        self.setup_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y - 5
        self.gravity: float = 1
        self.y_vel: float = -15
        self.initial_height = self.rect.bottom - 5
        self.score_group = score_group
        self.current_time: float = 0
        self.viewport: Optional[pg.Rect] = None

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Get the image frames from the sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK
        )

    def setup_frames(self) -> None:
        """create the frame list"""
        self.frames.append(self.get_image(52, 113, 8, 14))
        self.frames.append(self.get_image(4, 113, 8, 14))
        self.frames.append(self.get_image(20, 113, 8, 14))
        self.frames.append(self.get_image(36, 113, 8, 14))

    def update(self, game_info: Dict[str, Any], viewport: pg.Rect) -> None:
        """Update the coin's behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.viewport = viewport
        if self.state == c.SPIN:
            self.spinning()

    def spinning(self) -> None:
        """Action when the coin is in the SPIN state"""
        self.image = self.frames[self.frame_index]
        if self.rect:
            self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if (self.current_time - self.animation_timer) > 80:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.animation_timer = self.current_time

        if self.rect and self.rect.bottom > self.initial_height:
            self.kill()
            if self.rect and self.viewport:
                self.score_group.append(score.Score(int(self.rect.centerx - self.viewport.x), int(self.rect.y), 200))
