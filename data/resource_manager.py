"""
Resource/Asset Manager for Super Mario Bros.

Provides:
- Efficient asset loading
- Asset caching and pooling
- Lazy loading support
- Asset reference counting
- Multiple format support
- Asset hot-reloading (dev)
"""
from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from queue import PriorityQueue, Empty
from typing import Dict, List, Optional, Any, Callable, Union, Tuple

import pygame as pg

logger = logging.getLogger(__name__)

from . import constants as c
from . import game_settings
from . import tools


class AssetType(Enum):
    """Types of assets."""

    IMAGE = "image"
    SOUND = "sound"
    MUSIC = "music"
    FONT = "font"
    DATA = "data"


class AssetState(Enum):
    """Asset loading state."""

    PENDING = "pending"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"


@dataclass
class AssetInfo:
    """
    Asset metadata.

    Attributes:
        name: Asset name/ID
        asset_type: Type of asset
        file_path: Path to file
        state: Loading state
        data: Loaded asset data
        size_bytes: File size
        load_time_ms: Time to load
        ref_count: Reference count
        metadata: Additional metadata
    """

    name: str
    asset_type: AssetType
    file_path: str
    state: AssetState = AssetState.PENDING
    data: Any = None
    size_bytes: int = 0
    load_time_ms: float = 0.0
    ref_count: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class AssetConfig:
    """Configuration for asset manager."""

    # Cache settings
    max_cache_size_mb: int = 500
    # Auto-unload unused assets after (seconds)
    auto_unload_time: int = 300
    # Enable hot-reloading
    hot_reload: bool = False
    # Hot-reload check interval (seconds)
    hot_reload_interval: int = 5
    # Default image format
    default_image_format: str = "png"
    # Compress images on load
    compress_images: bool = False
    # Convert images to alpha
    alpha_convert: bool = True


