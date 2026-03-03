"""Mario player sprite."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import pygame as pg

from .. import setup, tools
from ..tools import sprite_utils
from data import constants as c
from ..constants_extended import (
    ANIMATION_NORMAL,
    TRANSITION_ANIMATION_SPEED,
    INVINCIBILITY_DURATION,
)

if TYPE_CHECKING:
    from . import powerups


class Mario(pg.sprite.Sprite):
    """Mario player sprite."""

    __slots__ = [
        'sprite_sheet',
        'walking_timer', 'invincible_animation_timer', 'invincible_start_timer',
        'fire_transition_timer', 'death_timer', 'transition_timer', 'last_fireball_time',
        'hurt_invisible_timer', 'hurt_invisible_timer2', 'flag_pole_timer',
        'facing_right', 'allow_jump', 'dead', 'invincible', 'big', 'fire',
        'allow_fireball', 'in_transition_state', 'hurt_invincible', 'in_castle',
        'crouching', 'losing_invincibility',
        'x_vel', 'y_vel', 'max_x_vel', 'max_y_vel', 'x_accel', 'jump_vel', 'gravity',
        'frame_index', 'invincible_index', 'fire_transition_index', 'fireball_count',
        'flag_pole_right',
        'state', 'image', 'rect', 'mask', 'key_timer',
        'right_frames', 'left_frames',
        'right_small_normal_frames', 'left_small_normal_frames',
        'right_small_green_frames', 'left_small_green_frames',
        'right_small_red_frames', 'left_small_red_frames',
        'right_small_black_frames', 'left_small_black_frames',
        'right_big_normal_frames', 'left_big_normal_frames',
        'right_big_green_frames', 'left_big_green_frames',
    ]

    def __init__(self) -> None:
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX["mario_bros"]

        self.setup_timers()
        self.setup_state_booleans()
        self.setup_forces()
        self.setup_counters()
        self.load_images_from_sheet()

        self.state = c.WALK
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

        self.key_timer = 0

    def setup_timers(self) -> None:
        """Sets up timers for animations"""
        self.walking_timer: float = 0
        self.invincible_animation_timer: float = 0
        self.invincible_start_timer: float = 0
        self.fire_transition_timer: float = 0
        self.death_timer: float = 0
        self.transition_timer: float = 0
        self.last_fireball_time: float = 0
        self.hurt_invisible_timer: float = 0
        self.hurt_invisible_timer2: float = 0
        self.flag_pole_timer: float = 0

    def setup_state_booleans(self) -> None:
        """Sets up booleans that affect Mario's behavior"""
        self.facing_right: bool = True
        self.allow_jump: bool = True
        self.dead: bool = False
        self.invincible: bool = False
        self.big: bool = False
        self.fire: bool = False
        self.allow_fireball: bool = True
        self.in_transition_state: bool = False
        self.hurt_invincible: bool = False
        self.in_castle: bool = False
        self.crouching: bool = False
        self.losing_invincibility: bool = False

    def setup_forces(self) -> None:
        """Sets up forces that affect Mario's velocity"""
        self.x_vel: float = 0
        self.y_vel: float = 0
        self.max_x_vel: float = c.MAX_WALK_SPEED
        self.max_y_vel: float = c.MAX_Y_VEL
        self.x_accel: float = c.WALK_ACCEL
        self.jump_vel: float = c.JUMP_VEL
        self.gravity: float = c.GRAVITY

    def setup_counters(self) -> None:
        """These keep track of various total for important values"""
        self.frame_index: int = 0
        self.invincible_index: int = 0
        self.fire_transition_index: int = 0
        self.fireball_count: int = 0
        self.flag_pole_right: int = 0

    def load_images_from_sheet(self) -> None:
        """Extracts Mario images from his sprite sheet and assigns
        them to appropriate lists"""
        self.right_frames: List[pg.Surface] = []
        self.left_frames: List[pg.Surface] = []

        self.right_small_normal_frames: List[pg.Surface] = []
        self.left_small_normal_frames: List[pg.Surface] = []
        self.right_small_green_frames: List[pg.Surface] = []
        self.left_small_green_frames: List[pg.Surface] = []
        self.right_small_red_frames: List[pg.Surface] = []
        self.left_small_red_frames: List[pg.Surface] = []
        self.right_small_black_frames: List[pg.Surface] = []
        self.left_small_black_frames: List[pg.Surface] = []

        self.right_big_normal_frames: List[pg.Surface] = []
        self.left_big_normal_frames: List[pg.Surface] = []
        self.right_big_green_frames: List[pg.Surface] = []
        self.left_big_green_frames: List[pg.Surface] = []
        self.right_big_red_frames: List[pg.Surface] = []
        self.left_big_red_frames: List[pg.Surface] = []
        self.right_big_black_frames: List[pg.Surface] = []
        self.left_big_black_frames: List[pg.Surface] = []

        self.right_fire_frames: List[pg.Surface] = []
        self.left_fire_frames: List[pg.Surface] = []

        # Images for normal small mario#

        self.right_small_normal_frames.append(self.get_image(178, 32, 12, 16))  # Right [0]
        self.right_small_normal_frames.append(self.get_image(80, 32, 15, 16))  # Right walking 1 [1]
        self.right_small_normal_frames.append(self.get_image(96, 32, 16, 16))  # Right walking 2 [2]
        self.right_small_normal_frames.append(self.get_image(112, 32, 16, 16))  # Right walking 3 [3]
        self.right_small_normal_frames.append(self.get_image(144, 32, 16, 16))  # Right jump [4]
        self.right_small_normal_frames.append(self.get_image(130, 32, 14, 16))  # Right skid [5]
        self.right_small_normal_frames.append(self.get_image(160, 32, 15, 16))  # Death frame [6]
        self.right_small_normal_frames.append(self.get_image(320, 8, 16, 24))  # Transition small to big [7]
        self.right_small_normal_frames.append(self.get_image(241, 33, 16, 16))  # Transition big to small [8]
        self.right_small_normal_frames.append(self.get_image(194, 32, 12, 16))  # Frame 1 of flag pole Slide [9]
        self.right_small_normal_frames.append(self.get_image(210, 33, 12, 16))  # Frame 2 of flag pole slide [10]

        # Images for small green mario (for invincible animation)#

        self.right_small_green_frames.append(self.get_image(178, 224, 12, 16))  # Right standing [0]
        self.right_small_green_frames.append(self.get_image(80, 224, 15, 16))  # Right walking 1 [1]
        self.right_small_green_frames.append(self.get_image(96, 224, 16, 16))  # Right walking 2 [2]
        self.right_small_green_frames.append(self.get_image(112, 224, 15, 16))  # Right walking 3 [3]
        self.right_small_green_frames.append(self.get_image(144, 224, 16, 16))  # Right jump [4]
        self.right_small_green_frames.append(self.get_image(130, 224, 14, 16))  # Right skid [5]

        # Images for red mario (for invincible animation)#

        self.right_small_red_frames.append(self.get_image(178, 272, 12, 16))  # Right standing [0]
        self.right_small_red_frames.append(self.get_image(80, 272, 15, 16))  # Right walking 1 [1]
        self.right_small_red_frames.append(self.get_image(96, 272, 16, 16))  # Right walking 2 [2]
        self.right_small_red_frames.append(self.get_image(112, 272, 15, 16))  # Right walking 3 [3]
        self.right_small_red_frames.append(self.get_image(144, 272, 16, 16))  # Right jump [4]
        self.right_small_red_frames.append(self.get_image(130, 272, 14, 16))  # Right skid [5]

        # Images for black mario (for invincible animation)#

        self.right_small_black_frames.append(self.get_image(178, 176, 12, 16))  # Right standing [0]
        self.right_small_black_frames.append(self.get_image(80, 176, 15, 16))  # Right walking 1 [1]
        self.right_small_black_frames.append(self.get_image(96, 176, 16, 16))  # Right walking 2 [2]
        self.right_small_black_frames.append(self.get_image(112, 176, 15, 16))  # Right walking 3 [3]
        self.right_small_black_frames.append(self.get_image(144, 176, 16, 16))  # Right jump [4]
        self.right_small_black_frames.append(self.get_image(130, 176, 14, 16))  # Right skid [5]

        # Images for normal big Mario

        self.right_big_normal_frames.append(self.get_image(176, 0, 16, 32))  # Right standing [0]
        self.right_big_normal_frames.append(self.get_image(81, 0, 16, 32))  # Right walking 1 [1]
        self.right_big_normal_frames.append(self.get_image(97, 0, 15, 32))  # Right walking 2 [2]
        self.right_big_normal_frames.append(self.get_image(113, 0, 15, 32))  # Right walking 3 [3]
        self.right_big_normal_frames.append(self.get_image(144, 0, 16, 32))  # Right jump [4]
        self.right_big_normal_frames.append(self.get_image(128, 0, 16, 32))  # Right skid [5]
        self.right_big_normal_frames.append(self.get_image(336, 0, 16, 32))  # Right throwing [6]
        self.right_big_normal_frames.append(self.get_image(160, 10, 16, 22))  # Right crouching [7]
        self.right_big_normal_frames.append(self.get_image(272, 2, 16, 29))  # Transition big to small [8]
        self.right_big_normal_frames.append(self.get_image(193, 2, 16, 30))  # Frame 1 of flag pole slide [9]
        self.right_big_normal_frames.append(self.get_image(209, 2, 16, 29))  # Frame 2 of flag pole slide [10]

        # Images for green big Mario#

        self.right_big_green_frames.append(self.get_image(176, 192, 16, 32))  # Right standing [0]
        self.right_big_green_frames.append(self.get_image(81, 192, 16, 32))  # Right walking 1 [1]
        self.right_big_green_frames.append(self.get_image(97, 192, 15, 32))  # Right walking 2 [2]
        self.right_big_green_frames.append(self.get_image(113, 192, 15, 32))  # Right walking 3 [3]
        self.right_big_green_frames.append(self.get_image(144, 192, 16, 32))  # Right jump [4]
        self.right_big_green_frames.append(self.get_image(128, 192, 16, 32))  # Right skid [5]
        self.right_big_green_frames.append(self.get_image(336, 192, 16, 32))  # Right throwing [6]
        self.right_big_green_frames.append(self.get_image(160, 202, 16, 22))  # Right Crouching [7]

        # Images for red big Mario#

        self.right_big_red_frames.append(self.get_image(176, 240, 16, 32))  # Right standing [0]
        self.right_big_red_frames.append(self.get_image(81, 240, 16, 32))  # Right walking 1 [1]
        self.right_big_red_frames.append(self.get_image(97, 240, 15, 32))  # Right walking 2 [2]
        self.right_big_red_frames.append(self.get_image(113, 240, 15, 32))  # Right walking 3 [3]
        self.right_big_red_frames.append(self.get_image(144, 240, 16, 32))  # Right jump [4]
        self.right_big_red_frames.append(self.get_image(128, 240, 16, 32))  # Right skid [5]
        self.right_big_red_frames.append(self.get_image(336, 240, 16, 32))  # Right throwing [6]
        self.right_big_red_frames.append(self.get_image(160, 250, 16, 22))  # Right crouching [7]

        # Images for black big Mario#

        self.right_big_black_frames.append(self.get_image(176, 144, 16, 32))  # Right standing [0]
        self.right_big_black_frames.append(self.get_image(81, 144, 16, 32))  # Right walking 1 [1]
        self.right_big_black_frames.append(self.get_image(97, 144, 15, 32))  # Right walking 2 [2]
        self.right_big_black_frames.append(self.get_image(113, 144, 15, 32))  # Right walking 3 [3]
        self.right_big_black_frames.append(self.get_image(144, 144, 16, 32))  # Right jump [4]
        self.right_big_black_frames.append(self.get_image(128, 144, 16, 32))  # Right skid [5]
        self.right_big_black_frames.append(self.get_image(336, 144, 16, 32))  # Right throwing [6]
        self.right_big_black_frames.append(self.get_image(160, 154, 16, 22))  # Right Crouching [7]

        # Images for Fire Mario#

        self.right_fire_frames.append(self.get_image(176, 48, 16, 32))  # Right standing [0]
        self.right_fire_frames.append(self.get_image(81, 48, 16, 32))  # Right walking 1 [1]
        self.right_fire_frames.append(self.get_image(97, 48, 15, 32))  # Right walking 2 [2]
        self.right_fire_frames.append(self.get_image(113, 48, 15, 32))  # Right walking 3 [3]
        self.right_fire_frames.append(self.get_image(144, 48, 16, 32))  # Right jump [4]
        self.right_fire_frames.append(self.get_image(128, 48, 16, 32))  # Right skid [5]
        self.right_fire_frames.append(self.get_image(336, 48, 16, 32))  # Right throwing [6]
        self.right_fire_frames.append(self.get_image(160, 58, 16, 22))  # Right crouching [7]
        self.right_fire_frames.append(self.get_image(0, 0, 0, 0))  # Place holder [8]
        self.right_fire_frames.append(self.get_image(193, 50, 16, 29))  # Frame 1 of flag pole slide [9]
        self.right_fire_frames.append(self.get_image(209, 50, 16, 29))  # Frame 2 of flag pole slide [10]

        # The left image frames are numbered the same as the right
        # frames but are simply reversed.

        for frame in self.right_small_normal_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_normal_frames.append(new_image)

        for frame in self.right_small_green_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_green_frames.append(new_image)

        for frame in self.right_small_red_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_red_frames.append(new_image)

        for frame in self.right_small_black_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_black_frames.append(new_image)

        for frame in self.right_big_normal_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_normal_frames.append(new_image)

        for frame in self.right_big_green_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_green_frames.append(new_image)

        for frame in self.right_big_red_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_red_frames.append(new_image)

        for frame in self.right_big_black_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_black_frames.append(new_image)

        for frame in self.right_fire_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_fire_frames.append(new_image)

        self.normal_small_frames = [self.right_small_normal_frames, self.left_small_normal_frames]

        self.green_small_frames = [self.right_small_green_frames, self.left_small_green_frames]

        self.red_small_frames = [self.right_small_red_frames, self.left_small_red_frames]

        self.black_small_frames = [self.right_small_black_frames, self.left_small_black_frames]

        self.invincible_small_frames_list = [
            self.normal_small_frames,
            self.green_small_frames,
            self.red_small_frames,
            self.black_small_frames,
        ]

        self.normal_big_frames = [self.right_big_normal_frames, self.left_big_normal_frames]

        self.green_big_frames = [self.right_big_green_frames, self.left_big_green_frames]

        self.red_big_frames = [self.right_big_red_frames, self.left_big_red_frames]

        self.black_big_frames = [self.right_big_black_frames, self.left_big_black_frames]

        self.fire_frames = [self.right_fire_frames, self.left_fire_frames]

        self.invincible_big_frames_list = [
            self.normal_big_frames,
            self.green_big_frames,
            self.red_big_frames,
            self.black_big_frames,
        ]

        self.all_images = [
            self.right_big_normal_frames,
            self.right_big_black_frames,
            self.right_big_red_frames,
            self.right_big_green_frames,
            self.right_small_normal_frames,
            self.right_small_green_frames,
            self.right_small_red_frames,
            self.right_small_black_frames,
            self.left_big_normal_frames,
            self.left_big_black_frames,
            self.left_big_red_frames,
            self.left_big_green_frames,
            self.left_small_normal_frames,
            self.left_small_red_frames,
            self.left_small_green_frames,
            self.left_small_black_frames,
        ]

        self.right_frames = self.normal_small_frames[0]
        self.left_frames = self.normal_small_frames[1]

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        return sprite_utils.extract_image(
            self.sprite_sheet, x, y, width, height, c.SIZE_MULTIPLIER, c.BLACK
        )

    def update(self, keys: Tuple[bool, ...], game_info: Dict[str, Any], fire_group: pg.sprite.Group) -> None:
        """Updates Mario's states and animations once per frame"""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state(keys, fire_group)
        self.check_for_special_state()
        self.animation()

    def handle_state(self, keys: Tuple[bool, ...], fire_group: pg.sprite.Group) -> None:
        """Determines Mario's behavior based on his state"""
        if self.state == c.STAND:
            self.standing(keys, fire_group)
        elif self.state == c.WALK:
            self.walking(keys, fire_group)
        elif self.state == c.JUMP:
            self.jumping(keys, fire_group)
        elif self.state == c.FALL:
            self.falling(keys, fire_group)
        elif self.state == c.DEATH_JUMP:
            self.jumping_to_death()
        elif self.state == c.SMALL_TO_BIG:
            self.changing_to_big()
        elif self.state == c.BIG_TO_FIRE:
            self.changing_to_fire()
        elif self.state == c.BIG_TO_SMALL:
            self.changing_to_small()
        elif self.state == c.FLAGPOLE:
            self.flag_pole_sliding()
        elif self.state == c.BOTTOM_OF_POLE:
            self.sitting_at_bottom_of_pole()
        elif self.state == c.WALKING_TO_CASTLE:
            self.walking_to_castle()
        elif self.state == c.END_OF_LEVEL_FALL:
            self.falling_at_end_of_level()

    def standing(self, keys: Tuple[bool, ...], fire_group: pg.sprite.Group) -> None:
        """This function is called if Mario is standing still"""
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0

        if keys[tools.keybinding["action"]]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

        if keys[tools.keybinding["down"]]:
            self.crouching = True

        if keys[tools.keybinding["left"]]:
            self.facing_right = False
            self.get_out_of_crouch()
            self.state = c.WALK
        elif keys[tools.keybinding["right"]]:
            self.facing_right = True
            self.get_out_of_crouch()
            self.state = c.WALK
        elif keys[tools.keybinding["jump"]]:
            if self.allow_jump:
                if self.big:
                    setup.SFX["big_jump"].play()
                else:
                    setup.SFX["small_jump"].play()
                self.state = c.JUMP
                self.y_vel = c.JUMP_VEL
        else:
            self.state = c.STAND

        if not keys[tools.keybinding["down"]]:
            self.get_out_of_crouch()

    def get_out_of_crouch(self) -> None:
        """Get out of crouch"""
        if self.rect is None:
            return
        bottom = self.rect.bottom
        left = self.rect.x
        if self.facing_right:
            self.image = self.right_frames[0]
        else:
            self.image = self.left_frames[0]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left
        self.crouching = False

    def check_to_allow_jump(self, keys: Tuple[bool, ...]) -> None:
        """Check to allow Mario to jump"""
        if not keys[tools.keybinding["jump"]]:
            self.allow_jump = True

    def check_to_allow_fireball(self, keys: Tuple[bool, ...]) -> None:
        """Check to allow the shooting of a fireball"""
        if not keys[tools.keybinding["action"]]:
            self.allow_fireball = True

    def shoot_fireball(self, powerup_group: pg.sprite.Group) -> None:
        """Shoots fireball, allowing no more than two to exist at once"""
        if self.rect is None:
            return
        setup.SFX["fireball"].play()
        self.fireball_count = self.count_number_of_fireballs(powerup_group)

        if (self.current_time - self.last_fireball_time) > 200:
            if self.fireball_count < 2:
                self.allow_fireball = False
                powerup_group.add(powerups.FireBall(int(self.rect.right), int(self.rect.y), self.facing_right))
                self.last_fireball_time = self.current_time

                self.frame_index = 6
                if self.facing_right:
                    self.image = self.right_frames[self.frame_index]
                else:
                    self.image = self.left_frames[self.frame_index]

    def count_number_of_fireballs(self, powerup_group: pg.sprite.Group) -> int:
        """Count number of fireballs that exist in the level"""
        fireball_list = []

        for powerup in powerup_group:
            if powerup.name == c.FIREBALL:
                fireball_list.append(powerup)

        return len(fireball_list)

    def walking(self, keys: Tuple[bool, ...], fire_group: pg.sprite.Group) -> None:
        """This function is called when Mario is in a walking state
        It changes the frame, checks for holding down the run button,
        checks for a jump, then adjusts the state if necessary"""

        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

        if self.frame_index == 0:
            self.frame_index += 1
            self.walking_timer = self.current_time
        else:
            if self.current_time - self.walking_timer > self.calculate_animation_speed():
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 1

                self.walking_timer = self.current_time

        if keys[tools.keybinding["action"]]:
            self.max_x_vel = c.MAX_RUN_SPEED
            self.x_accel = c.RUN_ACCEL
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)
        else:
            self.max_x_vel = c.MAX_WALK_SPEED
            self.x_accel = c.WALK_ACCEL

        if keys[tools.keybinding["jump"]]:
            if self.allow_jump:
                if self.big:
                    setup.SFX["big_jump"].play()
                else:
                    setup.SFX["small_jump"].play()
                self.state = c.JUMP
                if self.x_vel > 4.5 or self.x_vel < -4.5:
                    self.y_vel = c.JUMP_VEL - 0.5
                else:
                    self.y_vel = c.JUMP_VEL

        if keys[tools.keybinding["left"]]:
            self.get_out_of_crouch()
            self.facing_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND
            else:
                self.x_accel = c.WALK_ACCEL

            if self.x_vel > (self.max_x_vel * -1):
                self.x_vel -= self.x_accel
                if self.x_vel > -0.5:
                    self.x_vel = -0.5
            elif self.x_vel < (self.max_x_vel * -1):
                self.x_vel += self.x_accel

        elif keys[tools.keybinding["right"]]:
            self.get_out_of_crouch()
            self.facing_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND
            else:
                self.x_accel = c.WALK_ACCEL

            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel
                if self.x_vel < 0.5:
                    self.x_vel = 0.5
            elif self.x_vel > self.max_x_vel:
                self.x_vel -= self.x_accel

        else:
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND

    def calculate_animation_speed(self) -> int:
        """Used to make walking animation speed be in relation to
        Mario's x-vel"""
        if self.x_vel == 0:
            animation_speed = ANIMATION_NORMAL
        elif self.x_vel > 0:
            animation_speed = int(ANIMATION_NORMAL - (self.x_vel * 13))
        else:
            animation_speed = int(ANIMATION_NORMAL - (self.x_vel * 13 * -1))

        return animation_speed

    def jumping(self, keys: Tuple[bool, ...], fire_group: pg.sprite.Group) -> None:
        """Called when Mario is in a JUMP state."""
        self.allow_jump = False
        self.frame_index = 4
        self.gravity = c.JUMP_GRAVITY
        self.y_vel += self.gravity
        self.check_to_allow_fireball(keys)

        if self.y_vel >= 0 and self.y_vel < self.max_y_vel:
            self.gravity = c.GRAVITY
            self.state = c.FALL

        if keys[tools.keybinding["left"]]:
            if self.x_vel > (self.max_x_vel * -1):
                self.x_vel -= self.x_accel

        elif keys[tools.keybinding["right"]]:
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel

        if not keys[tools.keybinding["jump"]]:
            self.gravity = c.GRAVITY
            self.state = c.FALL

        if keys[tools.keybinding["action"]]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

        # Emit jump event for sound/effects systems
        if self.y_vel < 0:
            from ..event_system import get_event_manager, EventType

            events = get_event_manager()
            events.emit(
                EventType.PLAYER_JUMP,
                {
                    "player": self,
                    "y_vel": self.y_vel,
                },
            )

    def falling(self, keys: Tuple[bool, ...], fire_group: pg.sprite.Group) -> None:
        """Called when Mario is in a FALL state"""
        self.check_to_allow_fireball(keys)
        if self.y_vel < c.MAX_Y_VEL:
            self.y_vel += self.gravity

        if keys[tools.keybinding["left"]]:
            if self.x_vel > (self.max_x_vel * -1):
                self.x_vel -= self.x_accel

        elif keys[tools.keybinding["right"]]:
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel

        if keys[tools.keybinding["action"]]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group)

    def jumping_to_death(self) -> None:
        """Called when Mario is in a DEATH_JUMP state"""
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 500:
            if self.rect is not None:
                self.rect.y += self.y_vel
            self.y_vel += self.gravity

    def start_death_jump(self, game_info: Dict[str, Any]) -> None:
        """Used to put Mario in a DEATH_JUMP state"""
        self.dead = True
        game_info[c.MARIO_DEAD] = True
        self.y_vel = -11
        self.gravity = 0.5
        self.frame_index = 6
        self.image = self.right_frames[self.frame_index]
        self.state = c.DEATH_JUMP
        self.in_transition_state = True

    def changing_to_big(self) -> None:
        """Changes Mario's image attribute based on time while
        transitioning to big"""
        self.in_transition_state = True

        if self.transition_timer == 0:
            self.transition_timer = self.current_time
        elif self.timer_between_these_two_times(135, 200):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(200, 365):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(365, 430):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(430, 495):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(495, 560):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(560, 625):
            self.set_mario_to_big_image()
        elif self.timer_between_these_two_times(625, 690):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(690, 755):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(755, 820):
            self.set_mario_to_big_image()
        elif self.timer_between_these_two_times(820, 885):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(885, 950):
            self.set_mario_to_big_image()
            self.state = c.WALK
            self.in_transition_state = False
            self.transition_timer = 0
            self.become_big()

    def timer_between_these_two_times(self, start_time: int, end_time: int) -> Optional[bool]:
        """Checks if the timer is at the right time for the action. Reduces
        the ugly code."""
        if (self.current_time - self.transition_timer) >= start_time and (
            self.current_time - self.transition_timer
        ) < end_time:
            return True
        return None

    def set_mario_to_middle_image(self) -> None:
        """During a change from small to big, sets mario's image to the
        transition/middle size"""
        if self.facing_right:
            self.image = self.normal_small_frames[0][7]
        else:
            self.image = self.normal_small_frames[1][7]
        if self.rect is not None:
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx

    def set_mario_to_small_image(self) -> None:
        """During a change from small to big, sets mario's image to small"""
        if self.facing_right:
            self.image = self.normal_small_frames[0][0]
        else:
            self.image = self.normal_small_frames[1][0]
        if self.rect is not None:
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx

    def set_mario_to_big_image(self) -> None:
        """During a change from small to big, sets mario's image to big"""
        if self.facing_right:
            self.image = self.normal_big_frames[0][0]
        else:
            self.image = self.normal_big_frames[1][0]
        if self.rect is not None:
            bottom = self.rect.bottom
            centerx = self.rect.centerx
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.rect.centerx = centerx

    def become_big(self) -> None:
        self.big = True
        self.right_frames = self.right_big_normal_frames
        self.left_frames = self.left_big_normal_frames
        if self.rect is None:
            return
        bottom = self.rect.bottom
        left = self.rect.x
        image = self.right_frames[0]
        self.rect = image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left

    def changing_to_fire(self) -> None:
        """Called when Mario is in a BIG_TO_FIRE state (i.e. when
        he obtains a fire flower"""
        self.in_transition_state = True

        if self.facing_right:
            frames = [
                self.right_fire_frames[3],
                self.right_big_green_frames[3],
                self.right_big_red_frames[3],
                self.right_big_black_frames[3],
            ]
        else:
            frames = [
                self.left_fire_frames[3],
                self.left_big_green_frames[3],
                self.left_big_red_frames[3],
                self.left_big_black_frames[3],
            ]

        if self.fire_transition_timer == 0:
            self.fire_transition_timer = self.current_time
        elif (self.current_time - self.fire_transition_timer) > TRANSITION_ANIMATION_SPEED and (
            self.current_time - self.fire_transition_timer
        ) < TRANSITION_ANIMATION_SPEED * 2:
            self.image = frames[0]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 3:
            self.image = frames[1]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 4:
            self.image = frames[2]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 5:
            self.image = frames[3]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 6:
            self.image = frames[0]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 7:
            self.image = frames[1]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 8:
            self.image = frames[2]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 9:
            self.image = frames[3]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 10:
            self.image = frames[0]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 11:
            self.image = frames[1]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 12:
            self.image = frames[2]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 13:
            self.image = frames[3]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 14:
            self.image = frames[0]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 15:
            self.image = frames[1]
        elif (self.current_time - self.fire_transition_timer) < TRANSITION_ANIMATION_SPEED * 16:
            self.image = frames[2]
            self.fire = True
            self.in_transition_state = False
            self.state = c.WALK
            self.transition_timer = 0

    def changing_to_small(self) -> None:
        """Mario's state and animation when he shrinks from big to small
        after colliding with an enemy"""
        self.in_transition_state = True
        self.hurt_invincible = True
        self.state = c.BIG_TO_SMALL

        if self.facing_right:
            frames = [
                self.right_big_normal_frames[4],
                self.right_big_normal_frames[8],
                self.right_small_normal_frames[8],
            ]
        else:
            frames = [self.left_big_normal_frames[4], self.left_big_normal_frames[8], self.left_small_normal_frames[8]]

        if self.transition_timer == 0:
            self.transition_timer = self.current_time
        elif (self.current_time - self.transition_timer) < 265:
            self.image = frames[0]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 330:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 395:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 460:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 525:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 590:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 655:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 720:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 785:
            self.image = frames[2]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 850:
            self.image = frames[1]
            self.hurt_invincible_check()
            self.adjust_rect()
        elif (self.current_time - self.transition_timer) < 915:
            self.image = frames[2]
            self.adjust_rect()
            self.in_transition_state = False
            self.state = c.WALK
            self.big = False
            self.transition_timer = 0
            self.hurt_invisible_timer = 0
            self.become_small()

    def adjust_rect(self) -> None:
        """Makes sure new Rect has the same bottom and left
        location as previous Rect"""
        if self.rect is None or self.image is None:
            return
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = bottom

    def become_small(self) -> None:
        self.big = False
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames
        if self.rect is None:
            return
        bottom = self.rect.bottom
        left = self.rect.x
        image = self.right_frames[0]
        self.rect = image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left

    def flag_pole_sliding(self) -> None:
        """State where Mario is sliding down the flag pole"""
        self.state = c.FLAGPOLE
        self.in_transition_state = True
        self.x_vel = 0
        self.y_vel = 0

        if self.flag_pole_timer == 0:
            self.flag_pole_timer = self.current_time
        elif self.rect is not None and self.rect.bottom < 493:
            if (self.current_time - self.flag_pole_timer) < 65:
                self.image = self.right_frames[9]
            elif (self.current_time - self.flag_pole_timer) < 130:
                self.image = self.right_frames[10]
            elif (self.current_time - self.flag_pole_timer) >= 130:
                self.flag_pole_timer = self.current_time

            if self.rect is not None:
                self.rect.right = self.flag_pole_right
                self.y_vel = 5
                self.rect.y += self.y_vel

            if self.rect is not None and self.rect.bottom >= 488:
                self.flag_pole_timer = self.current_time

        elif self.rect is not None and self.rect.bottom >= 493:
            self.image = self.right_frames[10]

    def sitting_at_bottom_of_pole(self) -> None:
        """State when mario is at the bottom of the flag pole"""
        if self.flag_pole_timer == 0:
            self.flag_pole_timer = self.current_time
            self.image = self.left_frames[10]
        elif (self.current_time - self.flag_pole_timer) < 210:
            self.image = self.left_frames[10]
        else:
            self.in_transition_state = False
            if self.rect is not None and self.rect.bottom < 485:
                self.state = c.END_OF_LEVEL_FALL
            else:
                self.state = c.WALKING_TO_CASTLE

    def set_state_to_bottom_of_pole(self) -> None:
        """Sets Mario to the BOTTOM_OF_POLE state"""
        self.image = self.left_frames[9]
        if self.rect is None:
            return
        right = self.rect.right
        self.rect.x = right
        if self.big:
            self.rect.x -= 10
        self.flag_pole_timer = 0
        self.state = c.BOTTOM_OF_POLE

    def walking_to_castle(self) -> None:
        """State when Mario walks to the castle to end the level"""
        self.max_x_vel = 5
        self.x_accel = c.WALK_ACCEL

        if self.x_vel < self.max_x_vel:
            self.x_vel += self.x_accel

        if self.walking_timer == 0 or (self.current_time - self.walking_timer) > 200:
            self.walking_timer = self.current_time

        elif (self.current_time - self.walking_timer) > self.calculate_animation_speed():
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 1
            self.walking_timer = self.current_time

    def falling_at_end_of_level(self, *args: Any) -> None:
        """State when Mario is falling from the flag pole base"""
        self.y_vel += c.GRAVITY

    def check_for_special_state(self) -> None:
        """Determines if Mario is invincible, Fire Mario or recently hurt"""
        self.check_if_invincible()
        self.check_if_fire()
        self.check_if_hurt_invincible()
        self.check_if_crouching()

    def check_if_invincible(self) -> None:
        if self.invincible:
            if (self.current_time - self.invincible_start_timer) < INVINCIBILITY_DURATION:
                self.losing_invincibility = False
                self.change_frame_list(30)
            elif (self.current_time - self.invincible_start_timer) < INVINCIBILITY_DURATION + 2000:
                self.losing_invincibility = True
                self.change_frame_list(100)
            else:
                self.losing_invincibility = False
                self.invincible = False
        else:
            if self.big:
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames
            else:
                self.right_frames = self.invincible_small_frames_list[0][0]
                self.left_frames = self.invincible_small_frames_list[0][1]

    def change_frame_list(self, frame_switch_speed: int) -> None:
        if (self.current_time - self.invincible_animation_timer) > frame_switch_speed:
            if self.invincible_index < (len(self.invincible_small_frames_list) - 1):
                self.invincible_index += 1
            else:
                self.invincible_index = 0

            if self.big:
                frames = self.invincible_big_frames_list[self.invincible_index]
            else:
                frames = self.invincible_small_frames_list[self.invincible_index]

            self.right_frames = frames[0]
            self.left_frames = frames[1]

            self.invincible_animation_timer = self.current_time

    def check_if_fire(self) -> None:
        if self.fire and not self.invincible:
            self.right_frames = self.fire_frames[0]
            self.left_frames = self.fire_frames[1]

    def check_if_hurt_invincible(self) -> None:
        """Check if Mario is still temporarily invincible after getting hurt"""
        if self.hurt_invincible and self.state != c.BIG_TO_SMALL:
            if self.hurt_invisible_timer2 == 0:
                self.hurt_invisible_timer2 = self.current_time
            elif (self.current_time - self.hurt_invisible_timer2) < 2000:
                self.hurt_invincible_check()
            else:
                self.hurt_invincible = False
                self.hurt_invisible_timer = 0
                self.hurt_invisible_timer2 = 0
                for frames in self.all_images:
                    for image in frames:
                        if image is not None:
                            image.set_alpha(255)

    def hurt_invincible_check(self) -> None:
        """Makes Mario invincible on a fixed interval"""
        if self.hurt_invisible_timer == 0:
            self.hurt_invisible_timer = self.current_time
        elif (self.current_time - self.hurt_invisible_timer) < 35:
            if self.image is not None:
                self.image.set_alpha(0)
        elif (self.current_time - self.hurt_invisible_timer) < 70:
            if self.image is not None:
                self.image.set_alpha(255)
            self.hurt_invisible_timer = self.current_time

    def check_if_crouching(self) -> None:
        """Checks if mario is crouching"""
        if self.crouching and self.big:
            if self.rect is None:
                return
            bottom = self.rect.bottom
            left = self.rect.x
            if self.facing_right:
                self.image = self.right_frames[7]
            else:
                self.image = self.left_frames[7]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            self.rect.x = left

    def animation(self) -> None:
        """Adjusts Mario's image for animation"""
        if (
            self.state == c.DEATH_JUMP
            or self.state == c.SMALL_TO_BIG
            or self.state == c.BIG_TO_FIRE
            or self.state == c.BIG_TO_SMALL
            or self.state == c.FLAGPOLE
            or self.state == c.BOTTOM_OF_POLE
            or self.crouching
        ):
            pass
        elif self.facing_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]
