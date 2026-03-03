"""
Visual effects module for Super Mario Bros.

Includes:
- Particle system for brick breaks, coins, explosions
- Parallax scrolling background
- Screen shake effects
- Fade transitions
"""

from __future__ import annotations

from typing import List, Tuple, Optional
import pygame as pg

from . import constants as c


class Particle:
    """
    Single particle for visual effects.

    Attributes:
        x, y: Position
        vx, vy: Velocity
        lifetime: How long the particle lives (ms)
        color: RGB color
        size: Particle size in pixels
        gravity: Gravity effect on particle
        alpha: Transparency (0-255)
    """

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        lifetime: float,
        color: tuple[int, int, int] = c.GOLD,
        size: int = 4,
        gravity: float = 0.5,
        alpha: int = 255,
    ) -> None:
        """Initialize a particle."""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.age: float = 0
        self.color = color
        self.size = size
        self.gravity = gravity
        self.alpha = alpha
        self.initial_alpha = alpha

        # Create surface
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.rect(self.image, (*color, alpha), (0, 0, size, size))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, dt: float, viewport_x: int = 0) -> bool:
        """
        Update particle state.

        Args:
            dt: Delta time in milliseconds
            viewport_x: Camera X offset for culling

        Returns:
            True if particle is still alive
        """
        self.age += dt

        if self.age >= self.lifetime:
            return False

        # Update velocity and position
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

        # Update alpha (fade out)
        life_remaining = 1.0 - (self.age / self.lifetime)
        self.alpha = int(self.initial_alpha * life_remaining)

        # Update rect
        self.rect.centerx = int(self.x) - viewport_x
        self.rect.centery = int(self.y)

        # Recreate surface with new alpha
        self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
        pg.draw.rect(self.image, (*self.color, self.alpha), (0, 0, self.size, self.size))

        return True

    def draw(self, surface: pg.Surface) -> None:
        """Draw particle to surface."""
        surface.blit(self.image, self.rect)


class ParticleSystem:
    """
    Manages multiple particles for visual effects.

    Usage:
        particles = ParticleSystem()
        particles.emit_brick_break(400, 300)
        # In game loop:
        particles.update(dt)
        particles.draw(screen)
    """

    def __init__(self, max_particles: int = 200) -> None:
        """
        Initialize particle system.

        Args:
            max_particles: Maximum number of particles to maintain
        """
        self.max_particles = max_particles
        self.particles: List[Particle] = []

    def emit(
        self,
        x: float,
        y: float,
        count: int,
        vx_range: Tuple[float, float] = (-3, 3),
        vy_range: Tuple[float, float] = (-5, -1),
        lifetime_range: Tuple[int, int] = (300, 600),
        color: tuple[int, int, int] = c.GOLD,
        size_range: Tuple[int, int] = (3, 6),
        gravity: float = 0.5,
    ) -> None:
        """
        Emit particles at position.

        Args:
            x, y: Emission position
            count: Number of particles to emit
            vx_range: Range of X velocities
            vy_range: Range of Y velocities
            lifetime_range: Range of lifetimes (ms)
            color: Base color for particles
            size_range: Range of particle sizes
            gravity: Gravity effect
        """
        import random

        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                # Remove oldest particle if at capacity
                self.particles.pop(0)

            vx = random.uniform(*vx_range)
            vy = random.uniform(*vy_range)
            lifetime = random.randint(*lifetime_range)
            size = random.randint(*size_range)

            # Color variation
            color_var = random.randint(-20, 20)
            particle_color = (
                max(0, min(255, color[0] + color_var)),
                max(0, min(255, color[1] + color_var)),
                max(0, min(255, color[2] + color_var)),
            )

            particle = Particle(x, y, vx, vy, lifetime, color=particle_color, size=size, gravity=gravity)
            self.particles.append(particle)

    def emit_brick_break(self, x: float, y: float) -> None:
        """Emit particles for brick break effect."""
        self.emit(x, y, count=8, color=c.ORANGE, size_range=(4, 8))

    def emit_coin_sparkle(self, x: float, y: float) -> None:
        """Emit particles for coin collection."""
        self.emit(x, y, count=5, color=c.GOLD, vx_range=(-2, 2), vy_range=(-4, -1))

    def emit_stomp(self, x: float, y: float) -> None:
        """Emit particles for enemy stomp."""
        self.emit(x, y, count=6, color=(139, 69, 19), vx_range=(-4, 4), vy_range=(-3, -1))  # Brown

    def emit_fireball_trail(self, x: float, y: float) -> None:
        """Emit particles for fireball trail."""
        self.emit(x, y, count=2, color=c.RED, size_range=(2, 4), lifetime_range=(100, 200))

    def emit_flag_sparkle(self, x: float, y: float) -> None:
        """Emit sparkle for flag pole."""
        self.emit(x, y, count=10, color=c.WHITE, vx_range=(-1, 1), vy_range=(-2, 0), lifetime_range=(400, 800))

    def update(self, dt: float, viewport_x: int = 0) -> None:
        """
        Update all particles.

        Args:
            dt: Delta time in milliseconds
            viewport_x: Camera X offset
        """
        self.particles = [p for p in self.particles if p.update(dt, viewport_x)]

    def draw(self, surface: pg.Surface) -> None:
        """Draw all particles to surface."""
        for particle in self.particles:
            particle.draw(surface)

    def clear(self) -> None:
        """Clear all particles."""
        self.particles.clear()


