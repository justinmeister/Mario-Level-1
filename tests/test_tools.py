"""
Tests for the tools module (Control, _State classes).
"""
from __future__ import annotations

import pytest
import pygame as pg

from data import tools


class TestKeybinding:
    """Tests for keybinding configuration."""

    def test_keybinding_exists(self):
        """Test that keybinding dictionary exists."""
        assert isinstance(tools.keybinding, dict)

    def test_keybinding_required_keys(self):
        """Test that keybinding has all required keys."""
        required_keys = ["action", "jump", "left", "right", "down"]
        for key in required_keys:
            assert key in tools.keybinding
            assert isinstance(tools.keybinding[key], int)


class TestControl:
    """Tests for the Control class."""

    def test_control_creation(self, init_pygame):
        """Test that Control can be instantiated."""
        control = tools.Control("Test Game")
        assert control.caption == "Test Game"
        assert control.fps == 60
        assert control.done is False
        assert control.show_fps is False

    def test_control_setup_states(self, init_pygame):
        """Test setting up states on Control."""
        control = tools.Control("Test Game")
        state_dict = {"test": tools._State()}
        control.setup_states(state_dict, "test")

        assert control.state_name == "test"
        assert control.state is not None

    def test_control_flip_state(self, init_pygame):
        """Test state transition."""
        control = tools.Control("Test Game")

        state1 = tools._State()
        state1.next = "state2"

        state2 = tools._State()

        state_dict = {"state1": state1, "state2": state2}
        control.setup_states(state_dict, "state1")

        # Mark state as done to trigger flip
        control.state.done = True
        control.update()

        assert control.state_name == "state2"


class TestState:
    """Tests for the _State base class."""

    def test_state_creation(self):
        """Test that _State can be instantiated."""
        state = tools._State()
        assert state.done is False
        assert state.quit is False
        assert state.next is None
        assert state.previous is None
        assert state.persist == {}

    def test_state_startup(self):
        """Test state startup method."""
        state = tools._State()
        persist_data = {"score": 100}
        state.startup(1000.0, persist_data)

        assert state.start_time == 1000.0
        assert state.persist == persist_data

    def test_state_cleanup(self):
        """Test state cleanup method."""
        state = tools._State()
        state.done = True
        result = state.cleanup()

        assert state.done is False
        assert isinstance(result, dict)

    def test_state_get_event(self):
        """Test that get_event doesn't raise."""
        state = tools._State()
        event = pg.event.Event(pg.KEYDOWN, {"key": pg.K_SPACE})
        state.get_event(event)  # Should not raise

    def test_state_update(self, init_pygame):
        """Test that update doesn't raise."""
        state = tools._State()
        screen = pg.display.set_mode((100, 100))
        keys = pg.key.get_pressed()
        state.update(screen, keys, 1000.0)  # Should not raise
