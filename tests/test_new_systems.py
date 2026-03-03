"""
Tests for screenshot, debug, and statistics systems.

Note: Dialogue system tests are in test_wave2_systems.py (DialogManager)
"""
import tempfile
import os
from pathlib import Path

import pytest
import pygame as pg

from data.screenshot_manager import (
    ScreenshotManager,
    ScreenshotMetadata,
    get_screenshot_manager,
    capture_screenshot,
)

from data.debug import (
    DebugStats,
    DebugOverlay,
    CollisionVisualizer,
    EntityInspector,
    DebugConsole,
    PerformanceProfiler,
    DebugManager,
)

from data.statistics import (
    SessionStats,
    LifetimeStats,
    EnemyStats,
    PowerUpStats,
    StatisticsManager,
    StatsDisplay,
)


# =============================================================================
# Screenshot System Tests
# =============================================================================

class TestScreenshotMetadata:
    """Tests for ScreenshotMetadata."""

    def test_metadata_creation(self) -> None:
        """Test screenshot metadata creation."""
        metadata = ScreenshotMetadata(
            filename="test.png",
            timestamp="2026-02-28T12:00:00",
            resolution=(800, 600),
            game_state="level_1",
            level="1-1",
            score=1000,
            coin_total=10,
            fps=60.0,
            notes="Test screenshot"
        )

        assert metadata.filename == "test.png"
        assert metadata.resolution == (800, 600)
        assert metadata.score == 1000

    def test_metadata_to_dict(self) -> None:
        """Test metadata to_dict."""
        metadata = ScreenshotMetadata(
            filename="test.png",
            timestamp="2026-02-28T12:00:00",
            resolution=(800, 600),
            game_state="level_1",
            level="1-1",
            score=1000,
            coin_total=10,
            fps=60.0
        )

        data = metadata.to_dict()
        assert data["filename"] == "test.png"
        assert data["resolution"] == (800, 600)
        assert data["score"] == 1000