class ParallaxBackground:
    """
    Parallax scrolling background for depth effect.

    Creates illusion of depth by scrolling background
    layers at different speeds.
    """

    def __init__(self, width: int, height: int, layers: int = 3, scroll_speeds: Optional[List[float]] = None) -> None:
        """
        Initialize parallax background.

        Args:
            width: Background width
            height: Background height
            layers: Number of parallax layers
            scroll_speeds: Speed multiplier for each layer (0-1)
        """
        self.width = width
        self.height = height
        self.layers = layers

        # Default scroll speeds (slower = further away)
        if scroll_speeds is None:
            self.scroll_speeds = [0.1, 0.3, 0.6]
        else:
            self.scroll_speeds = scroll_speeds[:layers]

        # Create layer surfaces
        self.layer_surfaces: List[pg.Surface] = []
        self.layer_positions: List[float] = [0.0] * layers

        self._create_layers()

    def _create_layers(self) -> None:
        """Create background layer surfaces."""
        # In a full implementation, these would load actual images
        # For now, create colored placeholders
        colors = [
            (200, 230, 255),  # Light blue (far)
            (150, 200, 255),  # Medium blue (mid)
            (100, 170, 255),  # Dark blue (near)
        ]

        for i in range(self.layers):
            surface = pg.Surface((self.width * 2, self.height))
            surface.fill(colors[i % len(colors)])

            # Add some simple shapes for visual interest
            if i == 0:
                # Distant clouds/hills
                for x in range(0, self.width * 2, 200):
                    pg.draw.circle(surface, (220, 240, 255), (x + 100, 100 + (i * 30)), 50)
            elif i == 1:
                # Mid-ground elements
                for x in range(0, self.width * 2, 300):
                    pg.draw.rect(surface, (140, 190, 100), (x, 300, 100, 200))

            self.layer_surfaces.append(surface)

    def update(self, camera_x: float) -> None:
        """
        Update layer positions based on camera.

        Args:
            camera_x: Current camera X position
        """
        for i in range(self.layers):
            speed = self.scroll_speeds[i]
            self.layer_positions[i] = -(camera_x * speed) % self.width

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw all background layers.

        Args:
            surface: Surface to draw to
        """
        for i in range(self.layers):
            pos = self.layer_positions[i]
            layer = self.layer_surfaces[i]

            # Draw two copies for seamless scrolling
            surface.blit(layer, (pos, 0))
            surface.blit(layer, (pos + self.width, 0))

            # Handle wrap-around
            if pos < 0:
                surface.blit(layer, (pos + self.width * 2, 0))


class ScreenShake:
    """
    Screen shake effect for impacts and explosions.
    """

    def __init__(self, intensity: float = 10.0, decay: float = 0.9) -> None:
        """
        Initialize screen shake.

        Args:
            intensity: Initial shake intensity (pixels)
            decay: How quickly shake decays (0-1)
        """
        self.intensity = intensity
        self.decay = decay
        self.current_intensity = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def trigger(self, intensity: Optional[float] = None) -> None:
        """
        Trigger screen shake.

        Args:
            intensity: Shake intensity (uses default if None)
        """
        if intensity is not None:
            self.intensity = intensity
        self.current_intensity = self.intensity

    def update(self) -> Tuple[int, int]:
        """
        Update shake state.

        Returns:
            (offset_x, offset_y) for camera
        """
        import random

        if self.current_intensity > 0.5:
            self.offset_x = int(random.uniform(-self.current_intensity, self.current_intensity))
            self.offset_y = int(random.uniform(-self.current_intensity, self.current_intensity))
            self.current_intensity *= self.decay
        else:
            self.current_intensity = 0
            self.offset_x = 0
            self.offset_y = 0

        return (self.offset_x, self.offset_y)

    def is_active(self) -> bool:
        """Check if shake is currently active."""
        return self.current_intensity > 0.5


class FadeTransition:
    """
    Screen fade transition effect.
    """

    def __init__(self) -> None:
        """Initialize fade transition."""
        self.alpha = 0
        self.target_alpha = 0
        self.speed = 10  # Alpha change per frame
        self.color = c.BLACK
        self.surface: Optional[pg.Surface] = None

    def fade_in(self, speed: int = 10) -> None:
        """
        Start fade in effect.

        Args:
            speed: Fade speed
        """
        self.target_alpha = 0
        self.speed = speed
        self.alpha = 255

    def fade_out(self, color: tuple[int, int, int] = c.BLACK, speed: int = 10) -> None:
        """
        Start fade out effect.

        Args:
            color: Fade color
            speed: Fade speed
        """
        self.target_alpha = 255
        self.speed = speed
        self.color = color
        self.alpha = 0

    def update(self) -> bool:
        """
        Update fade state.

        Returns:
            True if fade is complete
        """
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + self.speed)
            return False
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - self.speed)
            return False
        return True

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw fade overlay.

        Args:
            surface: Surface to draw to
        """
        if self.alpha > 0:
            if self.surface is None or self.surface.get_size() != surface.get_size():
                self.surface = pg.Surface(surface.get_size())

            self.surface.fill(self.color)
            self.surface.set_alpha(self.alpha)
            surface.blit(self.surface, (0, 0))


