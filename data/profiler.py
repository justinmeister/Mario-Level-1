"""
Performance Profiling System for Super Mario Bros.

Features:
- Frame time profiling
- Function timing
- Memory tracking
- FPS statistics
- Performance logging
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple, TypeVar

import pygame as pg

T = TypeVar("T")


@dataclass
class FrameStats:
    """Statistics for a single frame."""

    frame_number: int
    frame_time: float  # ms
    fps: float
    timestamp: float

    # Sub-system timings
    update_time: float = 0.0
    render_time: float = 0.0
    event_time: float = 0.0
    collision_time: float = 0.0

    # Counts
    sprite_count: int = 0
    particle_count: int = 0
    draw_calls: int = 0

    # Slow frame marker
    slow_frames: int = 0


@dataclass
class ProfilerStats:
    """Aggregated profiler statistics."""

    fps_avg: float = 0.0
    fps_min: float = 0.0
    fps_max: float = 0.0
    frame_time_avg: float = 0.0
    frame_time_max: float = 0.0
    total_frames: int = 0
    slow_frames: int = 0  # Frames > threshold

    # Sub-system averages
    update_time_avg: float = 0.0
    render_time_avg: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fps_avg": round(self.fps_avg, 2),
            "fps_min": round(self.fps_min, 2),
            "fps_max": round(self.fps_max, 2),
            "frame_time_avg": round(self.frame_time_avg, 2),
            "frame_time_max": round(self.frame_time_max, 2),
            "total_frames": self.total_frames,
            "slow_frames": self.slow_frames,
            "update_time_avg": round(self.update_time_avg, 2),
            "render_time_avg": round(self.render_time_avg, 2),
        }


class FunctionTimer:
    """Timer for profiling function execution."""

    def __init__(self, name: str) -> None:
        """
        Initialize function timer.

        Args:
            name: Name of function being timed
        """
        self.name = name
        self.total_time: float = 0.0
        self.call_count: int = 0
        self.min_time: float = float("inf")
        self.max_time: float = 0.0
        self._start_time: float = 0.0

    def start(self) -> None:
        """Start timing."""
        self._start_time = time.perf_counter() * 1000

    def stop(self) -> float:
        """
        Stop timing and record result.

        Returns:
            Elapsed time in ms
        """
        elapsed = (time.perf_counter() * 1000) - self._start_time
        self.total_time += elapsed
        self.call_count += 1
        self.min_time = min(self.min_time, elapsed)
        self.max_time = max(self.max_time, elapsed)
        return elapsed

    @property
    def avg_time(self) -> float:
        """Get average execution time."""
        if self.call_count == 0:
            return 0.0
        return self.total_time / self.call_count

    def reset(self) -> None:
        """Reset timer."""
        self.total_time = 0.0
        self.call_count = 0
        self.min_time = float("inf")
        self.max_time = 0.0


class Profiler:
    """
    Main profiler class for performance monitoring.

    Features:
    - FPS tracking
    - Frame time profiling
    - Function timing
    - Memory tracking
    - Performance alerts

    Usage:
        profiler = Profiler()
        profiler.start()

        while running:
            with profiler.profile('update'):
                game.update()

            with profiler.profile('render'):
                game.render()

            profiler.end_frame()
    """

    def __init__(
        self,
        history_size: int = 60,
        slow_frame_threshold: float = 33.0,  # Below 30 FPS
    ) -> None:
        """
        Initialize profiler.

        Args:
            history_size: Number of frames to track for averages
            slow_frame_threshold: Frame time threshold for slow frame
        """
        self.history_size = history_size
        self.slow_frame_threshold = slow_frame_threshold

        # Frame history
        self._frame_history: Deque[FrameStats] = deque(maxlen=history_size)
        self._current_frame: int = 0

        # Timing
        self._frame_start: float = 0.0
        self._running: bool = False

        # Function timers
        self._timers: Dict[str, FunctionTimer] = {}

        # Current section timing
        self._section_stack: List[Tuple[str, float]] = []
        self._section_times: Dict[str, float] = {}

        # Callbacks
        self._slow_frame_callbacks: List[Callable[[FrameStats], None]] = []

        # Display
        self._show_overlay: bool = False
        self._font: Optional[pg.font.Font] = None

    def start(self) -> None:
        """Start profiling."""
        self._running = True
        self._frame_start = time.perf_counter() * 1000

    def stop(self) -> None:
        """Stop profiling."""
        self._running = False

    def profile(self, name: str) -> "ProfilerSection":
        """
        Profile a code section.

        Args:
            name: Section name

        Returns:
            Context manager for timing
        """
        return ProfilerSection(self, name)

    def _begin_section(self, name: str) -> None:
        """Begin timing section."""
        start_time = time.perf_counter() * 1000
        self._section_stack.append((name, start_time))

    def _end_section(self, name: str) -> float:
        """
        End timing section.

        Returns:
            Elapsed time in ms
        """
        if not self._section_stack:
            return 0.0

        # Find matching section
        for i in range(len(self._section_stack) - 1, -1, -1):
            if self._section_stack[i][0] == name:
                _, start_time = self._section_stack.pop(i)
                elapsed = (time.perf_counter() * 1000) - start_time

                # Accumulate time
                if name in self._section_times:
                    self._section_times[name] += elapsed
                else:
                    self._section_times[name] = elapsed

                return elapsed

        return 0.0

    def time_function(self, name: str) -> Callable[[T], T]:
        """
        Decorator for timing function execution.

        Args:
            name: Timer name

        Returns:
            Decorated function
        """
        from typing import TypeVar

        T = TypeVar("T", bound=Callable[..., Any])

        def decorator(func: T) -> T:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if name not in self._timers:
                    self._timers[name] = FunctionTimer(name)

                timer = self._timers[name]
                timer.start()
                try:
                    return func(*args, **kwargs)
                finally:
                    timer.stop()

            return wrapper  # type: ignore[return-value]

        return decorator  # type: ignore[return-value]

    def end_frame(
        self,
        update_time: float = 0.0,
        render_time: float = 0.0,
        event_time: float = 0.0,
        collision_time: float = 0.0,
        sprite_count: int = 0,
        particle_count: int = 0,
        draw_calls: int = 0,
    ) -> FrameStats:
        """
        End current frame and record statistics.

        Args:
            update_time: Time spent in update (ms)
            render_time: Time spent in rendering (ms)
            event_time: Time spent processing events (ms)
            collision_time: Time spent in collision detection (ms)
            sprite_count: Number of active sprites
            particle_count: Number of active particles
            draw_calls: Number of draw calls

        Returns:
            Frame statistics
        """
        current_time = time.perf_counter() * 1000
        frame_time = current_time - self._frame_start
        self._frame_start = current_time

        # Calculate FPS
        fps = 1000.0 / frame_time if frame_time > 0 else 0.0

        # Create frame stats
        self._current_frame += 1
        stats = FrameStats(
            frame_number=self._current_frame,
            frame_time=frame_time,
            fps=fps,
            timestamp=current_time,
            update_time=update_time,
            render_time=render_time,
            event_time=event_time,
            collision_time=collision_time,
            sprite_count=sprite_count,
            particle_count=particle_count,
            draw_calls=draw_calls,
        )

        self._frame_history.append(stats)

        # Check for slow frame
        if frame_time > self.slow_frame_threshold:
            stats.slow_frames = 1
            for callback in self._slow_frame_callbacks:
                callback(stats)

        # Reset section times
        self._section_times.clear()

        return stats

    def get_stats(self) -> ProfilerStats:
        """Get aggregated statistics."""
        if not self._frame_history:
            return ProfilerStats()

        result = ProfilerStats()
        result.total_frames = self._current_frame

        fps_values = [f.fps for f in self._frame_history]
        frame_times = [f.frame_time for f in self._frame_history]

        result.fps_avg = sum(fps_values) / len(fps_values)
        result.fps_min = min(fps_values)
        result.fps_max = max(fps_values)

        result.frame_time_avg = sum(frame_times) / len(frame_times)
        result.frame_time_max = max(frame_times)

        result.slow_frames = sum(1 for f in self._frame_history if f.frame_time > self.slow_frame_threshold)

        if self._frame_history:
            result.update_time_avg = sum(f.update_time for f in self._frame_history) / len(self._frame_history)
            result.render_time_avg = sum(f.render_time for f in self._frame_history) / len(self._frame_history)

        return result

    def get_timer_stats(self, name: str) -> Optional[Dict[str, float]]:
        """Get statistics for function timer."""
        if name not in self._timers:
            return None

        timer = self._timers[name]
        return {
            "avg_ms": round(timer.avg_time, 3),
            "min_ms": round(timer.min_time, 3) if timer.min_time != float("inf") else 0,
            "max_ms": round(timer.max_time, 3),
            "total_ms": round(timer.total_time, 3),
            "calls": timer.call_count,
        }

    def on_slow_frame(self, callback: Callable[[FrameStats], None]) -> None:
        """Register callback for slow frames."""
        self._slow_frame_callbacks.append(callback)

    def toggle_overlay(self) -> None:
        """Toggle performance overlay visibility."""
        self._show_overlay = not self._show_overlay

    def draw_overlay(self, surface: pg.Surface) -> None:
        """
        Draw performance overlay.

        Args:
            surface: Surface to draw on
        """
        if not self._show_overlay:
            return

        # Initialize font if needed
        if self._font is None:
            self._font = pg.font.Font(None, 24)

        stats = self.get_stats()
        lines = [
            f"FPS: {stats.fps_avg:.1f} (min: {stats.fps_min:.1f}, max: {stats.fps_max:.1f})",
            f"Frame: {stats.frame_time_avg:.2f}ms (max: {stats.frame_time_max:.2f}ms)",
            f"Update: {stats.update_time_avg:.2f}ms | Render: {stats.render_time_avg:.2f}ms",
            f"Slow frames: {stats.slow_frames}/{stats.total_frames}",
        ]

        # Add timer stats
        for name, timer_stats in self._timers.items():
            if timer_stats:
                if hasattr(timer_stats, 'to_dict'):
                    stats_dict = timer_stats.to_dict()
                    lines.append(f"{name}: {stats_dict['avg_ms']:.3f}ms ({stats_dict['calls']} calls)")

        # Draw background
        y_offset = 10
        for line in lines:
            text_surface = self._font.render(line, True, (0, 255, 0))
            surface.blit(text_surface, (10, y_offset))
            y_offset += 20

    def reset(self) -> None:
        """Reset all statistics."""
        self._frame_history.clear()
        self._current_frame = 0
        self._section_times.clear()
        for timer in self._timers.values():
            timer.reset()


class ProfilerSection:
    """Context manager for profiling code sections."""

    def __init__(self, profiler: Profiler, name: str) -> None:
        """
        Initialize profiler section.

        Args:
            profiler: Parent profiler
            name: Section name
        """
        self.profiler = profiler
        self.name = name

    def __enter__(self) -> "ProfilerSection":
        """Enter context."""
        self.profiler._begin_section(self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context."""
        self.profiler._end_section(self.name)


# Global profiler instance
_profiler: Optional[Profiler] = None


def get_profiler() -> Profiler:
    """Get global profiler instance."""
    global _profiler
    if _profiler is None:
        _profiler = Profiler()
    return _profiler


def profile(name: str) -> ProfilerSection:
    """Profile code section using global profiler."""
    return get_profiler().profile(name)


def time_function(name: str) -> Callable:
    """Decorate function for timing."""
    return get_profiler().time_function(name)