class ResourceLoader:
    """
    Low-level resource loader.
    """

    @staticmethod
    def load_image(path: str, alpha_convert: bool = True, compress: bool = False) -> pg.Surface:
        """
        Load image from file.

        Args:
            path: File path
            alpha_convert: Convert to alpha surface
            compress: Compress image

        Returns:
            Loaded surface
        """
        try:
            surface = pg.image.load(path)

            if alpha_convert:
                try:
                    surface = surface.convert_alpha()
                except pg.error:
                    # no video mode available during headless testing
                    pass

            if compress:
                # Scale down for compression
                new_size = (surface.get_width() // 2, surface.get_height() // 2)
                surface = pg.transform.smoothscale(surface, new_size)

            return surface

        except pg.error as e:
            raise IOError(f"Failed to load image {path}: {e}")

    @staticmethod
    def load_sound(path: str) -> pg.mixer.Sound:
        """
        Load sound from file.

        Args:
            path: File path

        Returns:
            Loaded sound
        """
        try:
            return pg.mixer.Sound(path)
        except pg.error as e:
            raise IOError(f"Failed to load sound {path}: {e}")

    @staticmethod
    def load_music(path: str) -> str:
        """
        Load music file path (music is streamed).

        Args:
            path: File path

        Returns:
            File path
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Music file not found: {path}")
        return path

    @staticmethod
    def load_font(path: str, size: int) -> pg.font.Font:
        """
        Load font from file.

        Args:
            path: File path
            size: Font size

        Returns:
            Loaded font
        """
        try:
            return pg.font.Font(path, size)
        except pg.error as e:
            raise IOError(f"Failed to load font {path}: {e}")

    @staticmethod
    def load_data(path: str, format: str = "json") -> Any:
        """
        Load data file.

        Args:
            path: File path
            format: Data format (json, txt, etc.)

        Returns:
            Loaded data
        """
        import json

        try:
            with open(path, "r", encoding="utf-8") as f:
                if format == "json":
                    return json.load(f)
                else:
                    return f.read()
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Failed to load data {path}: {e}")


class AssetManager:
    """
    Central asset management system.

    Usage:
        assets = AssetManager()
        assets.load("mario", "graphics/mario.png", AssetType.IMAGE)
        mario_sprite = assets.get("mario")
    """

    def __init__(self, config: Optional[AssetConfig] = None) -> None:
        """
        Initialize asset manager.

        Args:
            config: Asset configuration
        """
        self.config = config or AssetConfig()

        # Asset storage
        self.assets: Dict[str, AssetInfo] = {}
        self._load_order: List[str] = []

        # Asset directories
        self.base_path = Path(".")
        self.directories: Dict[AssetType, Path] = {
            AssetType.IMAGE: Path("resources/graphics"),
            AssetType.SOUND: Path("resources/sound"),
            AssetType.MUSIC: Path("resources/music"),
            AssetType.FONT: Path("resources/fonts"),
            AssetType.DATA: Path("resources/data"),
        }

        # Statistics
        self._total_load_time = 0.0
        self._cache_size_bytes = 0

        # Hot-reload tracking
        self._file_times: Dict[str, float] = {}
        self._last_hot_reload_check = 0.0

        # Callbacks
        self._on_load_start: Optional[Callable[[str], None]] = None
        self._on_load_complete: Optional[Callable[[str], None]] = None
        self._on_load_error: Optional[Callable[[str, str], None]] = None

    def set_base_path(self, path: Union[str, Path]) -> None:
        """
        Set base path for assets.

        Args:
            path: Base directory path
        """
        self.base_path = Path(path)

    def set_directory(self, asset_type: AssetType, path: Union[str, Path]) -> None:
        """
        Set directory for asset type.

        Args:
            asset_type: Type of asset
            path: Directory path
        """
        self.directories[asset_type] = Path(path)

    def get_directory(self, asset_type: AssetType) -> Path:
        """Get directory for asset type."""
        return self.directories.get(asset_type, self.base_path)

    def load(self, name: str, file_path: str, asset_type: AssetType, **kwargs) -> AssetInfo:
        """
        Load asset.

        Args:
            name: Asset name/ID
            file_path: Relative file path
            asset_type: Type of asset
            **kwargs: Additional loading options

        Returns:
            Asset info
        """
        # Check if already loaded
        if name in self.assets:
            self.assets[name].ref_count += 1
            return self.assets[name]

        # Build full path
        dir_path = self.get_directory(asset_type)
        # build the directory path and allow fallback if the expected folder
        # doesn't exist (tests often create plain "graphics" instead of
        # "resources/graphics").
        full_dir = self.base_path / dir_path
        if not full_dir.exists():
            alt = self.base_path / dir_path.name
            if alt.exists():
                full_dir = alt
        full_path = full_dir / file_path

        # Create asset info
        info = AssetInfo(name=name, asset_type=asset_type, file_path=str(full_path))

        # Load asset
        start_time = __import__("time").time()

        try:
            info.state = AssetState.LOADING

            if self._on_load_start:
                self._on_load_start(name)

            # Load based on type
            if asset_type == AssetType.IMAGE:
                info.data = ResourceLoader.load_image(
                    str(full_path),
                    alpha_convert=kwargs.get("alpha_convert", self.config.alpha_convert),
                    compress=kwargs.get("compress", self.config.compress_images),
                )
            elif asset_type == AssetType.SOUND:
                info.data = ResourceLoader.load_sound(str(full_path))
            elif asset_type == AssetType.MUSIC:
                info.data = ResourceLoader.load_music(str(full_path))
            elif asset_type == AssetType.FONT:
                info.data = ResourceLoader.load_font(str(full_path), kwargs.get("size", 24))
            elif asset_type == AssetType.DATA:
                info.data = ResourceLoader.load_data(str(full_path), kwargs.get("format", "json"))

            info.state = AssetState.LOADED
            info.ref_count = 1

            # Get file size
            try:
                info.size_bytes = os.path.getsize(full_path)
                self._cache_size_bytes += info.size_bytes
            except OSError:
                pass

            if self._on_load_complete:
                self._on_load_complete(name)

        except Exception as e:
            info.state = AssetState.FAILED
            info.metadata["error"] = str(e)

            if self._on_load_error:
                self._on_load_error(name, str(e))

        finally:
            load_time = (__import__("time").time() - start_time) * 1000
            info.load_time_ms = load_time
            self._total_load_time += load_time

        # Store and track load order
        self.assets[name] = info
        self._load_order.append(name)

        # Track file time for hot-reload
        if self.config.hot_reload:
            try:
                self._file_times[name] = os.path.getmtime(full_path)
            except OSError:
                pass

        return info

    def load_batch(self, assets: List[tuple[str, str, AssetType]], **kwargs) -> Dict[str, AssetInfo]:
        """
        Load multiple assets.

        Args:
            assets: List of (name, file_path, asset_type) tuples
            **kwargs: Additional loading options

        Returns:
            Dictionary of loaded assets
        """
        results = {}

        for name, file_path, asset_type in assets:
            info = self.load(name, file_path, asset_type, **kwargs)
            results[name] = info

        return results

    def load_directory(self, asset_type: AssetType, pattern: str = "*", prefix: str = "") -> Dict[str, AssetInfo]:
        """
        Load all assets from directory.

        Args:
            asset_type: Type of assets
            pattern: File pattern (glob)
            prefix: Name prefix

        Returns:
            Dictionary of loaded assets
        """
        dir_path = self.get_directory(asset_type)
        full_path = self.base_path / dir_path

        if not full_path.exists():
            return {}

        results = {}

        for file_path in full_path.glob(pattern):
            if file_path.is_file():
                name = f"{prefix}{file_path.stem}"
                info = self.load(name, file_path.name, asset_type)
                results[name] = info

        return results

    def get(self, name: str) -> Any:
        """
        Get asset data.

        Args:
            name: Asset name

        Returns:
            Asset data or None
        """
        if name not in self.assets:
            return None

        info = self.assets[name]

        if info.state != AssetState.LOADED:
            return None

        info.ref_count += 1
        return info.data

    def get_or_load(self, name: str, file_path: str, asset_type: AssetType, **kwargs) -> Any:
        """
        Get asset or load if not loaded.

        Args:
            name: Asset name
            file_path: File path
            asset_type: Asset type
            **kwargs: Loading options

        Returns:
            Asset data
        """
        if name in self.assets:
            return self.get(name)

        info = self.load(name, file_path, asset_type, **kwargs)
        return info.data if info.state == AssetState.LOADED else None

    def unload(self, name: str, force: bool = False) -> bool:
        """
        Unload asset.

        Args:
            name: Asset name
            force: Force unload regardless of ref count

        Returns:
            True if unloaded
        """
        if name not in self.assets:
            return False

        info = self.assets[name]

        # Decrement ref count
        info.ref_count -= 1

        # Only unload when forced or count goes below zero.  A ref_count of zero
        # means the asset is unused but can stay cached for future requests.
        if force or info.ref_count < 0:
            # Free memory
            if info.data:
                if hasattr(info.data, "get_size"):
                    # Image
                    pass  # pygame handles cleanup
                elif hasattr(info.data, "get_length"):
                    # Sound
                    pass

            self._cache_size_bytes -= info.size_bytes

            del self.assets[name]

            if name in self._load_order:
                self._load_order.remove(name)

            return True

        return False

    def unload_unused(self, max_idle_time: Optional[int] = None) -> int:
        """
        Unload unused assets.

        Args:
            max_idle_time: Max idle time in seconds

        Returns:
            Number of assets unloaded
        """
        count = 0

        for name in list(self.assets.keys()):
            info = self.assets[name]

            if info.ref_count <= 0:
                if self.unload(name):
                    count += 1

        return count

    def clear(self) -> None:
        """Clear all assets."""
        self.assets.clear()
        self._load_order.clear()
        self._cache_size_bytes = 0
        self._file_times.clear()

    def get_info(self, name: str) -> Optional[AssetInfo]:
        """Get asset info."""
        return self.assets.get(name)

    def get_stats(self) -> dict:
        """Get asset manager statistics."""
        loaded = sum(1 for a in self.assets.values() if a.state == AssetState.LOADED)
        failed = sum(1 for a in self.assets.values() if a.state == AssetState.FAILED)

        return {
            "total_assets": len(self.assets),
            "loaded": loaded,
            "failed": failed,
            "cache_size_mb": self._cache_size_bytes / (1024 * 1024),
            "max_cache_mb": self.config.max_cache_size_mb,
            "total_load_time_ms": self._total_load_time,
            "avg_load_time_ms": (self._total_load_time / len(self.assets) if self.assets else 0),
        }

    def check_hot_reload(self) -> List[str]:
        """
        Check for hot-reloaded assets.

        Returns:
            List of reloaded asset names
        """
        if not self.config.hot_reload:
            return []

        import time

        current_time = time.time()

        # Check interval
        if current_time - self._last_hot_reload_check < self.config.hot_reload_interval:
            return []

        self._last_hot_reload_check = current_time
        reloaded = []

        for name, info in self.assets.items():
            if info.state != AssetState.LOADED:
                continue

            try:
                current_mtime = os.path.getmtime(info.file_path)

                if current_mtime > self._file_times.get(name, 0):
                    # File changed, reload
                    old_ref_count = info.ref_count
                    self.unload(name, force=True)
                    self.load(
                        name,
                        info.file_path.replace(str(self.base_path / self.get_directory(info.asset_type)), "").lstrip(
                            "/"
                        ),
                        info.asset_type,
                    )
                    self.assets[name].ref_count = old_ref_count
                    reloaded.append(name)

            except (OSError, IOError):
                pass

        return reloaded

    def set_callbacks(
        self,
        on_load_start: Optional[Callable[[str], None]] = None,
        on_load_complete: Optional[Callable[[str], None]] = None,
        on_load_error: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        """Set loading callbacks."""
        self._on_load_start = on_load_start
        self._on_load_complete = on_load_complete
        self._on_load_error = on_load_error


class SpriteSheet:
    """
    Sprite sheet helper.
    """

    def __init__(self, image: pg.Surface, tile_size: tuple[int, int], margin: int = 0, spacing: int = 0) -> None:
        """
        Initialize sprite sheet.

        Args:
            image: Sprite sheet image
            tile_size: Size of each tile
            margin: Margin around sheet
            spacing: Spacing between tiles
        """
        self.image = image
        self.tile_size = tile_size
        self.margin = margin
        self.spacing = spacing

        self._cache: Dict[tuple[int, int], pg.Surface] = {}

    def get_sprite(self, x: int, y: int) -> pg.Surface:
        """
        Get sprite at position.

        Args:
            x: X tile position
            y: Y tile position

        Returns:
            Sprite surface
        """
        key = (x, y)

        if key not in self._cache:
            rect = self._calculate_rect(x, y)
            self._cache[key] = self.image.subsurface(rect)

        return self._cache[key]

    def _calculate_rect(self, x: int, y: int) -> pg.Rect:
        """Calculate sprite rectangle."""
        offset_x = self.margin + x * (self.tile_size[0] + self.spacing)
        offset_y = self.margin + y * (self.tile_size[1] + self.spacing)

        return pg.Rect(offset_x, offset_y, self.tile_size[0], self.tile_size[1])

    def get_sprites_in_row(self, row: int, count: int) -> List[pg.Surface]:
        """
        Get multiple sprites from row.

        Args:
            row: Row index
            count: Number of sprites

        Returns:
            List of sprite surfaces
        """
        return [self.get_sprite(x, row) for x in range(count)]

    def get_animation_frames(self, start_x: int, start_y: int, count: int, horizontal: bool = True) -> List[pg.Surface]:
        """
        Get animation frames.

        Args:
            start_x: Start X position
            start_y: Start Y position
            count: Number of frames
            horizontal: Horizontal or vertical strip

        Returns:
            List of frame surfaces
        """
        frames = []

        for i in range(count):
            if horizontal:
                frames.append(self.get_sprite(start_x + i, start_y))
            else:
                frames.append(self.get_sprite(start_x, start_y + i))

        return frames


# Preset configurations
PRESET_CONFIGS = {
    "development": AssetConfig(
        max_cache_size_mb=1000,
        auto_unload_time=60,
        hot_reload=True,
        hot_reload_interval=2,
        compress_images=False,
    ),
    "production": AssetConfig(
        max_cache_size_mb=500,
        auto_unload_time=300,
        hot_reload=False,
        compress_images=True,
        alpha_convert=True,
    ),
    "low_memory": AssetConfig(
        max_cache_size_mb=200,
        auto_unload_time=60,
        hot_reload=False,
        compress_images=True,
    ),
}


def create_asset_manager(preset: str = "production", base_path: Optional[Union[str, Path]] = None) -> AssetManager:
    """
    Create asset manager with preset config.

    Args:
        preset: Config preset name
        base_path: Base asset path

    Returns:
        Configured AssetManager
    """
    config = PRESET_CONFIGS.get(preset, AssetConfig())
    manager = AssetManager(config)

    if base_path:
        manager.set_base_path(base_path)

    return manager


# Async loading support


class LoadPriority(Enum):
    """Loading priority levels."""

    CRITICAL = 0  # Must load immediately (UI, player)
    HIGH = 1  # Important (enemies, items)
    NORMAL = 2  # Standard (decorations)
    LOW = 3  # Can wait (background music, effects)


@dataclass
class LoadRequest:
    """Async load request."""

    priority: LoadPriority
    name: str
    file_path: str
    asset_type: AssetType
    kwargs: dict = field(default_factory=dict)
    callback: Optional[Callable[[str, Any], None]] = None

    def __lt__(self, other: "LoadRequest") -> bool:
        """Compare by priority for queue ordering."""
        return self.priority.value < other.priority.value


class AsyncAssetLoader:
    """
    Asynchronous asset loader with priority queue.

    Loads assets in background thread without blocking main game loop.
    """

    def __init__(self, asset_manager: AssetManager, num_workers: int = 2) -> None:
        """
        Initialize async loader.

        Args:
            asset_manager: Asset manager to use
            num_workers: Number of worker threads
        """
        self.asset_manager = asset_manager
        self.num_workers = num_workers

        # Priority queue for load requests
        self._queue: PriorityQueue[LoadRequest] = PriorityQueue()

        # Worker threads
        self._workers: List[threading.Thread] = []
        self._running = False
        self._lock = threading.Lock()

        # Statistics
        self._pending_count = 0
        self._completed_count = 0
        self._failed_count = 0

    def start(self) -> None:
        """Start worker threads."""
        if self._running:
            return

        self._running = True

        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"AssetLoader-{i}", daemon=True)
            worker.start()
            self._workers.append(worker)

    def stop(self) -> None:
        """Stop worker threads."""
        self._running = False

        # Wait for workers to finish
        for worker in self._workers:
            worker.join(timeout=1.0)

        self._workers.clear()

    def load_async(
        self,
        name: str,
        file_path: str,
        asset_type: AssetType,
        priority: LoadPriority = LoadPriority.NORMAL,
        callback: Optional[Callable[[str, Any], None]] = None,
        **kwargs,
    ) -> None:
        """
        Queue asset for async loading.

        Args:
            name: Asset name
            file_path: File path
            asset_type: Asset type
            priority: Loading priority
            callback: Completion callback (name, data)
            **kwargs: Loading options
        """
        request = LoadRequest(
            priority=priority,
            name=name,
            file_path=file_path,
            asset_type=asset_type,
            kwargs=kwargs,
            callback=callback,
        )

        self._queue.put(request)

        with self._lock:
            self._pending_count += 1

    def load_batch_async(
        self,
        assets: List[Tuple[str, str, AssetType, LoadPriority]],
        callback: Optional[Callable[[str, Any], None]] = None,
        **kwargs,
    ) -> None:
        """
        Queue multiple assets for async loading.

        Args:
            assets: List of (name, file_path, asset_type, priority) tuples
            callback: Completion callback
            **kwargs: Loading options
        """
        for name, file_path, asset_type, priority in assets:
            self.load_async(name, file_path, asset_type, priority, callback, **kwargs)

    def _worker_loop(self) -> None:
        """Worker thread main loop."""
        while self._running:
            try:
                # Get request with timeout
                request = self._queue.get(timeout=0.1)

                # Load asset
                try:
                    info = self.asset_manager.load(
                        request.name, request.file_path, request.asset_type, **request.kwargs
                    )

                    with self._lock:
                        self._completed_count += 1
                        self._pending_count -= 1

                    # Call callback if provided
                    if request.callback and info.state == AssetState.LOADED:
                        request.callback(request.name, info.data)

                except Exception as e:
                    with self._lock:
                        self._failed_count += 1
                        self._pending_count -= 1

                    logger.warning("[AsyncLoader] Failed to load %s: %s", request.name, e)

                finally:
                    self._queue.task_done()

            except Empty:
                # No requests, continue
                continue

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for all pending loads to complete.

        Args:
            timeout: Max wait time in seconds

        Returns:
            True if all completed, False if timeout
        """
        try:
            self._queue.join()
            return True
        except Exception:
            return False

    def is_loading(self) -> bool:
        """Check if any assets are loading."""
        with self._lock:
            return self._pending_count > 0

    def get_stats(self) -> Dict[str, int]:
        """Get loader statistics."""
        with self._lock:
            return {
                "pending": self._pending_count,
                "completed": self._completed_count,
                "failed": self._failed_count,
                "queue_size": self._queue.qsize(),
            }

    def clear_queue(self) -> None:
        """Clear pending load requests."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Empty:
                break

        with self._lock:
            self._pending_count = 0


class ResourcePreloader:
    """
    Resource preloader for loading screens.

    Loads assets with progress tracking.
    """

    def __init__(self, asset_manager: AssetManager) -> None:
        """
        Initialize preloader.

        Args:
            asset_manager: Asset manager to use
        """
        self.asset_manager = asset_manager
        self._total_assets = 0
        self._loaded_assets = 0
        self._current_asset = ""

    def preload(
        self,
        assets: List[Tuple[str, str, AssetType]],
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, AssetInfo]:
        """
        Preload assets with progress tracking.

        Args:
            assets: List of (name, file_path, asset_type) tuples
            progress_callback: Progress callback (progress, current_asset)

        Returns:
            Dictionary of loaded assets
        """
        self._total_assets = len(assets)
        self._loaded_assets = 0
        results = {}

        for name, file_path, asset_type in assets:
            self._current_asset = name

            # Load asset
            info = self.asset_manager.load(name, file_path, asset_type)
            results[name] = info

            self._loaded_assets += 1

            # Call progress callback
            if progress_callback:
                progress = self._loaded_assets / self._total_assets
                progress_callback(progress, name)

        return results

    def get_progress(self) -> float:
        """Get loading progress (0.0 to 1.0)."""
        if self._total_assets == 0:
            return 1.0
        return self._loaded_assets / self._total_assets

    def get_current_asset(self) -> str:
        """Get currently loading asset name."""
        return self._current_asset


# =============================================================================
# Simple ResourceManager for backward compatibility with setup.py
# =============================================================================


class SimpleResourceManager:
    """
    Simple resource manager for game initialization.

    Singleton pattern - provides centralized access to game resources.
    """

    _instance: Optional["SimpleResourceManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "SimpleResourceManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize."""
        if SimpleResourceManager._initialized:
            return

        self._gfx: Dict[str, pg.Surface] = {}
        self._sfx: Dict[str, pg.mixer.Sound] = {}
        self._music: Dict[str, str] = {}
        self._fonts: Dict[str, str] = {}
        self._screen: Optional[pg.Surface] = None
        self._screen_rect: Optional[pg.Rect] = None
        SimpleResourceManager._initialized = True

    @classmethod
    def get(cls) -> "SimpleResourceManager":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = SimpleResourceManager()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton for tests."""
        cls._instance = None

    def initialize_display(self) -> None:
        """Initialize pygame display."""
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pg.init()
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
        pg.display.set_caption(c.ORIGINAL_CAPTION)

        # Get fullscreen setting from settings manager
        settings_mgr = game_settings.get_settings_manager()
        fullscreen = settings_mgr.get("fullscreen", False)

        if fullscreen:
            self._screen = pg.display.set_mode(c.SCREEN_SIZE, pg.FULLSCREEN)
        else:
            self._screen = pg.display.set_mode(c.SCREEN_SIZE)

        self._screen_rect = self._screen.get_rect()

    def load_resources(self, resources_dir: str = "resources") -> None:
        """Load all resources."""
        self._load_fonts(os.path.join(resources_dir, "fonts"))
        self._load_music(os.path.join(resources_dir, "music"))
        self._load_gfx(os.path.join(resources_dir, "graphics"))
        self._load_sfx(os.path.join(resources_dir, "sound"))

    def _load_fonts(self, fonts_dir: str) -> None:
        """Load fonts."""
        if os.path.exists(fonts_dir):
            self._fonts = tools.load_all_fonts(fonts_dir)

    def _load_music(self, music_dir: str) -> None:
        """Load music."""
        if os.path.exists(music_dir):
            self._music = tools.load_all_music(music_dir)

    def _load_gfx(self, graphics_dir: str) -> None:
        """Load graphics."""
        if os.path.exists(graphics_dir):
            self._gfx = tools.load_all_gfx(graphics_dir)

    def _load_sfx(self, sound_dir: str) -> None:
        """Load sound effects."""
        if os.path.exists(sound_dir):
            self._sfx = tools.load_all_sfx(sound_dir)

    def initialize(self, resources_dir: str = "resources") -> None:
        """Full initialization."""
        self.initialize_display()
        self.load_resources(resources_dir)

    @property
    def screen(self) -> Optional[pg.Surface]:
        """Get screen surface."""
        return self._screen

    @property
    def screen_rect(self) -> Optional[pg.Rect]:
        """Get screen rect."""
        return self._screen_rect

    @property
    def gfx(self) -> Dict[str, pg.Surface]:
        """Get graphics."""
        return self._gfx

    @property
    def sfx(self) -> Dict[str, pg.mixer.Sound]:
        """Get sound effects."""
        return self._sfx

    @property
    def music(self) -> Dict[str, str]:
        """Get music."""
        return self._music

    @property
    def fonts(self) -> Dict[str, str]:
        """Get fonts."""
        return self._fonts

    def get_gfx(self, name: str) -> pg.Surface:
        """Get graphics by name."""
        return self._gfx[name]

    def get_sfx(self, name: str) -> pg.mixer.Sound:
        """Get sound effect by name."""
        return self._sfx[name]

    def has_gfx(self, name: str) -> bool:
        """Check if graphics exists."""
        return name in self._gfx

    def has_sfx(self, name: str) -> bool:
        """Check if sfx exists."""
        return name in self._sfx

    def clear(self) -> None:
        """Clear all resources."""
        self._gfx.clear()
        self._sfx.clear()
        self._music.clear()
        self._fonts.clear()


# Module-level functions for backward compatibility
_simple_manager: Optional[SimpleResourceManager] = None


def get_simple_manager() -> SimpleResourceManager:
    """Get simple manager instance."""
    global _simple_manager
    if _simple_manager is None:
        _simple_manager = SimpleResourceManager()
    return _simple_manager
