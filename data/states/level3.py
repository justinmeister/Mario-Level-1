"""Level 3 state for Super Mario Bros."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level3(BaseLevel):
    """Level 3 - Sky/Cloud themed level"""

    level_file = "data/levels/level_1_3.json"

    def get_level_music_key(self) -> str:
        return "level3"

    def get_next_level(self) -> str:
        return c.LEVEL4