class TestScreenshotManager:
    """Tests for ScreenshotManager."""

    @pytest.fixture
    def screenshot_manager(self) -> ScreenshotManager:
        """Create screenshot manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ScreenshotManager(output_dir=tmpdir)

    def test_manager_creation(self, screenshot_manager: ScreenshotManager) -> None:
        """Test screenshot manager initialization."""
        assert screenshot_manager.max_screenshots == 100
        assert screenshot_manager.auto_cleanup is True

    def test_capture_screenshot(self, screenshot_manager: ScreenshotManager) -> None:
        """Test capturing screenshot."""
        pg.init()
        screen = pg.display.set_mode((800, 600))
        screen.fill((255, 255, 255))

        filename = screenshot_manager.capture(screen, {"level_state": "playing", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})

        assert filename is not None
        assert filename.endswith(".png")

        pg.quit()

    def test_capture_with_metadata(self, screenshot_manager: ScreenshotManager) -> None:
        """Test capturing screenshot with metadata."""
        pg.init()
        screen = pg.display.set_mode((800, 600))

        game_info = {
            "level_state": "playing",
            "current_level": "1-1",
            "score": 1500,
            "coin_total": 25,
            "fps": 59.5
        }

        filename = screenshot_manager.capture(screen, game_info, "Test note")

        assert filename is not None
        screenshots = screenshot_manager.get_screenshots()
        assert len(screenshots) == 1
        assert screenshots[0]["score"] == 1500
        assert screenshots[0]["coin_total"] == 25

        pg.quit()

    def test_get_screenshots(self, screenshot_manager: ScreenshotManager) -> None:
        """Test getting screenshots."""
        pg.init()
        screen = pg.display.set_mode((100, 100))

        screenshot_manager.capture(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})
        screenshot_manager.capture(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})

        screenshots = screenshot_manager.get_screenshots()
        assert len(screenshots) == 2

        pg.quit()

    def test_delete_screenshot(self, screenshot_manager: ScreenshotManager) -> None:
        """Test deleting screenshot."""
        pg.init()
        screen = pg.display.set_mode((100, 100))

        filename = screenshot_manager.capture(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})
        assert filename is not None

        result = screenshot_manager.delete_screenshot(filename)
        assert result is True

        screenshots = screenshot_manager.get_screenshots()
        assert len(screenshots) == 0

        pg.quit()

    def test_clear_all(self, screenshot_manager: ScreenshotManager) -> None:
        """Test clearing all screenshots."""
        pg.init()
        screen = pg.display.set_mode((100, 100))

        screenshot_manager.capture(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})
        screenshot_manager.capture(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})

        count = screenshot_manager.clear_all()
        assert count == 2

        screenshots = screenshot_manager.get_screenshots()
        assert len(screenshots) == 0

        pg.quit()

    def test_get_stats(self, screenshot_manager: ScreenshotManager) -> None:
        """Test getting stats."""
        stats = screenshot_manager.get_stats()
        assert stats["count"] == 0
        assert stats["total_size"] == 0

        pg.quit()

    def test_cleanup(self, screenshot_manager: ScreenshotManager) -> None:
        """Test auto cleanup."""
        pg.init()
        screen = pg.display.set_mode((100, 100))

        screenshot_manager.max_screenshots = 3

        for _ in range(5):
            screenshot_manager.capture(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})

        screenshots = screenshot_manager.get_screenshots()
        assert len(screenshots) <= 3

        pg.quit()


def test_global_screenshot_manager() -> None:
    """Test global screenshot manager singleton."""
    mgr1 = get_screenshot_manager()
    mgr2 = get_screenshot_manager()
    assert mgr1 is mgr2


def test_capture_screenshot_function() -> None:
    """Test global capture_screenshot function."""
    pg.init()
    screen = pg.display.set_mode((100, 100))

    # Use temp dir for global manager
    import data.screenshot_manager as sm
    sm._screenshot_manager = ScreenshotManager(output_dir=tempfile.gettempdir())

    filename = capture_screenshot(screen, {"level_state": "test", "current_level": "1-1", "score": 0, "coin_total": 0, "fps": 60.0})
    assert filename is not None

    pg.quit()


# =============================================================================
# Debug System Tests
# =============================================================================

class TestDebugStats:
    """Tests for DebugStats."""

    def test_debug_stats_creation(self) -> None:
        """Test debug stats creation."""
        stats = DebugStats()

        assert stats.sprite_count == 0


class TestDebugOverlay:
    """Tests for DebugOverlay."""

    @pytest.fixture
    def overlay(self) -> DebugOverlay:
        """Create debug overlay."""
        return DebugOverlay()

    def test_overlay_creation(self, overlay: DebugOverlay) -> None:
        """Test debug overlay initialization."""
        assert overlay.visible is False

    def test_toggle_overlay(self, overlay: DebugOverlay) -> None:
        """Test toggling overlay."""
        overlay.toggle()
        assert overlay.visible is True

        overlay.toggle()
        assert overlay.visible is False

    def test_update_stats(self, overlay: DebugOverlay) -> None:
        """Test updating stats."""
        pg.init()
        clock = pg.time.Clock()
        clock.tick(60)

        overlay.update(clock, [1, 2, 3], collisions=5)

        assert overlay.stats.fps > 0
        assert overlay.stats.sprite_count == 3
        assert overlay.stats.collision_count == 5

        pg.quit()


class TestCollisionVisualizer:
    """Tests for CollisionVisualizer."""

    @pytest.fixture
    def visualizer(self) -> CollisionVisualizer:
        """Create collision visualizer."""
        return CollisionVisualizer()

    def test_visualizer_creation(self, visualizer: CollisionVisualizer) -> None:
        """Test visualizer initialization."""
        assert visualizer.enabled is False

    def test_toggle_visualizer(self, visualizer: CollisionVisualizer) -> None:
        """Test toggling visualizer."""
        visualizer.toggle()
        assert visualizer.enabled is True


class TestDebugConsole:
    """Tests for DebugConsole."""

    @pytest.fixture
    def console(self) -> DebugConsole:
        """Create debug console."""
        return DebugConsole()

    def test_console_creation(self, console: DebugConsole) -> None:
        """Test console initialization."""
        assert console.visible is False
        assert len(console.commands) > 0

    def test_register_command(self, console: DebugConsole) -> None:
        """Test registering command."""

        def test_cmd(args: str) -> str:
            return "test"

        console.register_command("test", test_cmd)
        assert "test" in console.commands

    def test_help_command(self, console: DebugConsole) -> None:
        """Test help command."""
        result = console.cmd_help("")
        assert "Commands" in result


class TestPerformanceProfiler:
    """Tests for PerformanceProfiler."""

    @pytest.fixture
    def profiler(self) -> PerformanceProfiler:
        """Create performance profiler."""
        return PerformanceProfiler()

    def test_profiler_creation(self, profiler: PerformanceProfiler) -> None:
        """Test profiler initialization."""
        assert profiler.enabled is True
        assert len(profiler.timings) == 0

    def test_start_stop_timer(self, profiler: PerformanceProfiler) -> None:
        """Test starting and stopping timer."""
        profiler.start("test_op")

        import time
        time.sleep(0.01)  # 10ms

        duration = profiler.stop("test_op")
        assert duration is not None
        assert duration >= 10

    def test_get_stats(self, profiler: PerformanceProfiler) -> None:
        """Test getting stats."""
        profiler.start("test")
        
        import time
        time.sleep(0.01)
        profiler.stop("test")

        stats = profiler.get_stats("test")

        assert "count" in stats
        assert "avg" in stats

    def test_reset(self, profiler: PerformanceProfiler) -> None:
        """Test resetting profiler."""
        profiler.start("test")
        profiler.stop("test")

        profiler.reset()

        assert len(profiler.timings) == 0


class TestDebugManager:
    """Tests for DebugManager."""

    @pytest.fixture
    def debug_manager(self) -> DebugManager:
        """Create debug manager."""
        return DebugManager()

    def test_manager_creation(self, debug_manager: DebugManager) -> None:
        """Test debug manager initialization."""
        assert debug_manager.overlay is not None
        assert debug_manager.console is not None
        assert debug_manager.profiler is not None

    def test_handle_event_overlay(self, debug_manager: DebugManager) -> None:
        """Test handling overlay toggle event."""
        pg.init()

        event = pg.event.Event(pg.KEYDOWN, {"key": pg.K_F3})
        result = debug_manager.handle_event(event)

        assert result is True

        pg.quit()


# =============================================================================
# Statistics System Tests
# =============================================================================

class TestSessionStats:
    """Tests for SessionStats."""

    def test_session_stats_creation(self) -> None:
        """Test session stats creation."""
        stats = SessionStats()

        assert stats.score == 0
        assert stats.coins_collected == 0


class TestLifetimeStats:
    """Tests for LifetimeStats."""

    def test_lifetime_stats_creation(self) -> None:
        """Test lifetime stats creation."""
        stats = LifetimeStats()

        assert stats.total_deaths == 0
        assert stats.total_coins == 0

    def test_lifetime_stats_increment(self) -> None:
        """Test incrementing lifetime stats."""
        stats = LifetimeStats()
        stats.total_deaths += 1

        assert stats.total_deaths == 1


class TestStatisticsManager:
    """Tests for StatisticsManager."""

    @pytest.fixture
    def stats_manager(self) -> StatisticsManager:
        """Create statistics manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = str(Path(tmpdir) / "stats.json")
            yield StatisticsManager(save_path=save_path)

    def test_manager_creation(self, stats_manager: StatisticsManager) -> None:
        """Test statistics manager initialization."""
        assert stats_manager.session.score == 0
        assert stats_manager.lifetime.total_sessions == 0

    def test_increment_stat(self, stats_manager: StatisticsManager) -> None:
        """Test incrementing statistic."""
        stats_manager.increment("score", 100)

        assert stats_manager.session.score == 100

    def test_increment_multiple(self, stats_manager: StatisticsManager) -> None:
        """Test incrementing multiple times."""
        stats_manager.increment("coins_collected", 5)
        stats_manager.increment("coins_collected", 3)

        assert stats_manager.session.coins_collected == 8

    def test_get_stat(self, stats_manager: StatisticsManager) -> None:
        """Test getting statistic."""
        stats_manager.increment("score", 500)

        value = stats_manager.get_stat("score")
        assert value == 500

    def test_save_and_load(self, stats_manager: StatisticsManager) -> None:
        """Test save and load statistics."""
        stats_manager.increment("score", 1000)
        stats_manager.save()
        stats_manager.load()

        assert stats_manager.session.score >= 0


class TestStatsDisplay:
    """Tests for StatsDisplay."""

    @pytest.fixture
    def stats_display(self) -> StatsDisplay:
        """Create stats display."""
        manager = StatisticsManager()
        return StatsDisplay(manager)

    def test_stats_display_creation(self, stats_display: StatsDisplay) -> None:
        """Test stats display initialization."""
        assert stats_display.stats is not None

    def test_draw_session_stats(self, stats_display: StatsDisplay) -> None:
        """Test drawing session stats."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Should not crash
        stats_display.draw_session_stats(surface)

        pg.quit()
