"""Music manager for game levels with automatic track switching."""

from __future__ import annotations

import logging
from typing import Optional

import pygame as pg

from .new_audio_loader import get_level_music, load_new_music

logger = logging.getLogger(__name__)


class LevelMusicManager:
    """Manages music playback for game levels."""

    def __init__(self) -> None:
        """Initialize the level music manager."""
        self.music_tracks = load_new_music()
        self.current_track: Optional[str] = None
        self.current_level: Optional[str] = None
        self.is_sped_up = False
        self.time_warning_played = False

    def play_level_music(self, level_name: str, fade_ms: int = 1000) -> bool:
        """Play music for a specific level.

        Args:
            level_name: Level identifier (e.g. 'level1', 'level2')
            fade_ms: Fade in duration in milliseconds

        Returns:
            True if music started playing, False otherwise
        """
        track_name = get_level_music(level_name, time_low=False)
        if not track_name or track_name not in self.music_tracks:
            return False

        track_path = self.music_tracks[track_name]

        try:
            # Stop current music if playing
            if pg.mixer.music.get_busy():
                pg.mixer.music.fadeout(fade_ms // 2)
                pg.time.wait(fade_ms // 2)

            # Load and play new track
            pg.mixer.music.load(track_path)
            pg.mixer.music.play(-1, fade_ms=fade_ms)

            self.current_track = track_name
            self.current_level = level_name
            self.is_sped_up = False
            self.time_warning_played = False

            return True
        except pg.error as e:
            logger.warning("Could not play music for %s: %s", level_name, e)
            return False

    def switch_to_sped_up(self, fade_ms: int = 500) -> bool:
        """Switch to sped up version of current track.

        Args:
            fade_ms: Fade duration in milliseconds

        Returns:
            True if switched successfully, False otherwise
        """
        if self.is_sped_up or not self.current_level:
            return False

        track_name = get_level_music(self.current_level, time_low=True)
        if not track_name or track_name not in self.music_tracks:
            return False

        track_path = self.music_tracks[track_name]

        try:
            # Get current position
            pos = pg.mixer.music.get_pos() / 1000.0  # Convert to seconds

            # Fade out current music
            pg.mixer.music.fadeout(fade_ms)
            pg.time.wait(fade_ms)

            # Load and play sped up version
            pg.mixer.music.load(track_path)
            pg.mixer.music.play(-1, start=pos, fade_ms=fade_ms)

            self.current_track = track_name
            self.is_sped_up = True

            return True
        except pg.error as e:
            print(f"Could not switch to sped up music: {e}")
            return False

    def update(self, time_remaining: float) -> None:
        """Update music based on time remaining.

        Args:
            time_remaining: Time remaining in seconds
        """
        # Switch to sped up music when time is low
        if time_remaining <= 100 and not self.is_sped_up:
            self.switch_to_sped_up()

    def stop(self, fade_ms: int = 1000) -> None:
        """Stop current music.

        Args:
            fade_ms: Fade out duration in milliseconds
        """
        if pg.mixer.music.get_busy():
            pg.mixer.music.fadeout(fade_ms)

        self.current_track = None
        self.current_level = None
        self.is_sped_up = False
        self.time_warning_played = False

    def pause(self) -> None:
        """Pause current music."""
        pg.mixer.music.pause()

    def unpause(self) -> None:
        """Unpause current music."""
        pg.mixer.music.unpause()

    def set_volume(self, volume: float) -> None:
        """Set music volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        pg.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    def is_playing(self) -> bool:
        """Check if music is currently playing.

        Returns:
            True if music is playing, False otherwise
        """
        return pg.mixer.music.get_busy()


# Global instance
_level_music_manager: Optional[LevelMusicManager] = None


def get_level_music_manager() -> LevelMusicManager:
    """Get global level music manager instance.

    Returns:
        Level music manager instance
    """
    global _level_music_manager
    if _level_music_manager is None:
        _level_music_manager = LevelMusicManager()
    return _level_music_manager
