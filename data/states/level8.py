"""Level 8 state for Super Mario Bros - World 2-4."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level8(BaseLevel):
    """Level 8 - World 2-4 themed level"""

    level_file = "data/levels/level_2_4.json"

    def get_level_music_key(self) -> str:
        return "level8"

    def get_next_level(self) -> str:
        return c.GAME_OVER
