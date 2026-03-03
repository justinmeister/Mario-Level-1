"""
Tests for resource manager system.
"""
import os
import tempfile
from pathlib import Path

import pytest
import pygame as pg

from data.resource_manager import (
    AssetType,
    AssetState,
    AssetInfo,
    AssetConfig,
    ResourceLoader,
    AssetManager,
    SpriteSheet,
    PRESET_CONFIGS,
    create_asset_manager,
    LoadPriority,
    LoadRequest,
    AsyncAssetLoader,
    ResourcePreloader,
)


class TestAssetType:
    """Tests for AssetType enum."""

    def test_asset_types(self) -> None:
        """Test asset type enum values."""
        assert AssetType.IMAGE.value == "image"
        assert AssetType.SOUND.value == "sound"
        assert AssetType.MUSIC.value == "music"
        assert AssetType.FONT.value == "font"
        assert AssetType.DATA.value == "data"


class TestAssetState:
    """Tests for AssetState enum."""

    def test_asset_states(self) -> None:
        """Test asset state enum values."""
        assert AssetState.PENDING.value == "pending"
        assert AssetState.LOADED.value == "loaded"
        assert AssetState.FAILED.value == "failed"


class TestAssetInfo:
    """Tests for AssetInfo dataclass."""

    def test_asset_info_creation(self) -> None:
        """Test creating asset info."""
        info = AssetInfo(name="test_asset", asset_type=AssetType.IMAGE, file_path="/test/path.png")

        assert info.name == "test_asset"
        assert info.asset_type == AssetType.IMAGE
        assert info.state == AssetState.PENDING
        assert info.ref_count == 0

    def test_asset_info_with_metadata(self) -> None:
        """Test asset info with metadata."""
        info = AssetInfo(
            name="test",
            asset_type=AssetType.IMAGE,
            file_path="/test.png",
            metadata={"author": "test", "version": "1.0"},
        )

        assert info.metadata["author"] == "test"


class TestAssetConfig:
    """Tests for AssetConfig."""

    def test_default_config(self) -> None:
        """Test default asset config."""
        config = AssetConfig()

        assert config.max_cache_size_mb == 500
        assert config.auto_unload_time == 300
        assert config.hot_reload is False
        assert config.alpha_convert is True

    def test_custom_config(self) -> None:
        """Test custom asset config."""
        config = AssetConfig(
            max_cache_size_mb=1000,
            hot_reload=True,
            hot_reload_interval=10,
            compress_images=True,
        )

        assert config.max_cache_size_mb == 1000
        assert config.hot_reload is True
        assert config.hot_reload_interval == 10


class TestPresetConfigs:
    """Tests for preset configurations."""

    def test_preset_configs_exist(self) -> None:
        """Test that preset configs exist."""
        assert "development" in PRESET_CONFIGS
        assert "production" in PRESET_CONFIGS
        assert "low_memory" in PRESET_CONFIGS

    def test_development_config(self) -> None:
        """Test development config."""
        config = PRESET_CONFIGS["development"]

        assert config.hot_reload is True
        assert config.max_cache_size_mb == 1000

    def test_production_config(self) -> None:
        """Test production config."""
        config = PRESET_CONFIGS["production"]

        assert config.hot_reload is False
        assert config.compress_images is True


