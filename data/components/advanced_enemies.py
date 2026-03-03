"""
Advanced Enemies for Super Mario Bros.

New enemy types:
- Piranha Plant
- Bullet Bill
- Hammer Bro
- Buzzy Beetle
"""

from __future__ import annotations

from typing import Any, Optional
import pygame as pg

from data import setup
from data import constants as c
from .enemies import Enemy


class PiranhaPlant(Enemy):
    """
    Piranha Plant enemy.

    Behaviors:
    - Emerges from pipe periodically
    - Bites when Mario is near
    - Vulnerable only when fully emerged
    """

    EMERGE_TIME = 2000  # ms to fully emerge
    STAY_TIME = 1500  # ms to stay out
    RETRACT_TIME = 2000  # ms to retract
    WAIT_TIME = 3000  # ms to wait before emerging again

    def __init__(self, x: int = 0, y: int = 0, name: str = "piranha_plant") -> None:
        Enemy.__init__(self)
        self.sprite_sheet = setup.GFX["smb_enemies_sheet"]

        self.name = name
        self.start_x = x
        self.start_y = y
        self.direction = c.UP

        self.setup_frames()

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        self.state = c.HIDDEN
        self.emerge_timer: float = 0
        self.action_timer: float = 0
        self.y_vel: float = 0
        self.gravity: float = 0

        # Movement
        self.emerge_speed: float = 2
        self.base_y = y
        self.emerged_y = y - 100  # How far to emerge

    def setup_frames(self) -> None:
        """Setup animation frames."""
        # Frame 0: Hidden/closed
        self.frames.append(self.get_image(128, 21, 16, 23))
        # Frame 1: Emerging
        self.frames.append(self.get_image(128, 0, 16, 23))
        # Frame 2: Fully emerged (open)
        self.frames.append(self.get_image(160, 0, 16, 23))
        # Frame 3: Closing
        self.frames.append(self.get_image(160, 21, 16, 23))

    def update(self, game_info: dict, *args: Any) -> None:
        """Update piranha plant behavior."""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()
        self.animation()

    def handle_state(self) -> None:
        """Handle different states."""
        if self.state == c.HIDDEN:
            self.hidden()
        elif self.state == c.EMERGING:
            self.emerging()
        elif self.state == c.EMERGED:
            self.emerged()
        elif self.state == c.RETRACTING:
            self.retracting()

    def hidden(self) -> None:
        """Hidden state - wait before emerging."""
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        # Check if should emerge
        if (self.current_time - self.action_timer) > self.WAIT_TIME:
            self.state = c.EMERGING
            self.action_timer = self.current_time

    def emerging(self) -> None:
        """Emerging from pipe."""
        elapsed = self.current_time - self.action_timer

        if elapsed < self.EMERGE_TIME:
            # Move up
            progress = elapsed / self.EMERGE_TIME
            self.rect.y = self.base_y - (progress * 100)

            if progress < 0.5:
                self.frame_index = 1
            else:
                self.frame_index = 2
        else:
            self.rect.y = self.emerged_y
            self.state = c.EMERGED
            self.action_timer = self.current_time

    def emerged(self) -> None:
        """Fully emerged - vulnerable."""
        self.frame_index = 2
        self.image = self.frames[self.frame_index]

        # Check if should retract
        if (self.current_time - self.action_timer) > self.STAY_TIME:
            self.state = c.RETRACTING
            self.action_timer = self.current_time

    def retracting(self) -> None:
        """Retracting into pipe."""
        elapsed = self.current_time - self.action_timer

        if elapsed < self.RETRACT_TIME:
            # Move down
            progress = elapsed / self.RETRACT_TIME
            self.rect.y = self.emerged_y + (progress * 100)

            if progress < 0.5:
                self.frame_index = 2
            else:
                self.frame_index = 3
        else:
            self.rect.y = self.base_y
            self.state = c.HIDDEN
            self.action_timer = self.current_time

    def start_emerging(self) -> None:
        """Start the emerge cycle."""
        self.state = c.EMERGING
        self.action_timer = self.current_time

    def jumped_on(self) -> None:
        """Can only be killed when fully emerged."""
        if self.state == c.EMERGED:
            self.start_death_jump(c.RIGHT)


