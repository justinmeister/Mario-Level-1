"""
Optimization utilities for improved game performance.

Includes:
- Object pooling for frequently created/destroyed objects
- Sprite batching for efficient rendering
- Performance timing utilities
- Computation caching
"""
from __future__ import annotations

import time
from collections import deque
from typing import Any, Callable, Generic, Optional, TypeVar, List, Dict, Tuple, Hashable
import pygame as pg
from functools import wraps

from . import constants as c

T = TypeVar("T")


class ObjectPool(Generic[T]):
    """
    Generic object pool for reusing game objects.

    Reduces garbage collection overhead by recycling objects
    instead of creating/destroying them frequently.

    Example:
        fireball_pool = ObjectPool(max_size=10)
        fireball = fireball_pool.acquire()
        # ... use fireball ...
        fireball_pool.release(fireball)
    """

    def __init__(
        self, factory: Callable[[], T], reset_func: Optional[Callable[[T], None]] = None, max_size: int = 10
    ) -> None:
        """
        Initialize object pool.

        Args:
            factory: Function that creates new objects
            reset_func: Optional function to reset objects before reuse
            max_size: Maximum number of objects to pool
        """
        self._factory = factory
        self._reset_func = reset_func
        self._max_size = max_size
        self._available: deque[T] = deque()
        self._in_use: List[T] = []

    def acquire(self) -> T:
        """
        Acquire an object from the pool.

        Returns:
            An object from the pool or a new one if pool is empty
        """
        if self._available:
            obj = self._available.popleft()
        else:
            obj = self._factory()

        self._in_use.append(obj)
        return obj

    def release(self, obj: T) -> None:
        """
        Release an object back to the pool.

        Args:
            obj: The object to return to the pool
        """
        if obj in self._in_use:
            self._in_use.remove(obj)

            if self._reset_func:
                self._reset_func(obj)

            if len(self._available) < self._max_size:
                self._available.append(obj)

    def release_all(self) -> None:
        """Release all in-use objects back to the pool."""
        for obj in list(self._in_use):
            self.release(obj)

    @property
    def available_count(self) -> int:
        """Number of objects available in pool."""
        return len(self._available)

    @property
    def in_use_count(self) -> int:
        """Number of objects currently in use."""
        return len(self._in_use)

    @property
    def total_count(self) -> int:
        """Total number of objects (pooled + in use)."""
        return len(self._available) + len(self._in_use)


class FireballPool:
    """
    Specialized pool for fireball objects.

    Manages fireball lifecycle to reduce object creation overhead.
    """

    def __init__(self, max_fireballs: int = 4) -> None:
        """
        Initialize fireball pool.

        Args:
            max_fireballs: Maximum number of fireballs to pool
        """
        self.max_fireballs = max_fireballs
        self.available: List[Any] = []
        self.in_use: List[Any] = []

    def acquire(self, x: int, y: int, facing_right: bool) -> Optional[Any]:
        """
        Acquire or create a fireball.

        Args:
            x: Starting x position
            y: Starting y position
            facing_right: Direction the fireball should travel

        Returns:
            Fireball object or None if at capacity
        """
        if len(self.in_use) >= self.max_fireballs:
            return None

        from .components import powerups

        if self.available:
            fireball = self.available.pop()
            fireball.rect.x = x
            fireball.rect.y = y
            fireball.facing_right = facing_right
            fireball.state = c.FLYING
            fireball.alive = True
        else:
            fireball = powerups.FireBall(x, y, facing_right)

        self.in_use.append(fireball)
        return fireball

    def release(self, fireball: Any) -> None:
        """
        Release a fireball back to the pool.

        Args:
            fireball: The fireball to recycle
        """
        if fireball in self.in_use:
            self.in_use.remove(fireball)
            fireball.kill()
            if len(self.available) < self.max_fireballs:
                self.available.append(fireball)

    def release_all(self) -> None:
        """Release all active fireballs."""
        for fireball in list(self.in_use):
            self.release(fireball)

    def update(self, game_info: dict[str, Any], viewport: pg.Rect) -> None:
        """
        Update all active fireballs.

        Args:
            game_info: Game state dictionary
            viewport: Current camera viewport
        """
        for fireball in list(self.in_use):
            if not fireball.alive:
                self.release(fireball)
            else:
                fireball.update(game_info, viewport)


