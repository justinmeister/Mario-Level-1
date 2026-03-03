"""Base state class for game states."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

if TYPE_CHECKING:
    from pygame.event import Event
    from pygame.surface import Surface

__all__ = ["_State"]


class _State:
    """
    Base class for all game states.

    Provides common functionality for menu, level, game over screens, etc.
    Subclasses should override: startup, cleanup, update, get_event

    Attributes:
        start_time: Time when state was entered
        current_time: Current time within state
        done: Flag indicating state should transition
        quit: Flag indicating game should exit
        next: Name of next state
        previous: Name of previous state
        persist: Data to pass between states
    """

    def __init__(self) -> None:
        """Initialize state with default values."""
        self.start_time: float = 0.0
        self.current_time: float = 0.0
        self.done: bool = False
        self.quit: bool = False
        self.next: Optional[str] = None
        self.previous: Optional[str] = None
        self.persist: Dict[str, Any] = {}

    def get_event(self, event: Event) -> None:
        """
        Process a single event.

        Args:
            event: Pygame event to process
        """
        pass

    def startup(self, current_time: float, persistant: Dict[str, Any]) -> None:
        """
        Called when state is first entered.

        Args:
            current_time: Current game time in milliseconds
            persistant: Data passed from previous state
        """
        self.persist = persistant
        self.start_time = current_time

    def cleanup(self) -> Dict[str, Any]:
        """
        Called when state is exiting.

        Returns:
            Dictionary of data to pass to next state
        """
        self.done = False
        return self.persist

    def update(self, surface: Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """
        Update state logic and render.

        Args:
            surface: Display surface to render to
            keys: Current keyboard state
            current_time: Current game time in milliseconds
        """
        pass
