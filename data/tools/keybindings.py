"""Key bindings configuration."""

from __future__ import annotations

import pygame as pg

__all__ = ["keybinding", "KeyBindings"]

# Default key bindings
keybinding: dict[str, int] = {
    "action": pg.K_s,
    "jump": pg.K_a,
    "left": pg.K_LEFT,
    "right": pg.K_RIGHT,
    "down": pg.K_DOWN,
}


class KeyBindings:
    """
    Configurable key bindings for the game.

    Allows runtime reconfiguration of controls.

    Attributes:
        bindings: Dictionary mapping action names to key codes
    """

    def __init__(self) -> None:
        """Initialize with default key bindings."""
        self.bindings: dict[str, int] = keybinding.copy()

    def get(self, action: str) -> int | None:
        """
        Get the key code for an action.

        Args:
            action: Name of the action (e.g., 'jump', 'left')

        Returns:
            Key code or None if action not found
        """
        return self.bindings.get(action)

    def set(self, action: str, key: int) -> None:
        """
        Set the key code for an action.

        Args:
            action: Name of the action
            key: Pygame key code
        """
        self.bindings[action] = key

    def reset(self) -> None:
        """Reset all bindings to default values."""
        self.bindings = keybinding.copy()

    def is_action(self, key: int, action: str) -> bool:
        """
        Check if a key matches an action.

        Args:
            key: Key code to check
            action: Action name to compare against

        Returns:
            True if key matches the action
        """
        return self.bindings.get(action) == key
