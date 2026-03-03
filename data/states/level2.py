"""Level 2 state for Super Mario Bros."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level2(BaseLevel):
    """Level 2 - Underground themed level"""

    level_file = "data/levels/level_2_1.json"

    def get_level_music_key(self) -> str:
        return "level2"

    def get_background_key(self) -> str:
        return "level_1"  # Use level_1 background as fallback

    def get_next_level(self) -> str:
        return c.LEVEL3
