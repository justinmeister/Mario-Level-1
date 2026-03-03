"""Powerup classes for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

import pygame as pg

from data import constants as c
from .. import setup
from ..tools import sprite_utils


class Powerup(pg.sprite.Sprite):
    """Base class for all powerup_group"""

    image: pg.Surface
    rect: pg.Rect

    def __init__(self, x: int, y: int) -> None:
        super(Powerup, self).__init__()
        self.sprite_sheet: pg.Surface = setup.GFX["item_objects"]
        self.frames: List[pg.Surface] = []
        self.frame_index: int = 0
        self.state: str = c.REVEAL
        self.y_vel: float = -1
        self.x_vel: float = 0
        self.direction: str = c.RIGHT
        self.box_height: int = y
        self.gravity: float = 1
        self.max_y_vel: float = 8
        self.animate_timer: float = 0
        self.name: str = ""
        self.current_time: float = 0

    def setup_powerup(self, x: int, y: int, name: str, setup_frames: Callable[[], None]) -> None:
        """This separate setup function allows me to pass a different
        setup_frames method depending on what the powerup is"""
        self.frame_index = 0
        setup_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.state = c.REVEAL
        self.y_vel = -1
        self.x_vel = 0
        self.direction = c.RIGHT
        self.box_height = y - self.rect.height  # Top of the box where powerup came from
        self.gravity = 1
        self.max_y_vel = 8
        self.animate_timer = 0
        self.name = name

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Get the image frames from the sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, game_info: Dict[str, Any], *args: Any) -> None:
        """Updates powerup behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()

    def handle_state(self) -> None:
        pass

    def revealing(self, *args: Any) -> None:
        """Action when powerup leaves the coin box or brick"""
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.y_vel = 0
            self.state = c.SLIDE

    def sliding(self) -> None:
        """Action for when powerup slides along the ground"""
        if self.direction == c.RIGHT:
            self.x_vel = 3
        else:
            self.x_vel = -3

    def falling(self) -> None:
        """When powerups fall of a ledge"""
        if self.y_vel < self.max_y_vel:
            self.y_vel += self.gravity


class Mushroom(Powerup):
    """Powerup that makes Mario become bigger"""

    def __init__(self, x: int, y: int, name: str = "mushroom") -> None:
        super(Mushroom, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)

    def setup_frames(self) -> None:
        """Sets up frame list"""
        self.frames.append(self.get_image(0, 0, 16, 16))

    def handle_state(self) -> None:
        """Handles behavior based on state"""
        if self.state == c.REVEAL:
            self.revealing()
        elif self.state == c.SLIDE:
            self.sliding()
        elif self.state == c.FALL:
            self.falling()


class LifeMushroom(Mushroom):
    """1up mushroom"""

    def __init__(self, x: int, y: int, name: str = "1up_mushroom") -> None:
        super(LifeMushroom, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)

    def setup_frames(self) -> None:
        self.frames.append(self.get_image(16, 0, 16, 16))


