"""Sound effects manager for game events."""

from __future__ import annotations

import logging
from typing import Dict, Optional

import pygame as pg

from .new_audio_loader import load_new_sounds

logger = logging.getLogger(__name__)


class LevelSoundEffects:
    """Manages sound effects for game events."""

    def __init__(self) -> None:
        """Initialize sound effects manager."""
        self.sounds: Dict[str, pg.mixer.Sound] = load_new_sounds()
        self.sfx_volume = 0.8

        # Apply volume to all sounds
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def play_time_warning(self) -> bool:
        """Play time warning sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("time_warning")

    def play_pipe(self) -> bool:
        """Play pipe transition sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("pipe_new")

    def play_stage_clear(self) -> bool:
        """Play stage clear sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("stage_clear")

    def play_coin(self) -> bool:
        """Play coin collection sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("coin_new")

    def play_level_complete(self) -> bool:
        """Play level complete fanfare.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("level_complete")

    def play_world_clear(self) -> bool:
        """Play world clear fanfare.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("world_clear")

    def play_castle_complete(self) -> bool:
        """Play castle complete sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("castle_complete")

    def play_boss_defeat(self) -> bool:
        """Play boss defeat sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("boss_defeat")

    def play_game_over(self) -> bool:
        """Play game over sound.

        Returns:
            True if sound played, False otherwise
        """
        return self._play_sound("game_over_new")

    def _play_sound(self, sound_name: str) -> bool:
        """Play a sound by name.

        Args:
            sound_name: Name of the sound to play

        Returns:
            True if sound played, False otherwise
        """
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.play()
                return True
            except pg.error as e:
                logger.warning("Could not play sound %s: %s", sound_name, e)
        return False

    def set_volume(self, volume: float) -> None:
        """Set volume for all sound effects.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def stop_all(self) -> None:
        """Stop all playing sounds."""
        for sound in self.sounds.values():
            sound.stop()


# Global instance
_level_sound_effects: Optional[LevelSoundEffects] = None


def get_level_sound_effects() -> LevelSoundEffects:
    """Get global level sound effects instance.

    Returns:
        Level sound effects instance
    """
    global _level_sound_effects
    if _level_sound_effects is None:
        _level_sound_effects = LevelSoundEffects()
    return _level_sound_effects
