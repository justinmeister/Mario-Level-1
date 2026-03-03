"""
Enhanced Particle Effects for Super Mario Bros.

New particle types:
- Fire particles
- Smoke trails
- Spark particles
- Magic effects
- Weather particles
- Explosion debris
- Energy orbs
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

import pygame as pg


class ParticleShape(Enum):
    """Particle shapes."""

    CIRCLE = auto()
    SQUARE = auto()
    TRIANGLE = auto()
    STAR = auto()
    RING = auto()
    SPARK = auto()


class ParticleBehavior(Enum):
    """Particle behaviors."""

    NORMAL = auto()
    GRAVITY = auto()
    FLOAT = auto()
    ORBIT = auto()
    SPIRAL = auto()
    HOMING = auto()
    EXPLODE = auto()
    FADE_OUT = auto()
    PULSE = auto()
    WAVE = auto()


@dataclass
class ParticleConfig:
    """Particle configuration."""

    # Visual
    color: Tuple[int, int, int] = (255, 255, 255)
    color_end: Optional[Tuple[int, int, int]] = None  # Gradient end color
    shape: ParticleShape = ParticleShape.CIRCLE
    size: float = 5.0
    size_end: float = 0.0

    # Lifetime
    lifetime: float = 1.0  # seconds
    fade_in: float = 0.0
    fade_out: float = 0.0

    # Motion
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0)
    drag: float = 0.0
    gravity: float = 0.0

    # Behavior
    behavior: ParticleBehavior = ParticleBehavior.NORMAL
    behavior_params: Dict[str, Any] = field(default_factory=dict)

    # Rotation
    rotation: float = 0.0
    rotation_speed: float = 0.0

    # Alpha
    alpha: int = 255
    alpha_end: int = 0


class EnhancedParticle:
    """
    Enhanced particle with advanced features.

    Features:
    - Color gradients
    - Multiple shapes
    - Behaviors
    - Rotation
    - Size changes
    - Surface caching for performance
    """

    # Class-level cache for particle surfaces
    _surface_cache: Dict[Tuple[ParticleShape, int, Tuple[int, int, int], int], pg.Surface] = {}
    _cache_max_size = 500  # Maximum cached surfaces

    def __init__(self, x: float, y: float, config: Optional[ParticleConfig] = None) -> None:
        """
        Initialize particle.

        Args:
            x, y: Starting position
            config: Particle configuration
        """
        self.x = x
        self.y = y
        self.config = config or ParticleConfig()

        # State
        self.age: float = 0.0
        self.alive: bool = True
        self.current_size = self.config.size
        self.current_alpha = self.config.alpha
        self.current_color = self.config.color
        self.rotation = self.config.rotation

        # Velocity with slight randomization
        vx, vy = self.config.velocity
        self.vx = vx + random.uniform(-0.5, 0.5)
        self.vy = vy + random.uniform(-0.5, 0.5)

        # Pre-compute
        self._lifetime = self.config.lifetime
        self._color_delta: Optional[Tuple[float, ...]] = None
        if self.config.color_end:
            self._color_delta = tuple(
                (self.config.color_end[i] - self.config.color[i]) / self._lifetime for i in range(3)
            )

        # Cached surface
        self._cached_surface: Optional[pg.Surface] = None
        self._cache_key: Optional[Tuple] = None

    def update(self, dt: float, target: Optional[Tuple[float, float]] = None) -> None:
        """
        Update particle.

        Args:
            dt: Delta time in seconds
            target: Target position for homing behavior
        """
        if not self.alive:
            return

        self.age += dt

        # Check lifetime
        if self.age >= self._lifetime:
            self.alive = False
            return

        # Apply behavior
        self._apply_behavior(dt, target)

        # Apply physics
        self.vx += self.config.acceleration[0] * dt
        self.vy += self.config.acceleration[1] * dt
        self.vy += self.config.gravity * dt

        # Apply drag
        drag_factor = 1.0 - self.config.drag * dt
        self.vx *= drag_factor
        self.vy *= drag_factor

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Update rotation
        self.rotation += self.config.rotation_speed * dt

        # Update size
        progress = self.age / self._lifetime
        self.current_size = self.config.size + (self.config.size_end - self.config.size) * progress

        # Update alpha
        alpha_progress = self._get_alpha_progress(progress)
        self.current_alpha = int(self.config.alpha + (self.config.alpha_end - self.config.alpha) * alpha_progress)

        # Update color
        if self._color_delta:
            self.current_color = tuple(
                int(self.config.color[i] + self._color_delta[i] * self.age) for i in range(3)  # type: ignore
            )

    def _apply_behavior(self, dt: float, target: Optional[Tuple[float, float]] = None) -> None:
        """Apply particle behavior."""
        behavior = self.config.behavior
        params = self.config.behavior_params

        if behavior == ParticleBehavior.GRAVITY:
            self.vy += params.get("gravity", 9.8) * dt

        elif behavior == ParticleBehavior.FLOAT:
            self.vy += math.sin(self.age * params.get("frequency", 2)) * params.get("amplitude", 50) * dt

        elif behavior == ParticleBehavior.ORBIT:
            orbit_speed = params.get("speed", 2)
            orbit_radius = params.get("radius", 50)
            center = params.get("center", (self.x, self.y))
            angle = self.age * orbit_speed
            self.x = center[0] + math.cos(angle) * orbit_radius
            self.y = center[1] + math.sin(angle) * orbit_radius

        elif behavior == ParticleBehavior.SPIRAL:
            spiral_speed = params.get("speed", 3)
            radius_growth = params.get("radius_growth", 10)
            angle = self.age * spiral_speed
            radius = params.get("start_radius", 10) + radius_growth * self.age
            self.x += math.cos(angle) * radius * dt
            self.y += math.sin(angle) * radius * dt

        elif behavior == ParticleBehavior.HOMING and target:
            homing_speed = params.get("speed", 100)
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.vx += (dx / dist) * homing_speed * dt
                self.vy += (dy / dist) * homing_speed * dt

        elif behavior == ParticleBehavior.EXPLODE:
            explode_speed = params.get("speed", 200)
            angle = params.get("angle", random.uniform(0, math.pi * 2))
            self.vx = math.cos(angle) * explode_speed
            self.vy = math.sin(angle) * explode_speed

        elif behavior == ParticleBehavior.WAVE:
            wave_speed = params.get("speed", 5)
            wave_amplitude = params.get("amplitude", 20)
            self.x += math.sin(self.age * wave_speed) * wave_amplitude * dt

    def _get_alpha_progress(self, progress: float) -> float:
        """Get alpha progress with fade in/out."""
        fade_in = self.config.fade_in
        fade_out = self.config.fade_out

        if fade_in > 0 and progress < fade_in:
            return progress / fade_in
        elif fade_out > 0 and progress > 1 - fade_out:
            return 1 - (progress - (1 - fade_out)) / fade_out
        else:
            return progress

    def draw(self, surface: pg.Surface, offset: Tuple[float, float] = (0, 0)) -> None:
        """
        Draw particle.

        Args:
            surface: Surface to draw on
            offset: Camera offset
        """
        if not self.alive or self.current_size <= 0:
            return

        x = int(self.x - offset[0])
        y = int(self.y - offset[1])
        size = max(1, int(self.current_size))

        # Limit size for performance
        if size > 100:
            size = 100

        # Create cache key
        color_tuple = (int(self.current_color[0]), int(self.current_color[1]), int(self.current_color[2]))
        cache_key = (
            self.config.shape,
            size,
            color_tuple,
            self.current_alpha,
        )

        # Get or create cached surface
        if cache_key not in self._surface_cache:
            # Clear cache if too large
            if len(self._surface_cache) >= self._cache_max_size:
                # Remove oldest 20%
                keys_to_remove = list(self._surface_cache.keys())[:100]
                for key in keys_to_remove:
                    del self._surface_cache[key]

            # Create new surface
            particle_surface = self._create_particle_surface(size)
            self._surface_cache[cache_key] = particle_surface
        else:
            particle_surface = self._surface_cache[cache_key]

        # Rotate if needed
        if self.config.rotation_speed != 0:
            rotated = pg.transform.rotate(particle_surface, self.rotation)
            rect = rotated.get_rect(center=(x + size, y + size))
            surface.blit(rotated, rect)
        else:
            surface.blit(particle_surface, (x - size, y - size))

    def _create_particle_surface(self, size: int) -> pg.Surface:
        """
        Create particle surface.

        Args:
            size: Particle size

        Returns:
            Particle surface
        """
        particle_surface = pg.Surface((size * 2, size * 2), pg.SRCALPHA)
        color_with_alpha = (*self.current_color, self.current_alpha)
        shape = self.config.shape

        if shape == ParticleShape.CIRCLE:
            pg.draw.circle(particle_surface, color_with_alpha, (size, size), size)

        elif shape == ParticleShape.SQUARE:
            pg.draw.rect(particle_surface, color_with_alpha, (0, 0, size * 2, size * 2))

        elif shape == ParticleShape.TRIANGLE:
            points = [
                (size, 0),
                (0, size * 2),
                (size * 2, size * 2),
            ]
            pg.draw.polygon(particle_surface, color_with_alpha, points)

        elif shape == ParticleShape.STAR:
            points = []
            for i in range(10):
                angle = math.pi * 2 * i / 10 - math.pi / 2
                r = size if i % 2 == 0 else size / 2
                px = size + math.cos(angle) * r
                py = size + math.sin(angle) * r
                points.append((int(px), int(py)))
            pg.draw.polygon(particle_surface, color_with_alpha, points)

        elif shape == ParticleShape.RING:
            pg.draw.circle(particle_surface, color_with_alpha, (size, size), size, max(1, size // 4))

        elif shape == ParticleShape.SPARK:
            # Draw spark shape (cross)
            thickness = max(1, size // 3)
            pg.draw.rect(particle_surface, color_with_alpha, (size - thickness // 2, 0, thickness, size * 2))
            pg.draw.rect(particle_surface, color_with_alpha, (0, size - thickness // 2, size * 2, thickness))

        return particle_surface

    @classmethod
    def clear_surface_cache(cls) -> None:
        """Clear the surface cache to free memory."""
        cls._surface_cache.clear()

    @classmethod
    def get_cache_stats(cls) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_surfaces": len(cls._surface_cache),
            "max_cache_size": cls._cache_max_size,
        }


class EnhancedParticleSystem:
    """
    Enhanced particle system with object pooling.

    Features:
    - Multiple emitters
    - Particle pooling
    - Behavior presets
    - Performance optimization
    """

    # Particle presets
    PRESETS: Dict[str, ParticleConfig] = {
        "fire": ParticleConfig(
            color=(255, 100, 0),
            color_end=(255, 255, 0),
            shape=ParticleShape.CIRCLE,
            size=8.0,
            size_end=0.0,
            lifetime=0.5,
            velocity=(0, -50),
            acceleration=(0, -20),
            gravity=-10,
            behavior=ParticleBehavior.FLOAT,
            behavior_params={"frequency": 5, "amplitude": 20},
            fade_out=0.3,
        ),
        "smoke": ParticleConfig(
            color=(100, 100, 100),
            color_end=(50, 50, 50),
            shape=ParticleShape.CIRCLE,
            size=10.0,
            size_end=30.0,
            lifetime=2.0,
            velocity=(0, -20),
            alpha=150,
            alpha_end=0,
            fade_out=0.5,
        ),
        "spark": ParticleConfig(
            color=(255, 255, 200),
            color_end=(255, 200, 100),
            shape=ParticleShape.SPARK,
            size=4.0,
            size_end=0.0,
            lifetime=0.3,
            behavior=ParticleBehavior.EXPLODE,
            behavior_params={"speed": 150},
            fade_out=0.2,
        ),
        "magic": ParticleConfig(
            color=(150, 100, 255),
            color_end=(255, 100, 255),
            shape=ParticleShape.STAR,
            size=6.0,
            size_end=2.0,
            lifetime=1.0,
            behavior=ParticleBehavior.SPIRAL,
            behavior_params={"speed": 3, "radius_growth": 20},
            rotation_speed=180,
            fade_out=0.3,
        ),
        "explosion": ParticleConfig(
            color=(255, 200, 50),
            color_end=(255, 50, 0),
            shape=ParticleShape.CIRCLE,
            size=12.0,
            size_end=0.0,
            lifetime=0.8,
            behavior=ParticleBehavior.EXPLODE,
            behavior_params={"speed": 200},
            gravity=50,
            fade_out=0.4,
        ),
        "debris": ParticleConfig(
            color=(100, 80, 50),
            shape=ParticleShape.SQUARE,
            size=5.0,
            size_end=2.0,
            lifetime=1.5,
            behavior=ParticleBehavior.GRAVITY,
            behavior_params={"gravity": 200},
            rotation_speed=360,
            fade_out=0.2,
        ),
        "energy_orb": ParticleConfig(
            color=(0, 255, 255),
            color_end=(0, 100, 255),
            shape=ParticleShape.CIRCLE,
            size=8.0,
            size_end=15.0,
            lifetime=1.0,
            behavior=ParticleBehavior.ORBIT,
            behavior_params={"speed": 2, "radius": 30},
            alpha=200,
            alpha_end=0,
        ),
        "rain": ParticleConfig(
            color=(100, 150, 255),
            shape=ParticleShape.CIRCLE,
            size=2.0,
            lifetime=2.0,
            velocity=(0, 300),
            gravity=50,
        ),
        "snow": ParticleConfig(
            color=(255, 255, 255),
            shape=ParticleShape.CIRCLE,
            size=3.0,
            lifetime=4.0,
            velocity=(0, 50),
            behavior=ParticleBehavior.WAVE,
            behavior_params={"speed": 2, "amplitude": 30},
        ),
        "coin_burst": ParticleConfig(
            color=(255, 215, 0),
            shape=ParticleShape.STAR,
            size=6.0,
            size_end=0.0,
            lifetime=0.5,
            behavior=ParticleBehavior.EXPLODE,
            behavior_params={"speed": 100},
            fade_out=0.3,
        ),
    }

    def __init__(self, max_particles: int = 1000) -> None:
        """
        Initialize particle system.

        Args:
            max_particles: Maximum particles to manage
        """
        self.max_particles = max_particles
        self.particles: List[EnhancedParticle] = []
        self.pool: List[EnhancedParticle] = []

        # Emitters
        self.emitters: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.total_emitted = 0
        self.total_updated = 0

    def emit(
        self,
        x: float,
        y: float,
        preset: str,
        count: int = 1,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Emit particles.

        Args:
            x, y: Emission position
            preset: Particle preset name
            count: Number of particles
            config_override: Override config values

        Returns:
            Number of particles emitted
        """
        if preset not in self.PRESETS:
            return 0

        base_config = self.PRESETS[preset]
        emitted = 0

        for _ in range(count):
            # Get or create particle
            particle = self._get_particle()
            if particle is None:
                break

            # Create config
            config = self._create_config(base_config, config_override)

            # Initialize particle
            particle.x = x
            particle.y = y
            particle.config = config
            particle.age = 0.0
            particle.alive = True

            # Randomize velocity
            if config.velocity != (0, 0):
                angle_var = random.uniform(-0.3, 0.3)
                speed = math.sqrt(config.velocity[0] ** 2 + config.velocity[1] ** 2)
                base_angle = math.atan2(config.velocity[1], config.velocity[0])
                particle.vx = math.cos(base_angle + angle_var) * speed
                particle.vy = math.sin(base_angle + angle_var) * speed

            self.particles.append(particle)
            emitted += 1

        self.total_emitted += emitted
        return emitted

    def _get_particle(self) -> Optional[EnhancedParticle]:
        """Get particle from pool or create new."""
        if len(self.particles) >= self.max_particles:
            return None

        if self.pool:
            return self.pool.pop()

        return EnhancedParticle(0, 0)

    def _create_config(self, base: ParticleConfig, override: Optional[Dict[str, Any]]) -> ParticleConfig:
        """Create config with overrides."""
        if not override:
            return base

        # Create copy with overrides
        return ParticleConfig(
            color=override.get("color", base.color),
            color_end=override.get("color_end", base.color_end),
            shape=override.get("shape", base.shape),
            size=override.get("size", base.size),
            size_end=override.get("size_end", base.size_end),
            lifetime=override.get("lifetime", base.lifetime),
            fade_in=override.get("fade_in", base.fade_in),
            fade_out=override.get("fade_out", base.fade_out),
            velocity=override.get("velocity", base.velocity),
            acceleration=override.get("acceleration", base.acceleration),
            drag=override.get("drag", base.drag),
            gravity=override.get("gravity", base.gravity),
            behavior=override.get("behavior", base.behavior),
            behavior_params=override.get("behavior_params", base.behavior_params),
            rotation=override.get("rotation", base.rotation),
            rotation_speed=override.get("rotation_speed", base.rotation_speed),
            alpha=override.get("alpha", base.alpha),
            alpha_end=override.get("alpha_end", base.alpha_end),
        )

    def emit_continuous(
        self,
        emitter_id: str,
        x: float,
        y: float,
        preset: str,
        rate: float = 10,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Start continuous emission.

        Args:
            emitter_id: Emitter identifier
            x, y: Emission position
            preset: Particle preset
            rate: Particles per second
            config_override: Override config values
        """
        self.emitters[emitter_id] = {
            "x": x,
            "y": y,
            "preset": preset,
            "rate": rate,
            "config_override": config_override,
            "timer": 0.0,
            "active": True,
        }

    def stop_emitter(self, emitter_id: str) -> None:
        """Stop continuous emitter."""
        if emitter_id in self.emitters:
            self.emitters[emitter_id]["active"] = False

    def update(self, dt: float) -> None:
        """
        Update all particles.

        Args:
            dt: Delta time in seconds
        """
        # Update continuous emitters
        for emitter in self.emitters.values():
            if not emitter["active"]:
                continue

            emitter["timer"] += dt
            interval = 1.0 / emitter["rate"]

            while emitter["timer"] >= interval:
                emitter["timer"] -= interval
                self.emit(
                    emitter["x"],
                    emitter["y"],
                    emitter["preset"],
                    1,
                    emitter["config_override"],
                )

        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            self.total_updated += 1

        # Remove dead particles
        dead = [p for p in self.particles if not p.alive]
        for particle in dead:
            self.particles.remove(particle)
            self.pool.append(particle)

        # Limit pool size
        if len(self.pool) > 100:
            self.pool = self.pool[:100]

    def draw(self, surface: pg.Surface, offset: Tuple[float, float] = (0, 0)) -> None:
        """
        Draw all particles.

        Args:
            surface: Surface to draw on
            offset: Camera offset
        """
        # Sort by alpha for proper blending
        sorted_particles = sorted(self.particles, key=lambda p: p.current_alpha, reverse=True)

        for particle in sorted_particles:
            particle.draw(surface, offset)

    def clear(self) -> None:
        """Clear all particles."""
        self.pool.extend(self.particles)
        self.particles.clear()
        self.emitters.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get particle system statistics."""
        return {
            "active": len(self.particles),
            "pooled": len(self.pool),
            "max": self.max_particles,
            "emitters": len([e for e in self.emitters.values() if e["active"]]),
            "total_emitted": self.total_emitted,
            "total_updated": self.total_updated,
        }

    def create_effect(
        self,
        effect_name: str,
        x: float,
        y: float,
        **kwargs: Any,
    ) -> None:
        """
        Create predefined effect.

        Args:
            effect_name: Effect name
            x, y: Position
            **kwargs: Additional parameters
        """
        if effect_name == "jump":
            self.emit(x, y, "smoke", count=5)
            self.emit(x, y, "debris", count=3)

        elif effect_name == "land":
            self.emit(x, y, "smoke", count=8)
            self.emit(x, y, "debris", count=5)

        elif effect_name == "coin":
            self.emit(x, y, "coin_burst", count=10)
            self.emit(x, y, "magic", count=5)

        elif effect_name == "powerup":
            self.emit(x, y, "magic", count=20)
            self.emit(x, y, "energy_orb", count=10)

        elif effect_name == "explosion":
            self.emit(x, y, "explosion", count=30)
            self.emit(x, y, "fire", count=20)
            self.emit(x, y, "smoke", count=15)
            self.emit(x, y, "debris", count=20)

        elif effect_name == "fireball":
            self.emit_continuous(
                kwargs.get("emitter_id", "fireball"),
                x,
                y,
                "fire",
                rate=20,
            )

        elif effect_name == "death":
            self.emit(x, y, "explosion", count=50)
            self.emit(x, y, "debris", count=30)

        elif effect_name == "victory":
            for _ in range(5):
                ox = x + random.uniform(-100, 100)
                oy = y + random.uniform(-100, 100)
                self.emit(ox, oy, "coin_burst", count=5)
                self.emit(ox, oy, "magic", count=3)


# Global particle system instance
_particle_system: Optional[EnhancedParticleSystem] = None


def get_particle_system() -> EnhancedParticleSystem:
    """Get global particle system instance."""
    global _particle_system
    if _particle_system is None:
        _particle_system = EnhancedParticleSystem()
    return _particle_system