class TestResourceLoader:
    """Tests for ResourceLoader."""

    def test_load_image_nonexistent(self) -> None:
        """Test loading nonexistent image."""
        with pytest.raises(IOError):
            ResourceLoader.load_image("/nonexistent.png")

    def test_load_sound_nonexistent(self) -> None:
        """Test loading nonexistent sound."""
        with pytest.raises(IOError):
            ResourceLoader.load_sound("/nonexistent.wav")

    def test_load_music_nonexistent(self) -> None:
        """Test loading nonexistent music."""
        with pytest.raises(FileNotFoundError):
            ResourceLoader.load_music("/nonexistent.mp3")

    def test_load_data_json(self, tmp_path: Path) -> None:
        """Test loading JSON data."""
        # Create temp JSON file
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')

        data = ResourceLoader.load_data(str(json_file), format="json")

        assert data["key"] == "value"

    def test_load_data_text(self, tmp_path: Path) -> None:
        """Test loading text data."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello World")

        data = ResourceLoader.load_data(str(txt_file), format="txt")

        assert data == "Hello World"


class TestAssetManager:
    """Tests for AssetManager."""

    @pytest.fixture
    def asset_manager(self) -> AssetManager:
        """Create asset manager."""
        return AssetManager()

    @pytest.fixture
    def temp_asset_dir(self) -> Path:
        """Create temporary asset directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create subdirectories
            (path / "graphics").mkdir()
            (path / "sound").mkdir()
            (path / "fonts").mkdir()

            # Create test image
            pg.init()
            surface = pg.Surface((32, 32))
            surface.fill((255, 0, 0))
            pg.image.save(surface, str(path / "graphics" / "test.png"))

            # Create test font
            font = pg.font.Font(None, 24)
            font.render("Test", True, (255, 255, 255))

            pg.quit()

            yield path

    def test_manager_creation(self, asset_manager: AssetManager) -> None:
        """Test asset manager initialization."""
        assert len(asset_manager.assets) == 0
        assert asset_manager.base_path == Path(".")

    def test_set_base_path(self, asset_manager: AssetManager) -> None:
        """Test setting base path."""
        asset_manager.set_base_path("/assets")

        assert asset_manager.base_path == Path("/assets")

    def test_set_directory(self, asset_manager: AssetManager) -> None:
        """Test setting asset directory."""
        asset_manager.set_directory(AssetType.IMAGE, "/custom/graphics")

        assert asset_manager.get_directory(AssetType.IMAGE) == Path("/custom/graphics")

    def test_load_image(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test loading image asset."""
        asset_manager.set_base_path(temp_asset_dir)

        info = asset_manager.load("test_image", "test.png", AssetType.IMAGE)

        assert info.name == "test_image"
        assert info.state == AssetState.LOADED
        assert info.data is not None
        assert isinstance(info.data, pg.Surface)

    def test_load_data(self, asset_manager: AssetManager, tmp_path: Path) -> None:
        """Test loading data asset."""
        # Create temp data file
        data_file = tmp_path / "data.json"
        data_file.write_text('{"score": 100}')

        asset_manager.set_base_path(tmp_path)
        asset_manager.set_directory(AssetType.DATA, Path("."))

        info = asset_manager.load("test_data", "data.json", AssetType.DATA)

        assert info.state == AssetState.LOADED
        assert info.data["score"] == 100

    def test_load_nonexistent(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test loading nonexistent asset."""
        asset_manager.set_base_path(temp_asset_dir)

        info = asset_manager.load("missing", "nonexistent.png", AssetType.IMAGE)

        assert info.state == AssetState.FAILED
        assert "error" in info.metadata

    def test_get_asset(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test getting loaded asset."""
        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        data = asset_manager.get("test")

        assert data is not None
        assert isinstance(data, pg.Surface)

    def test_get_nonexistent_asset(self, asset_manager: AssetManager) -> None:
        """Test getting nonexistent asset."""
        data = asset_manager.get("nonexistent")

        assert data is None

    def test_get_or_load(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test get or load."""
        asset_manager.set_base_path(temp_asset_dir)

        # First call loads
        data1 = asset_manager.get_or_load("test", "test.png", AssetType.IMAGE)

        # Second call gets from cache
        data2 = asset_manager.get_or_load("test", "test.png", AssetType.IMAGE)

        assert data1 is not None
        assert data2 is data1

    def test_load_batch(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test loading batch of assets."""
        asset_manager.set_base_path(temp_asset_dir)

        # Create another test image
        pg.init()
        surface = pg.Surface((32, 32))
        surface.fill((0, 255, 0))
        pg.image.save(surface, str(temp_asset_dir / "graphics" / "test2.png"))
        pg.quit()

        assets = [
            ("img1", "test.png", AssetType.IMAGE),
            ("img2", "test2.png", AssetType.IMAGE),
        ]

        results = asset_manager.load_batch(assets)

        assert len(results) == 2
        assert "img1" in results
        assert "img2" in results

    def test_unload_asset(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test unloading asset."""
        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        # Decrement ref count
        asset_manager.unload("test")

        # Should still be loaded (ref_count was 1, now 0)
        assert "test" in asset_manager.assets

        # Force unload
        asset_manager.unload("test", force=True)

        assert "test" not in asset_manager.assets

    def test_unload_unused(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test unloading unused assets."""
        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        # Manually set ref_count to 0
        asset_manager.assets["test"].ref_count = 0

        count = asset_manager.unload_unused()

        assert count >= 1

    def test_clear_assets(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test clearing all assets."""
        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        asset_manager.clear()

        assert len(asset_manager.assets) == 0

    def test_get_info(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test getting asset info."""
        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        info = asset_manager.get_info("test")

        assert info is not None
        assert info.name == "test"

    def test_get_stats(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test getting statistics."""
        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        stats = asset_manager.get_stats()

        assert "total_assets" in stats
        assert "loaded" in stats
        assert "cache_size_mb" in stats
        assert stats["total_assets"] >= 1

    def test_ref_count_increment(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test reference count increment."""
        asset_manager.set_base_path(temp_asset_dir)

        # Load asset
        asset_manager.load("test", "test.png", AssetType.IMAGE)
        initial_ref = asset_manager.assets["test"].ref_count

        # Get asset (should increment ref count)
        asset_manager.get("test")

        assert asset_manager.assets["test"].ref_count > initial_ref

    def test_load_same_asset_twice(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test loading same asset twice."""
        asset_manager.set_base_path(temp_asset_dir)

        info1 = asset_manager.load("test", "test.png", AssetType.IMAGE)
        info2 = asset_manager.load("test", "test.png", AssetType.IMAGE)

        # Should return same info
        assert info1 is info2
        assert info2.ref_count >= 2

    def test_set_callbacks(self, asset_manager: AssetManager, temp_asset_dir: Path) -> None:
        """Test setting callbacks."""
        load_starts = []
        load_completes = []
        load_errors = []

        asset_manager.set_callbacks(
            on_load_start=lambda name: load_starts.append(name),
            on_load_complete=lambda name: load_completes.append(name),
            on_load_error=lambda name, error: load_errors.append((name, error)),
        )

        asset_manager.set_base_path(temp_asset_dir)
        asset_manager.load("test", "test.png", AssetType.IMAGE)

        assert "test" in load_starts
        assert "test" in load_completes
        assert len(load_errors) == 0


class TestSpriteSheet:
    """Tests for SpriteSheet."""

    @pytest.fixture
    def sprite_sheet(self) -> SpriteSheet:
        """Create sprite sheet."""
        pg.init()

        # Create 64x64 sprite sheet with 4 32x32 sprites
        image = pg.Surface((64, 64))
        image.fill((255, 0, 0))

        pg.quit()

        return SpriteSheet(image, tile_size=(32, 32), margin=0, spacing=0)

    def test_sprite_sheet_creation(self, sprite_sheet: SpriteSheet) -> None:
        """Test sprite sheet initialization."""
        assert sprite_sheet.tile_size == (32, 32)
        assert sprite_sheet.margin == 0
        assert sprite_sheet.spacing == 0

    def test_get_sprite(self, sprite_sheet: SpriteSheet) -> None:
        """Test getting sprite."""
        sprite = sprite_sheet.get_sprite(0, 0)

        assert sprite is not None
        assert sprite.get_size() == (32, 32)

    def test_get_sprite_cached(self, sprite_sheet: SpriteSheet) -> None:
        """Test sprite caching."""
        sprite1 = sprite_sheet.get_sprite(0, 0)
        sprite2 = sprite_sheet.get_sprite(0, 0)

        # Should be cached
        assert sprite1 is sprite2

    def test_get_sprites_in_row(self, sprite_sheet: SpriteSheet) -> None:
        """Test getting sprites from row."""
        sprites = sprite_sheet.get_sprites_in_row(0, 2)

        assert len(sprites) == 2
        assert all(s.get_size() == (32, 32) for s in sprites)

    def test_get_animation_frames(self, sprite_sheet: SpriteSheet) -> None:
        """Test getting animation frames."""
        frames = sprite_sheet.get_animation_frames(0, 0, 2, horizontal=True)

        assert len(frames) == 2
        assert all(f.get_size() == (32, 32) for f in frames)


class TestCreateAssetManager:
    """Tests for create_asset_manager function."""

    def test_create_with_preset(self) -> None:
        """Test creating manager with preset."""
        manager = create_asset_manager("development")

        assert manager.config.hot_reload is True

    def test_create_with_base_path(self) -> None:
        """Test creating manager with base path."""
        manager = create_asset_manager("production", base_path="/assets")

        assert manager.base_path == Path("/assets")

    def test_create_invalid_preset(self) -> None:
        """Test creating manager with invalid preset."""
        manager = create_asset_manager("invalid_preset")

        # Should use default config
        assert manager.config is not None


class TestAssetManagerIntegration:
    """Integration tests for asset manager."""

    def test_full_asset_workflow(self, temp_asset_dir: Path) -> None:
        """Test complete asset workflow."""
        pg.init()

        # Create manager
        manager = create_asset_manager("development", base_path=temp_asset_dir)

        # Load asset
        info = manager.load("player", "test.png", AssetType.IMAGE)
        assert info.state == AssetState.LOADED

        # Get asset
        sprite = manager.get("player")
        assert sprite is not None

        # Get stats
        stats = manager.get_stats()
        assert stats["loaded"] >= 1

        # Unload
        manager.unload("player")
        manager.unload("player", force=True)

        assert len(manager.assets) == 0

        pg.quit()

    def test_asset_with_callbacks(self, temp_asset_dir: Path) -> None:
        """Test asset loading with callbacks."""
        pg.init()

        events = []

        def on_start(name: str) -> None:
            events.append(("start", name))

        def on_complete(name: str) -> None:
            events.append(("complete", name))

        manager = create_asset_manager("production", base_path=temp_asset_dir)
        manager.set_callbacks(on_load_start=on_start, on_load_complete=on_complete)

        manager.load("test", "test.png", AssetType.IMAGE)

        assert ("start", "test") in events
        assert ("complete", "test") in events

        pg.quit()

    def test_sprite_sheet_workflow(self) -> None:
        """Test sprite sheet workflow."""
        pg.init()

        # Create sprite sheet image
        image = pg.Surface((128, 128))
        image.fill((255, 255, 255))

        # Create sprite sheet
        sheet = SpriteSheet(image, tile_size=(32, 32))

        # Get all sprites
        sprites = []
        for y in range(4):
            for x in range(4):
                sprites.append(sheet.get_sprite(x, y))

        assert len(sprites) == 16

        # Get animation frames
        frames = sheet.get_animation_frames(0, 0, 4)
        assert len(frames) == 4

        pg.quit()

    def test_multiple_asset_types(self, temp_asset_dir: Path) -> None:
        """Test loading multiple asset types."""
        pg.init()

        manager = create_asset_manager("production", base_path=temp_asset_dir)

        # Load image
        img_info = manager.load("image", "test.png", AssetType.IMAGE)

        # Create and load data file
        data_file = temp_asset_dir / "data.json"
        data_file.write_text('{"test": true}')
        manager.set_directory(AssetType.DATA, Path("."))
        data_info = manager.load("data", "data.json", AssetType.DATA)

        assert img_info.state == AssetState.LOADED
        assert data_info.state == AssetState.LOADED

        pg.quit()


# Fixtures for async tests
@pytest.fixture
def asset_manager():
    """Create asset manager for async tests."""
    return AssetManager()


@pytest.fixture
def temp_image(tmp_path):
    """Create temporary image file."""
    pg.init()
    image_path = tmp_path / "test_image.png"
    surface = pg.Surface((32, 32))
    surface.fill((255, 0, 0))
    pg.image.save(surface, str(image_path))
    
    class ImageFile:
        def __init__(self, path):
            self.name = str(path)
    
    yield ImageFile(image_path)
    pg.quit()


# Tests for async loading
class TestAsyncAssetLoader:
    """Test async asset loading."""

    def test_async_loader_creation(self, asset_manager):
        """Test async loader initialization."""
        loader = AsyncAssetLoader(asset_manager, num_workers=2)

        assert loader.asset_manager == asset_manager
        assert loader.num_workers == 2
        assert not loader._running

    def test_start_stop_workers(self, asset_manager):
        """Test starting and stopping worker threads."""
        loader = AsyncAssetLoader(asset_manager, num_workers=2)

        loader.start()
        assert loader._running
        assert len(loader._workers) == 2

        loader.stop()
        assert not loader._running

    def test_load_async(self, asset_manager, temp_image):
        """Test async asset loading."""
        loader = AsyncAssetLoader(asset_manager, num_workers=1)
        loader.start()

        loaded_assets = []

        def callback(name, data):
            loaded_assets.append(name)

        loader.load_async("test_async", temp_image.name, AssetType.IMAGE, LoadPriority.HIGH, callback)

        # Wait for completion
        loader.wait_for_completion(timeout=2.0)
        loader.stop()

        assert "test_async" in loaded_assets
        assert asset_manager.get("test_async") is not None

    def test_load_priority(self, asset_manager, temp_image):
        """Test priority-based loading."""
        loader = AsyncAssetLoader(asset_manager, num_workers=1)
        loader.start()

        load_order = []

        def callback(name, data):
            load_order.append(name)

        # Queue in reverse priority order
        loader.load_async("low", temp_image.name, AssetType.IMAGE, LoadPriority.LOW, callback)
        loader.load_async("critical", temp_image.name, AssetType.IMAGE, LoadPriority.CRITICAL, callback)
        loader.load_async("normal", temp_image.name, AssetType.IMAGE, LoadPriority.NORMAL, callback)

        loader.wait_for_completion(timeout=2.0)
        loader.stop()

        # Critical should load first
        assert load_order[0] == "critical"

    def test_load_batch_async(self, asset_manager, temp_image):
        """Test batch async loading."""
        loader = AsyncAssetLoader(asset_manager, num_workers=2)
        loader.start()

        assets = [
            ("batch1", temp_image.name, AssetType.IMAGE, LoadPriority.NORMAL),
            ("batch2", temp_image.name, AssetType.IMAGE, LoadPriority.HIGH),
        ]

        loader.load_batch_async(assets)
        loader.wait_for_completion(timeout=2.0)
        loader.stop()

        assert asset_manager.get("batch1") is not None
        assert asset_manager.get("batch2") is not None

    def test_get_stats(self, asset_manager, temp_image):
        """Test loader statistics."""
        loader = AsyncAssetLoader(asset_manager, num_workers=1)
        loader.start()

        loader.load_async("stats_test", temp_image.name, AssetType.IMAGE)

        # Check stats before completion
        stats = loader.get_stats()
        assert stats["pending"] >= 0

        loader.wait_for_completion(timeout=2.0)
        loader.stop()

        # Check stats after completion
        stats = loader.get_stats()
        assert stats["completed"] > 0

    def test_is_loading(self, asset_manager, temp_image):
        """Test loading status check."""
        loader = AsyncAssetLoader(asset_manager, num_workers=1)
        loader.start()

        assert not loader.is_loading()

        loader.load_async("loading_test", temp_image.name, AssetType.IMAGE)
        # May or may not be loading depending on timing
        # Just check it doesn't crash
        loader.is_loading()

        loader.wait_for_completion(timeout=2.0)
        loader.stop()

    def test_clear_queue(self, asset_manager, temp_image):
        """Test clearing load queue."""
        loader = AsyncAssetLoader(asset_manager, num_workers=1)

        # Queue without starting workers
        loader.load_async("clear1", temp_image.name, AssetType.IMAGE)
        loader.load_async("clear2", temp_image.name, AssetType.IMAGE)

        loader.clear_queue()

        stats = loader.get_stats()
        assert stats["pending"] == 0


class TestResourcePreloader:
    """Test resource preloader."""

    def test_preloader_creation(self, asset_manager):
        """Test preloader initialization."""
        preloader = ResourcePreloader(asset_manager)

        assert preloader.asset_manager == asset_manager
        assert preloader.get_progress() == 1.0

    def test_preload_assets(self, asset_manager, temp_image):
        """Test preloading assets."""
        preloader = ResourcePreloader(asset_manager)

        assets = [
            ("preload1", temp_image.name, AssetType.IMAGE),
            ("preload2", temp_image.name, AssetType.IMAGE),
        ]

        results = preloader.preload(assets)

        assert len(results) == 2
        assert "preload1" in results
        assert "preload2" in results
        assert preloader.get_progress() == 1.0

    def test_preload_with_progress(self, asset_manager, temp_image):
        """Test preloading with progress callback."""
        preloader = ResourcePreloader(asset_manager)

        progress_updates = []

        def progress_callback(progress, asset_name):
            progress_updates.append((progress, asset_name))

        assets = [
            ("progress1", temp_image.name, AssetType.IMAGE),
            ("progress2", temp_image.name, AssetType.IMAGE),
        ]

        preloader.preload(assets, progress_callback)

        assert len(progress_updates) == 2
        assert progress_updates[0][0] == 0.5  # 50% after first asset
        assert progress_updates[1][0] == 1.0  # 100% after second asset

    def test_get_current_asset(self, asset_manager, temp_image):
        """Test getting current asset name."""
        preloader = ResourcePreloader(asset_manager)

        assets = [("current_test", temp_image.name, AssetType.IMAGE)]

        preloader.preload(assets)

        assert preloader.get_current_asset() == "current_test"


class TestLoadPriority:
    """Test load priority enum."""

    def test_priority_values(self):
        """Test priority value ordering."""
        assert LoadPriority.CRITICAL.value < LoadPriority.HIGH.value
        assert LoadPriority.HIGH.value < LoadPriority.NORMAL.value
        assert LoadPriority.NORMAL.value < LoadPriority.LOW.value

    def test_load_request_comparison(self):
        """Test load request priority comparison."""
        req1 = LoadRequest(LoadPriority.CRITICAL, "test1", "path1", AssetType.IMAGE)
        req2 = LoadRequest(LoadPriority.LOW, "test2", "path2", AssetType.IMAGE)

        assert req1 < req2  # Critical has higher priority (lower value)
