"""Tests for Mario player sprite."""

import pytest
import pygame as pg

from data.components.mario import Mario
from data import constants as c


@pytest.fixture
def mario() -> Mario:
    """Create a Mario instance for testing."""
    return Mario()


class TestMarioInitialization:
    """Tests for Mario initialization."""

    def test_mario_creation(self, mario: Mario) -> None:
        """Test that Mario can be created."""
        assert mario is not None

    def test_mario_initial_state(self, mario: Mario) -> None:
        """Test Mario's initial state."""
        assert mario.state == c.WALK
        assert mario.dead is False
        assert mario.invincible is False
        assert mario.big is False
        assert mario.fire is False

    def test_mario_initial_position(self, mario: Mario) -> None:
        """Test Mario has a rect for position."""
        assert hasattr(mario, "rect")
        assert isinstance(mario.rect, pg.Rect)

    def test_mario_has_image(self, mario: Mario) -> None:
        """Test Mario has an image for rendering."""
        assert hasattr(mario, "image")
        assert isinstance(mario.image, pg.Surface)

    def test_mario_has_mask(self, mario: Mario) -> None:
        """Test Mario has a mask for collision."""
        assert hasattr(mario, "mask")
        assert isinstance(mario.mask, pg.Mask)


class TestMarioTimers:
    """Tests for Mario's timer attributes."""

    def test_walking_timer(self, mario: Mario) -> None:
        """Test walking timer is initialized."""
        assert mario.walking_timer == 0

    def test_invincible_animation_timer(self, mario: Mario) -> None:
        """Test invincible animation timer is initialized."""
        assert mario.invincible_animation_timer == 0

    def test_death_timer(self, mario: Mario) -> None:
        """Test death timer is initialized."""
        assert mario.death_timer == 0

    def test_fire_transition_timer(self, mario: Mario) -> None:
        """Test fire transition timer is initialized."""
        assert mario.fire_transition_timer == 0


class TestMarioStateBooleans:
    """Tests for Mario's boolean state attributes."""

    def test_facing_right(self, mario: Mario) -> None:
        """Test Mario initially faces right."""
        assert mario.facing_right is True

    def test_allow_jump(self, mario: Mario) -> None:
        """Test Mario can initially jump."""
        assert mario.allow_jump is True

    def test_dead(self, mario: Mario) -> None:
        """Test Mario is initially alive."""
        assert mario.dead is False

    def test_invincible(self, mario: Mario) -> None:
        """Test Mario is initially vulnerable."""
        assert mario.invincible is False

    def test_big(self, mario: Mario) -> None:
        """Test Mario is initially small."""
        assert mario.big is False

    def test_fire(self, mario: Mario) -> None:
        """Test Mario initially cannot shoot fireballs."""
        assert mario.fire is False


class TestMarioForces:
    """Tests for Mario's physics attributes."""

    def test_initial_velocity(self, mario: Mario) -> None:
        """Test Mario starts with zero velocity."""
        assert mario.x_vel == 0
        assert mario.y_vel == 0

    def test_gravity(self, mario: Mario) -> None:
        """Test Mario has gravity."""
        assert mario.gravity > 0

    def test_jump_velocity(self, mario: Mario) -> None:
        """Test Mario has jump velocity defined."""
        assert mario.jump_vel < 0

    def test_max_walk_speed(self, mario: Mario) -> None:
        """Test Mario has max walk speed."""
        assert mario.max_x_vel > 0


class TestMarioFrames:
    """Tests for Mario's animation frames."""

    def test_right_frames(self, mario: Mario) -> None:
        """Test right frames list exists."""
        assert hasattr(mario, "right_frames")
        assert isinstance(mario.right_frames, list)
        assert len(mario.right_frames) > 0

    def test_left_frames(self, mario: Mario) -> None:
        """Test left frames list exists."""
        assert hasattr(mario, "left_frames")
        assert isinstance(mario.left_frames, list)
        assert len(mario.left_frames) > 0

    def test_right_small_normal_frames(self, mario: Mario) -> None:
        """Test right small normal frames exist."""
        assert len(mario.right_small_normal_frames) > 0

    def test_left_small_normal_frames(self, mario: Mario) -> None:
        """Test left small normal frames exist."""
        assert len(mario.left_small_normal_frames) > 0


class TestMarioMethods:
    """Tests for Mario's methods."""

    def test_get_image(self, mario: Mario) -> None:
        """Test get_image method returns a surface."""
        image = mario.get_image(0, 0, 16, 16)
        assert isinstance(image, pg.Surface)

    def test_update_method_exists(self, mario: Mario) -> None:
        """Test update method exists and is callable."""
        assert callable(getattr(mario, "update", None))

    def test_handle_state_method_exists(self, mario: Mario) -> None:
        """Test handle_state method exists."""
        assert callable(getattr(mario, "handle_state", None))

    def test_animation_method_exists(self, mario: Mario) -> None:
        """Test animation method exists."""
        assert callable(getattr(mario, "animation", None))
