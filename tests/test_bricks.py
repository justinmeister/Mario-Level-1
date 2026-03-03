"""Tests for brick component."""

import pytest
import pygame as pg

from data.components.bricks import Brick
from data import constants as c


@pytest.fixture
def brick() -> Brick:
    """Create a Brick instance for testing."""
    return Brick(100, 200)


@pytest.fixture
def brick_6coins() -> Brick:
    """Create a Brick with 6coins contents."""
    return Brick(100, 200, contents="6coins")


class TestBrickInitialization:
    """Tests for Brick initialization."""

    def test_brick_creation(self, brick: Brick) -> None:
        """Test that Brick can be created."""
        assert brick is not None

    def test_brick_initial_state(self, brick: Brick) -> None:
        """Test Brick's initial state."""
        assert brick.state == c.RESTING
        assert brick.frame_index == 0

    def test_brick_has_rect(self, brick: Brick) -> None:
        """Test Brick has a rect."""
        assert hasattr(brick, "rect")
        assert isinstance(brick.rect, pg.Rect)

    def test_brick_position(self, brick: Brick) -> None:
        """Test Brick initial position."""
        assert brick.rect.x == 100
        assert brick.rect.y == 200

    def test_brick_has_frames(self, brick: Brick) -> None:
        """Test Brick has frames."""
        assert hasattr(brick, "frames")
        assert len(brick.frames) == 2

    def test_brick_has_mask(self, brick: Brick) -> None:
        """Test Brick has a collision mask."""
        assert hasattr(brick, "mask")
        assert isinstance(brick.mask, pg.Mask)

    def test_brick_contents_default(self, brick: Brick) -> None:
        """Test Brick default contents."""
        assert brick.contents is None

    def test_brick_gravity(self, brick: Brick) -> None:
        """Test Brick gravity value."""
        assert brick.gravity == 1.2

    def test_brick_name_default(self, brick: Brick) -> None:
        """Test Brick default name."""
        assert brick.name == "brick"


class TestBrickCustomization:
    """Tests for Brick customization."""

    def test_brick_custom_contents(self) -> None:
        """Test Brick with custom contents."""
        brick = Brick(100, 200, contents="star")
        assert brick.contents == "star"

    def test_brick_6coins_contents(self, brick_6coins: Brick) -> None:
        """Test Brick with 6coins contents."""
        assert brick_6coins.contents == "6coins"
        assert brick_6coins.coin_total == 6

    def test_brick_custom_name(self) -> None:
        """Test Brick with custom name."""
        brick = Brick(100, 200, name="mystery_block")
        assert brick.name == "mystery_block"

    def test_brick_rest_height(self, brick: Brick) -> None:
        """Test rest height is set to initial y."""
        assert brick.rest_height == 200


class TestBrickFrames:
    """Tests for Brick frame setup."""

    def test_setup_frames(self, brick: Brick) -> None:
        """Test frame setup creates 2 frames."""
        assert len(brick.frames) == 2
        for frame in brick.frames:
            assert isinstance(frame, pg.Surface)

    def test_setup_coin_total_zero(self, brick: Brick) -> None:
        """Test coin_total is 0 for non-6coins brick."""
        assert brick.coin_total == 0


class TestBrickUpdate:
    """Tests for Brick update behavior."""

    def test_brick_update(self, brick: Brick) -> None:
        """Test brick update method."""
        brick.update()

    def test_brick_handle_states_resting(self, brick: Brick) -> None:
        """Test handle_states in RESTING state."""
        brick.handle_states()

    def test_brick_handle_states_bumped(self, brick: Brick) -> None:
        """Test handle_states in BUMPED state."""
        brick.state = c.BUMPED
        brick.y_vel = -5
        brick.handle_states()

    def test_brick_handle_states_opened(self, brick: Brick) -> None:
        """Test handle_states in OPENED state."""
        brick.state = c.OPENED
        brick.handle_states()


class TestBrickResting:
    """Tests for Brick resting state."""

    def test_resting_with_no_contents(self, brick: Brick) -> None:
        """Test resting state with no contents."""
        brick.resting()
        assert brick.state == c.RESTING

    def test_resting_with_6coins_empty(self, brick_6coins: Brick) -> None:
        """Test resting state when 6coins is empty."""
        brick_6coins.coin_total = 0
        brick_6coins.resting()
        assert brick_6coins.state == c.OPENED


class TestBrickBumped:
    """Tests for Brick bumped state."""

    def test_bumped_moves_up(self, brick: Brick) -> None:
        """Test bumped state moves brick up."""
        brick.y_vel = -5
        brick.bumped()
        assert brick.rect.y < 200

    def test_bumped_returns_to_rest(self, brick: Brick) -> None:
        """Test bumped state returns to resting."""
        brick.rect.y = brick.rest_height + 10
        brick.y_vel = 5
        brick.bumped()
        assert brick.state == c.RESTING


class TestBrickIntegration:
    """Integration tests for Brick."""

    def test_multiple_bricks(self) -> None:
        """Test multiple bricks can be created."""
        brick1 = Brick(100, 200)
        brick2 = Brick(200, 200)
        brick3 = Brick(300, 200)

        group = pg.sprite.Group(brick1, brick2, brick3)
        assert len(group) == 3

    def test_brick_in_sprite_group(self, brick: Brick) -> None:
        """Test brick works in sprite group."""
        group = pg.sprite.Group(brick)
        assert len(group) == 1
        group.update()

    def test_brick_different_contents(self, brick_6coins: Brick) -> None:
        """Test bricks with different contents."""
        normal_brick = Brick(100, 200)
        star_brick = Brick(300, 200, contents="star")

        assert normal_brick.contents is None
        assert brick_6coins.contents == "6coins"
        assert star_brick.contents == "star"
        assert brick_6coins.coin_total == 6
        assert normal_brick.coin_total == 0

    def test_brick_mask_collision(self, brick: Brick) -> None:
        """Test brick mask for pixel-perfect collision."""
        assert brick.mask is not None
        assert isinstance(brick.mask, pg.Mask)

    def test_brick_state_transitions(self, brick_6coins: Brick) -> None:
        """Test brick state transitions."""
        assert brick_6coins.state == c.RESTING
        brick_6coins.coin_total = 0
        brick_6coins.resting()
        assert brick_6coins.state == c.OPENED