class FireFlower(Powerup):
    """Powerup that allows Mario to throw fire balls"""

    def __init__(self, x: int, y: int, name: str = c.FIREFLOWER) -> None:
        super(FireFlower, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)

    def setup_frames(self) -> None:
        """Sets up frame list"""
        self.frames.append(self.get_image(0, 32, 16, 16))
        self.frames.append(self.get_image(16, 32, 16, 16))
        self.frames.append(self.get_image(32, 32, 16, 16))
        self.frames.append(self.get_image(48, 32, 16, 16))

    def handle_state(self) -> None:
        """Handle behavior based on state"""
        if self.state == c.REVEAL:
            self.revealing()
        elif self.state == c.RESTING:
            self.resting()

    def revealing(self) -> None:
        """Animation of flower coming out of box"""
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.state = c.RESTING

        self.animation()

    def resting(self) -> None:
        """Fire Flower staying still on opened box"""
        self.animation()

    def animation(self) -> None:
        """Method to make the Fire Flower blink"""
        if (self.current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.image = self.frames[self.frame_index]
            self.animate_timer = self.current_time


class Star(Powerup):
    """A powerup that gives mario invincibility"""

    def __init__(self, x: int, y: int, name: str = "star") -> None:
        super(Star, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)
        self.animate_timer = 0
        self.rect.y += 1
        self.gravity = 0.4

    def setup_frames(self) -> None:
        """Creating the self.frames list where the images for the animation
        are stored"""
        self.frames.append(self.get_image(1, 48, 15, 16))
        self.frames.append(self.get_image(17, 48, 15, 16))
        self.frames.append(self.get_image(33, 48, 15, 16))
        self.frames.append(self.get_image(49, 48, 15, 16))

    def handle_state(self) -> None:
        """Handles behavior based on state"""
        if self.state == c.REVEAL:
            self.revealing()
        elif self.state == c.BOUNCE:
            self.bouncing()

    def revealing(self) -> None:
        """When the star comes out of the box"""
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.start_bounce(-2)
            self.state = c.BOUNCE

        self.animation()

    def animation(self) -> None:
        """sets image for animation"""
        if (self.current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animate_timer = self.current_time
            self.image = self.frames[self.frame_index]

    def start_bounce(self, vel: float) -> None:
        """Transitions into bouncing state"""
        self.y_vel = vel

    def bouncing(self) -> None:
        """Action when the star is bouncing around"""
        self.animation()

        if self.direction == c.LEFT:
            self.x_vel = -5
        else:
            self.x_vel = 5


class FireBall(pg.sprite.Sprite):
    """Shot from Fire Mario"""

    image: pg.Surface
    rect: pg.Rect

    def __init__(self, x: int, y: int, facing_right: bool, name: str = c.FIREBALL) -> None:
        super(FireBall, self).__init__()
        self.sprite_sheet = setup.GFX["item_objects"]
        self.frames: List[pg.Surface] = []
        self.setup_frames()
        if facing_right:
            self.direction = c.RIGHT
            self.x_vel = 12
        else:
            self.direction = c.LEFT
            self.x_vel = -12
        self.y_vel: float = 10
        self.gravity: float = 0.9
        self.frame_index: int = 0
        self.animation_timer: float = 0
        self.state = c.FLYING
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.right = x
        self.rect.y = y
        self.name = name
        self.current_time: float = 0

    def setup_frames(self) -> None:
        """Sets up animation frames"""
        self.frames.append(self.get_image(96, 144, 8, 8))
        self.frames.append(self.get_image(104, 144, 8, 8))
        self.frames.append(self.get_image(96, 152, 8, 8))
        self.frames.append(self.get_image(104, 152, 8, 8))
        self.frames.append(self.get_image(112, 144, 16, 16))
        self.frames.append(self.get_image(112, 160, 16, 16))
        self.frames.append(self.get_image(112, 176, 16, 16))

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Get the image frames from the sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, game_info: Dict[str, Any], viewport: pg.Rect) -> None:
        """Updates fireball behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()
        self.check_if_off_screen(viewport)

    def handle_state(self) -> None:
        """Handles behavior based on state"""
        if self.state == c.FLYING:
            self.animation()
        elif self.state == c.BOUNCING:
            self.animation()
        elif self.state == c.EXPLODING:
            self.animation()

    def animation(self) -> None:
        """adjusts frame for animation"""
        if self.state == c.FLYING or self.state == c.BOUNCING:
            if (self.current_time - self.animation_timer) > 200:
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 0
                self.animation_timer = self.current_time
                self.image = self.frames[self.frame_index]

        elif self.state == c.EXPLODING:
            if (self.current_time - self.animation_timer) > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                    self.image = self.frames[self.frame_index]
                    self.animation_timer = self.current_time
                else:
                    self.kill()

    def explode_transition(self) -> None:
        """Transitions fireball to EXPLODING state"""
        self.frame_index = 4
        centerx = self.rect.centerx
        self.image = self.frames[self.frame_index]
        self.rect.centerx = centerx
        self.state = c.EXPLODING

    def check_if_off_screen(self, viewport: pg.Rect) -> None:
        """Removes from sprite group if off screen"""
        if (self.rect.x > viewport.right) or (self.rect.y > viewport.bottom) or (self.rect.right < viewport.x):
            self.kill()


class Hammer(Powerup):
    """Hammer projectile thrown by Hammer Bro."""

    def __init__(self, x: int, y: int, direction: str = c.RIGHT) -> None:
        super().__init__(x, y)
        self.name = "hammer"
        self.direction = direction
        self.state = c.THROWN
        self.x_vel = 3 if direction == c.RIGHT else -3
        self.y_vel = -8
        self.gravity = 0.5
        self.rect.y = y

    def update(self, game_info: Dict[str, Any]) -> None:
        """Update hammer physics"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.x_vel = 3 if self.direction == c.RIGHT else -3

        if self.state == c.THROWN:
            self.rect.x += self.x_vel
            self.rect.y += self.y_vel
            self.y_vel += self.gravity

            if self.rect.y >= self.box_height:
                self.rect.y = self.box_height
                self.y_vel = 0
                self.state = c.SLIDE

        elif self.state == c.SLIDE:
            self.rect.x += self.x_vel

        self.check_if_off_screen(pg.Rect(0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT))

    def check_if_off_screen(self, viewport: pg.Rect) -> None:
        """Removes from sprite group if off screen"""
        if (self.rect.x > viewport.right) or (self.rect.y > viewport.bottom) or (self.rect.right < viewport.x):
            self.kill()
