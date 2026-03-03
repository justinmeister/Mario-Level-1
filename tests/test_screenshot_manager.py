"""
Tests for screenshot_manager module.
"""
import json
import os
import tempfile
import shutil

import pytest
import pygame as pg

from data.screenshot_manager import (
    ScreenshotManager,
    ScreenshotMetadata,
    get_screenshot_manager,
    capture_screenshot,
)


class TestScreenshotMetadata:
    """Tests for ScreenshotMetadata."""

    def test_metadata_creation(self) -> None:
        """Test metadata initialization."""
        meta = ScreenshotMetadata(
            filename="test.png",
            timestamp="2026-02-26T12:00:00",
            resolution=(800, 600),
            game_state="level1",
            level="1-1",
            score=1000,
            coin_total=10,
            fps=60.0,
        )

        assert meta.filename == "test.png"
        assert meta.resolution == (800, 600)
        assert meta.score == 1000

    def test_metadata_to_dict(self) -> None:
        """Test metadata serialization."""
        meta = ScreenshotMetadata(
            filename="test.png",
            timestamp="2026-02-26T12:00:00",
            resolution=(800, 600),
            game_state="level1",
            level="1-1",
            score=1000,
            coin_total=10,
            fps=60.0,
            notes="Test notes",
        )

        data = meta.to_dict()

        assert data["filename"] == "test.png"
        assert data["resolution"] == (800, 600)
        assert data["score"] == 1000
        assert data["notes"] == "Test notes"

    def test_metadata_default_notes(self) -> None:
        """Test metadata default notes."""
        meta = ScreenshotMetadata(
            filename="test.png",
            timestamp="2026-02-26T12:00:00",
            resolution=(800, 600),
            game_state="level1",
            level="1-1",
            score=1000,
            coin_total=10,
            fps=60.0,
        )

        assert meta.notes == ""


