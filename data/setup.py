"""
This module initializes the display and creates dictionaries of resources.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import pygame as pg

from .resource_manager import SimpleResourceManager, get_simple_manager

logger = logging.getLogger(__name__)

ORIGINAL_CAPTION: str = "Super Mario Bros"

# Backward compatibility globals
FONTS: Dict[str, str] = {}
MUSIC: Dict[str, str] = {}
GFX: Dict[str, pg.Surface] = {}
SFX: Dict[str, pg.mixer.Sound] = {}
SCREEN: Optional[pg.Surface] = None
SCREEN_RECT: Optional[pg.Rect] = None


def initialize_display() -> None:
    """Initialize pygame display."""
    global SCREEN, SCREEN_RECT
    manager = get_simple_manager()
    manager.initialize_display()
    SCREEN = manager.screen
    SCREEN_RECT = manager.screen_rect


def load_resources(resources_dir: str = "resources") -> None:
    """Load all game resources."""
    global FONTS, MUSIC, GFX, SFX
    manager = get_simple_manager()
    manager.load_resources(resources_dir)
    FONTS = manager.fonts
    MUSIC = manager.music
    GFX = manager.gfx
    SFX = manager.sfx


def initialize(resources_dir: str = "resources") -> None:
    """Initialize the entire setup (display + resources)."""
    get_simple_manager().initialize(resources_dir)


def get_resource_manager() -> SimpleResourceManager:
    """Get the resource manager singleton."""
    return get_simple_manager()


# =============================================================================
# Factory functions for game states
# =============================================================================


def _create_state(module_name: str, class_name: str) -> Optional[Any]:
    """Generic state factory."""
    try:
        module = __import__(f"data.{module_name}", fromlist=[class_name])
        cls = getattr(module, class_name)
        return cls()
    except Exception as e:
        logger.error(f"Failed to create {class_name}: {e}")
        return None


def create_main_menu() -> Optional[Any]:
    """Create main menu state."""
    return _create_state("states.main_menu", "Menu")


def create_level_select() -> Optional[Any]:
    """Create level select state."""
    return _create_state("states.level_select", "LevelSelect")


def create_settings() -> Optional[Any]:
    """Create settings state."""
    return _create_state("states.settings", "Settings")


def create_load_screen() -> Optional[Any]:
    """Create load screen state."""
    return _create_state("states.load_screen", "LoadScreen")


def create_timeout_screen() -> Optional[Any]:
    """Create timeout screen state."""
    return _create_state("states.load_screen", "TimeOut")


def create_game_over() -> Optional[Any]:
    """Create game over state."""
    return _create_state("states.load_screen", "GameOver")


def create_level1() -> Optional[Any]:
    """Create level 1 state."""
    return _create_state("states.level1", "Level1")


def create_level2() -> Optional[Any]:
    """Create level 2 state."""
    return _create_state("states.level2", "Level2")


def create_level3() -> Optional[Any]:
    """Create level 3 state."""
    return _create_state("states.level3", "Level3")


def create_level4() -> Optional[Any]:
    """Create level 4 state."""
    return _create_state("states.level4", "Level4")


def create_level5() -> Optional[Any]:
    """Create level 5 state."""
    return _create_state("states.level5", "Level5")


def create_level6() -> Optional[Any]:
    """Create level 6 state."""
    return _create_state("states.level6", "Level6")


def create_level7() -> Optional[Any]:
    """Create level 7 state."""
    return _create_state("states.level7", "Level7")


def create_level8() -> Optional[Any]:
    """Create level 8 state."""
    return _create_state("states.level8", "Level8")


# Auto-initialize on module import for backward compatibility
try:
    initialize()
except Exception:
    # If resources aren't available, just initialize display
    try:
        initialize_display()
    except Exception:
        # Create dummy surface for headless tests
        try:
            SCREEN = pg.Surface((800, 600))
            SCREEN_RECT = SCREEN.get_rect()
        except Exception:
            pass

    # Provide dummy resources for tests
    try:
        if not GFX.get("smb_enemies_sheet"):
            GFX["smb_enemies_sheet"] = pg.Surface((512, 512))
        if not GFX.get("mario_bros"):
            GFX["mario_bros"] = pg.Surface((512, 512))
        if not GFX.get("tile_set"):
            GFX["tile_set"] = pg.Surface((512, 512))
        if not GFX.get("item_objects"):
            GFX["item_objects"] = pg.Surface((512, 512))
        if not GFX.get("text_images"):
            GFX["text_images"] = pg.Surface((512, 512))
    except Exception:
        pass
