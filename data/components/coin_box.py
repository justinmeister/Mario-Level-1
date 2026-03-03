"""Coin box sprite"""

from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING

import pygame as pg

from .. import setup
from ..tools import sprite_utils
from .. import constants as c
from ..constants_extended import ANIMATION_FAST, ANIMATION_SLOW
from . import coin
from . import powerups

if TYPE_CHECKING:
    pass


class CoinBox(pg.sprite.Sprite):
    """Coin box sprite"""

    image: pg.Surface
    rect: pg.Rect

    def __init__(self, x: int, y: int, contents: str = "coin", group: Optional[pg.sprite.Group] = None) -> None:
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX["tile_set"]
        self.frames: list[pg.Surface] = []
        self.setup_frames()
        self.frame_index: int = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pg.mask.from_surface(self.image)
        self.animation_timer: float = 0
        self.first_half = True
        self.state = c.RESTING
        self.rest_height: float = y
        self.gravity: float = 1.2
        self.y_vel: float = 0
        self.contents = contents
        self.group = group
        self.powerup: Optional[Any] = None

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extract image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.BRICK_SIZE_MULTIPLIER, c.BLACK
        )

    def setup_frames(self) -> None:
        """Create frame list"""
        self.frames.append(self.get_image(384, 0, 16, 16))
        self.frames.append(self.get_image(400, 0, 16, 16))
        self.frames.append(self.get_image(416, 0, 16, 16))
        self.frames.append(self.get_image(432, 0, 16, 16))

    def update(self, game_info: dict) -> None:
        """Update coin box behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_states()

    def handle_states(self) -> None:
        """Determine action based on RESTING, BUMPED or OPENED
        state"""
        if self.state == c.RESTING:
            self.resting()
        elif self.state == c.BUMPED:
            self.bumped()
        elif self.state == c.OPENED:
            self.opened()

    def resting(self) -> None:
        """Action when in the RESTING state"""
        if self.first_half:
            if self.frame_index == 0:
                if (self.current_time - self.animation_timer) > ANIMATION_SLOW:
                    self.frame_index += 1
                    self.animation_timer = self.current_time
            elif self.frame_index < 2:
                if (self.current_time - self.animation_timer) > ANIMATION_FAST:
                    self.frame_index += 1
                    self.animation_timer = self.current_time
            elif self.frame_index == 2:
                if (self.current_time - self.animation_timer) > ANIMATION_FAST:
                    self.frame_index -= 1
                    self.first_half = False
                    self.animation_timer = self.current_time
        else:
            if self.frame_index == 1:
                if (self.current_time - self.animation_timer) > ANIMATION_FAST:
                    self.frame_index -= 1
                    self.first_half = True
                    self.animation_timer = self.current_time

        self.image = self.frames[self.frame_index]

    def bumped(self) -> None:
        """Action after Mario has bumped the box from below"""
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y > self.rest_height + 5:
            self.rect.y = self.rest_height
            self.state = c.OPENED
            if self.group is not None:
                if self.contents == "mushroom":
                    self.group.add(powerups.Mushroom(self.rect.centerx, self.rect.y))
                elif self.contents == "fireflower":
                    self.group.add(powerups.FireFlower(self.rect.centerx, self.rect.y))
                elif self.contents == "1up_mushroom":
                    self.group.add(powerups.LifeMushroom(self.rect.centerx, self.rect.y))

        self.frame_index = 3
        self.image = self.frames[self.frame_index]

    def start_bump(self, score_group: pg.sprite.Group) -> None:
        """Transitions box into BUMPED state"""
        self.y_vel = -6
        self.state = c.BUMPED

        if self.group is not None and self.contents == "coin":
            self.group.add(coin.Coin(self.rect.centerx, self.rect.y, list(score_group)))
            setup.SFX["coin"].play()
        else:
            setup.SFX["powerup_appears"].play()

    def opened(self) -> None:
        """Placeholder for OPENED state"""
        pass