class SpriteBatch:
    """
    Sprite batching for efficient rendering.

    Groups sprites by image/texture to reduce draw calls.
    """

    def __init__(self) -> None:
        """Initialize sprite batch."""
        self._batches: dict[str, pg.sprite.Group] = {}
        self._sprite_to_batch: dict[int, str] = {}

    def add(self, sprite: pg.sprite.Sprite, batch_name: str = "default") -> None:
        """
        Add sprite to a batch.

        Args:
            sprite: Sprite to add
            batch_name: Name of the batch to add to
        """
        if batch_name not in self._batches:
            self._batches[batch_name] = pg.sprite.Group()

        self._batches[batch_name].add(sprite)
        self._sprite_to_batch[id(sprite)] = batch_name

    def remove(self, sprite: pg.sprite.Sprite) -> None:
        """
        Remove sprite from its batch.

        Args:
            sprite: Sprite to remove
        """
        batch_name = self._sprite_to_batch.get(id(sprite))
        if batch_name and batch_name in self._batches:
            self._batches[batch_name].remove(sprite)
            del self._sprite_to_batch[id(sprite)]

    def clear(self) -> None:
        """Clear all batches."""
        self._batches.clear()
        self._sprite_to_batch.clear()

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw all batches to surface.

        Args:
            surface: Surface to draw to
        """
        for batch in self._batches.values():
            batch.draw(surface)

    def update(self) -> None:
        """Update all sprites in all batches."""
        for batch in self._batches.values():
            batch.update()


class PerformanceTimer:
    """
    Context manager for measuring code performance.

    Example:
        with PerformanceTimer("update"):
            # code to measure
            pass
    """

    def __init__(self, name: str = "Operation", threshold_ms: float = 16.0) -> None:
        """
        Initialize performance timer.

        Args:
            name: Name for logging
            threshold_ms: Warn if operation exceeds this time (default ~1 frame at 60fps)
        """
        self.name = name
        self.threshold_ms = threshold_ms
        self.start_time: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "PerformanceTimer":
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop timing and log if exceeded threshold."""
        end_time = time.perf_counter()
        self.elapsed_ms = (end_time - self.start_time) * 1000

        if self.elapsed_ms > self.threshold_ms:
            print(f"[PERF] {self.name}: {self.elapsed_ms:.2f}ms")


class FrameRateMonitor:
    """
    Monitor and track frame rate over time.

    Useful for detecting performance issues.
    """

    def __init__(self, window_size: int = 60) -> None:
        """
        Initialize frame rate monitor.

        Args:
            window_size: Number of frames to average over
        """
        self.window_size = window_size
        self.frame_times: deque[float] = deque(maxlen=window_size)
        self.last_frame_time: float = 0.0

    def tick(self) -> float:
        """
        Record a frame and return current FPS.

        Returns:
            Current frames per second
        """
        current_time = time.perf_counter()

        if self.last_frame_time > 0:
            frame_time = current_time - self.last_frame_time
            self.frame_times.append(frame_time)

        self.last_frame_time = current_time

        if self.frame_times:
            avg_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_time if avg_time > 0 else 0.0

        return 0.0

    def get_fps(self) -> float:
        """Get current average FPS."""
        if not self.frame_times:
            return 0.0

        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0

    def get_frame_time(self) -> float:
        """Get average frame time in milliseconds."""
        if not self.frame_times:
            return 0.0

        return (sum(self.frame_times) / len(self.frame_times)) * 1000

    def is_performance_acceptable(self, target_fps: float = 60.0, tolerance: float = 0.2) -> bool:
        """
        Check if performance is within acceptable range.

        Args:
            target_fps: Target frame rate
            tolerance: Acceptable deviation (0.2 = 20%)

        Returns:
            True if FPS is within tolerance of target
        """
        min_acceptable = target_fps * (1 - tolerance)
        return self.get_fps() >= min_acceptable


