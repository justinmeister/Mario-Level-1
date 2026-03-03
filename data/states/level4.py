"""Level 4 state for Super Mario Bros - Underground with Lava theme."""

from __future__ import annotations

from .. import constants as c
from .base_level import BaseLevel


class Level4(BaseLevel):
    """Level 4 - Underground with Lava themed level"""

    level_file = "data/levels/level_1_4.json"

    def get_level_music_key(self) -> str:
        return "level4"

    def get_next_level(self) -> str:
        return c.LEVEL5
