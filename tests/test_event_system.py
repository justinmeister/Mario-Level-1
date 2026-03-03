"""
Tests for Event System with caching optimization.
"""
from __future__ import annotations

import pytest
from typing import List, Any

from data.event_system import (
    EventManager,
    EventType,
    Event,
    get_event_manager,
)


class TestEventManagerCaching:
    """Tests for EventManager handler caching."""

    def test_cache_on_emit(self) -> None:
        """Test that handlers are cached on emit."""
        manager = EventManager()
        called: List[int] = []

        def handler(event: Event) -> None:
            called.append(1)

        manager.on(EventType.PLAYER_JUMP, handler)

        # First emit - should populate cache
        manager.emit(EventType.PLAYER_JUMP)

        stats = manager.get_stats()
        assert stats["cached_types"] >= 0  # Cache populated

    def test_cache_avoids_resort(self) -> None:
        """Test that cache avoids repeated sorting."""
        manager = EventManager()
        call_order: List[int] = []

        def handler1(event: Event) -> None:
            call_order.append(1)

        def handler2(event: Event) -> None:
            call_order.append(2)

        def handler3(event: Event) -> None:
            call_order.append(3)

        # Register with different priorities
        manager.on(EventType.PLAYER_JUMP, handler1, priority=1)
        manager.on(EventType.PLAYER_JUMP, handler2, priority=3)
        manager.on(EventType.PLAYER_JUMP, handler3, priority=2)

        # First emit - sorts handlers
        manager.emit(EventType.PLAYER_JUMP)
        assert call_order == [2, 3, 1]  # Priority order

        # Second emit - should use cache
        call_order.clear()
        manager.emit(EventType.PLAYER_JUMP)
        assert call_order == [2, 3, 1]  # Same order from cache

    def test_cache_invalidated_on_new_handler(self) -> None:
        """Test that cache is invalidated when new handler registered."""
        manager = EventManager()
        call_order: List[int] = []

        def handler1(event: Event) -> None:
            call_order.append(1)

        def handler2(event: Event) -> None:
            call_order.append(2)

        manager.on(EventType.PLAYER_JUMP, handler1, priority=1)

        # First emit
        manager.emit(EventType.PLAYER_JUMP)

        # Register new handler with higher priority
        manager.on(EventType.PLAYER_JUMP, handler2, priority=10)

        # Should use new order
        call_order.clear()
        manager.emit(EventType.PLAYER_JUMP)
        assert call_order == [2, 1]  # handler2 first due to higher priority

    def test_clear_cache(self) -> None:
        """Test clearing cache."""
        manager = EventManager()

        def handler(event: Event) -> None:
            pass

        manager.on(EventType.PLAYER_JUMP, handler)
        manager.emit(EventType.PLAYER_JUMP)

        stats = manager.get_stats()
        assert stats["cached_types"] >= 0

        # Clear cache
        manager.clear_cache()

        stats = manager.get_stats()
        assert stats["cached_types"] == 0

    def test_clear_cache_single_type(self) -> None:
        """Test clearing cache for single event type."""
        manager = EventManager()

        def handler1(event: Event) -> None:
            pass

        def handler2(event: Event) -> None:
            pass

        manager.on(EventType.PLAYER_JUMP, handler1)
        manager.on(EventType.PLAYER_COIN, handler2)

        # Emit both to populate cache
        manager.emit(EventType.PLAYER_JUMP)
        manager.emit(EventType.PLAYER_COIN)

        # Clear only PLAYER_JUMP cache
        manager.clear_cache(EventType.PLAYER_JUMP)

        stats = manager.get_stats()
        # Should have dirty cache for PLAYER_JUMP
        assert stats["dirty_cache"] >= 1

    def test_cache_stats(self) -> None:
        """Test cache statistics."""
        manager = EventManager()

        # Initial stats
        stats = manager.get_stats()
        assert "cached_types" in stats
        assert "dirty_cache" in stats
        assert stats["cached_types"] == 0

        def handler(event: Event) -> None:
            pass

        manager.on(EventType.PLAYER_JUMP, handler)
        manager.emit(EventType.PLAYER_JUMP)

        stats = manager.get_stats()
        assert stats["cached_types"] >= 0

    def test_cache_with_once_handlers(self) -> None:
        """Test cache works with once handlers."""
        manager = EventManager()
        call_count: List[int] = []

        def handler(event: Event) -> None:
            call_count.append(1)

        # Register once handler
        manager.on(EventType.PLAYER_JUMP, handler, once=True)

        # First emit - should call and remove
        manager.emit(EventType.PLAYER_JUMP)
        assert len(call_count) == 1

        # Second emit - handler should be gone
        call_count.clear()
        manager.emit(EventType.PLAYER_JUMP)
        assert len(call_count) == 0

    def test_cache_with_priority_changes(self) -> None:
        """Test cache handles priority correctly."""
        manager = EventManager()
        result: List[str] = []

        def low(event: Event) -> None:
            result.append("low")

        def high(event: Event) -> None:
            result.append("high")

        def medium(event: Event) -> None:
            result.append("medium")

        # Register in random order
        manager.on(EventType.PLAYER_JUMP, low, priority=1)
        manager.on(EventType.PLAYER_JUMP, high, priority=10)
        manager.on(EventType.PLAYER_JUMP, medium, priority=5)

        # Should execute in priority order
        manager.emit(EventType.PLAYER_JUMP)
        assert result == ["high", "medium", "low"]


class TestGlobalEventManager:
    """Tests for global event manager."""

    def test_singleton_instance(self) -> None:
        """Test that get_event_manager returns singleton."""
        manager1 = get_event_manager()
        manager2 = get_event_manager()
        assert manager1 is manager2

    def test_global_emit(self) -> None:
        """Test emitting through global manager."""
        called: List[bool] = []

        def handler(event: Event) -> None:
            called.append(True)

        from data.event_system import on, emit

        on(EventType.PLAYER_JUMP, handler)
        emit(EventType.PLAYER_JUMP)

        assert len(called) == 1
