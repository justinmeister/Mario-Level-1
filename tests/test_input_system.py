"""
Tests for input buffering system.
"""
import time

import pytest
import pygame as pg

from data.input_system import (
    InputType,
    InputEvent,
    InputConfig,
    InputBuffer,
    InputManager,
    ComboDetector,
    MARIO_COMBOS,
    create_mario_combos,
)


class TestInputType:
    """Tests for InputType enum."""

    def test_input_types(self) -> None:
        """Test input type enum values."""
        assert InputType.MOVE_LEFT.value == "move_left"
        assert InputType.JUMP.value == "jump"
        assert InputType.ACTION.value == "action"
        assert InputType.PAUSE.value == "pause"


class TestInputEvent:
    """Tests for InputEvent dataclass."""

    def test_input_event_creation(self) -> None:
        """Test creating input event."""
        event = InputEvent(input_type=InputType.JUMP, timestamp=1000.0)

        assert event.input_type == InputType.JUMP
        assert event.timestamp == 1000.0
        assert event.duration == 0
        assert event.consumed is False

    def test_input_event_with_position(self) -> None:
        """Test input event with position."""
        event = InputEvent(input_type=InputType.ACTION, timestamp=1000.0, position=(100, 200))

        assert event.position == (100, 200)


class TestInputConfig:
    """Tests for InputConfig."""

    def test_default_config(self) -> None:
        """Test default input config."""
        config = InputConfig()

        assert config.buffer_window == 150
        assert config.max_buffer_size == 10
        assert config.hold_threshold == 300
        assert config.combo_queue_size == 5
        assert config.deadzone == 0.1

    def test_custom_config(self) -> None:
        """Test custom input config."""
        config = InputConfig(buffer_window=200, max_buffer_size=20, hold_threshold=500)

        assert config.buffer_window == 200
        assert config.max_buffer_size == 20
        assert config.hold_threshold == 500


class TestInputBuffer:
    """Tests for InputBuffer."""

    @pytest.fixture
    def input_buffer(self) -> InputBuffer:
        """Create input buffer."""
        return InputBuffer()

    def test_buffer_creation(self, input_buffer: InputBuffer) -> None:
        """Test input buffer initialization."""
        assert input_buffer.get_count() == 0
        assert input_buffer.get_unconsumed_count() == 0

    def test_add_input(self, input_buffer: InputBuffer) -> None:
        """Test adding input to buffer."""
        event = input_buffer.add(InputType.JUMP)

        assert event.input_type == InputType.JUMP
        assert input_buffer.get_count() == 1
        assert input_buffer.get_unconsumed_count() == 1

    def test_release_input(self, input_buffer: InputBuffer) -> None:
        """Test releasing input."""
        input_buffer.add(InputType.JUMP)

        # Small delay to measure duration
        time.sleep(0.05)

        event = input_buffer.release(InputType.JUMP)

        assert event is not None
        assert event.duration >= 50  # 50ms

    def test_get_oldest(self, input_buffer: InputBuffer) -> None:
        """Test getting oldest input."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)

        event = input_buffer.get_oldest()

        assert event is not None
        assert event.input_type == InputType.JUMP

    def test_get_newest(self, input_buffer: InputBuffer) -> None:
        """Test getting newest input."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)

        event = input_buffer.get_newest()

        assert event is not None
        assert event.input_type == InputType.ACTION

    def test_get_within_window(self, input_buffer: InputBuffer) -> None:
        """Test getting inputs within window."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)

        events = input_buffer.get_within_window(200)

        assert len(events) == 2

    def test_consume_input(self, input_buffer: InputBuffer) -> None:
        """Test consuming input."""
        input_buffer.add(InputType.JUMP)

        result = input_buffer.consume(InputType.JUMP)

        assert result is True
        assert input_buffer.get_unconsumed_count() == 0

    def test_consume_oldest(self, input_buffer: InputBuffer) -> None:
        """Test consuming oldest input."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)

        result = input_buffer.consume_oldest()

        assert result is True
        assert input_buffer.get_unconsumed_count() == 1

    def test_clear_buffer(self, input_buffer: InputBuffer) -> None:
        """Test clearing buffer."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)

        input_buffer.clear()

        assert input_buffer.get_count() == 0

    def test_clear_old(self, input_buffer: InputBuffer) -> None:
        """Test clearing old inputs."""
        input_buffer.add(InputType.JUMP)

        # Wait a bit
        time.sleep(0.1)

        input_buffer.clear_old(50)  # Clear older than 50ms

        # Should be cleared
        assert input_buffer.get_count() == 0

    def test_is_held(self, input_buffer: InputBuffer) -> None:
        """Test checking if input is held."""
        input_buffer.add(InputType.JUMP)

        # Not held yet
        assert input_buffer.is_held(InputType.JUMP) is False

        # Wait for hold threshold
        time.sleep(0.35)

        assert input_buffer.is_held(InputType.JUMP) is True

    def test_get_combo_sequence(self, input_buffer: InputBuffer) -> None:
        """Test getting combo sequence."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)
        input_buffer.add(InputType.MOVE_RIGHT)

        sequence = input_buffer.get_combo_sequence(3)

        assert len(sequence) == 3
        assert sequence == [InputType.JUMP, InputType.ACTION, InputType.MOVE_RIGHT]

    def test_matches_combo(self, input_buffer: InputBuffer) -> None:
        """Test matching combo."""
        input_buffer.add(InputType.JUMP)
        input_buffer.add(InputType.ACTION)

        combo = [InputType.JUMP, InputType.ACTION]
        assert input_buffer.matches_combo(combo) is True

        wrong_combo = [InputType.JUMP, InputType.JUMP]
        assert input_buffer.matches_combo(wrong_combo) is False

    def test_buffer_max_size(self) -> None:
        """Test buffer respects max size."""
        config = InputConfig(max_buffer_size=3)
        buffer = InputBuffer(config)

        # Add more than max
        for _ in range(5):
            buffer.add(InputType.JUMP)

        assert buffer.get_count() == 3


