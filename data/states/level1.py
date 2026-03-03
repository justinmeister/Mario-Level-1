"""Level 1 state for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pygame as pg

from .. import setup, tools
from .. import constants as c
from .. import game_sound
from ..event_system import get_event_manager, EventType
from ..level_music_manager import get_level_music_manager
from ..level_sound_effects import get_level_sound_effects
from ..render_system import RenderLayer, RenderManager
from ..quadtree import CollisionDetector
from ..components import mario
from ..components import collider
from ..components import bricks
from ..components import coin_box as coin_box_module
from ..components import enemies
from ..components import checkpoint
from ..components import flagpole
from ..components import info
from ..components import score
from ..components import castle_flag


class Level1(tools._State):
    def __init__(self) -> None:
        tools._State.__init__(self)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called when the State object is created"""
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.game_info[c.LEVEL_STATE] = c.NOT_FROZEN
        self.game_info[c.MARIO_DEAD] = False

        self.state = c.NOT_FROZEN
        self.death_timer: float = 0
        self.flag_timer: float = 0
        self.flag_score: Optional[Any] = None
        self.flag_score_total = 0

        self.moving_score_list: List[score.Score] = []
        self.overhead_info_display = info.OverheadInfo(self.game_info, c.LEVEL)
        self.sound_manager = game_sound.Sound(self.overhead_info_display)

        # Initialize music and sound effects
        self.music_manager = get_level_music_manager()
        self.sound_effects = get_level_sound_effects()
        self.time_warning_played = False

        self.background: Optional[pg.Surface] = None
        self.back_rect: Optional[pg.Rect] = None
        self.level: Optional[pg.Surface] = None
        self.level_rect: Optional[pg.Rect] = None
        self.viewport: Optional[pg.Rect] = None
        self.ground_group: Optional[pg.sprite.Group] = None
        self.pipe_group: Optional[pg.sprite.Group] = None
        self.step_group: Optional[pg.sprite.Group] = None
        self.brick_group: Optional[pg.sprite.Group] = None
        self.coin_box_group: Optional[pg.sprite.Group] = None
        self.flag_pole_group: Optional[pg.sprite.Group] = None
        # enemy_group will be initialized in setup_enemies()
        self.enemy_group: Optional[pg.sprite.Group] = None
        self.mario: Optional[mario.Mario] = None
        self.checkpoint_group: Optional[pg.sprite.Group] = None
        self.flag: Optional[flagpole.Flag] = None
        self.pole: Optional[flagpole.Pole] = None
        self.finial: Optional[flagpole.Finial] = None
        self.coin_group: Optional[pg.sprite.Group] = None
        self.powerup_group: Optional[pg.sprite.Group] = None
        self.brick_pieces_group: Optional[pg.sprite.Group] = None
        self.fire_group: Optional[pg.sprite.Group] = None
        # These will be initialized in setup_spritegroups()
        self.sprites_about_to_die_group: Optional[pg.sprite.Group] = None
        self.shell_group: Optional[pg.sprite.Group] = None
        self.enemy_group_list: Optional[List[pg.sprite.Group]] = None

        self.setup_background()
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.setup_bricks()
        self.setup_coin_boxes()
        self.setup_flag_pole()
        self.setup_enemies()
        self.setup_mario()
        self.setup_checkpoints()
        self.setup_spritegroups()

        # Initialize sprite renderer for optimized rendering
        if setup.SCREEN is None:
            raise RuntimeError("Screen not initialized")
        self.render_manager = RenderManager(setup.SCREEN)
        if self.viewport is None:
            raise RuntimeError("Viewport not initialized")
        self.render_manager.renderer.set_viewport(self.viewport)

        # Initialize collision detector with QuadTree
        # World size matches level dimensions
        world_width = int(self.level_rect.width) if self.level_rect else 10000
        world_height = int(self.level_rect.height) if self.level_rect else 1000
        self.collision_detector = CollisionDetector(world_width, world_height, capacity=8)

        # Start level music
        self.music_manager.play_level_music("level1", fade_ms=1000)

    def setup_background(self) -> None:
        """Sets the background image, rect and scales it to the correct
        proportions"""
        self.background = setup.GFX["level_1"]
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(
            self.background,
            (int(self.back_rect.width * c.BACKGROUND_MULTIPLIER), int(self.back_rect.height * c.BACKGROUND_MULTIPLIER)),
        )
        self.back_rect = self.background.get_rect()
        width = self.back_rect.width
        height = self.back_rect.height

        # use an alpha-capable surface so tests don't need a display
        self.level = pg.Surface((width, height), pg.SRCALPHA)
        self.level_rect = self.level.get_rect()
        if setup.SCREEN is not None:
            self.viewport = setup.SCREEN.get_rect(bottom=self.level_rect.bottom)
        else:
            self.viewport = pg.Rect(0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT)
            self.viewport.bottom = self.level_rect.bottom
        self.viewport.x = self.game_info[c.CAMERA_START_X]

    def setup_ground(self) -> None:
        """Creates collideable, invisible rectangles over top of the ground for
        sprites to walk on"""
        ground_rect1 = collider.Collider(0, c.GROUND_HEIGHT, 2953, 60)
        ground_rect2 = collider.Collider(3048, c.GROUND_HEIGHT, 635, 60)
        ground_rect3 = collider.Collider(3819, c.GROUND_HEIGHT, 2735, 60)
        ground_rect4 = collider.Collider(6647, c.GROUND_HEIGHT, 2300, 60)

        self.ground_group = pg.sprite.Group(ground_rect1, ground_rect2, ground_rect3, ground_rect4)

    def setup_pipes(self) -> None:
        """Create collideable rects for all the pipes"""

        pipe1 = collider.Collider(1202, 452, 83, 82)
        pipe2 = collider.Collider(1631, 409, 83, 140)
        pipe3 = collider.Collider(1973, 366, 83, 170)
        pipe4 = collider.Collider(2445, 366, 83, 170)
        pipe5 = collider.Collider(6989, 452, 83, 82)
        pipe6 = collider.Collider(7675, 452, 83, 82)

        self.pipe_group = pg.sprite.Group(pipe1, pipe2, pipe3, pipe4, pipe5, pipe6)

    def setup_steps(self) -> None:
        """Create collideable rects for all the steps"""
        step1 = collider.Collider(5745, 495, 40, 44)
        step2 = collider.Collider(5788, 452, 40, 44)
        step3 = collider.Collider(5831, 409, 40, 44)
        step4 = collider.Collider(5874, 366, 40, 176)

        step5 = collider.Collider(6001, 366, 40, 176)
        step6 = collider.Collider(6044, 408, 40, 40)
        step7 = collider.Collider(6087, 452, 40, 40)
        step8 = collider.Collider(6130, 495, 40, 40)

        step9 = collider.Collider(6345, 495, 40, 40)
        step10 = collider.Collider(6388, 452, 40, 40)
        step11 = collider.Collider(6431, 409, 40, 40)
        step12 = collider.Collider(6474, 366, 40, 40)
        step13 = collider.Collider(6517, 366, 40, 176)

        step14 = collider.Collider(6644, 366, 40, 176)
        step15 = collider.Collider(6687, 408, 40, 40)
        step16 = collider.Collider(6728, 452, 40, 40)
        step17 = collider.Collider(6771, 495, 40, 40)

        step18 = collider.Collider(7760, 495, 40, 40)
        step19 = collider.Collider(7803, 452, 40, 40)
        step20 = collider.Collider(7845, 409, 40, 40)
        step21 = collider.Collider(7888, 366, 40, 40)
        step22 = collider.Collider(7931, 323, 40, 40)
        step23 = collider.Collider(7974, 280, 40, 40)
        step24 = collider.Collider(8017, 237, 40, 40)
        step25 = collider.Collider(8060, 194, 40, 40)
        step26 = collider.Collider(8103, 194, 40, 360)

        step27 = collider.Collider(8488, 495, 40, 40)

        self.step_group = pg.sprite.Group(
            step1,
            step2,
            step3,
            step4,
            step5,
            step6,
            step7,
            step8,
            step9,
            step10,
            step11,
            step12,
            step13,
            step14,
            step15,
            step16,
            step17,
            step18,
            step19,
            step20,
            step21,
            step22,
            step23,
            step24,
            step25,
            step26,
            step27,
        )

    def setup_bricks(self) -> None:
        """Creates all the breakable bricks for the level.  Coin and
        powerup groups are created so they can be passed to bricks."""
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.brick_pieces_group = pg.sprite.Group()

        brick1 = bricks.Brick(858, 365)
        brick2 = bricks.Brick(944, 365)
        brick3 = bricks.Brick(1030, 365)
        brick4 = bricks.Brick(3299, 365)
        brick5 = bricks.Brick(3385, 365)
        brick6 = bricks.Brick(3430, 193)
        brick7 = bricks.Brick(3473, 193)
        brick8 = bricks.Brick(3516, 193)
        brick9 = bricks.Brick(3559, 193)
        brick10 = bricks.Brick(3602, 193)
        brick11 = bricks.Brick(3645, 193)
        brick12 = bricks.Brick(3688, 193)
        brick13 = bricks.Brick(3731, 193)
        brick14 = bricks.Brick(3901, 193)
        brick15 = bricks.Brick(3944, 193)
        brick16 = bricks.Brick(3987, 193)
        brick17 = bricks.Brick(4030, 365, c.SIXCOINS, self.coin_group)
        brick18 = bricks.Brick(4287, 365)
        brick19 = bricks.Brick(4330, 365, c.STAR, self.powerup_group)
        brick20 = bricks.Brick(5058, 365)
        brick21 = bricks.Brick(5187, 193)
        brick22 = bricks.Brick(5230, 193)
        brick23 = bricks.Brick(5273, 193)
        brick24 = bricks.Brick(5488, 193)
        brick25 = bricks.Brick(5574, 193)
        brick26 = bricks.Brick(5617, 193)
        brick27 = bricks.Brick(5531, 365)
        brick28 = bricks.Brick(5574, 365)
        brick29 = bricks.Brick(7202, 365)
        brick30 = bricks.Brick(7245, 365)
        brick31 = bricks.Brick(7331, 365)

        self.brick_group = pg.sprite.Group(
            brick1,
            brick2,
            brick3,
            brick4,
            brick5,
            brick6,
            brick7,
            brick8,
            brick9,
            brick10,
            brick11,
            brick12,
            brick13,
            brick14,
            brick15,
            brick16,
            brick17,
            brick18,
            brick19,
            brick20,
            brick21,
            brick22,
            brick23,
            brick24,
            brick25,
            brick26,
            brick27,
            brick28,
            brick29,
            brick30,
            brick31,
        )

    def setup_coin_boxes(self) -> None:
        """Creates all the coin boxes and puts them in a sprite group"""
        coin_box1 = coin_box_module.CoinBox(685, 365, c.COIN, self.coin_group)
        coin_box2 = coin_box_module.CoinBox(901, 365, c.MUSHROOM, self.powerup_group)
        coin_box3 = coin_box_module.CoinBox(987, 365, c.COIN, self.coin_group)
        coin_box4 = coin_box_module.CoinBox(943, 193, c.COIN, self.coin_group)
        coin_box5 = coin_box_module.CoinBox(3342, 365, c.MUSHROOM, self.powerup_group)
        coin_box6 = coin_box_module.CoinBox(4030, 193, c.COIN, self.coin_group)
        coin_box7 = coin_box_module.CoinBox(4544, 365, c.COIN, self.coin_group)
        coin_box8 = coin_box_module.CoinBox(4672, 365, c.COIN, self.coin_group)
        coin_box9 = coin_box_module.CoinBox(4672, 193, c.MUSHROOM, self.powerup_group)
        coin_box10 = coin_box_module.CoinBox(4800, 365, c.COIN, self.coin_group)
        coin_box11 = coin_box_module.CoinBox(5531, 193, c.COIN, self.coin_group)
        coin_box12 = coin_box_module.CoinBox(7288, 365, c.COIN, self.coin_group)

        self.coin_box_group = pg.sprite.Group(
            coin_box1,
            coin_box2,
            coin_box3,
            coin_box4,
            coin_box5,
            coin_box6,
            coin_box7,
            coin_box8,
            coin_box9,
            coin_box10,
            coin_box11,
            coin_box12,
        )

    def setup_flag_pole(self) -> None:
        """Creates the flag pole at the end of the level"""
        self.flag = flagpole.Flag(8505, 100)

        pole0 = flagpole.Pole(8505, 97)
        pole1 = flagpole.Pole(8505, 137)
        pole2 = flagpole.Pole(8505, 177)
        pole3 = flagpole.Pole(8505, 217)
        pole4 = flagpole.Pole(8505, 257)
        pole5 = flagpole.Pole(8505, 297)
        pole6 = flagpole.Pole(8505, 337)
        pole7 = flagpole.Pole(8505, 377)
        pole8 = flagpole.Pole(8505, 417)
        pole9 = flagpole.Pole(8505, 450)

        finial = flagpole.Finial(8507, 97)

        self.flag_pole_group = pg.sprite.Group(
            self.flag, finial, pole0, pole1, pole2, pole3, pole4, pole5, pole6, pole7, pole8, pole9
        )

    def setup_enemies(self) -> None:
        """Creates all the enemies and stores them in a list of lists."""
        goomba0 = enemies.Goomba()
        goomba1 = enemies.Goomba()
        goomba2 = enemies.Goomba()
        goomba3 = enemies.Goomba()
        goomba4 = enemies.Goomba(193)
        goomba5 = enemies.Goomba(193)
        goomba6 = enemies.Goomba()
        goomba7 = enemies.Goomba()
        goomba8 = enemies.Goomba()
        goomba9 = enemies.Goomba()
        goomba10 = enemies.Goomba()
        goomba11 = enemies.Goomba()
        goomba12 = enemies.Goomba()
        goomba13 = enemies.Goomba()
        goomba14 = enemies.Goomba()
        goomba15 = enemies.Goomba()

        koopa0 = enemies.Koopa()

        enemy_group1 = pg.sprite.Group(goomba0)
        enemy_group2 = pg.sprite.Group(goomba1)
        enemy_group3 = pg.sprite.Group(goomba2, goomba3)
        enemy_group4 = pg.sprite.Group(goomba4, goomba5)
        enemy_group5 = pg.sprite.Group(goomba6, goomba7)
        enemy_group6 = pg.sprite.Group(koopa0)
        enemy_group7 = pg.sprite.Group(goomba8, goomba9)
        enemy_group8 = pg.sprite.Group(goomba10, goomba11)
        enemy_group9 = pg.sprite.Group(goomba12, goomba13)
        enemy_group10 = pg.sprite.Group(goomba14, goomba15)

        self.enemy_group_list = [
            enemy_group1,
            enemy_group2,
            enemy_group3,
            enemy_group4,
            enemy_group5,
            enemy_group6,
            enemy_group7,
            enemy_group8,
            enemy_group9,
            enemy_group10,
        ]

    def setup_mario(self) -> None:
        """Places Mario at the beginning of the level"""
        self.mario = mario.Mario()
        if self.viewport is not None and self.mario.rect is not None:
            self.mario.rect.x = self.viewport.x + 110
            self.mario.rect.bottom = c.GROUND_HEIGHT

    def setup_checkpoints(self) -> None:
        """Creates invisible checkpoints that when collided will trigger
        the creation of enemies from the self.enemy_group_list"""
        check1 = checkpoint.Checkpoint(510, "1")
        check2 = checkpoint.Checkpoint(1400, "2")
        check3 = checkpoint.Checkpoint(1740, "3")
        check4 = checkpoint.Checkpoint(3080, "4")
        check5 = checkpoint.Checkpoint(3750, "5")
        check6 = checkpoint.Checkpoint(4150, "6")
        check7 = checkpoint.Checkpoint(4470, "7")
        check8 = checkpoint.Checkpoint(4950, "8")
        check9 = checkpoint.Checkpoint(5100, "9")
        check10 = checkpoint.Checkpoint(6800, "10")
        check11 = checkpoint.Checkpoint(8504, "11", 5, 6)
        check12 = checkpoint.Checkpoint(8775, "12")
        check13 = checkpoint.Checkpoint(2740, "secret_mushroom", 360, 40, 12)

        self.check_point_group = pg.sprite.Group(
            check1, check2, check3, check4, check5, check6, check7, check8, check9, check10, check11, check12, check13
        )

    def setup_spritegroups(self) -> None:
        """Sprite groups created for convenience"""
        self.sprites_about_to_die_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()
        # enemy_group is already defined in __init__, just initialize it here
        if self.enemy_group is None:
            self.enemy_group = pg.sprite.Group()

        self.ground_step_pipe_group: pg.sprite.Group = pg.sprite.Group()
        if self.ground_group is not None:
            for sprite in self.ground_group:
                self.ground_step_pipe_group.add(sprite)
        if self.pipe_group is not None:
            for sprite in self.pipe_group:
                self.ground_step_pipe_group.add(sprite)
        if self.step_group is not None:
            for sprite in self.step_group:
                self.ground_step_pipe_group.add(sprite)

        self.mario_and_enemy_group: pg.sprite.Group = pg.sprite.Group()
        if self.enemy_group is not None:
            for sprite in self.enemy_group:
                self.mario_and_enemy_group.add(sprite)
        if self.mario is not None:
            self.mario_and_enemy_group.add(self.mario)

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Updates Entire level using states.  Called by the control object"""
        self.game_info[c.CURRENT_TIME] = self.current_time = current_time

        # Update music based on time remaining
        time_remaining = self.game_info.get(str(c.LEVEL_TIME), 400)
        self.music_manager.update(time_remaining)

        # Play time warning sound
        if time_remaining == 100 and not self.time_warning_played:
            self.sound_effects.play_time_warning()
            self.time_warning_played = True

        self.handle_states(keys)
        self.check_if_time_out()
        self.blit_everything(surface)
        self.sound_manager.update(self.game_info, self.mario)

    def handle_states(self, keys: Tuple[bool, ...]) -> None:
        """If the level is in a FROZEN state, only mario will update"""
        if self.state == c.FROZEN:
            self.update_during_transition_state(keys)
        elif self.state == c.NOT_FROZEN:
            self.update_all_sprites(keys)
        elif self.state == c.IN_CASTLE:
            self.update_while_in_castle()
        elif self.state == c.FLAG_AND_FIREWORKS:
            self.update_flag_and_fireworks()

    def update_during_transition_state(self, keys):
        """Updates mario in a transition state (like becoming big, small,
        or dies). Checks if he leaves the transition state or dies to
        change the level state back"""
        if self.mario is not None and self.powerup_group is not None:
            self.mario.update(keys, self.game_info, self.powerup_group)
        for moving_score in self.moving_score_list:
            moving_score.update(self.moving_score_list, self.game_info)
        if self.flag_score:
            self.flag_score.update(None, self.game_info)
            self.check_to_add_flag_score()
        if self.coin_box_group is not None:
            self.coin_box_group.update(self.game_info)
        if self.flag_pole_group is not None:
            self.flag_pole_group.update(self.game_info)
        self.check_if_mario_in_transition_state()
        self.check_flag()
        self.check_for_mario_death()
        self.overhead_info_display.update(self.game_info, self.mario)

    def check_if_mario_in_transition_state(self):
        """If mario is in a transition state, the level will be in a FREEZE
        state"""
        if self.mario is None:
            return
        if self.mario.in_transition_state:
            self.game_info[c.LEVEL_STATE] = self.state = c.FROZEN
        elif not self.mario.in_transition_state:
            if self.state == c.FROZEN:
                self.game_info[c.LEVEL_STATE] = self.state = c.NOT_FROZEN

    def update_all_sprites(self, keys):
        """Updates the location of all sprites on the screen with LOD optimization."""
        if self.mario is not None and self.powerup_group is not None:
            self.mario.update(keys, self.game_info, self.powerup_group)
        for moving_score in self.moving_score_list:
            moving_score.update(self.moving_score_list, self.game_info)
        if self.flag_score:
            self.flag_score.update(None, self.game_info)
            self.check_to_add_flag_score()
        if self.flag_pole_group is not None:
            self.flag_pole_group.update()
        self.check_points_check()

        # LOD: Only update visible enemies
        if self.enemy_group is not None:
            self._update_enemies_with_lod()
        if self.sprites_about_to_die_group is not None:
            self.sprites_about_to_die_group.update(self.game_info, self.viewport)
        # LOD: Only update visible shells
        if self.shell_group is not None:
            self._update_shells_with_lod()
        if self.brick_group is not None:
            self.brick_group.update()
        if self.coin_box_group is not None:
            self.coin_box_group.update(self.game_info)
        if self.powerup_group is not None:
            self.powerup_group.update(self.game_info, self.viewport)
        if self.coin_group is not None:
            self.coin_group.update(self.game_info, self.viewport)
        if self.brick_pieces_group is not None:
            self.brick_pieces_group.update()
        self.adjust_sprite_positions()
        self.check_if_mario_in_transition_state()
        self.check_for_mario_death()
        self.update_viewport()
        self.overhead_info_display.update(self.game_info, self.mario)

    def _is_sprite_visible(self, sprite, margin: int = 100) -> bool:
        """
        Check if sprite is within viewport + margin.

        Args:
            sprite: Sprite to check
            margin: Extra margin around viewport

        Returns:
            True if sprite should be updated
        """
        if self.viewport is None or not hasattr(sprite, "rect"):
            return True

        expanded_viewport = self.viewport.inflate(margin * 2, margin * 2)
        return sprite.rect.colliderect(expanded_viewport)

    def _update_enemies_with_lod(self) -> None:
        """Update enemies with LOD - only visible ones get full update."""
        if self.enemy_group is None or self.viewport is None:
            return

        for enemy in self.enemy_group.sprites():
            if self._is_sprite_visible(enemy, margin=150):
                # Full update for visible enemies
                enemy.update(self.game_info)
            else:
                # Minimal update for off-screen enemies (just track position)
                if hasattr(enemy, "state") and enemy.state in ["walk", "jump"]:
                    # Keep moving but skip expensive calculations
                    enemy.rect.x += getattr(enemy, "x_vel", 0)
                    enemy.rect.y += getattr(enemy, "y_vel", 0)

    def _update_shells_with_lod(self) -> None:
        """Update shells with LOD - only visible ones get full update."""
        if self.shell_group is None or self.viewport is None:
            return

        for shell in self.shell_group.sprites():
            if self._is_sprite_visible(shell, margin=200):
                shell.update(self.game_info)
            else:
                # Keep sliding shells moving even off-screen
                if hasattr(shell, "state") and shell.state == "shell_slide":
                    shell.rect.x += getattr(shell, "x_vel", 0)

    def check_points_check(self):
        """Detect if checkpoint collision occurs, delete checkpoint,
        add enemies to self.enemy_group"""
        if self.mario is None or self.check_point_group is None:
            return

        checkpoint = pg.sprite.spritecollideany(self.mario, self.check_point_group)
        if checkpoint:
            checkpoint.kill()

            if self.enemy_group_list is not None:
                for i in range(1, 11):
                    if checkpoint.name == str(i):
                        for index, enemy in enumerate(self.enemy_group_list[i - 1]):
                            if self.viewport is not None:
                                enemy.rect.x = self.viewport.right + (index * 60)
                            if self.enemy_group is not None:
                                self.enemy_group.add(enemy)
                        if self.mario_and_enemy_group is not None:
                            for enemy in self.enemy_group_list[i - 1]:
                                self.mario_and_enemy_group.add(enemy)

            if checkpoint.name == "11":
                if self.mario is not None:
                    self.mario.state = c.FLAGPOLE
                    self.mario.invincible = False
                    if checkpoint.rect is not None:
                        self.mario.flag_pole_right = int(checkpoint.rect.right)
                    if self.mario.rect is not None and self.flag is not None and self.flag.rect is not None:
                        if self.mario.rect.bottom < self.flag.rect.y:
                            self.mario.rect.bottom = self.flag.rect.y
                if self.flag is not None:
                    self.flag.state = c.SLIDE_DOWN
                self.create_flag_points()

            elif checkpoint.name == "12":
                self.state = c.IN_CASTLE
                if self.mario is not None:
                    self.mario.state = c.STAND
                    self.mario.in_castle = True
                    self.mario.x_vel = 0
                self.overhead_info_display.state = c.FAST_COUNT_DOWN

            elif checkpoint.name == "secret_mushroom" and self.mario.y_vel < 0:
                if checkpoint.rect is not None and self.powerup_group is not None:
                    mushroom_box = coin_box_module.CoinBox(
                        int(checkpoint.rect.x), int(checkpoint.rect.bottom - 40), "1up_mushroom", self.powerup_group
                    )
                    temp_score_group: pg.sprite.Group = pg.sprite.Group()
                    mushroom_box.start_bump(temp_score_group)
                    for s in temp_score_group:
                        self.moving_score_list.append(s)
                    if self.coin_box_group is not None:
                        self.coin_box_group.add(mushroom_box)

                    if self.mario.rect is not None:
                        self.mario.y_vel = 7
                        self.mario.rect.y = mushroom_box.rect.bottom
                    self.mario.state = c.FALL

            if self.mario_and_enemy_group is not None and self.enemy_group is not None:
                for sprite in self.enemy_group:
                    self.mario_and_enemy_group.add(sprite)

    def create_flag_points(self):
        """Creates the points that appear when Mario touches the
        flag pole"""
        x = 8518
        y = c.GROUND_HEIGHT - 60

        if self.mario is None or self.mario.rect is None:
            return

        mario_bottom = self.mario.rect.bottom

        if mario_bottom > (c.GROUND_HEIGHT - 40 - 40):
            self.flag_score = score.Score(x, y, 100, True)
            self.flag_score_total = 100
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 160):
            self.flag_score = score.Score(x, y, 400, True)
            self.flag_score_total = 400
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 240):
            self.flag_score = score.Score(x, y, 800, True)
            self.flag_score_total = 800
        elif mario_bottom > (c.GROUND_HEIGHT - 40 - 360):
            self.flag_score = score.Score(x, y, 2000, True)
            self.flag_score_total = 2000
        else:
            self.flag_score = score.Score(x, y, 5000, True)
            self.flag_score_total = 5000

    def adjust_sprite_positions(self):
        """Adjusts sprites by their x and y velocities and collisions"""
        # Rebuild QuadTree for optimized collision detection
        self._rebuild_collision_tree()

        self.adjust_mario_position()
        self.adjust_enemy_position()
        self.adjust_shell_position()
        self.adjust_powerup_position()

    def _rebuild_collision_tree(self) -> None:
        """Rebuild QuadTree with current sprite positions."""
        all_colliders = []

        # Add static colliders
        if self.ground_group:
            all_colliders.extend(self.ground_group.sprites())
        if self.pipe_group:
            all_colliders.extend(self.pipe_group.sprites())
        if self.step_group:
            all_colliders.extend(self.step_group.sprites())

        # Add interactive colliders
        if self.brick_group:
            all_colliders.extend(self.brick_group.sprites())
        if self.coin_box_group:
            all_colliders.extend(self.coin_box_group.sprites())

        # Add enemies
        if self.enemy_group:
            all_colliders.extend(self.enemy_group.sprites())
        if self.shell_group:
            all_colliders.extend(self.shell_group.sprites())

        # Rebuild QuadTree
        self.collision_detector.rebuild(all_colliders)  # type: ignore[has-type]

    def adjust_mario_position(self):
        """Adjusts Mario's position based on his x, y velocities and
        potential collisions"""
        if self.mario is None or self.mario.rect is None or self.viewport is None:
            return
        self.last_x_position = self.mario.rect.right
        self.mario.rect.x += round(self.mario.x_vel)
        self.check_mario_x_collisions()

        if not self.mario.in_transition_state:
            self.mario.rect.y += round(self.mario.y_vel)
            self.check_mario_y_collisions()

        if self.mario.rect.x < (self.viewport.x + 5):
            self.mario.rect.x = self.viewport.x + 5

    def check_mario_x_collisions(self) -> None:
        """Check for collisions after Mario is moved on the x axis using QuadTree"""
        if self.mario is None:
            return

        # Use QuadTree for optimized collision detection
        collider = self.collision_detector.check_collision(self.mario)  # type: ignore[has-type]

        if collider:
            # Determine collider type and handle accordingly
            if isinstance(collider, (collider.Collider, bricks.Brick, coin_box_module.CoinBox)):
                self.adjust_mario_for_x_collisions(collider)
                return

        # Fallback to sprite group checks for powerups and enemies
        enemy = powerup = None
        if self.enemy_group is not None:
            enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
        if self.powerup_group is not None:
            powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)

        if enemy:
            if self.mario.invincible:
                setup.SFX["kick"].play()
                self.game_info[c.SCORE] += 100
                if self.mario.rect is not None and self.viewport is not None:
                    self.moving_score_list.append(
                        score.Score(int(self.mario.rect.right - self.viewport.x), int(self.mario.rect.y), 100)
                    )
                enemy.kill()
                enemy.start_death_jump(c.RIGHT)
                if self.sprites_about_to_die_group is not None:
                    self.sprites_about_to_die_group.add(enemy)
            elif self.mario.big:
                setup.SFX["pipe"].play()
                self.mario.fire = False
                self.mario.y_vel = -1
                self.mario.state = c.BIG_TO_SMALL
                self.convert_fireflowers_to_mushrooms()
            elif self.mario.hurt_invincible:
                pass
            else:
                self.mario.start_death_jump(self.game_info)
                self.state = c.FROZEN

        elif powerup:
            if powerup.name == c.STAR:
                self.game_info[c.SCORE] += 1000

                if self.mario.rect is not None and self.viewport is not None:
                    self.moving_score_list.append(
                        score.Score(int(self.mario.rect.centerx - self.viewport.x), int(self.mario.rect.y), 1000)
                    )
                self.mario.invincible = True
                self.mario.invincible_start_timer = self.current_time
            elif powerup.name == c.MUSHROOM:
                setup.SFX["powerup"].play()
                self.game_info[c.SCORE] += 1000
                if self.mario.rect is not None and self.viewport is not None:
                    self.moving_score_list.append(
                        score.Score(int(self.mario.rect.centerx - self.viewport.x), int(self.mario.rect.y - 20), 1000)
                    )

                self.mario.y_vel = -1
                self.mario.state = c.SMALL_TO_BIG
                self.mario.in_transition_state = True
                self.convert_mushrooms_to_fireflowers()
            elif powerup.name == c.LIFE_MUSHROOM:
                if powerup.rect is not None and self.viewport is not None:
                    self.moving_score_list.append(
                        score.Score(int(powerup.rect.right - self.viewport.x), int(powerup.rect.y), int(c.ONEUP))
                    )

                self.game_info[c.LIVES] += 1
                setup.SFX["one_up"].play()
            elif powerup.name == c.FIREFLOWER:
                setup.SFX["powerup"].play()
                self.game_info[c.SCORE] += 1000
                if self.mario.rect is not None and self.viewport is not None:
                    self.moving_score_list.append(
                        score.Score(int(self.mario.rect.centerx - self.viewport.x), int(self.mario.rect.y), 1000)
                    )

                if self.mario.big and not self.mario.fire:
                    self.mario.state = c.BIG_TO_FIRE
                    self.mario.in_transition_state = True
                elif not self.mario.big:
                    self.mario.state = c.SMALL_TO_BIG
                    self.mario.in_transition_state = True
                    self.convert_mushrooms_to_fireflowers()

            if powerup.name != c.FIREBALL:
                powerup.kill()

    def convert_mushrooms_to_fireflowers(self):
        """When Mario becomees big, converts all fireflower powerups to
        mushroom powerups"""
        if self.brick_group is not None:
            for brick in self.brick_group:
                if brick.contents == c.MUSHROOM:
                    brick.contents = c.FIREFLOWER
        if self.coin_box_group is not None:
            for box in self.coin_box_group:
                if box.contents == c.MUSHROOM:
                    box.contents = c.FIREFLOWER

    def convert_fireflowers_to_mushrooms(self):
        """When Mario becomes small, converts all mushroom powerups to
        fireflower powerups"""
        if self.brick_group is not None:
            for brick in self.brick_group:
                if brick.contents == c.FIREFLOWER:
                    brick.contents = c.MUSHROOM
        if self.coin_box_group is not None:
            for box in self.coin_box_group:
                if box.contents == c.FIREFLOWER:
                    box.contents = c.MUSHROOM

    def adjust_mario_for_x_collisions(self, collider):
        """Puts Mario flush next to the collider after moving on the x axis"""
        if self.mario is None or self.mario.rect is None:
            return
        if self.mario.rect.x < collider.rect.x:
            self.mario.rect.right = collider.rect.left
        else:
            self.mario.rect.left = collider.rect.right

        self.mario.x_vel = 0

    def adjust_mario_for_x_shell_collisions(self, shell):
        """Deals with Mario if he hits a shell moving on the x axis"""
        if self.mario is None or self.mario.rect is None or self.viewport is None:
            return
        if shell.state == c.JUMPED_ON:
            if self.mario.rect.x < shell.rect.x:
                self.game_info[c.SCORE] += 400
                self.moving_score_list.append(
                    score.Score(int(shell.rect.centerx - self.viewport.x), int(shell.rect.y), 400)
                )
                self.mario.rect.right = shell.rect.left
                shell.direction = c.RIGHT
                shell.x_vel = 5
                shell.rect.x += 5

            else:
                self.mario.rect.left = shell.rect.right
                shell.direction = c.LEFT
                shell.x_vel = -5
                shell.rect.x += -5

            shell.state = c.SHELL_SLIDE

        elif shell.state == c.SHELL_SLIDE:
            if self.mario.big and not self.mario.invincible:
                self.mario.state = c.BIG_TO_SMALL
            elif self.mario.invincible:
                self.game_info[c.SCORE] += 200
                self.moving_score_list.append(
                    score.Score(int(shell.rect.right - self.viewport.x), int(shell.rect.y), 200)
                )
                shell.kill()
                if self.sprites_about_to_die_group is not None:
                    self.sprites_about_to_die_group.add(shell)
                shell.start_death_jump(c.RIGHT)
            else:
                if not self.mario.hurt_invincible and not self.mario.invincible:
                    self.state = c.FROZEN
                    self.mario.start_death_jump(self.game_info)

    def check_mario_y_collisions(self) -> None:
        """Checks for collisions when Mario moves along the y-axis using QuadTree"""
        if self.mario is None:
            return

        # Use QuadTree for optimized collision detection
        collider = self.collision_detector.check_collision(self.mario)  # type: ignore[has-type]

        ground_step_or_pipe = None
        enemy = None
        brick = None
        coin_box = None
        powerup = None

        # Check QuadTree result first
        if collider:
            if isinstance(collider, collider.Collider):
                ground_step_or_pipe = collider
            elif isinstance(collider, bricks.Brick):
                brick = collider
            elif isinstance(collider, coin_box_module.CoinBox):
                coin_box = collider
            elif isinstance(collider, enemies.Enemy):
                enemy = collider

        # Fallback to sprite groups if needed
        if not ground_step_or_pipe and self.ground_step_pipe_group is not None:
            ground_step_or_pipe = pg.sprite.spritecollideany(self.mario, self.ground_step_pipe_group)
        if not brick and self.brick_group is not None:
            brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        if not coin_box and self.coin_box_group is not None:
            coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
        if not enemy and self.enemy_group is not None:
            enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
        if not powerup and self.powerup_group is not None:
            powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)

        brick, coin_box = self.prevent_collision_conflict(brick, coin_box)

        if coin_box:
            self.adjust_mario_for_y_coin_box_collisions(coin_box)

        elif brick:
            self.adjust_mario_for_y_brick_collisions(brick)

        elif ground_step_or_pipe:
            self.adjust_mario_for_y_ground_pipe_collisions(ground_step_or_pipe)

        elif enemy:
            if self.mario.invincible:
                setup.SFX["kick"].play()
                enemy.kill()
                if self.sprites_about_to_die_group is not None:
                    self.sprites_about_to_die_group.add(enemy)
                enemy.start_death_jump(c.RIGHT)
            else:
                self.adjust_mario_for_y_enemy_collisions(enemy)

        elif powerup:
            if powerup.name == c.STAR:
                setup.SFX["powerup"].play()
                powerup.kill()
                self.mario.invincible = True
                self.mario.invincible_start_timer = self.current_time

        self.test_if_mario_is_falling()

    def prevent_collision_conflict(self, obstacle1, obstacle2):
        """Allows collisions only for the item closest to marios centerx"""
        if self.mario is None or self.mario.rect is None:
            return obstacle1, obstacle2
        if obstacle1 and obstacle2:
            obstacle1_distance = self.mario.rect.centerx - obstacle1.rect.centerx
            if obstacle1_distance < 0:
                obstacle1_distance *= -1
            obstacle2_distance = self.mario.rect.centerx - obstacle2.rect.centerx
            if obstacle2_distance < 0:
                obstacle2_distance *= -1

            if obstacle1_distance < obstacle2_distance:
                obstacle2 = False
            else:
                obstacle1 = False

        return obstacle1, obstacle2

    def adjust_mario_for_y_coin_box_collisions(self, coin_box):
        """Mario collisions with coin boxes on the y-axis"""
        if self.mario is None or self.mario.rect is None:
            return
        if self.mario.rect.y > coin_box.rect.y:
            if coin_box.state == c.RESTING:
                if coin_box.contents == c.COIN:
                    self.game_info[c.SCORE] += 200
                    temp_score_group1: pg.sprite.Group = pg.sprite.Group()
                    coin_box.start_bump(temp_score_group1)
                    for s in temp_score_group1:
                        self.moving_score_list.append(s)
                    if coin_box.contents == c.COIN:
                        self.game_info[c.COIN_TOTAL] += 1
                        # Emit coin collect event
                        events = get_event_manager()
                        events.emit(
                            EventType.PLAYER_COIN,
                            {
                                "player": self.mario,
                                "position": (self.mario.rect.x, self.mario.rect.y),
                            },
                        )
                else:
                    temp_score_group2: pg.sprite.Group = pg.sprite.Group()
                    coin_box.start_bump(temp_score_group2)
                    for s in temp_score_group2:
                        self.moving_score_list.append(s)

            elif coin_box.state == c.OPENED:
                pass
            setup.SFX["bump"].play()
            self.mario.y_vel = 7
            self.mario.rect.y = coin_box.rect.bottom
            self.mario.state = c.FALL
        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = coin_box.rect.top
            self.mario.state = c.WALK

    def adjust_mario_for_y_brick_collisions(self, brick):
        """Mario collisions with bricks on the y-axis"""
        if self.mario is None or self.mario.rect is None:
            return
        if self.mario.rect.y > brick.rect.y:
            if brick.state == c.RESTING:
                if self.mario.big and brick.contents is None:
                    setup.SFX["brick_smash"].play()
                    self.check_if_enemy_on_brick(brick)
                    brick.kill()
                    if self.brick_pieces_group is not None:
                        self.brick_pieces_group.add(
                            bricks.BrickPiece(brick.rect.x, brick.rect.y - (brick.rect.height / 2), -2, -12),
                            bricks.BrickPiece(brick.rect.right, brick.rect.y - (brick.rect.height / 2), 2, -12),
                            bricks.BrickPiece(brick.rect.x, brick.rect.y, -2, -6),
                            bricks.BrickPiece(brick.rect.right, brick.rect.y, 2, -6),
                        )
                else:
                    setup.SFX["bump"].play()
                    if brick.coin_total > 0:
                        self.game_info[c.COIN_TOTAL] += 1
                        self.game_info[c.SCORE] += 200
                    self.check_if_enemy_on_brick(brick)
                    temp_score_group: pg.sprite.Group = pg.sprite.Group()
                    brick.start_bump(temp_score_group)
                    for s in temp_score_group:
                        self.moving_score_list.append(s)
            elif brick.state == c.OPENED:
                setup.SFX["bump"].play()
            self.mario.y_vel = 7
            self.mario.rect.y = brick.rect.bottom
            self.mario.state = c.FALL

        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = brick.rect.top
            self.mario.state = c.WALK

    def check_if_enemy_on_brick(self, brick):
        """Kills enemy if on a bumped or broken brick"""
        if self.viewport is None:
            return
        brick.rect.y -= 5

        enemy = pg.sprite.spritecollideany(brick, self.enemy_group) if self.enemy_group is not None else None

        if enemy:
            setup.SFX["kick"].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(int(enemy.rect.centerx - self.viewport.x), int(enemy.rect.y), 100)
            )
            enemy.kill()
            if self.sprites_about_to_die_group is not None:
                self.sprites_about_to_die_group.add(enemy)
            if self.mario and self.mario.rect and self.mario.rect.centerx > brick.rect.centerx:
                enemy.start_death_jump("right")
            else:
                enemy.start_death_jump("left")

        brick.rect.y += 5

    def adjust_mario_for_y_ground_pipe_collisions(self, collider):
        """Mario collisions with pipes on the y-axis"""
        if self.mario is None or self.mario.rect is None:
            return
        if collider.rect.bottom > self.mario.rect.bottom:
            self.mario.y_vel = 0
            self.mario.rect.bottom = collider.rect.top
            if self.mario.state == c.END_OF_LEVEL_FALL:
                self.mario.state = c.WALKING_TO_CASTLE
            else:
                self.mario.state = c.WALK
        elif collider.rect.top < self.mario.rect.top:
            self.mario.y_vel = 7
            self.mario.rect.top = collider.rect.bottom
            self.mario.state = c.FALL

    def test_if_mario_is_falling(self):
        """Changes Mario to a FALL state if more than a pixel above a pipe,
        ground, step or box"""
        if self.mario is None or self.mario.rect is None:
            return
        self.mario.rect.y += 1
        test_collide_group: pg.sprite.Group = pg.sprite.Group()
        if self.ground_step_pipe_group is not None:
            for sprite in self.ground_step_pipe_group:
                test_collide_group.add(sprite)
        if self.brick_group is not None:
            for sprite in self.brick_group:
                test_collide_group.add(sprite)
        if self.coin_box_group is not None:
            for sprite in self.coin_box_group:
                test_collide_group.add(sprite)

        if pg.sprite.spritecollideany(self.mario, test_collide_group) is None:
            if (
                self.mario.state != c.JUMP
                and self.mario.state != c.DEATH_JUMP
                and self.mario.state != c.SMALL_TO_BIG
                and self.mario.state != c.BIG_TO_FIRE
                and self.mario.state != c.BIG_TO_SMALL
                and self.mario.state != c.FLAGPOLE
                and self.mario.state != c.WALKING_TO_CASTLE
                and self.mario.state != c.END_OF_LEVEL_FALL
            ):
                self.mario.state = c.FALL
            elif self.mario.state == c.WALKING_TO_CASTLE or self.mario.state == c.END_OF_LEVEL_FALL:
                self.mario.state = c.END_OF_LEVEL_FALL

        self.mario.rect.y -= 1

    def adjust_mario_for_y_enemy_collisions(self, enemy):
        """Mario collisions with all enemies on the y-axis"""
        if self.mario is None or self.mario.rect is None or self.viewport is None:
            return
        if self.mario.y_vel > 0:
            setup.SFX["stomp"].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(
                score.Score(int(enemy.rect.centerx - self.viewport.x), int(enemy.rect.y), 100)
            )
            enemy.state = c.JUMPED_ON
            enemy.kill()
            if enemy.name == c.GOOMBA:
                enemy.death_timer = self.current_time
                if self.sprites_about_to_die_group is not None:
                    self.sprites_about_to_die_group.add(enemy)
            elif enemy.name == c.KOOPA:
                if self.shell_group is not None:
                    self.shell_group.add(enemy)

            # Safety check for mario
            if self.mario is None:
                return
            self.mario.rect.bottom = enemy.rect.top
            self.mario.state = c.JUMP
            self.mario.y_vel = -7

    def adjust_mario_for_y_shell_collisions(self, shell):
        """Mario collisions with Koopas in their shells on the y axis"""
        if self.mario is None or self.viewport is None:
            return
        if self.mario.y_vel > 0:
            self.game_info[c.SCORE] += 400
            self.moving_score_list.append(
                score.Score(self.mario.rect.centerx - self.viewport.x, self.mario.rect.y, 400)
            )
            if shell.state == c.JUMPED_ON:
                setup.SFX["kick"].play()
                shell.state = c.SHELL_SLIDE
                if self.mario.rect.centerx < shell.rect.centerx:
                    shell.direction = c.RIGHT
                    shell.rect.left = self.mario.rect.right + 5
                else:
                    shell.direction = c.LEFT
                    shell.rect.right = self.mario.rect.left - 5
            else:
                shell.state = c.JUMPED_ON

    def adjust_enemy_position(self) -> None:
        """Moves all enemies along the x, y axes and check for collisions"""
        if self.enemy_group is None:
            return
        for enemy in self.enemy_group:
            enemy.rect.x += enemy.x_vel
            self.check_enemy_x_collisions(enemy)

            enemy.rect.y += enemy.y_vel
            self.check_enemy_y_collisions(enemy)
            self.delete_if_off_screen(enemy)

    def check_enemy_x_collisions(self, enemy: "enemies.Enemy") -> None:
        """Enemy collisions along the x axis.  Removes enemy from enemy group
        in order to check against all other enemies then adds it back."""
        enemy.kill()

        if self.ground_step_pipe_group is not None:
            collider = pg.sprite.spritecollideany(enemy, self.ground_step_pipe_group)
        else:
            collider = None
        if self.enemy_group is not None:
            enemy_collider = pg.sprite.spritecollideany(enemy, self.enemy_group)
        else:
            enemy_collider = None

        if collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = collider.rect.left
                enemy.direction = c.LEFT
                enemy.x_vel = -2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = collider.rect.right
                enemy.direction = c.RIGHT
                enemy.x_vel = 2

        elif enemy_collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = enemy_collider.rect.left
                enemy.direction = c.LEFT
                enemy_collider.direction = c.RIGHT
                enemy.x_vel = -2
                enemy_collider.x_vel = 2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = enemy_collider.rect.right
                enemy.direction = c.RIGHT
                enemy_collider.direction = c.LEFT
                enemy.x_vel = 2
                enemy_collider.x_vel = -2

        if self.enemy_group is not None:
            self.enemy_group.add(enemy)
        if self.mario_and_enemy_group is not None:
            self.mario_and_enemy_group.add(enemy)

    def check_enemy_y_collisions(self, enemy: "enemies.Enemy") -> None:
        """Enemy collisions on the y axis"""
        if self.ground_step_pipe_group is not None:
            collider = pg.sprite.spritecollideany(enemy, self.ground_step_pipe_group)
        else:
            collider = None
        if self.brick_group is not None:
            brick = pg.sprite.spritecollideany(enemy, self.brick_group)
        else:
            brick = None
        if self.coin_box_group is not None:
            coin_box = pg.sprite.spritecollideany(enemy, self.coin_box_group)
        else:
            coin_box = None

        if collider:
            if enemy.rect.bottom > collider.rect.bottom:
                enemy.y_vel = 7
                enemy.rect.top = collider.rect.bottom
                enemy.state = c.FALL
            elif enemy.rect.bottom < collider.rect.bottom:
                enemy.y_vel = 0
                enemy.rect.bottom = collider.rect.top
                enemy.state = c.WALK

        elif brick:
            if brick.state == c.BUMPED:
                enemy.kill()
                if self.sprites_about_to_die_group is not None:
                    self.sprites_about_to_die_group.add(enemy)
                if self.mario is not None and self.mario.rect is not None and brick.rect is not None:
                    if self.mario.rect.centerx > brick.rect.centerx:
                        enemy.start_death_jump("right")
                    else:
                        enemy.start_death_jump("left")

            elif enemy.rect.x > brick.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = brick.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = brick.rect.top
                enemy.state = c.WALK

        elif coin_box:
            if coin_box.state == c.BUMPED:
                self.game_info[c.SCORE] += 100
                if self.viewport is not None and enemy.rect is not None:
                    self.moving_score_list.append(score.Score(enemy.rect.centerx - self.viewport.x, enemy.rect.y, 100))
                enemy.kill()
                if self.sprites_about_to_die_group is not None:
                    self.sprites_about_to_die_group.add(enemy)
                if self.mario is not None and self.mario.rect is not None and coin_box.rect is not None:
                    if self.mario.rect.centerx > coin_box.rect.centerx:
                        enemy.start_death_jump("right")
                    else:
                        enemy.start_death_jump("left")

            elif enemy.rect.x > coin_box.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = coin_box.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = coin_box.rect.top
                enemy.state = c.WALK

        else:
            enemy.rect.y += 1
            test_group = pg.sprite.Group(self.ground_step_pipe_group, self.coin_box_group, self.brick_group)
            if pg.sprite.spritecollideany(enemy, test_group) is None:
                if enemy.state != c.JUMP:
                    enemy.state = c.FALL

            enemy.rect.y -= 1

    def adjust_shell_position(self):
        """Moves any koopa in a shell along the x, y axes and checks for
        collisions"""
        for shell in self.shell_group:
            shell.rect.x += shell.x_vel
            self.check_shell_x_collisions(shell)

            shell.rect.y += shell.y_vel
            self.check_shell_y_collisions(shell)
            self.delete_if_off_screen(shell)

    def check_shell_x_collisions(self, shell):
        """Shell collisions along the x axis"""
        collider = pg.sprite.spritecollideany(shell, self.ground_step_pipe_group)
        enemy = pg.sprite.spritecollideany(shell, self.enemy_group)

        if collider:
            setup.SFX["bump"].play()
            if shell.x_vel > 0:
                shell.direction = c.LEFT
                shell.rect.right = collider.rect.left
            else:
                shell.direction = c.RIGHT
                shell.rect.left = collider.rect.right

        if enemy:
            setup.SFX["kick"].play()
            self.game_info[c.SCORE] += 100
            self.moving_score_list.append(score.Score(enemy.rect.right - self.viewport.x, enemy.rect.y, 100))
            enemy.kill()
            self.sprites_about_to_die_group.add(enemy)
            enemy.start_death_jump(shell.direction)

    def check_shell_y_collisions(self, shell):
        """Shell collisions along the y axis"""
        collider = pg.sprite.spritecollideany(shell, self.ground_step_pipe_group)

        if collider:
            shell.y_vel = 0
            shell.rect.bottom = collider.rect.top
            shell.state = c.SHELL_SLIDE

        else:
            shell.rect.y += 1
            if pg.sprite.spritecollideany(shell, self.ground_step_pipe_group) is None:
                shell.state = c.FALL
            shell.rect.y -= 1

    def adjust_powerup_position(self):
        """Moves mushrooms, stars and fireballs along the x, y axes"""
        for powerup in self.powerup_group:
            if powerup.name == c.MUSHROOM:
                self.adjust_mushroom_position(powerup)
            elif powerup.name == c.STAR:
                self.adjust_star_position(powerup)
            elif powerup.name == c.FIREBALL:
                self.adjust_fireball_position(powerup)
            elif powerup.name == "1up_mushroom":
                self.adjust_mushroom_position(powerup)

    def adjust_mushroom_position(self, mushroom):
        """Moves mushroom along the x, y axes."""
        if mushroom.state != c.REVEAL:
            mushroom.rect.x += mushroom.x_vel
            self.check_mushroom_x_collisions(mushroom)

            mushroom.rect.y += mushroom.y_vel
            self.check_mushroom_y_collisions(mushroom)
            self.delete_if_off_screen(mushroom)

    def check_mushroom_x_collisions(self, mushroom):
        """Mushroom collisions along the x axis"""
        collider = None
        brick = None
        coin_box = None

        if self.ground_step_pipe_group is not None:
            collider = pg.sprite.spritecollideany(mushroom, self.ground_step_pipe_group)
        if self.brick_group is not None:
            brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        if self.coin_box_group is not None:
            coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)

        if collider:
            self.adjust_mushroom_for_collision_x(mushroom, collider)

        elif brick:
            self.adjust_mushroom_for_collision_x(mushroom, brick)

        elif coin_box:
            self.adjust_mushroom_for_collision_x(mushroom, coin_box)

    def check_mushroom_y_collisions(self, mushroom):
        """Mushroom collisions along the y axis"""
        collider = None
        brick = None
        coin_box = None

        if self.ground_step_pipe_group is not None:
            collider = pg.sprite.spritecollideany(mushroom, self.ground_step_pipe_group)
        if self.brick_group is not None:
            brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        if self.coin_box_group is not None:
            coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)

        if collider:
            self.adjust_mushroom_for_collision_y(mushroom, collider)
        elif brick:
            self.adjust_mushroom_for_collision_y(mushroom, brick)
        elif coin_box:
            self.adjust_mushroom_for_collision_y(mushroom, coin_box)
        else:
            if self.ground_step_pipe_group is not None:
                self.check_if_falling(mushroom, self.ground_step_pipe_group)
            if self.brick_group is not None:
                self.check_if_falling(mushroom, self.brick_group)
            if self.coin_box_group is not None:
                self.check_if_falling(mushroom, self.coin_box_group)

    def adjust_mushroom_for_collision_x(self, item, collider):
        """Changes mushroom direction if collision along x axis"""
        if item.rect.x < collider.rect.x:
            item.rect.right = collider.rect.x
            item.direction = c.LEFT
        else:
            item.rect.x = collider.rect.right
            item.direction = c.RIGHT

    def adjust_mushroom_for_collision_y(self, item, collider):
        """Changes mushroom state to SLIDE after hitting ground from fall"""
        item.rect.bottom = collider.rect.y
        item.state = c.SLIDE
        item.y_vel = 0

    def adjust_star_position(self, star):
        """Moves invincible star along x, y axes and checks for collisions"""
        if star.state == c.BOUNCE:
            star.rect.x += star.x_vel
            self.check_mushroom_x_collisions(star)
            star.rect.y += star.y_vel
            self.check_star_y_collisions(star)
            star.y_vel += star.gravity
            self.delete_if_off_screen(star)

    def check_star_y_collisions(self, star):
        """Invincible star collisions along y axis"""
        collider = pg.sprite.spritecollideany(star, self.ground_step_pipe_group)
        brick = pg.sprite.spritecollideany(star, self.brick_group)
        coin_box = pg.sprite.spritecollideany(star, self.coin_box_group)

        if collider:
            self.adjust_star_for_collision_y(star, collider)
        elif brick:
            self.adjust_star_for_collision_y(star, brick)
        elif coin_box:
            self.adjust_star_for_collision_y(star, coin_box)

    def adjust_star_for_collision_y(self, star, collider):
        """Allows for a star bounce off the ground and on the bottom of a
        box"""
        if star.rect.y > collider.rect.y:
            star.rect.y = collider.rect.bottom
            star.y_vel = 0
        else:
            star.rect.bottom = collider.rect.top
            star.start_bounce(-8)

    def adjust_fireball_position(self, fireball):
        """Moves fireball along the x, y axes and checks for collisions"""
        if fireball.state == c.FLYING:
            fireball.rect.x += fireball.x_vel
            self.check_fireball_x_collisions(fireball)
            fireball.rect.y += fireball.y_vel
            self.check_fireball_y_collisions(fireball)
        elif fireball.state == c.BOUNCING:
            fireball.rect.x += fireball.x_vel
            self.check_fireball_x_collisions(fireball)
            fireball.rect.y += fireball.y_vel
            self.check_fireball_y_collisions(fireball)
            fireball.y_vel += fireball.gravity
        self.delete_if_off_screen(fireball)

    def bounce_fireball(self, fireball):
        """Simulates fireball bounce off ground"""
        fireball.y_vel = -8
        if fireball.direction == c.RIGHT:
            fireball.x_vel = 15
        else:
            fireball.x_vel = -15

        if fireball in self.powerup_group:
            fireball.state = c.BOUNCING

    def check_fireball_x_collisions(self, fireball):
        """Fireball collisions along x axis"""
        collide_group = pg.sprite.Group(
            self.ground_group, self.pipe_group, self.step_group, self.coin_box_group, self.brick_group
        )

        collider = pg.sprite.spritecollideany(fireball, collide_group)

        if collider:
            fireball.kill()
            self.sprites_about_to_die_group.add(fireball)
            fireball.explode_transition()

    def check_fireball_y_collisions(self, fireball):
        """Fireball collisions along y axis"""
        collide_group = pg.sprite.Group(
            self.ground_group, self.pipe_group, self.step_group, self.coin_box_group, self.brick_group
        )

        collider = pg.sprite.spritecollideany(fireball, collide_group)
        enemy = pg.sprite.spritecollideany(fireball, self.enemy_group)

        if collider and (fireball in self.powerup_group):
            fireball.rect.bottom = collider.rect.y
            self.bounce_fireball(fireball)

        elif enemy:
            self.fireball_kill(fireball, enemy)

    def fireball_kill(self, fireball, enemy):
        """Kills enemy if hit with fireball"""
        setup.SFX["kick"].play()
        self.game_info[c.SCORE] += 100
        self.moving_score_list.append(score.Score(enemy.rect.centerx - self.viewport.x, enemy.rect.y, 100))
        fireball.kill()
        enemy.kill()
        self.sprites_about_to_die_group.add(enemy, fireball)
        enemy.start_death_jump(fireball.direction)
        fireball.explode_transition()

    def check_if_falling(self, sprite, sprite_group):
        """Checks if sprite should enter a falling state"""
        sprite.rect.y += 1

        if pg.sprite.spritecollideany(sprite, sprite_group) is None:
            if sprite.state != c.JUMP:
                sprite.state = c.FALL

        sprite.rect.y -= 1

    def delete_if_off_screen(self, enemy):
        """Removes enemy from sprite groups if 500 pixels left off the screen,
        underneath the bottom of the screen, or right of the screen if shell"""
        if enemy.rect.x < (self.viewport.x - 300):
            enemy.kill()

        elif enemy.rect.y > (self.viewport.bottom):
            enemy.kill()

        elif enemy.state == c.SHELL_SLIDE:
            if enemy.rect.x > (self.viewport.right + 500):
                enemy.kill()

    def check_flag(self):
        """Adjusts mario's state when the flag is at the bottom"""
        if self.flag.state == c.BOTTOM_OF_POLE and self.mario.state == c.FLAGPOLE:
            self.mario.set_state_to_bottom_of_pole()

    def check_to_add_flag_score(self):
        """Adds flag score if at top"""
        if self.flag_score.y_vel == 0:
            self.game_info[c.SCORE] += self.flag_score_total
            self.flag_score_total = 0

    def check_for_mario_death(self):
        """Restarts the level if Mario is dead"""
        if self.mario.rect.y > c.SCREEN_HEIGHT and not self.mario.in_castle:
            self.mario.dead = True
            self.mario.x_vel = 0
            self.state = c.FROZEN
            self.game_info[c.MARIO_DEAD] = True

        if self.mario.dead:
            self.play_death_song()

    def play_death_song(self):
        if self.death_timer == 0:
            self.death_timer = self.current_time
        elif (self.current_time - self.death_timer) > 3000:
            self.set_game_info_values()
            self.done = True

    def set_game_info_values(self):
        """sets the new game values after a player's death"""
        if self.game_info[c.SCORE] > self.persist[c.TOP_SCORE]:
            self.persist[c.TOP_SCORE] = self.game_info[c.SCORE]
        if self.mario.dead:
            self.persist[c.LIVES] -= 1

        if self.persist[c.LIVES] == 0:
            self.next = c.GAME_OVER
            self.game_info[c.CAMERA_START_X] = 0
        elif not self.mario.dead:
            self.next = c.MAIN_MENU
            self.game_info[c.CAMERA_START_X] = 0
        elif self.overhead_info_display.time == 0:
            self.next = c.TIME_OUT
        else:
            if self.mario.rect.x > 3670 and self.game_info[c.CAMERA_START_X] == 0:
                self.game_info[c.CAMERA_START_X] = 3440
            self.next = c.LOAD_SCREEN

    def check_if_time_out(self):
        """Check if time has run down to 0"""
        if self.overhead_info_display.time <= 0 and not self.mario.dead and not self.mario.in_castle:
            self.state = c.FROZEN
            self.mario.start_death_jump(self.game_info)

    def update_viewport(self) -> None:
        """Changes the view of the camera"""
        if self.viewport is None or self.mario is None or self.mario.rect is None or self.level_rect is None:
            return
        third = self.viewport.x + self.viewport.w // 3
        mario_center = self.mario.rect.centerx
        mario_right = self.mario.rect.right

        if self.mario.x_vel > 0 and mario_center >= third:
            mult = 0.5 if mario_right < self.viewport.centerx else 1
            new = self.viewport.x + mult * self.mario.x_vel
            highest = self.level_rect.w - self.viewport.w
            self.viewport.x = min(highest, new)

        # Update renderer viewport for culling
        self.render_manager.renderer.set_viewport(self.viewport)

    def update_while_in_castle(self):
        """Updates while Mario is in castle at the end of the level"""
        if self.mario is not None and self.mario.state == c.STAND:
            self.mario.state = c.WALKING_TO_CASTLE
        if self.mario is not None:
            self.mario.update(
                {}, self.game_info, self.powerup_group if self.powerup_group is not None else pg.sprite.Group()
            )
            self.mario.rect.x += round(self.mario.x_vel)
            self.check_points_check()
        for moving_score in self.moving_score_list:
            moving_score.update(self.moving_score_list, self.game_info)
        self.overhead_info_display.update(self.game_info, self.mario)

        if self.overhead_info_display.state == c.END_OF_LEVEL:
            self.state = c.FLAG_AND_FIREWORKS
            self.flag_pole_group.add(castle_flag.Flag(8745, 322))

    def update_flag_and_fireworks(self):
        """Updates the level for the fireworks and castle flag"""
        for moving_score in self.moving_score_list:
            moving_score.update(self.moving_score_list, self.game_info)
        self.overhead_info_display.update(self.game_info)
        self.flag_pole_group.update()

        self.end_game()

    def end_game(self):
        """End the game"""
        if self.flag_timer == 0:
            self.flag_timer = self.current_time
        elif (self.current_time - self.flag_timer) > 2000:
            self.set_game_info_values()
            # Set current level for load screen
            self.game_info[c.CURRENT_LEVEL] = c.LEVEL2
            self.sound_manager.stop_music()
            self.done = True

    def blit_everything(self, surface: pg.Surface) -> None:
        """Blit all sprites to the main surface using optimized renderer"""
        renderer = self.render_manager.renderer

        # Clear renderer for this frame
        renderer._sprites.clear()

        # Draw background directly (not a sprite)
        if self.background is not None and self.viewport is not None:
            surface.blit(self.background, self.viewport, self.viewport)

        # Add sprites to renderer by layer for proper z-ordering
        # Ground/pipe layer (background colliders - not rendered, but kept for compatibility)
        # Brick and coin box layer
        if self.brick_group:
            renderer.add_sprite_group(self.brick_group, RenderLayer.BRICKS)
        if self.coin_box_group:
            renderer.add_sprite_group(self.coin_box_group, RenderLayer.BRICKS)

        # Item layer
        if self.powerup_group:
            renderer.add_sprite_group(self.powerup_group, RenderLayer.ITEMS)
        if self.coin_group:
            renderer.add_sprite_group(self.coin_group, RenderLayer.ITEMS)
        if self.brick_pieces_group:
            renderer.add_sprite_group(self.brick_pieces_group, RenderLayer.ITEMS)

        # Enemy layer
        if self.enemy_group:
            renderer.add_sprite_group(self.enemy_group, RenderLayer.ENEMIES)
        if self.shell_group:
            renderer.add_sprite_group(self.shell_group, RenderLayer.ENEMIES)
        if self.sprites_about_to_die_group:
            renderer.add_sprite_group(self.sprites_about_to_die_group, RenderLayer.ENEMIES)

        # Player layer
        if self.mario:
            renderer.add_sprite_object(self.mario, RenderLayer.PLAYER)

        # Flag layer
        if self.flag_pole_group:
            renderer.add_sprite_group(self.flag_pole_group, RenderLayer.ITEMS)

        # Render all sprites with viewport offset
        offset = (self.viewport.x, self.viewport.y) if self.viewport else (0, 0)
        renderer.render(offset, clear=False)  # Don't clear - we drew background already

        # Draw flag score on top if exists
        if self.flag_score:
            self.flag_score.draw(surface)

        # Draw overhead info
        self.overhead_info_display.draw(surface)

        # Draw moving scores
        for moving_score in self.moving_score_list:
            moving_score.draw(surface)
