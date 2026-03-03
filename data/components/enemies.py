"""Enemy classes for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Callable, List

import pygame as pg

from .. import setup
from ..tools import sprite_utils
from .. import constants as c
from ..constants_extended import ANIMATION_FAST


class Enemy(pg.sprite.Sprite):
    """Base class for all enemies (Goombas, Koopas, etc.)"""

    __slots__ = [
        "sprite_sheet",
        "frames",
        "frame_index",
        "animate_timer",
        "death_timer",
        "gravity",
        "state",
        "name",
        "direction",
        "x_vel",
        "y_vel",
        "current_time",
        "mario",
        "image",
        "rect",
    ]

    rect: pg.Rect
    state: Any

    def __init__(self) -> None:
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet: pg.Surface = setup.GFX["smb_enemies_sheet"]
        self.frames: List[pg.Surface] = []
        self.frame_index: int = 0
        self.animate_timer: float = 0
        self.death_timer: float = 0
        self.gravity: float = 1.5
        self.state: Any = c.WALK
        self.name: str = ""
        self.direction: str = ""
        self.x_vel: float = 0
        self.y_vel: float = 0
        self.current_time: float = 0
        self.mario: Any = None

    def setup_enemy(self, x: int, y: int, direction: str, name: str, setup_frames: Callable[[], None]) -> None:
        """Sets up various values for enemy"""
        self.frame_index = 0
        self.animate_timer = 0
        self.death_timer = 0
        self.gravity = 1.5
        self.state = c.WALK

        self.name = name
        self.direction = direction
        setup_frames()

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.set_velocity()

    def set_velocity(self) -> None:
        """Sets velocity vector based on direction"""
        if self.direction == c.LEFT:
            self.x_vel = -2
        else:
            self.x_vel = 2

        self.y_vel = 0

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Get the image frames from the sprite sheet"""
        return sprite_utils.extract_image(self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK)

    def handle_state(self) -> None:
        """Enemy behavior based on state"""
        if self.state == c.WALK:
            self.walking()
        elif self.state == c.FALL:
            self.falling()
        elif self.state == c.SHELL_SLIDE:
            self.shell_sliding()  # type: ignore[attr-defined]
        elif self.state == c.DEATH_JUMP:
            self.death_jumping()

    def walking(self) -> None:
        """Default state of moving sideways"""
        if (self.current_time - self.animate_timer) > ANIMATION_FAST:
            if self.frame_index == 0:
                self.frame_index += 1
            elif self.frame_index == 1:
                self.frame_index = 0

            self.animate_timer = self.current_time

    def falling(self) -> None:
        """For when it falls off a ledge"""
        if self.y_vel < 10:
            self.y_vel += self.gravity

    def jumped_on(self) -> None:
        """When the enemy is stomped on - kills it after delay"""
        self.frame_index = 0
        if (self.current_time - self.death_timer) > 500:
            self.kill()
        else:
            self.death_timer = self.current_time

    def death_jumping(self) -> None:
        """Death animation"""
        self.rect.y += self.y_vel
        self.rect.x += self.x_vel
        self.y_vel += self.gravity

        if self.rect.y > 600:
            self.kill()

    def start_death_jump(self, direction: str) -> None:
        """Transitions enemy into a DEATH JUMP state"""
        self.y_vel = -8
        if direction == c.RIGHT:
            self.x_vel = 2
        else:
            self.x_vel = -2
        self.gravity = 0.5
        self.frame_index = 3
        self.image = self.frames[self.frame_index]
        self.state = c.DEATH_JUMP

    def animation(self) -> None:
        """Basic animation, switching between two frames"""
        self.image = self.frames[self.frame_index]

    def update(self, game_info: dict, *args: Any) -> None:
        """Updates enemy behavior"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()
        self.animation()


class Goomba(Enemy):
    def __init__(self, y: int = c.GROUND_HEIGHT, x: int = 0, direction: str = c.LEFT, name: str = "goomba") -> None:
        Enemy.__init__(self)
        self.setup_enemy(x, y, direction, name, self.setup_frames)

    def setup_frames(self) -> None:
        """Put the image frames in a list to be animated"""

        self.frames.append(self.get_image(0, 4, 16, 16))
        self.frames.append(self.get_image(30, 4, 16, 16))
        self.frames.append(self.get_image(61, 0, 16, 16))
        self.frames.append(pg.transform.flip(self.frames[1], False, True))

    def jumped_on(self) -> None:
        """When Mario squishes him - dies after 500ms"""
        self.frame_index = 2

        if self.death_timer == 0:
            self.death_timer = self.current_time

        if (self.current_time - self.death_timer) > 500:
            self.kill()


class Koopa(Enemy):
    def __init__(self, y: int = c.GROUND_HEIGHT, x: int = 0, direction: str = c.LEFT, name: str = "koopa") -> None:
        Enemy.__init__(self)
        self.setup_enemy(x, y, direction, name, self.setup_frames)

    def setup_frames(self) -> None:
        """Sets frame list"""
        self.frames.append(self.get_image(150, 0, 16, 24))
        self.frames.append(self.get_image(180, 0, 16, 24))
        self.frames.append(self.get_image(360, 5, 16, 15))
        self.frames.append(pg.transform.flip(self.frames[2], False, True))

    def jumped_on(self) -> None:
        """When Mario jumps on the Koopa and puts him in his shell"""
        self.x_vel = 0
        self.frame_index = 2
        shell_y = self.rect.bottom
        shell_x = self.rect.x
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.x = shell_x
        self.rect.bottom = shell_y

    def shell_sliding(self) -> None:
        """When the koopa is sliding along the ground in his shell"""
        if self.direction == c.RIGHT:
            self.x_vel = 10
        elif self.direction == c.LEFT:
            self.x_vel = -10
