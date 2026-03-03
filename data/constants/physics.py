"""Physics and movement constants."""

from __future__ import annotations

# =============================================================================
# MARIO PHYSICS & MOVEMENT
# =============================================================================
# Acceleration values
WALK_ACCEL: float = 0.15
RUN_ACCEL: float = 20.0
SMALL_TURNAROUND: float = 0.35

# Gravity and jumping
GRAVITY: float = 1.01
JUMP_GRAVITY: float = 0.31
JUMP_VEL: float = -10.0
FAST_JUMP_VEL: float = -12.5
MAX_Y_VEL: float = 11.0

# Maximum speeds (pixels per frame)
MAX_RUN_SPEED: float = 800.0
MAX_WALK_SPEED: float = 6.0

# =============================================================================
# SCALE MULTIPLIERS
# Used to scale up sprites from their original pixel art size
# =============================================================================
SIZE_MULTIPLIER: float = 2.5
BRICK_SIZE_MULTIPLIER: float = 2.69
BACKGROUND_MULTIPLIER: float = 2.679
