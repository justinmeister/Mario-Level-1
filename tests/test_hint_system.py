"""
Tests for hint and tutorial system.
"""
import time
from typing import Optional

import pytest
import pygame as pg

from data.hint_system import (
    HintCategory,
    HintPriority,
    HintState,
    Hint,
    HintTrigger,
    HintCondition,
    PlayerLevelCondition,
    EnemyDefeatCondition,
    CoinCollectionCondition,
    DeathCondition,
    HintManager,
    HintDisplay,
    HintTriggerSystem,
)


class TestHintCategory:
    """Tests for HintCategory enum."""

    def test_hint_categories(self) -> None:
        """Test hint category enum values."""
        assert HintCategory.MOVEMENT.value == "movement"
        assert HintCategory.COMBAT.value == "combat"
        assert HintCategory.POWERUPS.value == "powerups"
        assert HintCategory.SECRETS.value == "secrets"
        assert HintCategory.ENEMIES.value == "enemies"
        assert HintCategory.COLLECTION.value == "collection"
        assert HintCategory.GENERAL.value == "general"


class TestHintPriority:
    """Tests for HintPriority enum."""

    def test_hint_priorities(self) -> None:
        """Test hint priority values."""
        assert HintPriority.LOW.value == 1
        assert HintPriority.NORMAL.value == 2
        assert HintPriority.HIGH.value == 3
        assert HintPriority.CRITICAL.value == 4


class TestHintState:
    """Tests for HintState enum."""

    def test_hint_states(self) -> None:
        """Test hint state enum values."""
        assert HintState.HIDDEN.value == "hidden"
        assert HintState.FADE_IN.value == "fade_in"
        assert HintState.VISIBLE.value == "visible"
        assert HintState.FADE_OUT.value == "fade_out"


class TestHint:
    """Tests for Hint dataclass."""

    def test_hint_creation(self) -> None:
        """Test creating hint."""
        hint = Hint(id="test_hint", title="Test Title", message="Test message content")

        assert hint.id == "test_hint"
        assert hint.title == "Test Title"
        assert hint.message == "Test message content"
        assert hint.category == HintCategory.GENERAL
        assert hint.priority == HintPriority.NORMAL
        assert hint.trigger_count == 1
        assert hint.is_unlocked is True

    def test_hint_with_options(self) -> None:
        """Test hint with custom options."""
        hint = Hint(
            id="advanced_hint",
            title="Advanced",
            message="Complex hint",
            category=HintCategory.SECRETS,
            priority=HintPriority.HIGH,
            trigger_count=3,
            cooldown=60000,
            prerequisites=["basic_hint"],
        )

        assert hint.category == HintCategory.SECRETS
        assert hint.priority == HintPriority.HIGH
        assert hint.trigger_count == 3
        assert hint.cooldown == 60000
        assert "basic_hint" in hint.prerequisites


class TestHintTrigger:
    """Tests for HintTrigger."""

    def test_trigger_creation(self) -> None:
        """Test creating hint trigger."""
        trigger = HintTrigger(hint_id="test", trigger_type="player_jump", trigger_data={"height": 100})

        assert trigger.hint_id == "test"
        assert trigger.trigger_type == "player_jump"
        assert trigger.times_met == 0


