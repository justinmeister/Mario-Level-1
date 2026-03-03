"""
Debug Utilities for Super Mario Bros.

Provides:
- Debug overlay with FPS, memory
- Collision visualization
- Entity inspector
- Console commands
- Performance profiler
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, Callable, Any, Tuple

import pygame as pg

from . import constants as c

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pygame.font import Font


@dataclass
class DebugStats:
    """Debug statistics."""

    fps: float = 0.0
    frame_time: float = 0.0
    memory_mb: float = 0.0
    sprite_count: int = 0
    active_sounds: int = 0
    collision_count: int = 0


class DebugOverlay:
    """
    Debug information overlay.

    Usage:
        debug = DebugOverlay()
        debug.update(clock, sprites)
        debug.draw(screen)
    """

    def __init__(self, position: Tuple[int, int] = (10, 10), font_size: int = 18) -> None:
        """
        Initialize debug overlay.

        Args:
            position: Overlay position
            font_size: Font size
        """
        self.x, self.y = position
        self.font_size = font_size

        self.font: Optional["Font"] = None
        self.small_font: Optional["Font"] = None
        self._init_fonts()

        self.visible = False
        self.stats = DebugStats()

        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.text_color = c.WHITE
        self.highlight_color = c.GREEN

        # Frame timing
        self.frame_times: List[float] = []
        self.max_samples = 60

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font = pg.font.Font(None, self.font_size)
            self.small_font = pg.font.Font(None, self.font_size - 4)
        except pg.error:
            self.font = None
            self.small_font = None

    def toggle(self) -> None:
        """Toggle overlay visibility."""
        self.visible = not self.visible

    def show(self) -> None:
        """Show overlay."""
        self.visible = True

    def hide(self) -> None:
        """Hide overlay."""
        self.visible = False

    def update(
        self, clock: Optional[pg.time.Clock] = None, sprites: Optional[List] = None, collisions: int = 0
    ) -> None:
        """
        Update debug stats.

        Args:
            clock: Pygame clock
            sprites: List of sprites
            collisions: Number of collisions this frame
        """
        # FPS
        if clock:
            fps = clock.get_fps()
            if fps <= 0:
                # clock.get_fps() often returns 0 on the first tick, fall back
                # to calculating from get_time()
                dt = clock.get_time()
                fps = 1000 / dt if dt > 0 else 0
            self.stats.fps = fps
            self.stats.frame_time = 1000 / self.stats.fps if self.stats.fps > 0 else 0

        # Frame time tracking
        self.frame_times.append(self.stats.frame_time)
        if len(self.frame_times) > self.max_samples:
            self.frame_times.pop(0)

        # Memory
        try:
            import resource

            self.stats.memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # type: ignore[attr-defined]
        except (ImportError, AttributeError):
            # Windows doesn't have resource module
            self.stats.memory_mb = 0

        # Sprite count
        self.stats.sprite_count = len(sprites) if sprites else 0

        # Collision count
        self.stats.collision_count = collisions

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw debug overlay.

        Args:
            surface: Surface to draw to
        """
        if not self.visible or not self.font:
            return

        lines = self._get_info_lines()

        # Calculate size
        line_height = self.font_size + 4
        width = 200
        height = len(lines) * line_height + 10

        # Draw background
        bg_surface = pg.Surface((width, height), pg.SRCALPHA)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, (self.x, self.y))

        # Draw lines
        for i, (text, color) in enumerate(lines):
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (self.x + 5, self.y + 5 + i * line_height))

        # Draw frame time graph
        self._draw_frame_graph(surface, width, height)

    def _get_info_lines(self) -> List[Tuple[str, tuple]]:
        """Get info lines with colors."""
        lines = [
            ("=== DEBUG ===", self.highlight_color),
            (f"FPS: {self.stats.fps:.1f}", self._get_fps_color()),
            (f"Frame: {self.stats.frame_time:.2f}ms", self.text_color),
            (f"Memory: {self.stats.memory_mb:.1f} MB", self.text_color),
            (f"Sprites: {self.stats.sprite_count}", self.text_color),
            (f"Collisions: {self.stats.collision_count}", self.text_color),
        ]

        # Add average FPS
        if self.frame_times:
            avg_frame = sum(self.frame_times) / len(self.frame_times)
            lines.append((f"Avg Frame: {avg_frame:.2f}ms", self.text_color))

        return lines

    def _get_fps_color(self) -> tuple:
        """Get color based on FPS."""
        if self.stats.fps >= 55:
            return c.GREEN
        elif self.stats.fps >= 30:
            return c.YELLOW
        else:
            return c.RED

    def _draw_frame_graph(self, surface: pg.Surface, width: int, height: int) -> None:
        """Draw frame time graph."""
        if len(self.frame_times) < 10:
            return

        graph_width = width - 20
        graph_height = 50
        graph_x = self.x + 10
        graph_y = self.y + height + 5

        # Draw background
        pg.draw.rect(surface, (30, 30, 30), (graph_x, graph_y, graph_width, graph_height))

        # Draw frames
        max_time = max(self.frame_times) if self.frame_times else 1
        bar_width = graph_width / len(self.frame_times)

        for i, frame_time in enumerate(self.frame_times):
            bar_height = (frame_time / max_time) * graph_height
            x = graph_x + i * bar_width
            y = graph_y + graph_height - bar_height

            # Color based on frame time
            if frame_time < 16:  # 60 FPS
                color = c.GREEN
            elif frame_time < 33:  # 30 FPS
                color = c.YELLOW
            else:
                color = c.RED

            pg.draw.rect(surface, color, (x, y, bar_width - 1, bar_height))


