"""
Debug Utilities for Super Mario Bros.

Features:
- Debug overlay
- Console commands
- Hitbox visualization
- Memory monitoring
- Game state inspection
"""
from __future__ import annotations

import gc
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame as pg


class DebugOverlay:
    """
    Debug information overlay.

    Displays:
    - FPS counter
    - Memory usage
    - Object counts
    - Custom variables
    """

    def __init__(self, screen: pg.Surface) -> None:
        """
        Initialize debug overlay.

        Args:
            screen: Main game screen
        """
        self.screen = screen
        self.font: pg.font.Font = pg.font.Font(None, 20)
        self.small_font: pg.font.Font = pg.font.Font(None, 16)

        self.enabled: bool = False
        self.position: Tuple[int, int] = (10, 10)

        # Custom variables to display
        self.variables: Dict[str, Any] = {}

        # Colors
        self.bg_color: Tuple[int, int, int] = (0, 0, 0)
        self.text_color: Tuple[int, int, int] = (0, 255, 0)
        self.alpha: int = 180

    def toggle(self) -> None:
        """Toggle overlay visibility."""
        self.enabled = not self.enabled

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set variable to display.

        Args:
            name: Variable name
            value: Variable value
        """
        self.variables[name] = value

    def remove_variable(self, name: str) -> None:
        """Remove variable from display."""
        self.variables.pop(name, None)

    def clear_variables(self) -> None:
        """Clear all custom variables."""
        self.variables.clear()

    def _get_memory_usage(self) -> str:
        """Get current memory usage."""
        try:
            import tracemalloc

            current, peak = tracemalloc.get_traced_memory()
            return f"{current / 1024 / 1024:.2f} MB"
        except Exception:
            return "N/A"

    def _get_object_counts(self) -> Dict[str, int]:
        """Get counts of game objects."""
        counts = {
            "sprites": 0,
            "groups": 0,
        }

        # Count pygame sprites
        for name, obj in sys.modules.get("__main__", {}).__dict__.items():
            if isinstance(obj, pg.sprite.Group):
                counts["groups"] += 1
                counts["sprites"] += len(obj.sprites())

        return counts

    def render(self) -> None:
        """Render debug overlay."""
        if not self.enabled:
            return

        lines = []

        # Basic info
        lines.append(f"FPS: {pg.time.Clock().get_fps():.1f}")
        lines.append(f"Memory: {self._get_memory_usage()}")

        # Object counts
        counts = self._get_object_counts()
        lines.append(f"Sprites: {counts['sprites']}")
        lines.append(f"Groups: {counts['groups']}")

        # Custom variables
        for name, value in self.variables.items():
            lines.append(f"{name}: {value}")

        # Python version
        lines.append(f"Python: {sys.version.split()[0]}")
        lines.append(f"Pygame: {pg.ver}")

        # Render background
        line_height = 18
        padding = 5
        width = max(len(line) for line in lines) * 10 + padding * 2
        height = len(lines) * line_height + padding * 2

        overlay = pg.Surface((width, height), pg.SRCALPHA)
        overlay.fill((*self.bg_color, self.alpha))

        # Render text
        y = padding
        for line in lines:
            text = self.font.render(str(line), True, self.text_color)
            overlay.blit(text, (padding, y))
            y += line_height

        self.screen.blit(overlay, self.position)


class DebugConsole:
    """
    Interactive debug console.

    Features:
    - Command execution
    - Variable inspection
    - Game manipulation
    """

    def __init__(self) -> None:
        """Initialize debug console."""
        self.enabled: bool = False
        self.input_text: str = ""
        self.history: List[str] = []
        self.history_index: int = 0
        self.output: List[str] = []

        self.font: pg.font.Font = pg.font.Font(None, 20)
        self.bg_color: Tuple[int, int, int] = (0, 0, 0)
        self.text_color: Tuple[int, int, int] = (255, 255, 255)

        # Registered commands
        self.commands: Dict[str, Callable] = {}
        self.variables: Dict[str, Any] = {}

        # Register default commands
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        """Register default debug commands."""

        def help_cmd() -> str:
            return "Available commands: " + ", ".join(self.commands.keys())

        def vars_cmd() -> str:
            return str(self.variables)

        def gc_cmd() -> str:
            collected = gc.collect()
            return f"Garbage collected: {collected} objects"

        def fps_cmd() -> str:
            return f"FPS: {pg.time.Clock().get_fps():.2f}"

        self.register_command("help", help_cmd)
        self.register_command("vars", vars_cmd)
        self.register_command("gc", gc_cmd)
        self.register_command("fps", fps_cmd)

    def register_command(self, name: str, func: Callable[[], str]) -> None:
        """
        Register console command.

        Args:
            name: Command name
            func: Command function (returns string output)
        """
        self.commands[name] = func

    def set_variable(self, name: str, value: Any) -> None:
        """
        Set console variable.

        Args:
            name: Variable name
            value: Variable value
        """
        self.variables[name] = value

    def get_event(self, event: pg.event.Event) -> None:
        """
        Handle pygame event.

        Args:
            event: Pygame event
        """
        if not self.enabled:
            return

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                self._execute_command()
            elif event.key == pg.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pg.K_UP:
                if self.history:
                    self.history_index = max(0, self.history_index - 1)
                    if self.history_index < len(self.history):
                        self.input_text = self.history[self.history_index]
            elif event.key == pg.K_DOWN:
                if self.history:
                    self.history_index = min(len(self.history) - 1, self.history_index + 1)
                    if self.history_index < len(self.history):
                        self.input_text = self.history[self.history_index]
            elif event.key == pg.K_ESCAPE:
                self.enabled = False
            else:
                # Add character
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text += event.unicode

    def _execute_command(self) -> None:
        """Execute current command."""
        command = self.input_text.strip()
        if not command:
            return

        # Add to history
        self.history.append(command)
        self.history_index = len(self.history)

        # Parse command
        parts = command.split(" ", 1)
        cmd_name = parts[0]
        _ = parts[1] if len(parts) > 1 else ""  # args reserved for future use

        # Execute
        output = ""
        if cmd_name in self.commands:
            try:
                output = self.commands[cmd_name]()
            except Exception as e:
                output = f"Error: {e}"
        else:
            # Try as Python expression
            try:
                # Try eval first
                result = eval(cmd_name, {}, {**self.variables, **globals()})
                output = str(result)
            except SyntaxError:
                # Try exec
                try:
                    exec(cmd_name, {}, {**self.variables, **globals()})
                    output = "Executed."
                except Exception as e:
                    output = f"Error: {e}"
            except Exception as e:
                output = f"Error: {e}"

        self.output.append(f"> {command}")
        if output:
            self.output.append(output)

        # Limit output
        self.output = self.output[-50:]

        self.input_text = ""

    def render(self, screen: pg.Surface) -> None:
        """
        Render console.

        Args:
            screen: Surface to render to
        """
        if not self.enabled:
            return

        # Calculate size
        height = 200
        width = screen.get_width()

        # Background
        bg = pg.Surface((width, height), pg.SRCALPHA)
        bg.fill((*self.bg_color, 200))
        screen.blit(bg, (0, screen.get_height() - height))

        # Render output
        y = screen.get_height() - height + 5
        for line in self.output[-10:]:
            text = self.font.render(line, True, self.text_color)
            screen.blit(text, (10, y))
            y += 18

        # Render input
        input_y = screen.get_height() - 25
        prompt = self.font.render(f"> {self.input_text}", True, (0, 255, 0))
        screen.blit(prompt, (10, input_y))

        # Cursor
        cursor_x = 10 + prompt.get_width()
        if time.time() % 1 > 0.5:
            pg.draw.line(screen, (0, 255, 0), (cursor_x, input_y), (cursor_x, input_y + 15))


class HitboxVisualizer:
    """Visualize collision hitboxes."""

    def __init__(self) -> None:
        """Initialize hitbox visualizer."""
        self.enabled: bool = False
        self.color: Tuple[int, int, int] = (255, 0, 0)
        self.width: int = 1

    def toggle(self) -> None:
        """Toggle visibility."""
        self.enabled = not self.enabled

    def draw_rect(
        self,
        surface: pg.Surface,
        rect: pg.Rect,
        offset: Tuple[int, int] = (0, 0),
    ) -> None:
        """
        Draw hitbox rectangle.

        Args:
            surface: Target surface
            rect: Rectangle to draw
            offset: Camera offset
        """
        if not self.enabled:
            return

        ox, oy = offset
        draw_rect = pg.Rect(
            rect.x - ox,
            rect.y - oy,
            rect.width,
            rect.height,
        )
        pg.draw.rect(surface, self.color, draw_rect, self.width)

    def draw_group(
        self,
        surface: pg.Surface,
        group: pg.sprite.Group,
        offset: Tuple[int, int] = (0, 0),
    ) -> None:
        """
        Draw hitboxes for sprite group.

        Args:
            surface: Target surface
            group: Sprite group
            offset: Camera offset
        """
        if not self.enabled:
            return

        for sprite in group.sprites():
            if hasattr(sprite, "rect"):
                self.draw_rect(surface, sprite.rect, offset)


# Global debug instances
_debug_overlay: Optional[DebugOverlay] = None
_debug_console: Optional[DebugConsole] = None
_hitbox_visualizer: Optional[HitboxVisualizer] = None


def get_debug_overlay(screen: pg.Surface) -> DebugOverlay:
    """Get global debug overlay."""
    global _debug_overlay
    if _debug_overlay is None:
        _debug_overlay = DebugOverlay(screen)
    return _debug_overlay


def get_debug_console() -> DebugConsole:
    """Get global debug console."""
    global _debug_console
    if _debug_console is None:
        _debug_console = DebugConsole()
    return _debug_console


def get_hitbox_visualizer() -> HitboxVisualizer:
    """Get global hitbox visualizer."""
    global _hitbox_visualizer
    if _hitbox_visualizer is None:
        _hitbox_visualizer = HitboxVisualizer()
    return _hitbox_visualizer


def debug_mode(screen: pg.Surface) -> None:
    """
    Enable all debug features.

    Args:
        screen: Main game screen
    """
    get_debug_overlay(screen).enabled = True
    get_debug_console().enabled = True
    get_hitbox_visualizer().enabled = True