class VisualEffectsManager:
    """
    Central manager for all visual effects.
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize visual effects manager.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.particle_system = ParticleSystem()
        self.parallax = ParallaxBackground(screen_width, screen_height)
        self.screen_shake = ScreenShake()
        self.fade = FadeTransition()

        self.shake_enabled = True
        self.parallax_enabled = True
        self.particles_enabled = True

    def update(self, dt: float, camera_x: float) -> None:
        """
        Update all visual effects.

        Args:
            dt: Delta time in milliseconds
            camera_x: Camera X position
        """
        if self.parallax_enabled:
            self.parallax.update(camera_x)

        if self.particles_enabled:
            self.particle_system.update(dt, int(camera_x))

        if self.shake_enabled:
            self.screen_shake.update()

        self.fade.update()

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw all visual effects.

        Args:
            surface: Surface to draw to
        """
        if self.parallax_enabled:
            self.parallax.draw(surface)

        if self.particles_enabled:
            self.particle_system.draw(surface)

        self.fade.draw(surface)

    def get_camera_offset(self) -> Tuple[int, int]:
        """
        Get current camera offset from screen shake.

        Returns:
            (offset_x, offset_y)
        """
        if self.shake_enabled:
            return self.screen_shake.update()
        return (0, 0)

    # Convenience methods
    def brick_break(self, x: float, y: float) -> None:
        """Trigger brick break effect."""
        if self.particles_enabled:
            self.particle_system.emit_brick_break(x, y)

    def coin_collect(self, x: float, y: float) -> None:
        """Trigger coin collection effect."""
        if self.particles_enabled:
            self.particle_system.emit_coin_sparkle(x, y)

    def enemy_stomp(self, x: float, y: float) -> None:
        """Trigger enemy stomp effect."""
        if self.particles_enabled:
            self.particle_system.emit_stomp(x, y)
        if self.shake_enabled:
            self.screen_shake.trigger(5.0)

    def fireball_trail(self, x: float, y: float) -> None:
        """Trigger fireball trail effect."""
        if self.particles_enabled:
            self.particle_system.emit_fireball_trail(x, y)

    def flag_sparkle(self, x: float, y: float) -> None:
        """Trigger flag pole sparkle."""
        if self.particles_enabled:
            self.particle_system.emit_flag_sparkle(x, y)