class TestScreenshotManager:
    """Tests for ScreenshotManager."""

    @pytest.fixture
    def temp_dir(self) -> str:
        """Create temporary directory for tests."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def test_surface(self) -> pg.Surface:
        """Create test surface."""
        pg.init()
        surface = pg.Surface((800, 600))
        surface.fill((255, 0, 0))
        yield surface
        pg.quit()

    def test_manager_creation(self, temp_dir: str) -> None:
        """Test manager initialization."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        assert mgr.output_dir == temp_dir
        assert mgr.max_screenshots == 100
        assert mgr.auto_cleanup is True

    def test_manager_custom_config(self, temp_dir: str) -> None:
        """Test manager with custom config."""
        mgr = ScreenshotManager(
            output_dir=temp_dir,
            max_screenshots=50,
            auto_cleanup=False,
        )

        assert mgr.max_screenshots == 50
        assert mgr.auto_cleanup is False

    def test_ensure_output_dir(self, temp_dir: str) -> None:
        """Test directory creation."""
        new_dir = os.path.join(temp_dir, "new_screenshots")
        mgr = ScreenshotManager(output_dir=new_dir)

        assert os.path.exists(new_dir)

    def test_capture_screenshot(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test capturing screenshot."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        filename = mgr.capture(test_surface)

        assert filename is not None
        assert filename.endswith(".png")
        assert os.path.exists(os.path.join(temp_dir, filename))

    def test_capture_with_game_info(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test capturing with game info."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        game_info = {
            "level_state": "playing",
            "current_level": "1-1",
            "score": 5000,
            "coin_total": 25,
            "fps": 60.0,
        }

        filename = mgr.capture(test_surface, game_info=game_info, notes="Test")

        assert filename is not None

        metadata = mgr.get_screenshots()
        assert len(metadata) > 0
        assert metadata[0]["score"] == 5000
        assert metadata[0]["level"] == "1-1"

    def test_capture_default_game_info(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test capturing without game info."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        filename = mgr.capture(test_surface)

        assert filename is not None

        metadata = mgr.get_screenshots()
        assert metadata[0]["game_state"] == "unknown"
        assert metadata[0]["score"] == 0

    def test_get_screenshots(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test getting screenshot list."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        mgr.capture(test_surface)
        mgr.capture(test_surface)

        screenshots = mgr.get_screenshots()

        assert len(screenshots) == 2

    def test_get_screenshot_path(self, temp_dir: str) -> None:
        """Test getting screenshot path."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        path = mgr.get_screenshot_path("test.png")

        assert path == os.path.join(temp_dir, "test.png")

    def test_delete_screenshot(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test deleting screenshot."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        filename = mgr.capture(test_surface)
        assert filename is not None

        result = mgr.delete_screenshot(filename)

        assert result is True
        assert len(mgr.get_screenshots()) == 0

    def test_delete_nonexistent(self, temp_dir: str) -> None:
        """Test deleting nonexistent screenshot."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        result = mgr.delete_screenshot("nonexistent.png")

        assert result is True

    def test_clear_all(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test clearing all screenshots."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        for _ in range(5):
            mgr.capture(test_surface)

        count = mgr.clear_all()

        assert count == 5
        assert len(mgr.get_screenshots()) == 0

    def test_clear_empty(self, temp_dir: str) -> None:
        """Test clearing empty directory."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        count = mgr.clear_all()

        assert count == 0

    def test_get_stats(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test getting statistics."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        mgr.capture(test_surface)

        stats = mgr.get_stats()

        assert stats["count"] == 1
        assert "total_size" in stats
        assert "oldest" in stats
        assert "newest" in stats

    def test_get_stats_empty(self, temp_dir: str) -> None:
        """Test stats with no screenshots."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        stats = mgr.get_stats()

        assert stats["count"] == 0
        assert stats["total_size"] == 0
        assert stats["oldest"] is None
        assert stats["newest"] is None

    def test_cleanup(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test auto cleanup."""
        mgr = ScreenshotManager(output_dir=temp_dir, max_screenshots=3, auto_cleanup=True)

        for _ in range(5):
            mgr.capture(test_surface)

        screenshots = mgr.get_screenshots()
        assert len(screenshots) <= 3

    def test_no_cleanup_disabled(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test with cleanup disabled."""
        mgr = ScreenshotManager(output_dir=temp_dir, max_screenshots=2, auto_cleanup=False)

        for _ in range(5):
            mgr.capture(test_surface)

        screenshots = mgr.get_screenshots()
        assert len(screenshots) == 5

    def test_metadata_persistence(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test metadata saved to file."""
        mgr = ScreenshotManager(output_dir=temp_dir)

        mgr.capture(test_surface)

        metadata_file = os.path.join(temp_dir, "metadata.json")
        assert os.path.exists(metadata_file)

        with open(metadata_file, "r") as f:
            data = json.load(f)

        assert len(data) == 1

    def test_metadata_load(self, temp_dir: str, test_surface: pg.Surface) -> None:
        """Test loading existing metadata."""
        mgr1 = ScreenshotManager(output_dir=temp_dir)
        mgr1.capture(test_surface)

        mgr2 = ScreenshotManager(output_dir=temp_dir)

        assert len(mgr2.get_screenshots()) == 1

    def test_corrupt_metadata(self, temp_dir: str) -> None:
        """Test handling corrupt metadata."""
        metadata_file = os.path.join(temp_dir, "metadata.json")

        with open(metadata_file, "w") as f:
            f.write("not valid json")

        mgr = ScreenshotManager(output_dir=temp_dir)

        assert len(mgr.get_screenshots()) == 0


class TestGlobalManager:
    """Tests for global screenshot manager functions."""

    @pytest.fixture
    def temp_dir(self) -> str:
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    def test_get_screenshot_manager(self, temp_dir: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting global manager."""
        import data.screenshot_manager as sm

        monkeypatch.setattr(sm, "_screenshot_manager", None)
        monkeypatch.setattr(sm, "ScreenshotManager", lambda **kwargs: ScreenshotManager(output_dir=temp_dir))

        mgr = get_screenshot_manager()

        assert mgr is not None

    def test_capture_screenshot_function(self, temp_dir: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test global capture function."""
        import data.screenshot_manager as sm

        pg.init()
        surface = pg.Surface((100, 100))
        surface.fill((0, 255, 0))

        monkeypatch.setattr(sm, "_screenshot_manager", ScreenshotManager(output_dir=temp_dir))

        filename = capture_screenshot(surface)

        assert filename is not None
        assert os.path.exists(os.path.join(temp_dir, filename))

        pg.quit()
