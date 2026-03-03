"""Loader for new audio files from resources/music/new/"""

from __future__ import annotations

import logging
import os
from typing import Dict

import pygame as pg

logger = logging.getLogger(__name__)


def load_new_music() -> Dict[str, str]:
    """Load new music tracks from resources/music/new/

    Returns:
        Dictionary mapping track names to file paths
    """
    music_dir = "resources/music/new"
    music_tracks = {}

    # Main themes
    tracks = {
        "main_theme": "main_theme.mp3",
        "main_theme_sped_up": "main_theme_sped_up.mp3",
        "underground": "underground.mp3",
        "underground_sped_up": "underground_sped_up.mp3",
        "underwater": "underwater.mp3",
        "underwater_sped_up": "underwater_sped_up.mp3",
        "castle": "castle.mp3",
        "castle_sped_up": "castle_sped_up.mp3",
        "star_power": "star_power.mp3",
        "star_power_sped_up": "star_power_sped_up.mp3",
        "ending": "ending.mp3",
    }

    for name, filename in tracks.items():
        filepath = os.path.join(music_dir, filename)
        if os.path.exists(filepath):
            music_tracks[name] = filepath

    return music_tracks


def load_new_sounds() -> Dict[str, pg.mixer.Sound]:
    """Load new sound effects from resources/music/new/

    Returns:
        Dictionary mapping sound names to Sound objects
    """
    music_dir = "resources/music/new"
    sounds = {}

    # Sound effects
    sound_files = {
        "time_warning": "time_warning.mp3",
        "pipe_new": "pipe.mp3",
        "stage_clear": "stage_clear.mp3",
        "coin_new": "coin.mp3",
        "level_complete": "level_complete.mp3",
        "world_clear": "world_clear.mp3",
        "castle_complete": "castle_complete.mp3",
        "boss_defeat": "boss_defeat.mp3",
        "game_over_new": "game_over.mp3",
    }

    for name, filename in sound_files.items():
        filepath = os.path.join(music_dir, filename)
        if os.path.exists(filepath):
            try:
                sounds[name] = pg.mixer.Sound(filepath)
            except pg.error as e:
                logger.warning("Could not load sound %s: %s", name, e)

    return sounds


# Level music mapping
LEVEL_MUSIC_MAP = {
    "level1": "main_theme",
    "level2": "underground",  # 1-2 underground
    "level3": "main_theme",  # 1-3 tree platforms
    "level4": "castle",  # 1-4 castle
    "level5": "main_theme",  # 2-1 overworld
    "level6": "underwater",  # 2-2 underwater
    "level7": "main_theme",  # 2-3 bridge
    "level8": "castle",  # 2-4 castle
}


def get_level_music(level_name: str, time_low: bool = False) -> str | None:
    """Get music track name for a level.

    Args:
        level_name: Level identifier (e.g. 'level1', 'level2')
        time_low: Whether time is running low (< 100 seconds)

    Returns:
        Music track name or None if not found
    """
    base_track = LEVEL_MUSIC_MAP.get(level_name)
    if base_track and time_low:
        return f"{base_track}_sped_up"
    return base_track
