"""Level 5 state for Super Mario Bros - World 2-1."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level5(BaseLevel):
    """Level 5 - World 2-1 themed level"""

    level_file = "data/levels/level_2_1.json"

    def get_level_music_key(self) -> str:
        return "level5"

    def get_next_level(self) -> str:
        return c.LEVEL6
