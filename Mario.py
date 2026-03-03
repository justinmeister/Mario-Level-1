#!/usr/bin/env python3
"""
Super Mario Bros Level 1 - Python/Pygame Recreation

This is an attempt to recreate the first level of
Super Mario Bros for the NES.

Requirements:
    - Python 3.10+
    - pygame>=2.5.0

Controls:
    - Arrow keys: Move left/right, crouch
    - 'A' key: Jump
    - 'S' key: Action (fireball, run)
    - F5: Toggle FPS display

Author: justinarmstrong (original), Enhanced by community
License: Educational purposes only
"""
from __future__ import annotations

import sys
import pygame as pg
from data.main import main

__version__ = "2.7.0"
__python_version__ = "3.10+"


if __name__ == "__main__":
    main()
    pg.quit()
    sys.exit()

# =============================================================================
# Version 2.7.0 - Player Progression & Advanced AI Edition
# Release Date: February 2026
# Author: justinarmstrong (original), Enhanced by community
# =============================================================================
#
# New Features in v2.7:
# - Player Progression System: XP, levels, 7 rank tiers, persistent stats
# - Character Customization: 14+ unlockable skins with bonuses
# - Daily & Weekly Challenges: Auto-generated with 6 categories
# - Advanced AI System: State machines, group coordination, AI director
# - Enhanced from v2.6: Bosses, Combo 2.0, 4 new enemies, advanced particles
#