class ComputationCache:
    """
    LRU cache for expensive computations.

    Caches results of expensive operations to avoid recomputation.
    Automatically evicts least recently used entries when full.
    """

    def __init__(self, max_size: int = 100) -> None:
        """
        Initialize computation cache.

        Args:
            max_size: Maximum number of cached entries
        """
        self.max_size = max_size
        self._cache: Dict[Hashable, Any] = {}
        self._access_order: deque[Hashable] = deque()
        self._hits = 0
        self._misses = 0

    def get(self, key: Hashable) -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self._cache:
            self._hits += 1
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]

        self._misses += 1
        return None

    def put(self, key: Hashable, value: Any) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self._cache:
            # Update existing entry
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            # Evict least recently used
            lru_key = self._access_order.popleft()
            del self._cache[lru_key]

        self._cache[key] = value
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._access_order.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
        }


def memoize(max_size: int = 128):
    """
    Decorator for memoizing function results.

    Args:
        max_size: Maximum cache size

    Example:
        @memoize(max_size=100)
        def expensive_calculation(x, y):
            return x ** y
    """

    def decorator(func: Callable) -> Callable:
        cache = ComputationCache(max_size=max_size)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))

            result = cache.get(key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache.put(key, result)
            return result

        wrapper.cache = cache  # type: ignore
        return wrapper

    return decorator


class SpatialHash:
    """
    Spatial hashing for efficient collision detection.

    Divides space into grid cells for fast proximity queries.
    """

    def __init__(self, cell_size: int = 64) -> None:
        """
        Initialize spatial hash.

        Args:
            cell_size: Size of each grid cell
        """
        self.cell_size = cell_size
        self._grid: Dict[Tuple[int, int], List[Any]] = {}

    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get grid cell for position."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, obj: Any, x: float, y: float, width: float, height: float) -> None:
        """
        Insert object into spatial hash.

        Args:
            obj: Object to insert
            x, y: Position
            width, height: Size
        """
        # Get all cells the object overlaps
        min_cell = self._get_cell(x, y)
        max_cell = self._get_cell(x + width, y + height)

        for cx in range(min_cell[0], max_cell[0] + 1):
            for cy in range(min_cell[1], max_cell[1] + 1):
                cell = (cx, cy)
                if cell not in self._grid:
                    self._grid[cell] = []
                if obj not in self._grid[cell]:
                    self._grid[cell].append(obj)

    def query(self, x: float, y: float, width: float, height: float) -> List[Any]:
        """
        Query objects in area.

        Args:
            x, y: Position
            width, height: Size

        Returns:
            List of objects in area
        """
        results = []
        seen = set()
        min_cell = self._get_cell(x, y)
        max_cell = self._get_cell(x + width, y + height)

        for cx in range(min_cell[0], max_cell[0] + 1):
            for cy in range(min_cell[1], max_cell[1] + 1):
                cell = (cx, cy)
                if cell in self._grid:
                    for obj in self._grid[cell]:
                        obj_id = id(obj)
                        if obj_id not in seen:
                            seen.add(obj_id)
                            results.append(obj)

        return results

    def clear(self) -> None:
        """Clear all objects from spatial hash."""
        self._grid.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get spatial hash statistics."""
        total_objects = sum(len(cell) for cell in self._grid.values())
        return {
            "cells": len(self._grid),
            "objects": total_objects,
            "avg_per_cell": total_objects // len(self._grid) if self._grid else 0,
        }
