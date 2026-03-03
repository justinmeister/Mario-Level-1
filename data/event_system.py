"""
Event System for Super Mario Bros.

Provides a decoupled communication system between game components.
Features:
- Event types with payloads
- Priority-based handlers
- Event cancellation
- Async event support
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class EventType(Enum):
    """Built-in event types."""

    # Player events
    PLAYER_JUMP = auto()
    PLAYER_LAND = auto()
    PLAYER_HURT = auto()
    PLAYER_DIE = auto()
    PLAYER_POWERUP = auto()
    PLAYER_COIN = auto()
    PLAYER_SCORE = auto()

    # Enemy events
    ENEMY_SPAWN = auto()
    ENEMY_DEFEAT = auto()
    ENEMY_STOMP = auto()

    # World events
    BLOCK_HIT = auto()
    BLOCK_BREAK = auto()
    ITEM_SPAWN = auto()
    CHECKPOINT_REACH = auto()
    LEVEL_COMPLETE = auto()

    # UI events
    UI_UPDATE = auto()
    UI_SHOW_MESSAGE = auto()
    UI_PAUSE = auto()
    UI_RESUME = auto()

    # Audio events
    AUDIO_PLAY_MUSIC = auto()
    AUDIO_PLAY_SFX = auto()
    AUDIO_STOP = auto()

    # Custom events
    CUSTOM = auto()


@dataclass
class Event:
    """
    Base event class.

    Attributes:
        type: Event type
        data: Event payload data
        timestamp: When event was created
        cancelled: Whether event was cancelled
        source: Component that emitted the event
    """

    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    cancelled: bool = False
    source: Optional[Any] = None

    def cancel(self) -> None:
        """Cancel this event."""
        self.cancelled = True

    def is_cancelled(self) -> bool:
        """Check if event is cancelled."""
        return self.cancelled

    def get(self, key: str, default: Any = None) -> Any:
        """Get data value."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set data value."""
        self.data[key] = value


@dataclass
class EventHandler:
    """
    Event handler wrapper.

    Stores handler callback with priority and metadata.
    """

    callback: Callable[[Event], None]
    priority: int = 0  # Higher = called first
    once: bool = False  # Remove after first call
    enabled: bool = True

    # Weak reference for instance methods
    weak_ref: Optional[Any] = None

    def invoke(self, event: Event) -> bool:
        """
        Invoke handler with event.

        Returns:
            True if handler should be kept, False if removed
        """
        if not self.enabled:
            return not self.once

        try:
            # Use weak ref if available
            if self.weak_ref is not None:
                target = self.weak_ref()
                if target is None:
                    return False  # Object was garbage collected

            self.callback(event)
            return not self.once

        except Exception as e:
            logger.error("Event handler error: %s", e)
            return not self.once


