"""Performance optimization utilities for collision detection and sprite management."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from .components.mario import Mario


class CollisionOptimizer:
    """Optimizes collision detection by combining sprite groups."""

    def __init__(self) -> None:
        """Initialize collision optimizer."""
        self.combined_static_group: Optional[pg.sprite.Group] = None
        self.combined_interactive_group: Optional[pg.sprite.Group] = None
        self._cache_valid = False

    def setup_combined_groups(
        self,
        ground_group: pg.sprite.Group,
        pipe_group: pg.sprite.Group,
        step_group: pg.sprite.Group,
        brick_group: pg.sprite.Group,
        coin_box_group: pg.sprite.Group,
    ) -> None:
        """Setup combined sprite groups for optimized collision detection.

        Args:
            ground_group: Ground sprites
            pipe_group: Pipe sprites
            step_group: Step sprites
            brick_group: Brick sprites
            coin_box_group: Coin box sprites
        """
        # Static colliders (ground, pipes, steps)
        self.combined_static_group = pg.sprite.Group()
        self.combined_static_group.add(*ground_group.sprites())
        self.combined_static_group.add(*pipe_group.sprites())
        self.combined_static_group.add(*step_group.sprites())

        # Interactive colliders (bricks, coin boxes)
        self.combined_interactive_group = pg.sprite.Group()
        self.combined_interactive_group.add(*brick_group.sprites())
        self.combined_interactive_group.add(*coin_box_group.sprites())

        self._cache_valid = True

    def invalidate_cache(self) -> None:
        """Invalidate cached groups when sprites are added/removed."""
        self._cache_valid = False

    def check_collision_optimized(
        self,
        mario: Mario,
        check_static: bool = True,
        check_interactive: bool = True,
    ) -> Dict[str, Any]:
        """Optimized collision check using combined groups.

        Args:
            mario: Mario sprite
            check_static: Check static colliders
            check_interactive: Check interactive colliders

        Returns:
            Dictionary with collision results
        """
        result: Dict[str, Any] = {
            "static": None,
            "interactive": None,
            "has_collision": False,
        }

        if not self._cache_valid:
            return result

        if check_static and self.combined_static_group:
            static_collider = pg.sprite.spritecollideany(mario, self.combined_static_group)
            if static_collider:
                result["static"] = static_collider
                result["has_collision"] = True

        if check_interactive and self.combined_interactive_group:
            interactive_collider = pg.sprite.spritecollideany(mario, self.combined_interactive_group)
            if interactive_collider:
                result["interactive"] = interactive_collider
                result["has_collision"] = True

        return result


class SpritePoolManager:
    """Manages sprite object pooling to reduce memory allocation."""

    def __init__(self, sprite_class: type, pool_size: int = 20) -> None:
        """Initialize sprite pool.

        Args:
            sprite_class: Class of sprites to pool
            pool_size: Initial pool size
        """
        self.sprite_class = sprite_class
        self.pool: List[Any] = []
        self.active: List[Any] = []
        self.pool_size = pool_size

        # Pre-allocate pool
        for _ in range(pool_size):
            self.pool.append(self._create_sprite())

    def _create_sprite(self) -> Any:
        """Create a new sprite instance.

        Returns:
            New sprite instance
        """
        return self.sprite_class()

    def acquire(self, *args: Any, **kwargs: Any) -> Any:
        """Acquire a sprite from the pool.

        Args:
            *args: Positional arguments for sprite initialization
            **kwargs: Keyword arguments for sprite initialization

        Returns:
            Sprite instance
        """
        if self.pool:
            sprite = self.pool.pop()
        else:
            sprite = self._create_sprite()

        # Reinitialize sprite
        if hasattr(sprite, "reset"):
            sprite.reset(*args, **kwargs)

        self.active.append(sprite)
        return sprite

    def release(self, sprite: Any) -> None:
        """Release a sprite back to the pool.

        Args:
            sprite: Sprite to release
        """
        if sprite in self.active:
            self.active.remove(sprite)
            self.pool.append(sprite)

    def clear_active(self) -> None:
        """Clear all active sprites and return them to pool."""
        self.pool.extend(self.active)
        self.active.clear()


class AnimationCache:
    """Caches animation frames to avoid repeated image loading."""

    def __init__(self) -> None:
        """Initialize animation cache."""
        self._cache: Dict[str, List[pg.Surface]] = {}

    def get_frames(self, key: str) -> Optional[List[pg.Surface]]:
        """Get cached animation frames.

        Args:
            key: Cache key

        Returns:
            List of frames or None if not cached
        """
        return self._cache.get(key)

    def set_frames(self, key: str, frames: List[pg.Surface]) -> None:
        """Cache animation frames.

        Args:
            key: Cache key
            frames: List of frames to cache
        """
        self._cache[key] = frames

    def clear(self) -> None:
        """Clear animation cache."""
        self._cache.clear()

    def get_or_create(
        self,
        key: str,
        creator_func: Callable[..., List[pg.Surface]],
        *args: Any,
        **kwargs: Any,
    ) -> List[pg.Surface]:
        """Get cached frames or create them if not cached.

        Args:
            key: Cache key
            creator_func: Function to create frames
            *args: Positional arguments for creator function
            **kwargs: Keyword arguments for creator function

        Returns:
            List of animation frames
        """
        frames = self.get_frames(key)
        if frames is None:
            frames = creator_func(*args, **kwargs)
            self.set_frames(key, frames)
        return frames


# Global instances
_collision_optimizer: Optional[CollisionOptimizer] = None
_animation_cache: Optional[AnimationCache] = None


def get_collision_optimizer() -> CollisionOptimizer:
    """Get global collision optimizer instance.

    Returns:
        Collision optimizer instance
    """
    global _collision_optimizer
    if _collision_optimizer is None:
        _collision_optimizer = CollisionOptimizer()
    return _collision_optimizer


def get_animation_cache() -> AnimationCache:
    """Get global animation cache instance.

    Returns:
        Animation cache instance
    """
    global _animation_cache
    if _animation_cache is None:
        _animation_cache = AnimationCache()
    return _animation_cache