class BulletBill(Enemy):
    """
    Bullet Bill enemy.

    Behaviors:
    - Flies horizontally at high speed
    - Spawned from Bill Blaster
    - Disappears after distance or time
    """

    MAX_DISTANCE = 800  # pixels before disappearing
    LIFETIME = 5000  # ms lifetime
    SPEED = 6  # pixels per frame

    def __init__(self, x: int = 0, y: int = 0, direction: str = c.LEFT, name: str = "bullet_bill") -> None:
        Enemy.__init__(self)
        self.sprite_sheet = setup.GFX["smb_enemies_sheet"]

        self.name = name
        self.direction = direction
        self.start_x = x
        self.start_y = y
        self.traveled_distance = 0

        self.setup_frames()

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        self.spawn_time: float = 0
        self.gravity: float = 0.3

    def setup_frames(self) -> None:
        """Setup animation frames."""
        # Frame 0: Normal
        self.frames.append(self.get_image(320, 0, 16, 16))
        # Frame 1: Animation frame
        self.frames.append(self.get_image(336, 0, 16, 16))
        # Frame 2: Death
        self.frames.append(self.get_image(352, 0, 16, 16))

    def update(self, game_info: dict, *args: Any) -> None:
        """Update bullet bill."""
        self.current_time = game_info[c.CURRENT_TIME]

        if self.spawn_time == 0:
            self.spawn_time = self.current_time

        self.handle_state()
        self.animation()

        # Check lifetime
        if (self.current_time - self.spawn_time) > self.LIFETIME:
            self.kill()

        # Check distance
        if self.traveled_distance > self.MAX_DISTANCE:
            self.kill()

    def handle_state(self) -> None:
        """Handle bullet bill state."""
        if self.state == c.WALK:
            self.flying()
        elif self.state == c.DEATH_JUMP:
            self.death_jumping()

    def flying(self) -> None:
        """Flying horizontally."""
        # Move in direction
        if self.direction == c.LEFT:
            self.rect.x -= self.SPEED
            self.x_vel = -self.SPEED
        else:
            self.rect.x += self.SPEED
            self.x_vel = self.SPEED

        self.traveled_distance += self.SPEED

        # Slight gravity
        self.y_vel += self.gravity
        self.rect.y += self.y_vel

        # Animation
        if (self.current_time - self.animate_timer) > 100:
            self.frame_index = (self.frame_index + 1) % 2
            self.animate_timer = self.current_time

    def start_death_jump(self, direction: str) -> None:
        """Death animation."""
        self.y_vel = -5
        self.x_vel = 0
        self.frame_index = 2
        self.image = self.frames[self.frame_index]
        self.state = c.DEATH_JUMP
        self.gravity = 0.5


class HammerBro(Enemy):
    """
    Hammer Bro enemy.

    Behaviors:
    - Jumps periodically
    - Throws hammers at Mario
    - More aggressive when Mario is near
    """

    JUMP_INTERVAL = 2000  # ms between jumps
    HAMMER_INTERVAL = 1500  # ms between hammer throws

    def __init__(self, x: int = 0, y: int = 0, name: str = "hammer_bro") -> None:
        Enemy.__init__(self)
        self.sprite_sheet = setup.GFX["smb_enemies_sheet"]

        self.name = name
        self.direction = c.LEFT

        self.setup_frames()

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        self.start_y = y
        self.y_vel = 0
        self.jump_timer: float = 0
        self.hammer_timer: float = 0
        self.jump_vel: float = 0
        self.on_ground: bool = True

        # Reference to hammer group for spawning
        self.hammer_group: Optional[pg.sprite.Group] = None

    def setup_frames(self) -> None:
        """Setup animation frames."""
        # Frame 0: Standing
        self.frames.append(self.get_image(0, 32, 16, 24))
        # Frame 1: Walking 1
        self.frames.append(self.get_image(16, 32, 16, 24))
        # Frame 2: Walking 2
        self.frames.append(self.get_image(32, 32, 16, 24))
        # Frame 3: Jumping
        self.frames.append(self.get_image(48, 32, 16, 24))
        # Frame 4: Throwing
        self.frames.append(self.get_image(64, 32, 16, 24))

    def update(self, game_info: dict, mario: Any = None, *args: Any) -> None:
        """Update hammer bro."""
        self.current_time = game_info[c.CURRENT_TIME]
        self.mario = mario

        self.handle_state()
        self.animation()

        # Apply gravity
        if not self.on_ground:
            self.y_vel += self.gravity
            self.rect.y += self.y_vel

            if self.rect.bottom >= self.start_y:
                self.rect.bottom = self.start_y
                self.on_ground = True
                self.y_vel = 0

    def handle_state(self) -> None:
        """Handle hammer bro states."""
        if self.state == c.WALK:
            self.walking()
        elif self.state == c.JUMP:
            self.jumping()

    def walking(self) -> None:
        """Walking behavior."""
        # Move slowly
        if self.direction == c.LEFT:
            self.x_vel = -1
        else:
            self.x_vel = 1

        self.rect.x += self.x_vel

        # Check for jump
        if (self.current_time - self.jump_timer) > self.JUMP_INTERVAL:
            self.jump()

        # Check for hammer throw
        if (self.current_time - self.hammer_timer) > self.HAMMER_INTERVAL:
            self.throw_hammer()

        # Animation
        if (self.current_time - self.animate_timer) > 200:
            self.frame_index = (self.frame_index + 1) % 2 + 1  # Frames 1-2
            self.animate_timer = self.current_time

    def jumping(self) -> None:
        """Jumping behavior."""
        self.frame_index = 3

    def jump(self) -> None:
        """Perform a jump."""
        if self.on_ground:
            self.y_vel = -8
            self.on_ground = False
            self.state = c.JUMP

            # Jump towards Mario if nearby
            if self.mario and hasattr(self.mario, "rect"):
                if self.mario.rect.x < self.rect.x:
                    self.x_vel = -2
                else:
                    self.x_vel = 2

            self.jump_timer = self.current_time

    def throw_hammer(self) -> None:
        """Throw a hammer."""
        if self.hammer_group is not None:
            from .powerups import Hammer

            direction = c.LEFT if self.mario and self.mario.rect.x < self.rect.x else c.RIGHT

            hammer = Hammer(self.rect.centerx, self.rect.y, direction)
            self.hammer_group.add(hammer)

        self.frame_index = 4
        self.hammer_timer = self.current_time