class EventManager:
    """
    Central event management system.

    Features:
    - Register/unregister handlers
    - Priority-based execution
    - Event cancellation
    - Global and typed handlers
    - Statistics tracking
    - Handler caching for performance

    Usage:
        events = EventManager()

        # Register handler
        events.on(EventType.PLAYER_JUMP, on_player_jump)

        # Emit event
        events.emit(EventType.PLAYER_JUMP, {'player': mario})
    """

    def __init__(self) -> None:
        """Initialize event manager."""
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._stats: Dict[str, int] = {
            "emitted": 0,
            "handled": 0,
            "cancelled": 0,
        }
        self._enabled: bool = True
        self._event_queue: List[Event] = []

        # Cache for sorted handlers (avoids repeated sorting)
        self._handler_cache: Dict[EventType, List[EventHandler]] = {}
        self._cache_dirty: Dict[EventType, bool] = {}

    def on(
        self,
        event_type: EventType,
        callback: Callable[[Event], None],
        priority: int = 0,
        once: bool = False,
    ) -> None:
        """
        Register event handler.

        Args:
            event_type: Type of event to handle
            callback: Handler function
            priority: Execution priority (higher = first)
            once: Remove after first invocation
        """
        handler = EventHandler(
            callback=callback,
            priority=priority,
            once=once,
        )

        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

        # Mark cache as dirty (lazy sorting)
        self._cache_dirty[event_type] = True
        self._handler_cache.pop(event_type, None)

    def off(
        self,
        event_type: EventType,
        callback: Optional[Callable[[Event], None]] = None,
    ) -> int:
        """
        Unregister event handler(s).

        Args:
            event_type: Type of event
            callback: Specific handler to remove (None for all)

        Returns:
            Number of handlers removed
        """
        if event_type not in self._handlers:
            return 0

        if callback is None:
            count = len(self._handlers[event_type])
            del self._handlers[event_type]
            self._cache_dirty.pop(event_type, None)
            self._handler_cache.pop(event_type, None)
            return count

        removed = 0
        handlers = self._handlers[event_type]
        self._handlers[event_type] = [
            h for h in handlers if h.callback != callback or (removed := removed + 1) and False
        ]
        return removed

    def on_global(
        self,
        callback: Callable[[Event], None],
        priority: int = 0,
    ) -> None:
        """
        Register global handler (receives all events).

        Args:
            callback: Handler function
            priority: Execution priority
        """
        handler = EventHandler(callback=callback, priority=priority)
        self._global_handlers.append(handler)
        self._global_handlers.sort(key=lambda h: h.priority, reverse=True)

    def _get_sorted_handlers(self, event_type: EventType) -> List[EventHandler]:
        """
        Get sorted handlers with caching.

        Args:
            event_type: Type of event

        Returns:
            List of sorted event handlers
        """
        # Check cache first
        if event_type in self._handler_cache and not self._cache_dirty.get(event_type, False):
            return self._handler_cache[event_type]

        # Sort and cache
        if event_type in self._handlers:
            handlers = self._handlers[event_type]
            handlers.sort(key=lambda h: h.priority, reverse=True)
            self._handler_cache[event_type] = handlers
            self._cache_dirty[event_type] = False
            return handlers

        return []

    def emit(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, source: Optional[Any] = None) -> Event:
        """
        Emit event.

        Args:
            event_type: Type of event
            data: Event payload
            source: Event source component

        Returns:
            The emitted event
        """
        if not self._enabled:
            return Event(event_type, data=data or {}, source=source)

        event = Event(type=event_type, data=data or {}, source=source)
        self._stats["emitted"] += 1

        # Process global handlers first
        self._invoke_handlers(self._global_handlers, event)

        if event.is_cancelled():
            self._stats["cancelled"] += 1
            return event

        # Process type-specific handlers (using cache)
        handlers = self._get_sorted_handlers(event_type)
        if handlers:
            self._invoke_handlers(handlers, event)

        return event

    def _invoke_handlers(self, handlers: List[EventHandler], event: Event) -> None:
        """Invoke handlers with event, removing cancelled ones."""
        i = 0
        while i < len(handlers):
            handler = handlers[i]

            if event.is_cancelled():
                break

            keep = handler.invoke(event)
            self._stats["handled"] += 1

            if not keep:
                handlers.pop(i)
            else:
                i += 1

    def queue_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Queue event for later processing.

        Args:
            event_type: Type of event
            data: Event payload
        """
        event = Event(type=event_type, data=data or {})
        self._event_queue.append(event)

    def process_queue(self) -> int:
        """
        Process all queued events.

        Returns:
            Number of events processed
        """
        count = len(self._event_queue)
        for event in self._event_queue:
            self.emit(event.type, event.data, event.source)
        self._event_queue.clear()
        return count

    def enable(self, enable: bool = True) -> None:
        """Enable or disable event processing."""
        self._enabled = enable

    def clear(self) -> None:
        """Clear all handlers and queued events."""
        self._handlers.clear()
        self._global_handlers.clear()
        self._event_queue.clear()
        self._handler_cache.clear()
        self._cache_dirty.clear()

    def clear_cache(self, event_type: Optional[EventType] = None) -> None:
        """
        Clear handler cache.

        Args:
            event_type: Specific event type to clear, or None for all
        """
        if event_type is not None:
            self._handler_cache.pop(event_type, None)
            self._cache_dirty[event_type] = True
        else:
            self._handler_cache.clear()
            self._cache_dirty.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get event statistics."""
        return {
            **self._stats.copy(),
            "cached_types": len(self._handler_cache),
            "dirty_cache": sum(1 for v in self._cache_dirty.values() if v),
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._stats = {
            "emitted": 0,
            "handled": 0,
            "cancelled": 0,
        }


# Global event manager instance
_event_manager: Optional[EventManager] = None


def get_event_manager() -> EventManager:
    """Get global event manager instance."""
    global _event_manager
    if _event_manager is None:
        _event_manager = EventManager()
    return _event_manager


def emit(event_type: EventType, data: Optional[Dict[str, Any]] = None, source: Optional[Any] = None) -> Event:
    """Emit event through global manager."""
    return get_event_manager().emit(event_type, data, source)


def on(
    event_type: EventType,
    callback: Callable[[Event], None],
    priority: int = 0,
) -> None:
    """Register handler with global manager."""
    get_event_manager().on(event_type, callback, priority)


def off(
    event_type: EventType,
    callback: Optional[Callable[[Event], None]] = None,
) -> int:
    """Unregister handler from global manager."""
    return get_event_manager().off(event_type, callback)
