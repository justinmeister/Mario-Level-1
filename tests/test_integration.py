"""
Integration tests for Super Mario Bros Level 1.

These tests verify that multiple components work together correctly.
Unlike unit tests, integration tests check interactions between systems.
"""

from __future__ import annotations

import os
import sys

import pygame as pg

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGameLoopIntegration:
    """Test game loop and state management integration."""

    def test_control_initialization(self):
        """Test that Control class initializes correctly."""
        from data.tools.controllers import Control

        control = Control("Test Game")
        assert control.caption == "Test Game"
        assert control.fps == 60
        assert not control.done
        assert control.state is None

    def test_state_transition(self):
        """Test state transition mechanism."""
        from data.tools.controllers import Control
        from data.tools.states import _State

        control = Control("Test")

        class TestState1(_State):
            def __init__(self):
                super().__init__()
                self.update_count = 0

            def update(self, surface, keys, current_time):
                self.update_count += 1
                if self.update_count >= 2:
                    self.done = True
                    self.next = "state2"

        class TestState2(_State):
            def __init__(self):
                super().__init__()
                self.started = False

            def startup(self, current_time, persistant):
                super().startup(current_time, persistant)
                self.started = True

        state1 = TestState1()
        state2 = TestState2()

        control.setup_states({"state1": state1, "state2": state2}, "state1")

        # Simulate updates until state transition
        for _ in range(5):
            control.current_time = pg.time.get_ticks()
            control.update()

        # Verify transition occurred
        assert control.state_name == "state2"
        assert state2.started

    def test_state_persist_data(self):
        """Test that data persists between state transitions."""
        from data.tools.controllers import Control
        from data.tools.states import _State

        control = Control("Test")

        class StateWithPersist(_State):
            def cleanup(self):
                persist = super().cleanup()
                persist["test_data"] = 42
                return persist

        state1 = StateWithPersist()
        state2 = _State()

        control.setup_states({"state1": state1, "state2": state2}, "state1")
        state1.done = True
        state1.next = "state2"

        control.update()

        assert state2.persist.get("test_data") == 42


class TestResourceLoadingIntegration:
    """Test resource loading systems integration."""

    def test_image_cache_singleton(self):
        """Test that ImageCache works as a singleton."""
        from data.tools.resources import ImageCache

        ImageCache.clear()

        # Create multiple "loads" - should use same cache
        cache1 = ImageCache
        cache2 = ImageCache

        assert cache1 is cache2
        assert cache1.size() == 0

    def test_lazy_loader_caching(self):
        """Test that LazyImageLoader caches loaded images."""
        from data.tools.resources import LazyImageLoader

        # Create a temporary test directory
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        try:
            # Create a simple test image
            test_surface = pg.Surface((10, 10))
            pg.draw.rect(test_surface, (255, 0, 0), (0, 0, 10, 10))
            pg.image.save(test_surface, os.path.join(temp_dir, "test.png"))

            loader = LazyImageLoader(temp_dir)

            # First load
            img1 = loader.get("test")
            assert img1 is not None

            # Second load should use cache
            img2 = loader.get("test")
            assert img2 is img1  # Same object reference

            assert loader.cache["test"] is img1

        finally:
            shutil.rmtree(temp_dir)

    def test_load_all_gfx_missing_directory(self):
        """Test that load_all_gfx handles missing directories gracefully."""
        from data.tools.resources import load_all_gfx

        result = load_all_gfx("/nonexistent/path/that/does/not/exist")
        assert result == {}


class TestComponentIntegration:
    """Test game component integration."""

    def test_collider_creation(self):
        """Test collider creation and basic properties."""
        from data.components.collider import Collider

        collider = Collider(100, 200, 50, 30)

        assert collider.rect.x == 100
        assert collider.rect.y == 200
        assert collider.rect.width == 50
        assert collider.rect.height == 30

    def test_collider_collision(self):
        """Test collider collision detection."""
        from data.components.collider import Collider

        collider1 = Collider(0, 0, 50, 50)
        collider2 = Collider(40, 40, 50, 50)  # Overlapping
        collider3 = Collider(100, 100, 50, 50)  # Not overlapping

        assert collider1.rect.colliderect(collider2.rect)
        assert not collider1.rect.colliderect(collider3.rect)


class TestConstantsIntegration:
    """Test that constants are properly organized and accessible."""

    def test_constants_submodules(self):
        """Test that constants can be imported from submodules."""
        from data.constants import colors, physics, states

        assert hasattr(colors, "WHITE")
        assert hasattr(physics, "GRAVITY")
        assert hasattr(states, "WALK")

    def test_all_constants_accessible(self):
        """Test that all expected constants are accessible."""
        from data import constants as c

        expected_constants = [
            "SCREEN_WIDTH",
            "SCREEN_HEIGHT",
            "GRAVITY",
            "JUMP_VEL",
            "MAX_WALK_SPEED",
            "WHITE",
            "BLACK",
            "RED",
            "GREEN",
            "BLUE",
            "GOOMBA",
            "KOOPA",
            "MUSHROOM",
            "COIN",
            "WALK",
            "JUMP",
            "FALL",
            "STAND",
        ]

        for const_name in expected_constants:
            assert hasattr(c, const_name), f"Missing constant: {const_name}"


class TestKeyBindingsIntegration:
    """Test key bindings system integration."""

    def test_keybindings_default(self):
        """Test default key bindings."""
        from data.tools.keybindings import keybinding

        assert "jump" in keybinding
        assert "left" in keybinding
        assert "right" in keybinding

    def test_keybindings_configurable(self):
        """Test that key bindings can be reconfigured."""
        import pygame as pg

        from data.tools.keybindings import KeyBindings

        bindings = KeyBindings()

        # Test default
        assert bindings.get("jump") == pg.K_a

        # Test reconfiguration
        bindings.set("jump", pg.K_SPACE)
        assert bindings.get("jump") == pg.K_SPACE

        # Test reset
        bindings.reset()
        assert bindings.get("jump") == pg.K_a

    def test_keybindings_is_action(self):
        """Test key action checking."""
        import pygame as pg

        from data.tools.keybindings import KeyBindings

        bindings = KeyBindings()

        assert bindings.is_action(pg.K_a, "jump")
        assert not bindings.is_action(pg.K_SPACE, "jump")


class TestEndToEndScenarios:
    """End-to-end test scenarios."""

    def test_full_game_initialization(self):
        """Test that game can initialize without errors."""
        from data import setup

        # Verify setup module is loaded
        assert hasattr(setup, "initialize")
        assert hasattr(setup, "GFX")
        assert len(setup.GFX) > 0

    def test_multiple_state_cycles(self):
        """Test multiple state transition cycles."""
        from data.tools.controllers import Control
        from data.tools.states import _State

        control = Control("Test")

        class CyclicState(_State):
            def __init__(self, name, next_state):
                super().__init__()
                self.name = name
                self.next_state = next_state
                self.frames = 0

            def update(self, surface, keys, current_time):
                self.frames += 1
                if self.frames >= 3:
                    self.done = True
                    self.next = self.next_state

        states = {
            "a": CyclicState("a", "b"),
            "b": CyclicState("b", "c"),
            "c": CyclicState("c", "a"),
        }

        control.setup_states(states, "a")

        # Run for multiple state transitions
        for _ in range(15):
            if control.done:
                break
            control.current_time = pg.time.get_ticks()
            control.update()

        # Should have cycled through states
        assert control.state_name in ["a", "b", "c"]
