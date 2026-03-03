"""
Asynchronous Resource Loading for Super Mario Bros.

Provides non-blocking resource loading using background threads
to prevent game freezes during asset loading.

Features:
- Background thread loading
- Loading queue with priority
- Progress tracking
- Callback support
- Loading screen integration
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue, Empty
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame as pg

logger = logging.getLogger(__name__)


class LoadPriority(Enum):
    """Loading priority levels."""

    CRITICAL = 0  # Must load immediately
    HIGH = 1  # Important for current level
    NORMAL = 2  # Standard loading
    LOW = 3  # Background/preload


@dataclass(order=True)
class LoadTask:
    """Task for loading queue."""

    priority: int
    name: str = field(compare=False)
    path: str = field(compare=False)
    asset_type: str = field(compare=False)
    callback: Optional[Callable] = field(compare=False, default=None)
    created_at: float = field(default_factory=time.time)


@dataclass
class LoadProgress:
    """Loading progress information."""

    total_items: int = 0
    loaded_items: int = 0
    current_item: str = ""
    progress_percent: float = 0.0
    is_complete: bool = False
    has_error: bool = False
    error_message: str = ""


class AsyncResourceLoader:
    """
    Asynchronous resource loader.

    Loads resources in background thread to prevent
    game freezes during asset loading.

    Example:
        loader = AsyncResourceLoader()
        loader.queue_load("mario", "resources/mario.png", "image")
        loader.start()

        # In game loop:
        progress = loader.get_progress()
        if progress.is_complete:
            # All resources loaded
    """

    def __init__(self, max_workers: int = 2) -> None:
        """
        Initialize async loader.

        Args:
            max_workers: Number of parallel loading threads
        """
        self.max_workers = max_workers
        self._queue: PriorityQueue[LoadTask] = PriorityQueue()
        self._loaded: Dict[str, Any] = {}
        self._failed: Dict[str, str] = {}
        self._progress = LoadProgress()
        self._lock = threading.Lock()
        self._workers: List[threading.Thread] = []
        self._running = False
        self._stop_event = threading.Event()

        # Callbacks
        self._on_item_loaded: Optional[Callable[[str, Any], None]] = None
        self._on_complete: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[str, str], None]] = None

    def queue_load(
        self,
        name: str,
        path: str,
        asset_type: str,
        priority: LoadPriority = LoadPriority.NORMAL,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Queue a resource for loading.

        Args:
            name: Resource identifier
            path: File path
            asset_type: Type (image, sound, music, font)
            priority: Loading priority
            callback: Optional callback when loaded
        """
        task = LoadTask(
            priority=priority.value,
            name=name,
            path=path,
            asset_type=asset_type,
            callback=callback,
        )
        self._queue.put(task)

        with self._lock:
            self._progress.total_items += 1

    def queue_batch(
        self,
        items: List[Tuple[str, str, str]],
        priority: LoadPriority = LoadPriority.NORMAL,
    ) -> None:
        """
        Queue multiple resources for loading.

        Args:
            items: List of (name, path, asset_type) tuples
            priority: Loading priority
        """
        for name, path, asset_type in items:
            self.queue_load(name, path, asset_type, priority)

    def start(self) -> None:
        """Start background loading threads."""
        if self._running:
            return

        self._running = True
        self._stop_event.clear()

        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"ResourceLoader-{i}",
                daemon=True,
            )
            worker.start()
            self._workers.append(worker)

        logger.info(f"Started {self.max_workers} loading threads")

    def stop(self) -> None:
        """Stop background loading threads."""
        self._running = False
        self._stop_event.set()

        # Wait for workers to finish
        for worker in self._workers:
            worker.join(timeout=2.0)

        self._workers.clear()
        logger.info("Stopped loading threads")

    def _worker_loop(self) -> None:
        """Worker thread main loop."""
        while self._running and not self._stop_event.is_set():
            try:
                # Get task with timeout
                task = self._queue.get(timeout=0.5)
            except Empty:
                continue

            # Check if should stop
            if self._stop_event.is_set():
                break

            # Load the resource
            self._load_task(task)

            # Mark task as done
            self._queue.task_done()

    def _load_task(self, task: LoadTask) -> None:
        """Load a single resource."""
        with self._lock:
            self._progress.current_item = task.name

        try:
            # Load based on type
            data: Any
            if task.asset_type == "image":
                data = self._load_image(task.path)
            elif task.asset_type == "sound":
                data = self._load_sound(task.path)
            elif task.asset_type == "music":
                data = self._load_music(task.path)
            elif task.asset_type == "font":
                data = self._load_font(task.path)
            else:
                raise ValueError(f"Unknown asset type: {task.asset_type}")

            # Store loaded resource
            with self._lock:
                self._loaded[task.name] = data
                self._progress.loaded_items += 1
                self._progress.progress_percent = (
                    self._progress.loaded_items / self._progress.total_items * 100
                    if self._progress.total_items > 0
                    else 0
                )

            # Call callback if provided
            if task.callback:
                try:
                    task.callback(task.name, data)
                except Exception as e:
                    logger.error(f"Error in load callback for {task.name}: {e}")

            # Call on_item_loaded callback
            if self._on_item_loaded:
                self._on_item_loaded(task.name, data)

            logger.debug(f"Loaded {task.asset_type}: {task.name}")

        except Exception as e:
            logger.error(f"Failed to load {task.name}: {e}")

            with self._lock:
                self._failed[task.name] = str(e)
                self._progress.has_error = True
                self._progress.error_message = f"Failed: {task.name}"

            if self._on_error:
                self._on_error(task.name, str(e))

        # Check if complete
        self._check_complete()

    def _load_image(self, path: str) -> pg.Surface:
        """Load image resource."""
        surface = pg.image.load(path)
        return surface.convert_alpha()

    def _load_sound(self, path: str) -> pg.mixer.Sound:
        """Load sound resource."""
        return pg.mixer.Sound(path)

    def _load_music(self, path: str) -> str:
        """Load music resource (returns path for streaming)."""
        return path

    def _load_font(self, path: str) -> pg.font.Font:
        """Load font resource."""
        return pg.font.Font(path, 24)

    def _check_complete(self) -> None:
        """Check if loading is complete."""
        with self._lock:
            if self._progress.loaded_items >= self._progress.total_items:
                self._progress.is_complete = True

                if self._on_complete:
                    self._on_complete()

    def get_progress(self) -> LoadProgress:
        """Get current loading progress."""
        with self._lock:
            return LoadProgress(
                total_items=self._progress.total_items,
                loaded_items=self._progress.loaded_items,
                current_item=self._progress.current_item,
                progress_percent=self._progress.progress_percent,
                is_complete=self._progress.is_complete,
                has_error=self._progress.has_error,
                error_message=self._progress.error_message,
            )

    def get_loaded(self, name: str) -> Optional[Any]:
        """Get loaded resource by name."""
        return self._loaded.get(name)

    def get_all_loaded(self) -> Dict[str, Any]:
        """Get all loaded resources."""
        with self._lock:
            return self._loaded.copy()

    def get_failed(self) -> Dict[str, str]:
        """Get failed resources with error messages."""
        with self._lock:
            return self._failed.copy()

    def is_complete(self) -> bool:
        """Check if loading is complete."""
        with self._lock:
            return self._progress.is_complete

    def is_running(self) -> bool:
        """Check if loader is running."""
        return self._running

    def set_on_item_loaded(self, callback: Callable[[str, Any], None]) -> None:
        """Set callback for when an item is loaded."""
        self._on_item_loaded = callback

    def set_on_complete(self, callback: Callable[[], None]) -> None:
        """Set callback for when all loading is complete."""
        self._on_complete = callback

    def set_on_error(self, callback: Callable[[str, str], None]) -> None:
        """Set callback for when an item fails to load."""
        self._on_error = callback

    def wait_complete(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for loading to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if complete, False if timeout
        """
        start_time = time.time()

        while not self.is_complete():
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.01)

        return True


class LoadingScreen:
    """
    Visual loading screen for async loading.

    Displays progress bar and loading status.
    """

    def __init__(
        self,
        screen: pg.Surface,
        font_size: int = 24,
        bar_width: int = 400,
        bar_height: int = 30,
    ) -> None:
        """
        Initialize loading screen.

        Args:
            screen: Surface to draw on
            font_size: Font size for text
            bar_width: Progress bar width
            bar_height: Progress bar height
        """
        self.screen = screen
        self.font = pg.font.Font(None, font_size)
        self.bar_width = bar_width
        self.bar_height = bar_height
        self.bar_rect = pg.Rect(
            (screen.get_width() - bar_width) // 2,
            screen.get_height() // 2,
            bar_width,
            bar_height,
        )

        # Colors
        self.bg_color = (20, 20, 30)
        self.bar_bg_color = (50, 50, 60)
        self.bar_fill_color = (0, 200, 100)
        self.text_color = (255, 255, 255)

    def draw(self, progress: LoadProgress) -> None:
        """
        Draw loading screen.

        Args:
            progress: Current loading progress
        """
        # Clear screen
        self.screen.fill(self.bg_color)

        # Draw title
        title = self.font.render("Loading...", True, self.text_color)
        title_rect = title.get_rect(centerx=self.screen.get_width() // 2, bottom=self.bar_rect.top - 20)
        self.screen.blit(title, title_rect)

        # Draw progress bar background
        pg.draw.rect(self.screen, self.bar_bg_color, self.bar_rect)

        # Draw progress bar fill
        fill_width = int(self.bar_width * progress.progress_percent / 100)
        fill_rect = pg.Rect(self.bar_rect.x, self.bar_rect.y, fill_width, self.bar_rect.height)
        pg.draw.rect(self.screen, self.bar_fill_color, fill_rect)

        # Draw percentage
        percent_text = self.font.render(f"{progress.progress_percent:.0f}%", True, self.text_color)
        percent_rect = percent_text.get_rect(center=self.bar_rect.center)
        self.screen.blit(percent_text, percent_rect)

        # Draw current item
        if progress.current_item:
            item_text = self.font.render(progress.current_item, True, self.text_color)
            item_rect = item_text.get_rect(centerx=self.screen.get_width() // 2, top=self.bar_rect.bottom + 20)
            self.screen.blit(item_text, item_rect)

        # Draw error if exists
        if progress.has_error:
            error_text = self.font.render(f"Error: {progress.error_message}", True, (255, 50, 50))
            error_rect = error_text.get_rect(centerx=self.screen.get_width() // 2, top=self.bar_rect.bottom + 60)
            self.screen.blit(error_text, error_rect)

        pg.display.flip()

    def update(self, progress: LoadProgress) -> bool:
        """
        Update and draw loading screen.

        Args:
            progress: Current loading progress

        Returns:
            True if loading is complete
        """
        self.draw(progress)
        return progress.is_complete


# Global async loader instance
_async_loader: Optional[AsyncResourceLoader] = None
_loading_screen: Optional[LoadingScreen] = None


def get_async_loader() -> AsyncResourceLoader:
    """Get global async loader instance."""
    global _async_loader
    if _async_loader is None:
        _async_loader = AsyncResourceLoader()
    return _async_loader


def get_loading_screen(screen: pg.Surface) -> LoadingScreen:
    """Get global loading screen instance."""
    global _loading_screen
    if _loading_screen is None:
        _loading_screen = LoadingScreen(screen)
    return _loading_screen