class CollisionVisualizer:
    """
    Visualize collision boxes.
    """

    def __init__(self) -> None:
        """Initialize collision visualizer."""
        self.enabled = False
        self.color = c.RED
        self.line_width = 1

    def toggle(self) -> None:
        """Toggle visibility."""
        self.enabled = not self.enabled

    def draw(self, surface: pg.Surface, rects: List[pg.Rect], camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Draw collision boxes.

        Args:
            surface: Surface to draw to
            rects: List of rectangles
            camera_offset: Camera offset
        """
        if not self.enabled:
            return

        cam_x, cam_y = camera_offset

        for rect in rects:
            draw_rect = pg.Rect(rect.x - cam_x, rect.y - cam_y, rect.width, rect.height)
            pg.draw.rect(surface, self.color, draw_rect, self.line_width)

    def draw_sprite(self, surface: pg.Surface, sprite: Any, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """
        Draw sprite collision box.

        Args:
            surface: Surface to draw to
            sprite: Sprite with rect attribute
            camera_offset: Camera offset
        """
        if not self.enabled or not hasattr(sprite, "rect"):
            return

        self.draw(surface, [sprite.rect], camera_offset)


class EntityInspector:
    """
    Inspect entity properties.
    """

    def __init__(self) -> None:
        """Initialize entity inspector."""
        self.selected: Optional[Any] = None
        self.visible = False
        self.position = (600, 10)

        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font = pg.font.Font(None, 20)
        except pg.error:
            self.font = None  # type: ignore[assignment]

    def select(self, entity: Any) -> None:
        """Select entity for inspection."""
        self.selected = entity

    def deselect(self) -> None:
        """Deselect current entity."""
        self.selected = None

    def toggle(self) -> None:
        """Toggle visibility."""
        self.visible = not self.visible

    def draw(self, surface: pg.Surface) -> None:
        """Draw inspector panel."""
        if not self.visible or not self.selected or not self.font:
            return

        lines = self._get_entity_info()

        # Draw background
        width = 250
        height = len(lines) * 22 + 10
        bg_surface = pg.Surface((width, height), pg.SRCALPHA)
        bg_surface.fill((0, 0, 0, 200))
        surface.blit(bg_surface, self.position)

        # Draw info
        for i, (text, color) in enumerate(lines):
            text_surface = self.font.render(text, True, color)
            y = self.position[1] + 5 + i * 22
            surface.blit(text_surface, (self.position[0] + 5, y))

    def _get_entity_info(self) -> List[Tuple[str, tuple]]:
        """Get entity info lines."""
        if not self.selected:
            return []

        lines = [("=== INSPECTOR ===", c.GOLD)]

        # Class name
        class_name = type(self.selected).__name__
        lines.append((f"Class: {class_name}", c.GREEN))

        # Position
        if hasattr(self.selected, "rect"):
            rect = self.selected.rect
            lines.append((f"Position: ({rect.x}, {rect.y})", c.WHITE))
            lines.append((f"Size: {rect.width}x{rect.height}", c.WHITE))

        # Velocity
        if hasattr(self.selected, "vx"):
            lines.append((f"Velocity X: {self.selected.vx:.2f}", c.WHITE))
        if hasattr(self.selected, "vy"):
            lines.append((f"Velocity Y: {self.selected.vy:.2f}", c.WHITE))

        # State
        if hasattr(self.selected, "state"):
            lines.append((f"State: {self.selected.state}", c.WHITE))

        # Health
        if hasattr(self.selected, "health"):
            lines.append((f"Health: {self.selected.health}", c.WHITE))

        # Custom attributes
        if hasattr(self.selected, "__dict__"):
            for key, value in self.selected.__dict__.items():
                if key not in ["rect", "image", "state"]:
                    if isinstance(value, (int, float, str, bool)):
                        lines.append((f"{key}: {value}", c.GRAY))

        return lines[:15]  # Limit lines


class DebugConsole:
    """
    In-game debug console.
    """

    def __init__(self) -> None:
        """Initialize debug console."""
        self.visible = False
        self.input_text = ""
        self.history: List[str] = []
        self.output: List[str] = []

        self.commands: Dict[str, Callable] = {}
        self.font: Optional["Font"] = None
        self._init_fonts()
        self._register_default_commands()

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font = pg.font.Font(None, 24)
        except pg.error:
            self.font = None

    def _register_default_commands(self) -> None:
        """Register default console commands."""
        self.register_command("help", self.cmd_help)
        self.register_command("clear", self.cmd_clear)
        self.register_command("fps", self.cmd_fps)
        self.register_command("quit", self.cmd_quit)

    def register_command(self, name: str, callback: Callable[[str], str]) -> None:
        """
        Register console command.

        Args:
            name: Command name
            callback: Function to execute
        """
        self.commands[name] = callback

    def cmd_help(self, args: str) -> str:
        """Show available commands."""
        return f"Commands: {', '.join(self.commands.keys())}"

    def cmd_clear(self, args: str) -> str:
        """Clear console output."""
        self.output.clear()
        return "Console cleared"

    def cmd_fps(self, args: str) -> str:
        """Show FPS."""
        return "FPS: N/A (use debug overlay)"

    def cmd_quit(self, args: str) -> str:
        """Quit game."""
        import sys

        sys.exit()

    def toggle(self) -> None:
        """Toggle console."""
        self.visible = not self.visible

    def handle_event(self, event: pg.event.Event) -> bool:
        """
        Handle console input.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.visible:
            return False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                self._execute_command()
                return True
            elif event.key == pg.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.key == pg.K_ESCAPE:
                self.visible = False
                return True
            elif hasattr(event, "unicode") and event.unicode:
                self.input_text += event.unicode
                return True

        return False

    def _execute_command(self) -> None:
        """Execute current command."""
        if not self.input_text.strip():
            return

        command = self.input_text.strip()
        self.history.append(command)

        # Parse command and args
        parts = command.split(" ", 1)
        cmd_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Execute
        if cmd_name in self.commands:
            try:
                result = self.commands[cmd_name](args)
                self.output.append(f"> {command}")
                self.output.append(f"  {result}")
            except Exception as e:
                self.output.append(f"> {command}")
                self.output.append(f"  Error: {e}")
        else:
            self.output.append(f"> {command}")
            self.output.append(f"  Unknown command: {cmd_name}")

        self.input_text = ""

        # Limit output
        if len(self.output) > 100:
            self.output = self.output[-100:]

    def draw(self, surface: pg.Surface) -> None:
        """Draw console."""
        if not self.visible or not self.font:
            return

        # Background
        height = 200
        bg_surface = pg.Surface((surface.get_width(), height), pg.SRCALPHA)
        bg_surface.fill((0, 0, 0, 220))
        surface.blit(bg_surface, (0, 0))

        # Output
        y = 10
        for line in self.output[-8:]:
            color = c.WHITE if line.startswith(">") else c.GRAY
            text_surface = self.font.render(line, True, color)
            surface.blit(text_surface, (10, y))
            y += 22

        # Input
        input_y = height - 30
        pg.draw.line(surface, c.WHITE, (10, input_y), (surface.get_width() - 10, input_y), 1)

        input_text = f"> {self.input_text}"
        text_surface = self.font.render(input_text, True, c.GREEN)
        surface.blit(text_surface, (10, input_y + 5))


class PerformanceProfiler:
    """
    Simple performance profiler.
    """

    def __init__(self) -> None:
        """Initialize profiler."""
        self.timings: Dict[str, List[float]] = {}
        self.active_timers: Dict[str, float] = {}
        self.enabled = True

    def start(self, name: str) -> None:
        """Start timing."""
        if not self.enabled:
            return
        self.active_timers[name] = time.perf_counter()

    def stop(self, name: str) -> Optional[float]:
        """
        Stop timing and return duration.

        Args:
            name: Timer name

        Returns:
            Duration in ms or None
        """
        if not self.enabled or name not in self.active_timers:
            return None

        duration = (time.perf_counter() - self.active_timers[name]) * 1000
        del self.active_timers[name]

        if name not in self.timings:
            self.timings[name] = []
        self.timings[name].append(duration)

        # Keep last 100 samples
        if len(self.timings[name]) > 100:
            self.timings[name].pop(0)

        return duration

    def get_stats(self, name: str) -> dict:
        """
        Get timing statistics.

        Args:
            name: Timer name

        Returns:
            Statistics dictionary
        """
        if name not in self.timings or not self.timings[name]:
            return {}

        timings = self.timings[name]
        return {
            "count": len(timings),
            "min": min(timings),
            "max": max(timings),
            "avg": sum(timings) / len(timings),
            "total": sum(timings),
        }

    def reset(self) -> None:
        """Reset all timings."""
        self.timings.clear()
        self.active_timers.clear()

    def get_report(self) -> str:
        """Get performance report."""
        lines = ["=== Performance Report ==="]

        for name, stats in self.timings.items():
            if stats:
                avg = sum(stats) / len(stats)
                lines.append(f"{name}: avg={avg:.2f}ms, count={len(stats)}")

        return "\n".join(lines)


class DebugManager:
    """
    Central debug manager.
    """

    def __init__(self) -> None:
        """Initialize debug manager."""
        self.overlay = DebugOverlay()
        self.collision_visualizer = CollisionVisualizer()
        self.inspector = EntityInspector()
        self.console = DebugConsole()
        self.profiler = PerformanceProfiler()

        self.screenshot_on_f12 = True

    def handle_event(self, event: pg.event.Event) -> bool:
        """
        Handle debug events.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        # Console takes priority when visible
        if self.console.visible:
            return self.console.handle_event(event)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_F3:
                self.overlay.toggle()
                return True
            elif event.key == pg.K_F4:
                self.collision_visualizer.toggle()
                return True
            elif event.key == pg.K_F5:
                self.inspector.toggle()
                return True
            elif event.key == pg.K_BACKQUOTE:  # ` key
                self.console.toggle()
                return True
            elif event.key == pg.K_F12 and self.screenshot_on_f12:
                return True  # Handled by screenshot system

        return False

    def update(self, clock: Optional[pg.time.Clock] = None, sprites: Optional[List] = None) -> None:
        """
        Update debug systems.

        Args:
            clock: Pygame clock
            sprites: List of sprites
        """
        self.overlay.update(clock, sprites)

    def draw(self, surface: pg.Surface) -> None:
        """Draw all debug elements."""
        self.overlay.draw(surface)
        self.inspector.draw(surface)
        self.console.draw(surface)

    def draw_collisions(
        self, surface: pg.Surface, rects: List[pg.Rect], camera_offset: Tuple[int, int] = (0, 0)
    ) -> None:
        """Draw collision boxes."""
        self.collision_visualizer.draw(surface, rects, camera_offset)


# =============================================================================
# Debug Mode Manager - New Feature v2.7.1
# =============================================================================


class DebugModeManager:
    """
    Manages debug game modes for testing and development.

    Features:
    - God mode (invincibility)
    - Teleport on click
    - No clip mode
    - Speed hack
    - Jump hack

    Usage:
        debug_modes = DebugModeManager()
        debug_modes.toggle_god_mode()
        debug_modes.handle_click(mouse_pos, mario)
    """

    def __init__(self) -> None:
        """Initialize debug mode manager."""
        self.god_mode = False  # Invincibility
        self.teleport_on_click = False  # Teleport to mouse position
        self.no_clip = False  # Pass through walls
        self.speed_hack = False  # 2x speed
        self.super_jump = False  # 2x jump height

        # Visual feedback
        self.active_modes: List[str] = []

    def toggle_god_mode(self) -> None:
        """Toggle god mode (invincibility)."""
        self.god_mode = not self.god_mode
        self._update_active_modes()
        logger.info("God Mode: %s", "ON" if self.god_mode else "OFF")

    def toggle_teleport(self) -> None:
        """Toggle teleport on click."""
        self.teleport_on_click = not self.teleport_on_click
        self._update_active_modes()
        logger.info("Teleport on Click: %s", "ON" if self.teleport_on_click else "OFF")

    def toggle_no_clip(self) -> None:
        """Toggle no clip mode."""
        self.no_clip = not self.no_clip
        self._update_active_modes()
        logger.info("No Clip: %s", "ON" if self.no_clip else "OFF")

    def toggle_speed_hack(self) -> None:
        """Toggle speed hack (2x speed)."""
        self.speed_hack = not self.speed_hack
        self._update_active_modes()
        logger.info("Speed Hack: %s", "ON" if self.speed_hack else "OFF")

    def toggle_super_jump(self) -> None:
        """Toggle super jump (2x jump height)."""
        self.super_jump = not self.super_jump
        self._update_active_modes()
        logger.info("Super Jump: %s", "ON" if self.super_jump else "OFF")

    def _update_active_modes(self) -> None:
        """Update list of active modes for display."""
        self.active_modes = []
        if self.god_mode:
            self.active_modes.append("GOD")
        if self.teleport_on_click:
            self.active_modes.append("TELEPORT")
        if self.no_clip:
            self.active_modes.append("NOCLIP")
        if self.speed_hack:
            self.active_modes.append("SPEED")
        if self.super_jump:
            self.active_modes.append("SUPERJUMP")

    def handle_mouse_click(
        self,
        pos: Tuple[int, int],
        mario: Optional[Any],
        camera_offset: Tuple[int, int] = (0, 0),
    ) -> bool:
        """
        Handle mouse click for teleport feature.

        Args:
            pos: Mouse position
            mario: Mario object
            camera_offset: Camera offset (x, y)

        Returns:
            True if teleport was performed
        """
        if not self.teleport_on_click or not mario or not hasattr(mario, "rect"):
            return False

        # Calculate world position
        world_x = pos[0] + camera_offset[0]
        world_y = pos[1] + camera_offset[1]

        # Teleport Mario
        mario.rect.x = world_x
        mario.rect.y = world_y
        mario.x_vel = 0
        mario.y_vel = 0

        logger.info("Teleported to (%d, %d)", world_x, world_y)
        return True

    def apply_debug_mode(self, mario: Optional[Any]) -> None:
        """
        Apply debug mode effects to Mario.

        Args:
            mario: Mario object
        """
        if not mario:
            return

        # God mode - make invincible
        if self.god_mode:
            mario.invincible = True
            mario.in_transition_state = False

        # Speed hack
        if self.speed_hack:
            if hasattr(mario, "max_speed"):
                mario.max_speed = mario.max_speed * 2

        # Super jump
        if self.super_jump:
            if hasattr(mario, "jump_vel"):
                mario.jump_vel = mario.jump_vel * 2

    def reset_debug_mode(self, mario: Optional[Any]) -> None:
        """
        Reset debug mode effects.

        Args:
            mario: Mario object
        """
        if not mario:
            return

        # Reset invincibility if god mode is off
        if not self.god_mode:
            mario.invincible = False

        # Reset speed
        if hasattr(mario, "max_speed"):
            mario.max_speed = c.MAX_RUN_SPEED

        # Reset jump
        if hasattr(mario, "jump_vel"):
            mario.jump_vel = c.JUMP_VEL

    def get_active_modes_display(self) -> str:
        """
        Get string representation of active modes.

        Returns:
            Comma-separated list of active modes
        """
        if not self.active_modes:
            return "NONE"
        return ", ".join(self.active_modes)

    def handle_debug_keys(self, event: pg.Event) -> None:
        """
        Handle debug mode key bindings.

        Args:
            event: Pygame event
        """
        if event.type != pg.KEYDOWN:
            return

        # F1 - Toggle god mode
        if event.key == pg.K_F1:
            self.toggle_god_mode()

        # F2 - Toggle teleport
        elif event.key == pg.K_F2:
            self.toggle_teleport()

        # F6 - Toggle no clip
        elif event.key == pg.K_F6:
            self.toggle_no_clip()

        # F7 - Toggle speed hack
        elif event.key == pg.K_F7:
            self.toggle_speed_hack()

        # F8 - Toggle super jump
        elif event.key == pg.K_F8:
            self.toggle_super_jump()


# =============================================================================
# Global debug mode manager
# =============================================================================

_debug_mode_manager: Optional[DebugModeManager] = None


def get_debug_mode_manager() -> DebugModeManager:
    """
    Get global debugModeManager instance.

    Returns:
        DebugModeManager instance
    """
    global _debug_mode_manager
    if _debug_mode_manager is None:
        _debug_mode_manager = DebugModeManager()
    return _debug_mode_manager


def reset_debug_mode_manager() -> None:
    """Reset global DebugModeManager."""
    global _debug_mode_manager
    _debug_mode_manager = None