class BuzzyBeetle(Enemy):
    """
    Buzzy Beetle enemy.

    Behaviors:
    - Immune to fireballs
    - Can be stomped
    - Slides in shell when stomped
    """

    def __init__(self, x: int = 0, y: int = 0, direction: str = c.LEFT, name: str = "buzzy_beetle") -> None:
        Enemy.__init__(self)
        self.sprite_sheet = setup.GFX["smb_enemies_sheet"]

        self.name = name
        self.direction = direction

        self.setup_frames()

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

        self.fire_immunity: bool = True

    def setup_frames(self) -> None:
        """Setup animation frames."""
        # Frame 0: Walking
        self.frames.append(self.get_image(192, 0, 16, 16))
        # Frame 1: Walking 2
        self.frames.append(self.get_image(208, 0, 16, 16))
        # Frame 2: In shell
        self.frames.append(self.get_image(224, 0, 16, 16))
        # Frame 3: Shell sliding
        self.frames.append(self.get_image(240, 0, 16, 16))

    def update(self, game_info: dict, *args: Any) -> None:
        """Update buzzy beetle."""
        self.current_time = game_info[c.CURRENT_TIME]
        self.handle_state()
        self.animation()

    def jumped_on(self) -> None:
        """Stomped - goes into shell."""
        self.x_vel = 0
        self.frame_index = 2
        shell_y = self.rect.bottom
        shell_x = self.rect.x
        self.rect = self.frames[self.frame_index].get_rect()
        self.rect.x = shell_x
        self.rect.bottom = shell_y

        # Start shell slide after delay
        self.state = c.SHELL_SLIDE
        self.shell_sliding()

    def shell_sliding(self) -> None:
        """Sliding in shell at high speed."""
        if self.direction == c.RIGHT:
            self.x_vel = 12
        else:
            self.x_vel = -12


# Enemy factory function
def create_enemy(enemy_type: str, x: int, y: int, direction: str = c.LEFT, **kwargs: Any) -> Enemy:
    """
    Factory function to create enemies.

    Args:
        enemy_type: Type of enemy ("goomba", "koopa", "piranha", "bullet", "hammer", "buzzy")
        x: X position
        y: Y position
        direction: Initial direction
        **kwargs: Additional arguments

    Returns:
        Enemy instance
    """
    enemies = {
        "goomba": lambda: setup_enemy_instance("Goomba", y, x, direction),
        "koopa": lambda: setup_enemy_instance("Koopa", y, x, direction),
        "piranha": lambda: PiranhaPlant(x, y),
        "bullet": lambda: BulletBill(x, y, direction),
        "hammer": lambda: HammerBro(x, y),
        "buzzy": lambda: BuzzyBeetle(x, y, direction),
    }

    if enemy_type.lower() in enemies:
        return enemies[enemy_type.lower()]()
    else:
        raise ValueError(f"Unknown enemy type: {enemy_type}")


def setup_enemy_instance(cls_name: str, y: int, x: int, direction: str) -> Enemy:
    """Helper to create classic enemies."""
    from .enemies import Goomba, Koopa

    if cls_name == "Goomba":
        return Goomba(y, x, direction)
    elif cls_name == "Koopa":
        return Koopa(y, x, direction)
    else:
        raise ValueError(f"Unknown enemy class: {cls_name}")