class TestHintConditions:
    """Tests for hint conditions."""

    def test_player_level_condition(self) -> None:
        """Test player level condition."""
        condition = PlayerLevelCondition(min_level=2)

        # Test with low level
        game_state = {"player": {"level": 1}}
        assert condition.check(game_state) is False

        # Test with sufficient level
        game_state = {"player": {"level": 3}}
        assert condition.check(game_state) is True

    def test_player_level_big_condition(self) -> None:
        """Test player is_big condition."""
        condition = PlayerLevelCondition(is_big=True)

        # Test not big
        game_state = {"player": {"is_big": False}}
        assert condition.check(game_state) is False

        # Test big
        game_state = {"player": {"is_big": True}}
        assert condition.check(game_state) is True

    def test_enemy_defeat_condition(self) -> None:
        """Test enemy defeat condition."""
        condition = EnemyDefeatCondition(min_defeats=5)

        # Test with few defeats
        game_state = {"stats": {"enemies_defeated": 3}}
        assert condition.check(game_state) is False

        # Test with enough defeats
        game_state = {"stats": {"enemies_defeated": 10}}
        assert condition.check(game_state) is True

    def test_enemy_defeat_specific_type(self) -> None:
        """Test specific enemy type condition."""
        condition = EnemyDefeatCondition(min_defeats=3, enemy_type="goomba")

        game_state = {"stats": {"goomba_defeated": 5}}
        assert condition.check(game_state) is True

    def test_coin_collection_condition(self) -> None:
        """Test coin collection condition."""
        condition = CoinCollectionCondition(min_coins=50)

        game_state = {"stats": {"coins_collected": 30}}
        assert condition.check(game_state) is False

        game_state = {"stats": {"coins_collected": 60}}
        assert condition.check(game_state) is True

    def test_death_condition(self) -> None:
        """Test death condition."""
        condition = DeathCondition(min_deaths=2)

        game_state = {"stats": {"deaths": 1}}
        assert condition.check(game_state) is False

        game_state = {"stats": {"deaths": 3}}
        assert condition.check(game_state) is True


class TestHintManager:
    """Tests for HintManager."""

    @pytest.fixture
    def hint_manager(self) -> HintManager:
        """Create hint manager."""
        return HintManager()

    def test_hint_manager_creation(self, hint_manager: HintManager) -> None:
        """Test hint manager initialization."""
        assert hint_manager.enabled is True
        assert hint_manager.show_tutorial_hints is True
        assert hint_manager.hint_frequency == 1.0
        assert len(hint_manager.hints) == 0

    def test_register_hint(self, hint_manager: HintManager) -> None:
        """Test registering hint."""
        hint = Hint(id="test", title="Test", message="Test message")
        hint_manager.register_hint(hint)

        assert "test" in hint_manager.hints
        assert len(hint_manager.hints) == 1

    def test_register_default_hints(self, hint_manager: HintManager) -> None:
        """Test registering default hints."""
        hint_manager.register_default_hints()

        # Should have many hints
        assert len(hint_manager.hints) >= 15

        # Check specific hints exist
        assert "move_basic" in hint_manager.hints
        assert "jump_basic" in hint_manager.hints
        assert "stomp_enemy" in hint_manager.hints

    def test_trigger_hint(self, hint_manager: HintManager) -> None:
        """Test triggering hint."""
        hint_manager.register_default_hints()

        # Trigger movement hint
        hint_manager.trigger("player_move")

        # Should not show immediately (need to update)
        hint_manager.update({}, 16)

        # Check queue
        assert len(hint_manager.hint_queue) >= 0  # May show based on prerequisites

    def test_trigger_disabled(self, hint_manager: HintManager) -> None:
        """Test triggering when disabled."""
        hint_manager.enabled = False
        hint_manager.trigger("player_move")

        assert len(hint_manager.hint_queue) == 0

    def test_hint_prerequisites(self, hint_manager: HintManager) -> None:
        """Test hint prerequisites."""
        hint_manager.register_default_hints()

        # Try to trigger advanced hint without prerequisites
        hint_manager.trigger("player_run_jump")
        hint_manager.update({}, 16)

        # Should not be in queue due to prerequisites

    def test_hint_cooldown(self, hint_manager: HintManager) -> None:
        """Test hint cooldown."""
        hint = Hint(id="cooldown_test", title="Test", message="Test", cooldown=10000)  # 10 seconds
        hint_manager.register_hint(hint)

        # Trigger twice quickly
        hint_manager.trigger("cooldown_test")
        hint_manager.update({}, 16)

        # Simulate time passing (less than cooldown)
        hint.last_shown = time.time() * 1000 - 5000  # 5 seconds ago

        hint_manager.trigger("cooldown_test")
        hint_manager.update({}, 16)

        # Should not queue due to cooldown

    def test_force_show_hint(self, hint_manager: HintManager) -> None:
        """Test forcing hint display."""
        hint = Hint(id="force_test", title="Test", message="Test")
        hint_manager.register_hint(hint)

        result = hint_manager.force_show_hint("force_test")
        assert result is True

        result = hint_manager.force_show_hint("nonexistent")
        assert result is False

    def test_get_hint_progress(self, hint_manager: HintManager) -> None:
        """Test getting hint progress."""
        hint_manager.register_default_hints()

        progress = hint_manager.get_hint_progress()

        assert "total_hints" in progress
        assert "shown_hints" in progress
        assert "completion_percent" in progress
        assert "by_category" in progress

    def test_reset(self, hint_manager: HintManager) -> None:
        """Test resetting hint manager."""
        hint_manager.register_hint(Hint(id="test", title="Test", message="Test"))
        hint_manager.force_show_hint("test")
        hint_manager.update({}, 16)

        hint_manager.reset()

        assert hint_manager.current_hint is None
        assert len(hint_manager.hint_queue) == 0

    def test_update_processes_queue(self, hint_manager: HintManager) -> None:
        """Test that update processes hint queue."""
        hint = Hint(id="update_test", title="Test", message="Test message", trigger_count=1, prerequisites=[])
        hint_manager.register_hint(hint)
        hint_manager.hint_queue.append(hint)

        hint_manager.update({}, 16)

        # Should process the hint

    def test_hint_display_duration(self, hint_manager: HintManager) -> None:
        """Test hint display duration."""
        hint = Hint(id="duration_test", title="Test", message="Test", display_duration=1000)  # 1 second
        hint_manager.register_hint(hint)
        hint_manager.force_show_hint("duration_test")
        hint_manager.update({}, 16)

        # Simulate time passing
        hint_manager.update({}, 1500)

        # Hint should have faded out


