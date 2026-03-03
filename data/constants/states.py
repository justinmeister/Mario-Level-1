"""State string constants for game entities."""

from __future__ import annotations

# =============================================================================
# MARIO STATES
# String constants for Mario's animation/behavior state machine
# =============================================================================
STAND: str = "standing"
WALK: str = "walk"
JUMP: str = "jump"
FALL: str = "fall"
UP: str = "up"
DOWN: str = "down"
SMALL_TO_BIG: str = "small to big"
BIG_TO_FIRE: str = "big to fire"
BIG_TO_SMALL: str = "big to small"
FLAGPOLE: str = "flag pole"
WALKING_TO_CASTLE: str = "walking to castle"
END_OF_LEVEL_FALL: str = "end of level fall"
DEATH_JUMP: str = "death jump"
BOTTOM_OF_POLE: str = "bottom of pole"

# =============================================================================
# ENEMY STATES (GOOMBA)
# =============================================================================
LEFT: str = "left"
RIGHT: str = "right"
JUMPED_ON: str = "jumped on"
ENEMY_DEATH_JUMP: str = "death jump"
HIDDEN: str = "hidden"
EMERGING: str = "emerging"
EMERGED: str = "emerged"
RETRACTING: str = "retracting"

# =============================================================================
# KOOPA STATES
# =============================================================================
SHELL_SLIDE: str = "shell slide"

# =============================================================================
# BRICK STATES
# =============================================================================
RESTING: str = "resting"
BUMPED: str = "bumped"

# =============================================================================
# COIN STATES
# =============================================================================
OPENED: str = "opened"
SPIN: str = "spin"

# =============================================================================
# MUSHROOM STATES
# =============================================================================
REVEAL: str = "reveal"
SLIDE: str = "slide"

# =============================================================================
# STAR STATES
# =============================================================================
BOUNCE: str = "bounce"

# =============================================================================
# FIRE STATES
# =============================================================================
FLYING: str = "flying"
BOUNCING: str = "bouncing"
EXPLODING: str = "exploding"
THROWN: str = "thrown"

# =============================================================================
# LEVEL STATES
# =============================================================================
FROZEN: str = "frozen"
NOT_FROZEN: str = "not frozen"
IN_CASTLE: str = "in castle"
FLAG_AND_FIREWORKS: str = "flag and fireworks"

# =============================================================================
# FLAG STATES
# =============================================================================
TOP_OF_POLE: str = "top of pole"
SLIDE_DOWN: str = "slide down"
FLAG_BOTTOM_OF_POLE: str = "bottom of pole"

# =============================================================================
# MAIN MENU STATES
# =============================================================================
PLAYER1: str = "1 player"
PLAYER2: str = "2 player"
LEVEL_SELECT: str = "level select"
SETTINGS: str = "settings"

# =============================================================================
# OVERHEAD INFO STATES
# =============================================================================
MAIN_MENU: str = "main menu"
LOAD_SCREEN: str = "loading screen"
LEVEL: str = "level"
GAME_OVER: str = "game over"
FAST_COUNT_DOWN: str = "fast count down"
END_OF_LEVEL: str = "end of level"

# =============================================================================
# GLOBAL GAME STATES
# States for the entire game state machine
# =============================================================================
MAIN_MENU_STATE: str = "main menu"
LOAD_SCREEN_STATE: str = "load screen"
TIME_OUT: str = "time out"
GAME_OVER_STATE: str = "game over"
LEVEL1: str = "level1"
LEVEL2: str = "level2"
LEVEL3: str = "level3"
LEVEL4: str = "level4"
LEVEL5: str = "level5"
LEVEL6: str = "level6"
LEVEL7: str = "level7"
LEVEL8: str = "level8"

# =============================================================================
# SOUND STATES
# =============================================================================
NORMAL: str = "normal"
STAGE_CLEAR: str = "stage clear"
WORLD_CLEAR: str = "world clear"
TIME_WARNING: str = "time warning"
SPED_UP_NORMAL: str = "sped up normal"
MARIO_INVINCIBLE: str = "mario invincible"
