"""Bricks that can be destroyed"""

from __future__ import annotations

from typing import Optional, Any, TYPE_CHECKING

import pygame as pg

from .. import setup
from ..tools import sprite_utils
from .. import constants as c

if TYPE_CHECKING:
    from . import powerups
    from . import coin


class Brick(pg.sprite.Sprite):
    """Bricks that can be destroyed"""

    def __init__(
        self,
        x: int,
        y: int,
        contents: Optional[str] = None,
        powerup_group: Optional[pg.sprite.Group] = None,
        name: str = "brick",
    ) -> None:
        """Initialize the object"""
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX["tile_set"]

        self.frames: list[pg.Surface] = []
        self.frame_index: int = 0
        self.setup_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pg.mask.from_surface(self.image)
        self.bumped_up = False
        self.rest_height: float = y
        self.state = c.RESTING
        self.y_vel: float = 0
        self.gravity: float = 1.2
        self.name = name
        self.contents = contents
        self.coin_total: int = 0
        self.group = powerup_group
        self.powerup_in_box = True
        self.powerup: Optional[Any] = None

        self.setup_contents()

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts the image from the sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.BRICK_SIZE_MULTIPLIER, c.BLACK
        )

    def setup_frames(self) -> None:
        """Set the frames to a list"""
        self.frames.append(self.get_image(16, 0, 16, 16))
        self.frames.append(self.get_image(432, 0, 16, 16))

    def setup_contents(self) -> None:
        """Put 6 coins in contents if needed"""
        if self.contents == "6coins":
            self.coin_total = 6
        else:
            self.coin_total = 0

    def update(self) -> None:
        """Updates the brick"""
        self.handle_states()

    def handle_states(self) -> None:
        """Determines brick behavior based on state"""
        if self.state == c.RESTING:
            self.resting()
        elif self.state == c.BUMPED:
            self.bumped()
        elif self.state == c.OPENED:
            self.opened()

    def resting(self) -> None:
        """State when not moving"""
        if self.contents == "6coins":
            if self.coin_total == 0:
                self.state = c.OPENED

    def bumped(self) -> None:
        """Action during a BUMPED state"""
        if self.rect is None:
            return
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y >= (self.rest_height + 5):
            self.rect.y = self.rest_height
            if self.contents == "star":
                self.state = c.OPENED
            elif self.contents == "6coins":
                if self.coin_total == 0:
                    self.state = c.OPENED
                else:
                    self.state = c.RESTING
            else:
                self.state = c.RESTING

    def start_bump(self, score_group: pg.sprite.Group) -> None:
        """Transitions brick into BUMPED state"""
        self.y_vel = -6

        if self.contents == "6coins":
            setup.SFX["coin"].play()

            if self.coin_total > 0 and self.rect is not None and self.group is not None:
                self.group.add(coin.Coin(int(self.rect.centerx), int(self.rect.y), list(score_group)))
                self.coin_total -= 1
                if self.coin_total == 0:
                    self.frame_index = 1
                    self.image = self.frames[self.frame_index]
        elif self.contents == "star":
            setup.SFX["powerup_appears"].play()
            self.frame_index = 1
            self.image = self.frames[self.frame_index]

        self.state = c.BUMPED

    def opened(self) -> None:
        """Action during OPENED state"""
        self.frame_index = 1
        self.image = self.frames[self.frame_index]

        if self.contents == "star" and self.powerup_in_box:
            if self.rect is not None and self.group is not None:
                self.group.add(powerups.Star(int(self.rect.centerx), int(self.rest_height)))
            self.powerup_in_box = False


class BrickPiece(pg.sprite.Sprite):
    """Pieces that appear when bricks are broken"""

    image: pg.Surface
    rect: pg.Rect

    def __init__(self, x: int, y: int, xvel: float, yvel: float) -> None:
        super(BrickPiece, self).__init__()
        self.sprite_sheet = setup.GFX["item_objects"]
        self.setup_frames()
        self.frame_index: int = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_vel = xvel
        self.y_vel = yvel
        self.gravity = 0.8

    def setup_frames(self) -> None:
        """create the frame list"""
        self.frames: list[pg.Surface] = []

        image = self.get_image(68, 20, 8, 8)
        reversed_image = pg.transform.flip(image, True, False)

        self.frames.append(image)
        self.frames.append(reversed_image)

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extract image from sprite sheet"""
        image = pg.Surface((width, height), pg.SRCALPHA)
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(
            image, (int(rect.width * c.BRICK_SIZE_MULTIPLIER), int(rect.height * c.BRICK_SIZE_MULTIPLIER))
        )
        return image

    def update(self) -> None:
        """Update brick piece"""
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        self.check_if_off_screen()

    def check_if_off_screen(self) -> None:
        """Remove from sprite groups if off screen"""
        if self.rect.y > c.SCREEN_HEIGHT:
            self.kill()