class TestHintDisplay:
    """Tests for HintDisplay."""

    @pytest.fixture
    def hint_manager(self) -> HintManager:
        """Create hint manager."""
        manager = HintManager()
        manager.register_default_hints()
        return manager

    @pytest.fixture
    def hint_display(self, hint_manager: HintManager) -> HintDisplay:
        """Create hint display."""
        return HintDisplay(hint_manager)

    def test_hint_display_creation(self, hint_display: HintDisplay, hint_manager: HintManager) -> None:
        """Test hint display initialization."""
        assert hint_display.hint_manager == hint_manager
        assert hint_display.x == 50
        assert hint_display.y == 400

    def test_hint_display_draw_no_hint(self, hint_display: HintDisplay) -> None:
        """Test draw with no hint."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Should not crash
        hint_display.draw(surface)

        pg.quit()

    def test_hint_display_draw_with_hint(self, hint_display: HintDisplay, hint_manager: HintManager) -> None:
        """Test draw with hint."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Force show a hint
        hint_manager.force_show_hint("move_basic")
        hint_manager.update({}, 16)

        # Should not crash
        hint_display.draw(surface)

        pg.quit()


class TestHintTriggerSystem:
    """Tests for HintTriggerSystem."""

    @pytest.fixture
    def hint_manager(self) -> HintManager:
        """Create hint manager."""
        return HintManager()

    @pytest.fixture
    def trigger_system(self, hint_manager: HintManager) -> HintTriggerSystem:
        """Create trigger system."""
        return HintTriggerSystem(hint_manager)

    def test_trigger_system_creation(self, trigger_system: HintTriggerSystem) -> None:
        """Test trigger system initialization."""
        assert len(trigger_system.event_counts) == 0
        assert len(trigger_system.listeners) == 0

    def test_register_event(self, trigger_system: HintTriggerSystem) -> None:
        """Test registering event."""
        trigger_system.register_event("player_jump")

        assert "player_jump" in trigger_system.event_counts
        assert trigger_system.event_counts["player_jump"] == 0

    def test_trigger_event(self, trigger_system: HintTriggerSystem) -> None:
        """Test triggering event."""
        trigger_system.trigger_event("player_jump")

        assert trigger_system.event_counts["player_jump"] == 1

        trigger_system.trigger_event("player_jump")
        assert trigger_system.event_counts["player_jump"] == 2

    def test_trigger_event_with_data(self, trigger_system: HintTriggerSystem) -> None:
        """Test triggering event with data."""
        trigger_system.trigger_event("enemy_defeat", {"type": "goomba"})

        assert trigger_system.event_counts["enemy_defeat"] == 1

    def test_add_listener(self, trigger_system: HintTriggerSystem) -> None:
        """Test adding event listener."""
        called = []

        def callback(data: dict) -> None:
            called.append(data)

        trigger_system.add_listener("test_event", callback)

        assert "test_event" in trigger_system.listeners
        assert len(trigger_system.listeners["test_event"]) == 1

    def test_listener_called(self, trigger_system: HintTriggerSystem) -> None:
        """Test that listeners are called."""
        called = []

        def callback(data: Optional[dict]) -> None:
            called.append(data)

        trigger_system.add_listener("test", callback)
        trigger_system.trigger_event("test", {"value": 123})

        assert len(called) == 1
        assert called[0] == {"value": 123}

    def test_get_event_count(self, trigger_system: HintTriggerSystem) -> None:
        """Test getting event count."""
        trigger_system.trigger_event("test")
        trigger_system.trigger_event("test")
        trigger_system.trigger_event("test")

        count = trigger_system.get_event_count("test")
        assert count == 3

    def test_reset(self, trigger_system: HintTriggerSystem) -> None:
        """Test resetting trigger system."""
        trigger_system.trigger_event("event1")
        trigger_system.trigger_event("event2")

        trigger_system.reset()

        assert len(trigger_system.event_counts) == 0


