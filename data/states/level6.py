"""Level 6 state for Super Mario Bros - World 2-2."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level6(BaseLevel):
    """Level 6 - World 2-2 themed level"""

    level_file = "data/levels/level_2_2.json"

    def get_level_music_key(self) -> str:
        return "level6"

    def get_next_level(self) -> str:
        return c.LEVEL7
