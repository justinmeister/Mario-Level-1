"""Item, enemy, and game constants."""

from __future__ import annotations

# =============================================================================
# BRICK AND COIN BOX CONTENTS
# =============================================================================
MUSHROOM: str = "mushroom"
STAR: str = "star"
FIREFLOWER: str = "fireflower"
SIXCOINS: str = "6coins"
COIN: str = "coin"
LIFE_MUSHROOM: str = "1up_mushroom"
FIREBALL: str = "fireball"

# =============================================================================
# ENEMY TYPES
# =============================================================================
GOOMBA: str = "goomba"
KOOPA: str = "koopa"

# =============================================================================
# GAME INFO DICTIONARY KEYS
# =============================================================================
COIN_TOTAL: str = "coin total"
SCORE: str = "score"
TOP_SCORE: str = "top score"
LIVES: str = "lives"
CURRENT_TIME: str = "current time"
LEVEL_STATE: str = "level state"
CAMERA_START_X: str = "camera start x"
MARIO_DEAD: str = "mario dead"
CURRENT_LEVEL: str = "current_level"

# =============================================================================
# SCORE VALUES
# =============================================================================
ONEUP: str = "379"  # 1UP score display value
SCORE_GOOMBA_STOMP: int = 100
SCORE_KOOPA_STOMP: int = 100
SCORE_STAR: int = 1000
SCORE_MUSHROOM: int = 1000
SCORE_1UP: int = 100
SCORE_FLAG_POLE_LOW: int = 100
SCORE_FLAG_POLE_MID: int = 400
SCORE_FLAG_POLE_HIGH: int = 800
SCORE_FLAG_POLE_HIGHER: int = 2000
SCORE_FLAG_POLE_TOP: int = 5000

# =============================================================================
# TIMING CONSTANTS (milliseconds)
# =============================================================================
ENEMY_ANIMATION_INTERVAL: int = 125  # Enemy frame switch timing
GOOMBA_DEATH_DELAY: int = 500  # Delay before goomba disappears after being stomped
FIREBALL_INTERVAL: int = 200  # Minimum time between fireball shots
INVINCIBLE_DURATION: int = 2000  # Duration of star power invincibility
HURT_INVINCIBLE_DURATION: int = 1000  # Duration of invincibility after getting hurt
FLAG_SLIDE_DURATION: int = 1000  # Duration of flag slide animation
LEVEL_TIME: int = 400  # Level time limit (in seconds)
