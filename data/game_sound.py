"""
Sound management system for Super Mario Bros.

Handles music playback, sound effects, volume control,
and dynamic music transitions based on game state.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import pygame as pg

from . import setup
from . import constants as c

logger = logging.getLogger(__name__)

__author__ = "justinarmstrong"


class SoundSettings:
    """Configuration for sound system."""

    def __init__(self) -> None:
        # Volume levels (0.0 to 1.0)
        self.music_volume: float = 0.5
        self.sfx_volume: float = 0.7
        self.max_channels: int = 16  # Maximum simultaneous sound effects


class Sound:
    """
    Handles all sound for the game.

    Manages background music transitions and sound effect playback
    with support for volume control and audio mixing.

    Attributes:
        sfx_dict: Dictionary of sound effect objects
        music_dict: Dictionary of music file paths
        overhead_info: Reference to overhead info display
        game_info: Game state dictionary
        settings: Sound configuration settings
    """

    def __init__(self, overhead_info: Any) -> None:
        """
        Initialize the sound system.

        Args:
            overhead_info: OverheadInfo instance for game state access
        """
        self.sfx_dict: Dict[str, pg.mixer.Sound] = setup.SFX
        self.music_dict: Dict[str, str] = setup.MUSIC
        self.overhead_info: Any = overhead_info
        self.game_info: dict[str, Any] = overhead_info.game_info
        self.state: str = c.NORMAL
        self.settings: SoundSettings = SoundSettings()

        # Apply initial volume settings
        self.set_volumes(self.settings.music_volume, self.settings.sfx_volume)

        # Initialize mixer with multiple channels
        pg.mixer.set_num_channels(self.settings.max_channels)

        self.set_music_mixer()

    def set_volumes(self, music_volume: float, sfx_volume: float) -> None:
        """
        Set volume levels for music and sound effects.

        Args:
            music_volume: Music volume (0.0 to 1.0)
            sfx_volume: Sound effects volume (0.0 to 1.0)
        """
        self.settings.music_volume = max(0.0, min(1.0, music_volume))
        self.settings.sfx_volume = max(0.0, min(1.0, sfx_volume))

        pg.mixer.music.set_volume(self.settings.music_volume)

        for sfx in self.sfx_dict.values():
            sfx.set_volume(self.settings.sfx_volume)

    def set_music_mixer(self) -> None:
        """Sets music for level based on current game state."""
        try:
            if self.overhead_info.state == c.LEVEL:
                if "main_theme" in self.music_dict:
                    pg.mixer.music.load(self.music_dict["main_theme"])
                    pg.mixer.music.play(loops=-1)  # Loop indefinitely
                    self.state = c.NORMAL
            elif self.overhead_info.state == c.GAME_OVER:
                if "game_over" in self.music_dict:
                    pg.mixer.music.load(self.music_dict["game_over"])
                    pg.mixer.music.play()
                    self.state = c.GAME_OVER
        except pg.error as e:
            logger.error("Audio error: %s", e)

    def update(self, game_info: dict[str, Any], mario: Any) -> None:
        """
        Update sound system with current game state.

        Args:
            game_info: Current game state dictionary
            mario: Mario sprite instance
        """
        self.game_info = game_info
        self.mario = mario
        self.handle_state()

    def handle_state(self) -> None:
        """Handle music state transitions based on game events."""
        if self.state == c.NORMAL:
            self._handle_normal_state()
        elif self.state == c.FLAGPOLE:
            self._handle_flagpole_state()
        elif self.state == c.STAGE_CLEAR:
            self._handle_stage_clear_state()
        elif self.state == c.FAST_COUNT_DOWN:
            self._handle_fast_count_down_state()
        elif self.state == c.TIME_WARNING:
            self._handle_time_warning_state()
        elif self.state == c.SPED_UP_NORMAL:
            self._handle_sped_up_normal_state()
        elif self.state == c.MARIO_INVINCIBLE:
            self._handle_invincible_state()
        # Other states (WORLD_CLEAR, MARIO_DEAD, GAME_OVER) don't need updates

    def _handle_normal_state(self) -> None:
        """Handle sound during normal gameplay."""
        if self.mario.dead:
            self.play_music("death", c.MARIO_DEAD)
        elif self.mario.invincible and not self.mario.losing_invincibility:
            self.play_music("invincible", c.MARIO_INVINCIBLE)
        elif self.mario.state == c.FLAGPOLE:
            self.play_music("flagpole", c.FLAGPOLE)
        elif self.overhead_info.time == 100:
            self.play_music("out_of_time", c.TIME_WARNING)

    def _handle_flagpole_state(self) -> None:
        """Handle sound during flagpole sequence."""
        if self.mario.state == c.WALKING_TO_CASTLE:
            self.play_music("stage_clear", c.STAGE_CLEAR)

    def _handle_stage_clear_state(self) -> None:
        """Handle sound during stage clear."""
        if self.mario.in_castle:
            if "count_down" in self.sfx_dict:
                self.sfx_dict["count_down"].play()
            self.state = c.FAST_COUNT_DOWN

    def _handle_fast_count_down_state(self) -> None:
        """Handle sound during fast countdown."""
        if self.overhead_info.time == 0:
            if "count_down" in self.sfx_dict:
                self.sfx_dict["count_down"].stop()
            self.state = c.WORLD_CLEAR

    def _handle_time_warning_state(self) -> None:
        """Handle sound when time is running low."""
        if pg.mixer.music.get_busy() == 0:
            if "main_theme_sped_up" in self.music_dict:
                self.play_music("main_theme_sped_up", c.SPED_UP_NORMAL)
        elif self.mario.dead:
            self.play_music("death", c.MARIO_DEAD)

    def _handle_sped_up_normal_state(self) -> None:
        """Handle sound during sped-up normal gameplay."""
        if self.mario.dead:
            self.play_music("death", c.MARIO_DEAD)
        elif self.mario.state == c.FLAGPOLE:
            self.play_music("flagpole", c.FLAGPOLE)

    def _handle_invincible_state(self) -> None:
        """Handle sound during invincibility power-up."""
        invincible_duration = self.mario.current_time - self.mario.invincible_start_timer
        if invincible_duration > 11000:
            self.play_music("main_theme", c.NORMAL)
        elif self.mario.dead:
            self.play_music("death", c.MARIO_DEAD)

    def play_music(self, key: str, state: str) -> None:
        """
        Play background music track.

        Args:
            key: Key for music dictionary
            state: New sound state
        """
        try:
            if key in self.music_dict:
                pg.mixer.music.load(self.music_dict[key])
                pg.mixer.music.play(loops=-1 if key.startswith("main_theme") else 0)
                self.state = state
        except pg.error as e:
            logger.error("Music playback error: %s", e)

    def stop_music(self) -> None:
        """Stops background music playback."""
        pg.mixer.music.stop()

    def play_sfx(self, key: str, loops: int = 0) -> None:
        """
        Play a sound effect.

        Args:
            key: Key for sound effect dictionary
            loops: Number of times to loop (-1 for infinite)
        """
        if key in self.sfx_dict:
            self.sfx_dict[key].play(loops=loops)

    def pause_music(self) -> None:
        """Pause background music."""
        pg.mixer.music.pause()

    def unpause_music(self) -> None:
        """Resume paused background music."""
        pg.mixer.music.unpause()

    def fadeout_music(self, milliseconds: int = 1000) -> None:
        """
        Fade out and stop background music.

        Args:
            milliseconds: Duration of fade out
        """
        pg.mixer.music.fadeout(milliseconds)

    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return pg.mixer.music.get_busy()
