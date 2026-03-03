"""
Super Mario Bros Level 1 - Data Package

This package contains all game data, states, and components.
"""
__author__ = "justinarmstrong"
__version__ = "2.7.0"

from . import level_loader
from . import tools
from . import setup
from . import achievements_v2 as achievements
from . import combo_system
from . import game_settings
from . import visual_effects
from . import optimization
from . import animation_system
from . import ui
from . import weather_system
from . import audio_manager
from . import hint_system
from . import dialog_system as dialogue_system  # Alias for backwards compatibility
from . import screenshot_manager as screenshot
from . import debug
from . import statistics
from . import input_system
from . import resource_manager
from . import enhanced_particles_v2 as advanced_particles

__all__ = [
    "level_loader",
    "constants",
    "tools",
    "setup",
    "achievements",
    "combo_system",
    "game_settings",
    "visual_effects",
    "optimization",
    "animation_system",
    "ui",
    "weather_system",
    "audio_manager",
    "hint_system",
    "dialogue_system",
    "screenshot",
    "debug",
    "statistics",
    "input_system",
    "resource_manager",
    "advanced_particles",
]
