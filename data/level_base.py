"""Base class for all game levels to reduce code duplication."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import pygame as pg

from . import constants as c
from .error_handler import LevelDataValidator, GameStateValidator
from .level_music_manager import get_level_music_manager
from .level_sound_effects import get_level_sound_effects
from .performance_optimizer import get_collision_optimizer

logger = logging.getLogger(__name__)


class LevelBase:
    """Base class for all game levels with common functionality."""

    def __init__(self, level_file: str, level_name: str) -> None:
        """Initialize level base.

        Args:
            level_file: Path to level JSON file
            level_name: Level identifier (e.g. 'level1')
        """
        self.level_file = level_file
        self.level_name = level_name
        self.level_data: Optional[Dict[str, Any]] = None

        # Audio managers
        self.music_manager = get_level_music_manager()
        self.sound_effects = get_level_sound_effects()
        self.time_warning_played = False

        # Performance optimizer
        self.collision_optimizer = get_collision_optimizer()

        # Game state
        self.game_info: Dict[str, Any] = {}
        self.current_time: float = 0
        self.done = False

    def load_level_data(self) -> bool:
        """Load and validate level data from JSON file.

        Returns:
            True if loaded successfully, False otherwise
        """
        data, error = LevelDataValidator.load_and_validate_level(self.level_file)

        if error:
            logger.error("Error loading level: %s", error)
            self.done = True
            return False

        self.level_data = data
        return True

    def setup_audio(self, fade_ms: int = 1000) -> None:
        """Setup and start level music.

        Args:
            fade_ms: Fade in duration in milliseconds
        """
        success = self.music_manager.play_level_music(self.level_name, fade_ms=fade_ms)
        if not success:
            logger.warning("Could not start music for %s", self.level_name)

    def update_audio(self) -> None:
        """Update audio based on game state."""
        # Validate game_info
        if not GameStateValidator.validate_game_info(self.game_info):
            return

        # Get time remaining
        time_remaining = GameStateValidator.safe_get_game_value(self.game_info, str(c.LEVEL_TIME), 400)

        # Update music (auto-switches to sped up version)
        self.music_manager.update(time_remaining)

        # Play time warning sound
        if time_remaining == 100 and not self.time_warning_played:
            self.sound_effects.play_time_warning()
            self.time_warning_played = True

    def cleanup_audio(self, fade_ms: int = 500) -> None:
        """Stop level music on cleanup.

        Args:
            fade_ms: Fade out duration in milliseconds
        """
        self.music_manager.stop(fade_ms=fade_ms)

    def setup_collision_optimizer(
        self,
        ground_group: pg.sprite.Group,
        pipe_group: pg.sprite.Group,
        step_group: pg.sprite.Group,
        brick_group: pg.sprite.Group,
        coin_box_group: pg.sprite.Group,
    ) -> None:
        """Setup collision optimizer with sprite groups.

        Args:
            ground_group: Ground sprites
            pipe_group: Pipe sprites
            step_group: Step sprites
            brick_group: Brick sprites
            coin_box_group: Coin box sprites
        """
        self.collision_optimizer.setup_combined_groups(
            ground_group,
            pipe_group,
            step_group,
            brick_group,
            coin_box_group,
        )

    def handle_coin_collection(self, coin_score: int = 200) -> None:
        """Handle coin collection with sound effect.

        Args:
            coin_score: Score value for collecting coin
        """
        self.sound_effects.play_coin()
        self.game_info[c.SCORE] = self.game_info.get(c.SCORE, 0) + coin_score
        self.game_info[c.COIN_TOTAL] = self.game_info.get(c.COIN_TOTAL, 0) + 1

    def handle_level_complete(self) -> None:
        """Handle level completion with sound effect."""
        self.music_manager.stop(fade_ms=500)
        self.sound_effects.play_level_complete()

    def handle_game_over(self) -> None:
        """Handle game over with sound effect."""
        self.music_manager.stop(fade_ms=200)
        self.sound_effects.play_game_over()

    def handle_pipe_transition(self) -> None:
        """Handle pipe transition with sound effect."""
        self.sound_effects.play_pipe()

    def get_level_section_data(self, section_name: str) -> list:
        """Safely get level section data.

        Args:
            section_name: Name of the section

        Returns:
            List of section data or empty list
        """
        if not self.level_data:
            return []

        return self.level_data.get(section_name, [])  # type: ignore[no-any-return]

    def validate_sprite_groups(self, *groups: pg.sprite.Group) -> bool:
        """Validate that sprite groups exist and are not None.

        Args:
            *groups: Sprite groups to validate

        Returns:
            True if all groups valid, False otherwise
        """
        for group in groups:
            if group is None:
                logger.warning("Sprite group is None")
                return False
        return True
