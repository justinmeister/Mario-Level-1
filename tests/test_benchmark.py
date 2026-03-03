"""
Benchmark tests for Super Mario Bros Level 1.

Performance tests to measure:
- Frame time
- Sprite update time
- Collision detection time
- Particle system performance
- Memory usage

Usage:
    pytest tests/test_benchmark.py --benchmark-only
    pytest tests/test_benchmark.py --benchmark-compare
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any, Dict, List

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def init_pygame():
    """Initialize pygame for benchmarks."""
    import pygame as pg

    pg.init()
    pg.display.set_mode((100, 100))
    yield
    pg.quit()


class TestParticleBenchmark:
    """Benchmark tests for particle system."""

    def test_particle_creation(self, benchmark, init_pygame):
        """Benchmark particle creation speed."""
        from data.enhanced_particles_v2 import EnhancedParticleSystem

        def create_and_emit():
            system = EnhancedParticleSystem(max_particles=500)
            system.emit(400, 300, "fire")
            return system

        result = benchmark(create_and_emit)
        assert result is not None

    def test_particle_update(self, benchmark, init_pygame):
        """Benchmark particle update speed."""
        from data.enhanced_particles_v2 import EnhancedParticleSystem

        system = EnhancedParticleSystem(max_particles=500)
        # Emit some particles
        for _ in range(10):
            system.emit(400, 300, "fire")

        def update_particles():
            system.update(16)  # ~60fps delta
            return len(system.particles)

        result = benchmark(update_particles)
        assert result >= 0

    def test_particle_batch_render(self, benchmark, init_pygame):
        """Benchmark batch rendering of particles."""
        import pygame as pg
        from data.enhanced_particles_v2 import EnhancedParticleSystem

        system = EnhancedParticleSystem(max_particles=500)
        surface = pg.Surface((800, 600))

        # Emit particles
        for _ in range(20):
            system.emit(400, 300, "spark")

        def render_particles():
            surface.fill((0, 0, 0))
            for particle in system.particles:
                particle.draw(surface)
            return True

        result = benchmark(render_particles)
        assert result is True


class TestCollisionBenchmark:
    """Benchmark tests for collision detection."""

    def test_collider_creation(self, benchmark):
        """Benchmark collider creation speed."""
        from data.components.collider import Collider

        def create_collider():
            return Collider(100, 200, 50, 50)

        result = benchmark(create_collider)
        assert result is not None

    def test_collider_collision_check(self, benchmark, init_pygame):
        """Benchmark collision detection speed."""
        from data.components.collider import Collider

        # Create multiple colliders
        colliders = [Collider(i * 10, i * 10, 50, 50) for i in range(20)]

        def check_collisions():
            count = 0
            for i, c1 in enumerate(colliders):
                for c2 in colliders[i + 1 :]:
                    if c1.rect.colliderect(c2.rect):
                        count += 1
            return count

        result = benchmark(check_collisions)
        assert result >= 0


class TestResourceLoadingBenchmark:
    """Benchmark tests for resource loading."""

    def test_image_cache_loading(self, benchmark, init_pygame):
        """Benchmark image caching speed."""
        from data.tools.resources import ImageCache

        # Clear cache first
        ImageCache.clear()

        def load_cached_image():
            # This will return None since file doesn't exist,
            # but tests the cache lookup path
            return ImageCache.get("nonexistent.png")

        result = benchmark(load_cached_image)
        assert result is None

    def test_lazy_loader_scan(self, benchmark, init_pygame, tmp_path):
        """Benchmark lazy loader directory scanning."""
        from data.tools.resources import LazyImageLoader

        # Create test images
        for i in range(10):
            surface = pygame.Surface((10, 10))
            pygame.image.save(surface, str(tmp_path / f"img_{i}.png"))

        loader = LazyImageLoader(str(tmp_path))

        def scan_directory():
            loader._scan_directory()
            return loader._available_images

        import pygame

        result = benchmark(scan_directory)
        assert result is not None


class TestSaveSystemBenchmark:
    """Benchmark tests for save system."""

    def test_save_game_performance(self, benchmark, init_pygame, tmp_path):
        """Benchmark save game speed."""
        from data.save_system import SaveManager, GameData

        # Create temp save directory
        import os

        original_dir = os.environ.get("SAVE_DIR")

        manager = SaveManager()
        manager.save_dir = str(tmp_path)
        manager.metadata_file = str(tmp_path / "metadata.json")

        game_data = GameData(
            score=10000,
            coin_total=50,
            lives=3,
            play_time=600,
        )

        def save_game():
            return manager.save_game(1, game_data)

        result = benchmark(save_game)
        assert result is True

    def test_load_game_performance(self, benchmark, init_pygame, tmp_path):
        """Benchmark load game speed."""
        from data.save_system import SaveManager, GameData

        manager = SaveManager()
        manager.save_dir = str(tmp_path)
        manager.metadata_file = str(tmp_path / "metadata.json")

        # Create save first
        game_data = GameData(score=10000, coin_total=50)
        manager.save_game(1, game_data)

        def load_game():
            return manager.load_game(1)

        result = benchmark(load_game)
        assert result is not None


class TestConstantsBenchmark:
    """Benchmark tests for constants access."""

    def test_constant_access_speed(self, benchmark):
        """Benchmark constant lookup speed."""
        from data import constants as c

        def access_constants():
            _ = c.SCREEN_WIDTH
            _ = c.GRAVITY
            _ = c.JUMP_VEL
            _ = c.WHITE
            _ = c.GOOMBA
            return True

        result = benchmark(access_constants)
        assert result is True


class TestMemoryUsage:
    """Memory usage tests."""

    def test_particle_system_memory(self, init_pygame):
        """Test particle system memory usage."""
        from data.advanced_particles import AdvancedParticleSystem
        import tracemalloc

        tracemalloc.start()

        system = AdvancedParticleSystem(max_particles=1000)
        for _ in range(50):
            system.emit(400, 300, "coin_burst")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be reasonable (< 10MB)
        assert peak < 10 * 1024 * 1024

    def test_save_manager_memory(self, init_pygame, tmp_path):
        """Test save manager memory usage."""
        from data.save_system import SaveManager
        import tracemalloc

        tracemalloc.start()

        manager = SaveManager()
        manager.save_dir = str(tmp_path)
        manager.metadata_file = str(tmp_path / "metadata.json")

        # Create multiple saves
        for i in range(3):
            from data.save_system import GameData

            manager.save_game(i + 1, GameData(score=i * 1000))

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be reasonable (< 5MB)
        assert peak < 5 * 1024 * 1024


# Performance thresholds for CI
PERFORMANCE_THRESHOLDS = {
    "test_particle_creation": {"max_time": 0.001},  # 1ms
    "test_particle_update": {"max_time": 0.0005},  # 0.5ms
    "test_collider_creation": {"max_time": 0.0001},  # 0.1ms
    "test_save_game_performance": {"max_time": 0.01},  # 10ms
    "test_load_game_performance": {"max_time": 0.005},  # 5ms
}


@pytest.fixture
def benchmark_threshold(benchmark):
    """Fixture to check performance thresholds."""

    def check_threshold(test_name: str) -> None:
        if test_name in PERFORMANCE_THRESHOLDS:
            threshold = PERFORMANCE_THRESHOLDS[test_name]["max_time"]
            assert benchmark.stats.get("mean", 0) < threshold

    return check_threshold
