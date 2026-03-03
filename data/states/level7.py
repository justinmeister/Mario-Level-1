"""Level 7 state for Super Mario Bros - World 2-3."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level7(BaseLevel):
    """Level 7 - World 2-3 themed level"""

    level_file = "data/levels/level_2_3.json"

    def get_level_music_key(self) -> str:
        return "level7"

    def get_next_level(self) -> str:
        return c.LEVEL8