class TestInputManager:
    """Tests for InputManager."""

    @pytest.fixture
    def input_manager(self) -> InputManager:
        """Create input manager."""
        return InputManager()

    def test_manager_creation(self, input_manager: InputManager) -> None:
        """Test input manager initialization."""
        assert input_manager.enabled is True
        assert input_manager.buffer.get_count() == 0

    def test_set_binding(self, input_manager: InputManager) -> None:
        """Test setting key binding."""
        input_manager.set_binding(pg.K_z, InputType.JUMP)

        assert input_manager.get_binding(pg.K_z) == InputType.JUMP

    def test_handle_keydown_event(self, input_manager: InputManager) -> None:
        """Test handling keydown event."""
        pg.init()

        event = pg.event.Event(pg.KEYDOWN, {"key": pg.K_a})
        result = input_manager.handle_event(event)

        assert result is True
        assert input_manager.is_action_pressed(InputType.JUMP)

        pg.quit()

    def test_handle_keyup_event(self, input_manager: InputManager) -> None:
        """Test handling keyup event."""
        pg.init()

        # Press
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        # Release
        result = input_manager.handle_event(pg.event.Event(pg.KEYUP, {"key": pg.K_a}))

        assert result is True

        pg.quit()

    def test_handle_event_disabled(self, input_manager: InputManager) -> None:
        """Test handling events when disabled."""
        input_manager.enabled = False

        pg.init()
        event = pg.event.Event(pg.KEYDOWN, {"key": pg.K_a})
        result = input_manager.handle_event(event)

        assert result is False

        pg.quit()

    def test_update(self, input_manager: InputManager) -> None:
        """Test manager update."""
        input_manager.update()
        # Should not crash

    def test_is_action_pressed(self, input_manager: InputManager) -> None:
        """Test checking if action is pressed."""
        pg.init()

        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        assert input_manager.is_action_pressed(InputType.JUMP) is True
        assert input_manager.is_action_pressed(InputType.ACTION) is False

        pg.quit()

    def test_consume_action(self, input_manager: InputManager) -> None:
        """Test consuming action."""
        pg.init()

        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        result = input_manager.consume_action(InputType.JUMP)

        assert result is True
        assert input_manager.is_action_pressed(InputType.JUMP) is False

        pg.quit()

    def test_get_direction(self, input_manager: InputManager) -> None:
        """Test getting direction."""
        pg.init()

        # No input
        assert input_manager.get_direction() == (0, 0)

        # Left
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_LEFT}))
        assert input_manager.get_direction() == (-1, 0)

        pg.quit()

    def test_get_combo_sequence(self, input_manager: InputManager) -> None:
        """Test getting combo sequence."""
        pg.init()

        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_s}))

        sequence = input_manager.get_combo_sequence(2)

        assert len(sequence) >= 1

        pg.quit()

    def test_reset(self, input_manager: InputManager) -> None:
        """Test resetting input manager."""
        pg.init()

        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        input_manager.reset()

        assert input_manager.buffer.get_count() == 0

        pg.quit()


