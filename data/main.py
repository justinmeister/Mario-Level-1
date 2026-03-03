"""
Main game initialization and startup module.

This module handles the initialization of the game and sets up
the initial game states.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict

import pygame as pg

from . import constants as c
from . import setup, tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    """
    Main entry point for the game.

    Initializes pygame, sets up game states, and starts the game loop.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        logger.info("Initializing Super Mario Bros Level 1")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Pygame version: {pg.ver}")

        # Initialize display first
        setup.initialize_display()
        logger.info("Display initialized")

        # Load resources
        setup.load_resources()
        logger.info(f"Loaded {len(setup.GFX)} graphics, {len(setup.SFX)} sounds")

        # Initialize game controller
        run_it = tools.Control(setup.ORIGINAL_CAPTION)
        logger.info("Controller created")

        # Define game states
        state_dict: Dict[str, Any] = {
            c.MAIN_MENU: setup.create_main_menu(),
            c.LEVEL_SELECT: setup.create_level_select(),
            c.SETTINGS: setup.create_settings(),
            c.LOAD_SCREEN: setup.create_load_screen(),
            c.TIME_OUT: setup.create_timeout_screen(),
            c.GAME_OVER: setup.create_game_over(),
            c.LEVEL1: setup.create_level1(),
            c.LEVEL2: setup.create_level2(),
            c.LEVEL3: setup.create_level3(),
            c.LEVEL4: setup.create_level4(),
            c.LEVEL5: setup.create_level5(),
            c.LEVEL6: setup.create_level6(),
            c.LEVEL7: setup.create_level7(),
            c.LEVEL8: setup.create_level8(),
        }

        # Validate states
        for state_name, state in state_dict.items():
            if state is None:
                logger.error(f"Failed to create state: {state_name}")
                return 1
            logger.debug(f"Created state: {state_name}")

        # Setup and run
        run_it.setup_states(state_dict, c.MAIN_MENU)
        logger.info("Starting game loop")
        run_it.main()

        logger.info("Game exited normally")
        return 0

    except pg.error as e:
        logger.error("Pygame error: %s", e, exc_info=True)
        logger.error("Pygame failed")
        return 2

    except FileNotFoundError as e:
        logger.error("Missing game file: %s", e, exc_info=True)
        logger.error("Missing game file. Please ensure all resources are installed correctly.")
        return 3

    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        return 4

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 5

    finally:
        # Cleanup
        try:
            pg.quit()
        except Exception as e:
            logger.warning(f"Error during pygame cleanup: {e}")
