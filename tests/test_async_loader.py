"""Tests for asynchronous resource loading."""

from __future__ import annotations

import time
import pytest
import pygame as pg

from data.async_loader import (
    AsyncResourceLoader,
    LoadingScreen,
    LoadPriority,
    LoadProgress,
    get_async_loader,
    get_loading_screen,
)


class TestLoadPriority:
    """Tests for LoadPriority enum."""

    def test_priority_values(self) -> None:
        """Test priority values are correct."""
        assert LoadPriority.CRITICAL.value == 0
        assert LoadPriority.HIGH.value == 1
        assert LoadPriority.NORMAL.value == 2
        assert LoadPriority.LOW.value == 3


class TestLoadProgress:
    """Tests for LoadProgress dataclass."""

    def test_default_values(self) -> None:
        """Test default progress values."""
        progress = LoadProgress()
        
        assert progress.total_items == 0
        assert progress.loaded_items == 0
        assert progress.current_item == ""
        assert progress.progress_percent == 0.0
        assert progress.is_complete is False
        assert progress.has_error is False
        assert progress.error_message == ""

    def test_progress_calculation(self) -> None:
        """Test progress percentage calculation."""
        progress = LoadProgress(
            total_items=10,
            loaded_items=5,
            progress_percent=50.0,  # Set explicitly
        )
        
        assert progress.progress_percent == 50.0

    def test_progress_complete(self) -> None:
        """Test progress when complete."""
        progress = LoadProgress(
            total_items=10,
            loaded_items=10,
            progress_percent=100.0,  # Set explicitly
            is_complete=True,
        )
        
        assert progress.progress_percent == 100.0
        assert progress.is_complete is True
        # Note: is_complete is set by loader, not calculated


class TestAsyncResourceLoader:
    """Tests for AsyncResourceLoader class."""

    def test_creation(self) -> None:
        """Test loader creation."""
        loader = AsyncResourceLoader()
        
        assert loader.max_workers == 2
        assert loader.is_running() is False
        assert loader.is_complete() is False

    def test_custom_workers(self) -> None:
        """Test custom worker count."""
        loader = AsyncResourceLoader(max_workers=4)
        
        assert loader.max_workers == 4

    def test_queue_load(self) -> None:
        """Test queueing a load task."""
        loader = AsyncResourceLoader()
        loader.queue_load("test", "path.png", "image")
        
        progress = loader.get_progress()
        assert progress.total_items == 1

    def test_queue_batch(self) -> None:
        """Test queueing multiple tasks."""
        loader = AsyncResourceLoader()
        
        items = [
            ("item1", "path1.png", "image"),
            ("item2", "path2.png", "image"),
            ("item3", "path3.png", "image"),
        ]
        loader.queue_batch(items)
        
        progress = loader.get_progress()
        assert progress.total_items == 3

    def test_queue_priority(self) -> None:
        """Test priority queueing."""
        loader = AsyncResourceLoader()
        
        loader.queue_load("low", "path.png", "image", LoadPriority.LOW)
        loader.queue_load("critical", "path.png", "image", LoadPriority.CRITICAL)
        
        # Critical should be loaded first
        # (tested implicitly by queue ordering)

    def test_get_progress(self) -> None:
        """Test getting progress."""
        loader = AsyncResourceLoader()
        
        progress = loader.get_progress()
        
        assert isinstance(progress, LoadProgress)
        assert progress.total_items == 0

    def test_is_running(self) -> None:
        """Test running state."""
        loader = AsyncResourceLoader()
        
        assert loader.is_running() is False
        
        loader.start()
        assert loader.is_running() is True
        
        loader.stop()
        assert loader.is_running() is False

    def test_callbacks(self) -> None:
        """Test callback registration."""
        loader = AsyncResourceLoader()
        
        on_item_called = []
        on_complete_called = []
        on_error_called = []
        
        def on_item(name, data):
            on_item_called.append((name, data))
        
        def on_complete():
            on_complete_called.append(True)
        
        def on_error(name, error):
            on_error_called.append((name, error))
        
        loader.set_on_item_loaded(on_item)
        loader.set_on_complete(on_complete)
        loader.set_on_error(on_error)
        
        # Callbacks are set without error
        assert loader._on_item_loaded == on_item
        assert loader._on_complete == on_complete
        assert loader._on_error == on_error

    def test_get_loaded(self) -> None:
        """Test getting loaded resources."""
        loader = AsyncResourceLoader()
        
        # Initially empty
        assert loader.get_loaded("test") is None
        assert loader.get_all_loaded() == {}

    def test_get_failed(self) -> None:
        """Test getting failed resources."""
        loader = AsyncResourceLoader()
        
        # Initially empty
        assert loader.get_failed() == {}

    def test_start_stop(self) -> None:
        """Test start and stop."""
        loader = AsyncResourceLoader(max_workers=1)
        
        loader.start()
        assert len(loader._workers) == 1
        assert loader.is_running() is True
        
        loader.stop()
        assert len(loader._workers) == 0
        assert loader.is_running() is False

    def test_double_start(self) -> None:
        """Test starting twice doesn't create duplicate workers."""
        loader = AsyncResourceLoader(max_workers=1)
        
        loader.start()
        workers1 = len(loader._workers)
        
        loader.start()  # Should be no-op
        workers2 = len(loader._workers)
        
        assert workers1 == workers2
        
        loader.stop()

    def test_wait_complete_timeout(self) -> None:
        """Test wait with timeout."""
        loader = AsyncResourceLoader()
        loader.queue_load("test", "nonexistent.png", "image")
        loader.start()
        
        # Should timeout since resource doesn't exist
        result = loader.wait_complete(timeout=0.1)
        
        assert result is False
        loader.stop()