class TestComboDetector:
    """Tests for ComboDetector."""

    @pytest.fixture
    def input_manager(self) -> InputManager:
        """Create input manager."""
        return InputManager()

    @pytest.fixture
    def combo_detector(self, input_manager: InputManager) -> ComboDetector:
        """Create combo detector."""
        return ComboDetector(input_manager)

    def test_detector_creation(self, combo_detector: ComboDetector, input_manager: InputManager) -> None:
        """Test combo detector initialization."""
        assert combo_detector.input_manager == input_manager
        assert len(combo_detector.combos) == 0

    def test_register_combo(self, combo_detector: ComboDetector) -> None:
        """Test registering combo."""
        called = []

        def callback() -> None:
            called.append(True)

        combo_detector.register_combo("test_combo", [InputType.JUMP, InputType.ACTION], callback=callback, cooldown=100)

        assert "test_combo" in combo_detector.combos
        assert "test_combo" in combo_detector.callbacks

    def test_check_combo_no_match(self, combo_detector: ComboDetector, input_manager: InputManager) -> None:
        """Test checking combo with no match."""
        combo_detector.register_combo("test", [InputType.JUMP, InputType.ACTION], cooldown=100)

        pg.init()

        # Only press jump
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        result = combo_detector.check_combos()

        assert result is None

        pg.quit()

    def test_check_combo_match(self, combo_detector: ComboDetector, input_manager: InputManager) -> None:
        """Test checking combo with match."""
        combo_detector.register_combo("test", [InputType.JUMP, InputType.JUMP], cooldown=1000)

        pg.init()

        # Press jump twice
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        result = combo_detector.check_combos()

        assert result == "test"

        pg.quit()

    def test_combo_cooldown(self, combo_detector: ComboDetector, input_manager: InputManager) -> None:
        """Test combo cooldown."""
        combo_detector.register_combo("test", [InputType.JUMP, InputType.JUMP], cooldown=500)

        pg.init()

        # Trigger combo
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))
        input_manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        result = combo_detector.check_combos()
        assert result == "test"

        # Try again immediately
        result = combo_detector.check_combos()
        assert result is None  # On cooldown

        pg.quit()

    def test_reset_detector(self, combo_detector: ComboDetector) -> None:
        """Test resetting detector."""
        combo_detector.register_combo("test", [InputType.JUMP])
        combo_detector.last_triggered["test"] = 1000

        combo_detector.reset()

        assert len(combo_detector.last_triggered) == 0


class TestMarioCombos:
    """Tests for Mario combo presets."""

    def test_mario_combos_exist(self) -> None:
        """Test that Mario combos are defined."""
        assert "jump_attack" in MARIO_COMBOS
        assert "run_jump" in MARIO_COMBOS
        assert "backflip" in MARIO_COMBOS
        assert "ground_pound" in MARIO_COMBOS

    def test_create_mario_combos(self) -> None:
        """Test creating Mario combo detector."""
        input_manager = InputManager()
        detector = create_mario_combos(input_manager)

        assert detector is not None
        assert len(detector.combos) >= 4


class TestInputIntegration:
    """Integration tests for input system."""

    def test_full_input_flow(self) -> None:
        """Test complete input flow."""
        pg.init()

        manager = InputManager()
        detector = ComboDetector(manager)

        # Register combo
        detector.register_combo("jump_action", [InputType.JUMP, InputType.ACTION], cooldown=200)

        # Simulate inputs
        manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))
        manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_s}))

        # Update
        manager.update()

        # Check state
        assert manager.is_action_pressed(InputType.JUMP)

        pg.quit()

    def test_input_with_buffer_config(self) -> None:
        """Test input with custom buffer config."""
        config = InputConfig(buffer_window=300, max_buffer_size=20, hold_threshold=200)

        manager = InputManager(config)

        pg.init()

        # Test with config
        manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))

        assert manager.is_action_pressed(InputType.JUMP)

        pg.quit()

    def test_combo_chain(self) -> None:
        """Test chaining combos."""
        pg.init()

        manager = InputManager()
        detector = ComboDetector(manager)

        # Register multiple combos
        detector.register_combo("combo1", [InputType.JUMP], cooldown=100)
        detector.register_combo("combo2", [InputType.ACTION], cooldown=100)

        # Trigger both
        manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_a}))
        manager.handle_event(pg.event.Event(pg.KEYDOWN, {"key": pg.K_s}))

        # Check combos
        result1 = detector.check_combos()
        result2 = detector.check_combos()

        assert result1 is not None or result2 is not None

        pg.quit()
