"""Base class for game levels.

Provides common functionality for all level states.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pygame as pg

from .. import setup, tools
from .. import constants as c
from .. import level_loader
from ..components import mario as mario_module
from ..components import collider
from ..components import bricks
from ..components import coin_box
from ..components import enemies
from ..components import advanced_enemies
from ..components import checkpoint
from ..components import flagpole
from ..components import info
from ..components import score
from ..level_music_manager import get_level_music_manager
from ..level_sound_effects import get_level_sound_effects

if TYPE_CHECKING:
    from ..components.info import OverheadInfo

logger = logging.getLogger(__name__)


class BaseLevel(tools._State):
    """
    Base class for all level states.

    Provides common methods and attributes for level management.
    Supports loading levels from JSON files via level_loader.
    """

    # Level file path - override in subclasses
    level_file: str = ""

    def __init__(self) -> None:
        super().__init__()
        self.game_info: Dict[str, Any] = {}
        self.persist: Dict[str, Any] = {}

        # Timing
        self.death_timer: float = 0
        self.flag_timer: float = 0
        self.flag_score: Optional[score.Score] = None
        self.time_warning_played: bool = False

        # Sprite groups
        self.moving_score_list: List[score.Score] = []
        self.overhead_info_display: Optional[OverheadInfo] = None

        # Display
        self.background: Optional[pg.Surface] = None
        self.back_rect: Optional[pg.Rect] = None
        self.level: Optional[pg.Surface] = None
        self.level_rect: Optional[pg.Rect] = None
        self.viewport: Optional[pg.Rect] = None

        # Sprite groups
        self.ground_group: Optional[pg.sprite.Group] = None
        self.pipe_group: Optional[pg.sprite.Group] = None
        self.step_group: Optional[pg.sprite.Group] = None
        self.brick_group: Optional[pg.sprite.Group] = None
        self.coin_box_group: Optional[pg.sprite.Group] = None
        self.flag_pole_group: Optional[pg.sprite.Group] = None
        self.enemy_group: Optional[pg.sprite.Group] = None
        self.mario: Optional[mario_module.Mario] = None
        self.checkpoint_group: Optional[pg.sprite.Group] = None
        self.flag: Optional[flagpole.Flag] = None
        self.pole: Optional[flagpole.Pole] = None
        self.finial: Optional[flagpole.Finial] = None
        self.coin_group: Optional[pg.sprite.Group] = None
        self.powerup_group: Optional[pg.sprite.Group] = None
        self.fire_group: Optional[pg.sprite.Group] = None
        self.brick_pieces_group: Optional[pg.sprite.Group] = None
        self.mario_and_enemy_group: Optional[pg.sprite.Group] = None
        self.sprites_about_to_die_group: Optional[pg.sprite.Group] = None
        self.shell_group: Optional[pg.sprite.Group] = None
        self.ground_step_pipe_group: Optional[pg.sprite.Group] = None

        # Level data from JSON
        self.level_data: Optional[level_loader.LevelData] = None

        # Audio
        self.music_manager = get_level_music_manager()
        self.sound_effects = get_level_sound_effects()

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called when the State object is created."""
        self.game_info = persist
        self.persist = self.game_info
        self.game_info[c.CURRENT_TIME] = current_time
        self.game_info[c.LEVEL_STATE] = c.NOT_FROZEN
        self.game_info[c.MARIO_DEAD] = False

        self.state = c.NOT_FROZEN
        self.start_time = current_time
        self.time_warning_played = False

        # Load level data if level_file is specified
        if self.level_file:
            try:
                logger.info(f"Loading level: {self.level_file}")
                self.level_data = level_loader.load_level_from_json(self.level_file)
                logger.info(f"Level loaded: {self.level_data.name if self.level_data else 'None'}")
            except (FileNotFoundError, Exception) as e:
                logger.error(f"Failed to load level {self.level_file}: {e}", exc_info=True)
                self.next = c.GAME_OVER
                self.done = True
                return

        # Initialize groups and setup
        self._init_groups()
        self.create_overhead_display()
        self.setup_all()
        logger.info(f"Level setup complete: {self.__class__.__name__}")

        # Start level music (override in subclass for specific music)
        self.music_manager.play_level_music(self.get_level_music_key(), fade_ms=1000)

    def _init_groups(self) -> None:
        """Initialize all sprite groups."""
        self.ground_group = pg.sprite.Group()
        self.pipe_group = pg.sprite.Group()
        self.step_group = pg.sprite.Group()
        self.brick_group = pg.sprite.Group()
        self.coin_box_group = pg.sprite.Group()
        self.flag_pole_group = pg.sprite.Group()
        self.enemy_group = pg.sprite.Group()
        self.checkpoint_group = pg.sprite.Group()
        self.coin_group = pg.sprite.Group()
        self.powerup_group = pg.sprite.Group()
        self.fire_group = pg.sprite.Group()
        self.mario_and_enemy_group = pg.sprite.Group()
        self.sprites_about_to_die_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()
        self.brick_pieces_group = pg.sprite.Group()

    def create_overhead_display(self) -> None:
        """Create the overhead info display."""
        self.overhead_info_display = info.OverheadInfo(self.game_info, c.LEVEL)

    def setup_all(self) -> None:
        """Setup all level components. Override in subclass if needed."""
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
        self._setup_ground_step_pipe_group()

    def get_level_music_key(self) -> str:
        """Return music key for this level. Override in subclass."""
        return "level1"

    def _setup_ground_step_pipe_group(self) -> None:
        """Create combined group for ground, steps, and pipes."""
        self.ground_step_pipe_group = pg.sprite.Group()
        for sprite in self.ground_group or []:
            self.ground_step_pipe_group.add(sprite)
        for sprite in self.pipe_group or []:
            self.ground_step_pipe_group.add(sprite)
        for sprite in self.step_group or []:
            self.ground_step_pipe_group.add(sprite)

    def setup_background(self) -> None:
        """Set up background image and rect from level data."""
        if self.level_data is None:
            return

        width = self.level_data.width
        height = self.level_data.height

        bg_key = self.get_background_key()
        self.background = setup.GFX.get(bg_key, pg.Surface((width, height)))
        if hasattr(self.level_data, "background_color"):
            self.background.fill(self.level_data.background_color)
        self.back_rect = self.background.get_rect()

        self.level = pg.Surface((width, height), pg.SRCALPHA)
        self.level_rect = self.level.get_rect()

        if setup.SCREEN is not None and self.level_rect:
            self.viewport = setup.SCREEN.get_rect(bottom=self.level_rect.bottom)
            self.viewport.x = self.game_info.get(str(c.CAMERA_START_X), 0)

    def get_background_key(self) -> str:
        """Return background key for this level. Override in subclass."""
        return "level_1"

    def setup_ground(self) -> None:
        """Set up ground collision rectangles from level data."""
        if self.ground_group is None or self.level_data is None:
            return

        for section in getattr(self.level_data, "ground_sections", []):
            self.ground_group.add(collider.Collider(
                section["x"], section["y"], section["width"], section["height"]
            ))

    def setup_pipes(self) -> None:
        """Set up pipe obstacles from level data."""
        if self.pipe_group is None or self.level_data is None:
            return

        for p in getattr(self.level_data, "pipes", []):
            self.pipe_group.add(collider.Collider(p["x"], p["y"], p["width"], p["height"]))

    def setup_steps(self) -> None:
        """Set up step obstacles from level data."""
        if self.step_group is None or self.level_data is None:
            return

        for s in getattr(self.level_data, "steps", []):
            self.step_group.add(collider.Collider(s["x"], s["y"], s["width"], s["height"]))

    def setup_bricks(self) -> None:
        """Set up brick blocks from level data."""
        if self.brick_group is None or self.level_data is None:
            return

        for brick_info in getattr(self.level_data, "bricks", []):
            self.brick_group.add(bricks.Brick(
                brick_info["x"], brick_info["y"],
                contents=brick_info.get("contents")
            ))

    def setup_coin_boxes(self) -> None:
        """Set up coin boxes from level data."""
        if self.coin_box_group is None or self.level_data is None:
            return

        for box_info in getattr(self.level_data, "coin_boxes", []):
            self.coin_box_group.add(coin_box.CoinBox(
                box_info["x"], box_info["y"],
                contents=box_info.get("contents")
            ))

    def setup_flag_pole(self) -> None:
        """Set up flag pole at level end from level data."""
        if self.flag_pole_group is None or self.level_data is None:
            return

        flag_pole_data = getattr(self.level_data, "flag_pole", {})
        if flag_pole_data:
            self.flag = flagpole.Flag(flag_pole_data["x"], flag_pole_data["y"])
            self.pole = flagpole.Pole(flag_pole_data["x"], flag_pole_data["y"])
            self.finial = flagpole.Finial(flag_pole_data["x"], flag_pole_data["y"])
            self.flag_pole_group.add(self.flag, self.pole, self.finial)

    def setup_enemies(self) -> None:
        """Set up enemy sprites from level data."""
        if self.enemy_group is None or self.level_data is None:
            return

        enemy_map = {
            "goomba": enemies.Goomba,
            "koopa": enemies.Koopa,
            "piranha": advanced_enemies.PiranhaPlant,
            "bullet_bill": advanced_enemies.BulletBill,
            "hammer_bro": advanced_enemies.HammerBro,
        }

        for enemy_info in getattr(self.level_data, "enemies", []):
            enemy_type = enemy_info.get("type", "goomba")
            enemy_class = enemy_map.get(enemy_type, enemies.Goomba)
            x = enemy_info.get("x", 0)
            y = enemy_info.get("y", c.GROUND_HEIGHT)
            direction = enemy_info.get("direction", "left")
            self.enemy_group.add(enemy_class(x, y, direction))

    def setup_mario(self) -> None:
        """Set up Mario player sprite."""
        self.mario = mario_module.Mario()

        if self.mario and self.mario.rect is not None:
            mario_start = getattr(self.level_data, "mario_start", {"x": 110, "y": c.GROUND_HEIGHT})
            self.mario.rect.x = mario_start.get("x", 110)
            self.mario.rect.y = mario_start.get("y", c.GROUND_HEIGHT)

        if self.mario and self.mario_and_enemy_group is not None:
            self.mario_and_enemy_group.add(self.mario)

    def setup_checkpoints(self) -> None:
        """Set up checkpoint triggers from level data."""
        if self.checkpoint_group is None or self.level_data is None:
            return

        for cp_info in getattr(self.level_data, "checkpoints", []):
            self.checkpoint_group.add(checkpoint.Checkpoint(
                cp_info["x"],
                cp_info["name"],
                cp_info.get("y", 0),
                cp_info.get("width", 10),
                cp_info.get("height", 600),
            ))

    def update(self, surface: pg.Surface, keys: tuple, current_time: float) -> None:
        """Update level state."""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = current_time

        # Debug logging for level 2
        if self.__class__.__name__ == "Level2" and not hasattr(self, '_logged_update'):
            logger.info(f"Level2 update called: state={self.state}, mario={self.mario is not None}")
            self._logged_update = True

        # Update music based on time remaining
        time_remaining = self.game_info.get(str(c.LEVEL_TIME), 400)
        self.music_manager.update(time_remaining)

        # Play time warning sound
        if time_remaining == 100 and not self.time_warning_played:
            self.sound_effects.play_time_warning()
            self.time_warning_played = True

        if self.state == c.FROZEN:
            self.draw(surface)
            return

        if self.state == c.NOT_FROZEN:
            if self.game_info.get(c.MARIO_DEAD):
                self._handle_death()
            elif self.game_info.get(c.FLAG_AND_FIREWORKS):
                self._handle_flag_and_fireworks(current_time)
            else:
                self.update_entities(keys, current_time)
                self.check_collisions()
                self.check_checkpoints()
                self.check_state_triggers()

                if self.mario and not self.mario.dead:
                    self.update_viewport()

        self.draw(surface)

    def _handle_death(self) -> None:
        """Handle Mario's death."""
        self.death_timer += 1
        if self.death_timer == 90 and self.mario:
            self.mario.update((), self.game_info, self.fire_group or pg.sprite.Group())
        elif self.death_timer == 120:
            self.next = c.GAME_OVER
            self.done = True

    def _handle_flag_and_fireworks(self, current_time: float) -> None:
        """Handle reaching the flag pole."""
        if not self.flag_score:
            return
        self.flag_timer = current_time
        if self.flag_timer >= 200:
            self.game_info["current_level"] = self.get_next_level()
            self.next = c.LOAD_SCREEN
            self.done = True

    def get_next_level(self) -> str:
        """Return next level key. Override in subclass."""
        return c.LEVEL2

    def update_entities(self, keys: tuple, current_time: float) -> None:
        """Update all game entities."""
        if self.mario:
            self.mario.update(keys, self.game_info, self.powerup_group or pg.sprite.Group())

        if self.enemy_group:
            self.enemy_group.update(self.game_info)

        if self.powerup_group:
            self.powerup_group.update(self.game_info, self.viewport)

        if self.fire_group:
            self.fire_group.update(self.game_info)

        if self.brick_group:
            self.brick_group.update()

        if self.coin_box_group:
            self.coin_box_group.update(self.game_info)

    def check_collisions(self) -> None:
        """Check all collisions with static objects and enemies."""
        if not self.mario:
            return

        # Check static colliders (ground, steps, pipes)
        if self.ground_step_pipe_group:
            collide = pg.sprite.spritecollideany(self.mario, self.ground_step_pipe_group)
            if collide:
                self._handle_static_collision(collide)

        # Check bricks
        if self.brick_group:
            brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
            if brick:
                self._handle_brick_collision(brick)

        # Check coin boxes
        if self.coin_box_group:
            coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
            if coin_box:
                self._handle_coin_box_collision(coin_box)

        # Check enemies
        if self.enemy_group:
            enemy = pg.sprite.spritecollideany(self.mario, self.enemy_group)
            if enemy:
                self._handle_enemy_collision(enemy)

        # Check powerups
        if self.powerup_group:
            powerup = pg.sprite.spritecollideany(self.mario, self.powerup_group)
            if powerup:
                self._handle_powerup_collision(powerup)

        # Check coins
        if self.coin_group:
            coin = pg.sprite.spritecollideany(self.mario, self.coin_group)
            if coin:
                coin.kill()
                self.game_info[c.SCORE] += 200
                self.game_info[c.COIN_TOTAL] += 1

    def _handle_static_collision(self, collider: Any) -> None:
        """Handle collision with static objects. Override in subclass for full physics."""
        pass

    def _handle_brick_collision(self, brick: Any) -> None:
        """Handle collision with brick. Override in subclass for full physics."""
        pass

    def _handle_coin_box_collision(self, coin_box: Any) -> None:
        """Handle collision with coin box. Override in subclass for full physics."""
        pass

    def _handle_enemy_collision(self, enemy: Any) -> None:
        """Handle collision with enemy. Override in subclass for full physics."""
        pass

    def _handle_powerup_collision(self, powerup: Any) -> None:
        """Handle collision with powerup."""
        if powerup and self.mario:
            powerup.collide_action(self.mario, self.game_info, self.current_time)

    def check_checkpoints(self) -> None:
        """Check for checkpoint collisions."""
        if self.mario and self.checkpoint_group:
            checkpoint = pg.sprite.spritecollideany(self.mario, self.checkpoint_group)
            if checkpoint:
                checkpoint.kill()

    def check_state_triggers(self) -> None:
        """Check for state transition triggers."""
        if self.mario and self.mario.dead:
            self.state = c.FROZEN
            self.game_info[c.MARIO_DEAD] = True

        if self.mario and self.flag_pole_group:
            flag_pole = pg.sprite.spritecollideany(self.mario, self.flag_pole_group)
            if flag_pole and hasattr(flag_pole, "state") and flag_pole.state == c.TOP_OF_POLE:
                self.state = c.FLAG_AND_FIREWORKS
                if self.mario.rect:
                    self.flag_score = score.Score(
                        int(self.mario.rect.centerx),
                        int(self.mario.rect.y),
                        c.SCORE_FLAG_POLE_TOP
                    )
                    self.moving_score_list.append(self.flag_score)

    def update_viewport(self) -> None:
        """Update camera viewport based on Mario position."""
        if not self.mario or not self.viewport or not self.level_rect or not self.mario.rect:
            return

        if self.mario.rect.right > self.viewport.centerx:
            self.viewport.centerx = self.mario.rect.centerx

        if self.mario.rect.left < self.viewport.x:
            self.mario.rect.left = self.viewport.x

        self.viewport.x = max(0, self.viewport.x)
        self.viewport.right = min(self.viewport.right, self.level_rect.right)

    def draw(self, surface: pg.Surface) -> None:
        """Render the level."""
        if self.level is None or self.background is None or self.viewport is None or self.back_rect is None:
            return

        self.level.blit(self.background, self.back_rect, self.viewport)

        # Draw all sprite groups
        for group in [
            self.ground_group,
            self.pipe_group,
            self.step_group,
            self.brick_group,
            self.coin_box_group,
            self.flag_pole_group,
            self.enemy_group,
            self.powerup_group,
            self.coin_group,
            self.fire_group,
            self.mario_and_enemy_group,
        ]:
            if group:
                group.draw(self.level)

        if self.overhead_info_display:
            self.overhead_info_display.draw(self.level)

        surface.blit(self.level, (0, 0), self.viewport)

    def get_event(self, event: pg.event.Event) -> None:
        """Handle pygame events."""
        if self.mario and hasattr(self.mario, "get_event"):
            self.mario.get_event(event)
