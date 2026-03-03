"""Extended constants to replace magic numbers throughout the codebase."""

from __future__ import annotations

# Animation timing constants (milliseconds)
ANIMATION_FAST = 125
ANIMATION_NORMAL = 200
ANIMATION_SLOW = 375
ANIMATION_VERY_SLOW = 500

# Collision detection constants
COLLISION_TOLERANCE = 2  # pixels
MAX_COLLISION_CHECKS_PER_FRAME = 10

# Enemy spawn constants
ENEMY_SPAWN_OFFSET = 60  # pixels between enemies
ENEMY_ACTIVATION_DISTANCE = 800  # pixels from viewport

# Score values
SCORE_COIN = 200
SCORE_ENEMY_STOMP = 100
SCORE_MUSHROOM = 1000
SCORE_STAR = 1000
SCORE_FIREFLOWER = 1000
SCORE_FLAG_POLE_TOP = 5000
SCORE_FLAG_POLE_HIGH = 2000
SCORE_FLAG_POLE_MID = 800
SCORE_FLAG_POLE_LOW = 400

# Time constants
TIME_WARNING_THRESHOLD = 100  # seconds
TIME_HURRY_MUSIC_THRESHOLD = 100  # seconds

# Physics constants
GRAVITY_NORMAL = 1.5
GRAVITY_UNDERWATER = 0.5
FRICTION_GROUND = 0.8
FRICTION_ICE = 0.95
FRICTION_AIR = 0.98

# Mario state transition timings
INVINCIBILITY_DURATION = 10000  # milliseconds
HURT_INVINCIBILITY_DURATION = 2000  # milliseconds
STAR_POWER_DURATION = 10000  # milliseconds
TRANSITION_ANIMATION_SPEED = 65  # milliseconds per frame

# Fireball constants
FIREBALL_COOLDOWN = 200  # milliseconds
MAX_FIREBALLS = 2

# Level boundaries
LEVEL_BOTTOM_DEATH = 600  # y-coordinate for death
LEVEL_TOP_BOUNDARY = -100  # y-coordinate for top

# Viewport constants
VIEWPORT_SCROLL_SPEED = 5  # pixels per frame
VIEWPORT_FORWARD_OFFSET = 300  # pixels ahead of Mario

# Audio constants
MUSIC_FADE_IN_MS = 1000
MUSIC_FADE_OUT_MS = 500
MUSIC_SWITCH_FADE_MS = 500
SFX_VOLUME_DEFAULT = 0.8
MUSIC_VOLUME_DEFAULT = 0.7

# Performance constants
SPRITE_CULL_DISTANCE = 1000  # pixels off-screen before culling
MAX_PARTICLES = 50
PARTICLE_LIFETIME = 2000  # milliseconds

# Checkpoint names
CHECKPOINT_ENEMY_SPAWN = "enemy_spawn"
CHECKPOINT_FLAG_POLE = "11"
CHECKPOINT_CASTLE_ENTRY = "12"
CHECKPOINT_SECRET_MUSHROOM = "secret_mushroom"

# Enemy types
ENEMY_GOOMBA = "goomba"
ENEMY_KOOPA = "koopa"
ENEMY_FLY_KOOPA = "fly_koopa"
ENEMY_PIRANHA = "piranha"
ENEMY_FIRE_KOOPA = "fire_koopa"

# Powerup types
POWERUP_MUSHROOM = "mushroom"
POWERUP_FIREFLOWER = "fireflower"
POWERUP_STAR = "star"
POWERUP_1UP = "1up_mushroom"

# Brick contents
BRICK_COIN = "coin"
BRICK_MUSHROOM = "mushroom"
BRICK_STAR = "star"
BRICK_FIREFLOWER = "fireflower"
BRICK_1UP = "1up_mushroom"
BRICK_6COINS = "6coins"

# Level types
LEVEL_TYPE_OVERWORLD = "overworld"
LEVEL_TYPE_UNDERGROUND = "underground"
LEVEL_TYPE_UNDERWATER = "underwater"
LEVEL_TYPE_CASTLE = "castle"

# Music track names
MUSIC_MAIN_THEME = "main_theme"
MUSIC_UNDERGROUND = "underground"
MUSIC_UNDERWATER = "underwater"
MUSIC_CASTLE = "castle"
MUSIC_STAR_POWER = "star_power"
MUSIC_ENDING = "ending"

# Sound effect names
SFX_COIN = "coin_new"
SFX_PIPE = "pipe_new"
SFX_TIME_WARNING = "time_warning"
SFX_STAGE_CLEAR = "stage_clear"
SFX_LEVEL_COMPLETE = "level_complete"
SFX_WORLD_CLEAR = "world_clear"
SFX_CASTLE_COMPLETE = "castle_complete"
SFX_BOSS_DEFEAT = "boss_defeat"
SFX_GAME_OVER = "game_over_new"