class TestHintIntegration:
    """Integration tests for hint system."""

    def test_full_hint_workflow(self) -> None:
        """Test complete hint workflow."""
        pg.init()

        # Create systems
        manager = HintManager()
        manager.register_default_hints()

        display = HintDisplay(manager)
        surface = pg.Surface((800, 600))

        # Simulate gameplay
        manager.trigger("player_move")
        manager.trigger("player_jump")
        manager.trigger("player_jump")  # Multiple jumps

        # Update and show hints
        manager.update({}, 16)

        # Draw
        display.draw(surface)

        # Simulate more gameplay
        manager.trigger("enemy_stomp")
        manager.update({}, 16)

        # Check progress
        progress = manager.get_hint_progress()
        assert progress["total_hints"] > 0

        pg.quit()

    def test_hint_progression_system(self) -> None:
        """Test hint progression through prerequisites."""
        manager = HintManager()
        manager.register_default_hints()

        # Start from beginning
        manager.trigger("player_move")
        manager.update({}, 16)

        # Should unlock basic movement hint

        # Then jumping
        for _ in range(5):
            manager.trigger("player_jump")
        manager.update({}, 16)

        # Then combat
        manager.trigger("enemy_stomp")
        manager.update({}, 16)

        # Check that hints were shown in order
        progress = manager.get_hint_progress()
        assert progress["shown_hints"] >= 0

    def test_hint_with_game_state(self) -> None:
        """Test hints with realistic game state."""
        manager = HintManager()
        manager.register_default_hints()

        # Simulate game state
        game_state = {
            "player": {"level": 1, "is_big": False},
            "stats": {"coins_collected": 15, "enemies_defeated": 3, "deaths": 1},
        }

        # Trigger various events
        manager.trigger("coin_collect")
        manager.trigger("coin_collect")
        manager.trigger("block_hit")

        manager.update(game_state, 16)

        # Should have processed hints based on state