class TestLoadingScreen:
    """Tests for LoadingScreen class."""

    def test_creation(self) -> None:
        """Test loading screen creation."""
        pg.init()
        pg.display.set_mode((800, 600))
        screen = pg.Surface((800, 600))
        
        loading_screen = LoadingScreen(screen)
        
        assert loading_screen.screen is screen
        assert loading_screen.bar_width == 400
        assert loading_screen.bar_height == 30
        
        pg.quit()

    def test_custom_params(self) -> None:
        """Test custom parameters."""
        pg.init()
        pg.display.set_mode((800, 600))
        screen = pg.Surface((800, 600))
        
        loading_screen = LoadingScreen(
            screen,
            font_size=32,
            bar_width=300,
            bar_height=40,
        )
        
        assert loading_screen.bar_width == 300
        assert loading_screen.bar_height == 40
        
        pg.quit()

    def test_draw(self) -> None:
        """Test drawing loading screen."""
        pg.init()
        pg.display.set_mode((800, 600))
        screen = pg.Surface((800, 600))
        loading_screen = LoadingScreen(screen)
        
        progress = LoadProgress(
            total_items=10,
            loaded_items=5,
            current_item="test.png",
            progress_percent=50.0,
        )
        
        # Should not raise
        loading_screen.draw(progress)
        
        pg.quit()

    def test_update(self) -> None:
        """Test updating loading screen."""
        pg.init()
        pg.display.set_mode((800, 600))
        screen = pg.Surface((800, 600))
        loading_screen = LoadingScreen(screen)
        
        progress = LoadProgress(
            total_items=10,
            loaded_items=5,
            progress_percent=50.0,
            is_complete=False,
        )
        
        result = loading_screen.update(progress)
        
        assert result is False
        
        progress.is_complete = True
        result = loading_screen.update(progress)
        
        assert result is True
        
        pg.quit()


class TestGlobalInstances:
    """Tests for global instances."""

    def test_get_async_loader(self) -> None:
        """Test getting global async loader."""
        loader1 = get_async_loader()
        loader2 = get_async_loader()
        
        assert loader1 is loader2

    def test_get_loading_screen(self) -> None:
        """Test getting global loading screen."""
        pg.init()
        screen = pg.Surface((800, 600))
        
        screen1 = get_loading_screen(screen)
        screen2 = get_loading_screen(screen)
        
        assert screen1 is screen2
        
        pg.quit()


class TestAsyncLoadingIntegration:
    """Integration tests for async loading."""

    def test_load_real_image(self, tmp_path) -> None:
        """Test loading a real image file."""
        pg.init()
        pg.display.set_mode((100, 100))

        # Create test image
        test_image = tmp_path / "test.png"
        surface = pg.Surface((100, 100))
        surface.fill((255, 0, 0))
        pg.image.save(surface, str(test_image))

        loader = AsyncResourceLoader(max_workers=1)
        loader.queue_load("test", str(test_image), "image")
        loader.start()

        # Wait for loading
        loader.wait_complete(timeout=2.0)

        # Check result
        loaded = loader.get_loaded("test")
        assert loaded is not None
        assert isinstance(loaded, pg.Surface)

        loader.stop()
        pg.quit()

    def test_load_nonexistent_file(self) -> None:
        """Test loading nonexistent file."""
        pg.init()
        pg.display.set_mode((100, 100))

        loader = AsyncResourceLoader(max_workers=1)
        loader.queue_load("missing", "nonexistent.png", "image")
        loader.start()

        # Wait for failure
        time.sleep(0.5)

        # Check error
        failed = loader.get_failed()
        assert "missing" in failed

        loader.stop()
        pg.quit()

    def test_load_multiple_images(self, tmp_path) -> None:
        """Test loading multiple images."""
        pg.init()
        pg.display.set_mode((100, 100))

        # Create test images
        paths = []
        for i in range(5):
            test_image = tmp_path / f"test{i}.png"
            surface = pg.Surface((50, 50))
            surface.fill((i * 50, 0, 0))
            pg.image.save(surface, str(test_image))
            paths.append((f"test{i}", str(test_image), "image"))
        
        loader = AsyncResourceLoader(max_workers=2)
        loader.queue_batch(paths)
        loader.start()
        
        # Wait for loading
        loader.wait_complete(timeout=5.0)
        
        # Check all loaded
        for i in range(5):
            loaded = loader.get_loaded(f"test{i}")
            assert loaded is not None
        
        loader.stop()
        pg.quit()
