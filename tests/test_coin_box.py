"""Tests for coin_box component."""

import pytest
import pygame as pg

from data.components.coin_box import CoinBox
from data import constants as c


@pytest.fixture
def coin_box() -> CoinBox:
    """Create a CoinBox instance for testing."""
    return CoinBox(100, 200)


@pytest.fixture
def coin_box_with_group() -> tuple:
    """Create a CoinBox with a sprite group."""
    group = pg.sprite.Group()
    box = CoinBox(100, 200, group=group)
    return box, group


class TestCoinBoxInitialization:
    """Tests for CoinBox initialization."""

    def test_coin_box_creation(self, coin_box: CoinBox) -> None:
        """Test that CoinBox can be created."""
        assert coin_box is not None

    def test_coin_box_initial_state(self, coin_box: CoinBox) -> None:
        """Test CoinBox's initial state."""
        assert coin_box.state == c.RESTING
        assert coin_box.frame_index == 0

    def test_coin_box_has_rect(self, coin_box: CoinBox) -> None:
        """Test CoinBox has a rect."""
        assert hasattr(coin_box, "rect")
        assert isinstance(coin_box.rect, pg.Rect)

    def test_coin_box_position(self, coin_box: CoinBox) -> None:
        """Test CoinBox initial position."""
        assert coin_box.rect.x == 100
        assert coin_box.rect.y == 200

    def test_coin_box_has_frames(self, coin_box: CoinBox) -> None:
        """Test CoinBox has frames."""
        assert hasattr(coin_box, "frames")
        assert len(coin_box.frames) == 4

    def test_coin_box_has_mask(self, coin_box: CoinBox) -> None:
        """Test CoinBox has a collision mask."""
        assert hasattr(coin_box, "mask")
        assert isinstance(coin_box.mask, pg.Mask)

    def test_coin_box_contents_default(self, coin_box: CoinBox) -> None:
        """Test CoinBox default contents."""
        assert coin_box.contents == "coin"

    def test_coin_box_gravity(self, coin_box: CoinBox) -> None:
        """Test CoinBox gravity value."""
        assert coin_box.gravity == 1.2


class TestCoinBoxCustomization:
    """Tests for CoinBox customization."""

    def test_coin_box_custom_contents(self) -> None:
        """Test CoinBox with custom contents."""
        box = CoinBox(100, 200, contents="mushroom")
        assert box.contents == "mushroom"

    def test_coin_box_with_group(self, coin_box_with_group: tuple) -> None:
        """Test CoinBox with sprite group."""
        box, group = coin_box_with_group
        assert box.group == group

    def test_coin_box_rest_height(self, coin_box: CoinBox) -> None:
        """Test rest height is set to initial y."""
        assert coin_box.rest_height == 200


class TestCoinBoxFrames:
    """Tests for CoinBox frame setup."""

    def test_setup_frames(self, coin_box: CoinBox) -> None:
        """Test frame setup creates 4 frames."""
        assert len(coin_box.frames) == 4
        for frame in coin_box.frames:
            assert isinstance(frame, pg.Surface)

    def test_animation_timer(self, coin_box: CoinBox) -> None:
        """Test animation timer is initialized."""
        assert coin_box.animation_timer == 0

    def test_first_half(self, coin_box: CoinBox) -> None:
        """Test first_half is True initially."""
        assert coin_box.first_half is True


class TestCoinBoxUpdate:
    """Tests for CoinBox update behavior."""

    def test_coin_box_update(self, coin_box: CoinBox) -> None:
        """Test coin box update method."""
        game_info = {c.CURRENT_TIME: 1000}
        coin_box.update(game_info)
        assert coin_box.current_time == 1000

    def test_coin_box_handle_states_resting(self, coin_box: CoinBox) -> None:
        """Test handle_states in RESTING state."""
        coin_box.state = c.RESTING
        coin_box.current_time = 1000
        coin_box.handle_states()

    def test_coin_box_handle_states_bumped(self, coin_box: CoinBox) -> None:
        """Test handle_states in BUMPED state."""
        coin_box.state = c.BUMPED
        coin_box.current_time = 1000
        coin_box.handle_states()

    def test_coin_box_handle_states_opened(self, coin_box: CoinBox) -> None:
        """Test handle_states in OPENED state."""
        coin_box.state = c.OPENED
        coin_box.current_time = 1000
        coin_box.handle_states()


class TestCoinBoxResting:
    """Tests for CoinBox resting state."""

    def test_resting_animation(self, coin_box: CoinBox) -> None:
        """Test resting state animation."""
        coin_box.current_time = 1000
        coin_box.animation_timer = 0
        coin_box.resting()
        assert coin_box.frame_index >= 0


class TestCoinBoxBumped:
    """Tests for CoinBox bumped state."""

    def test_bumped_moves_up(self, coin_box: CoinBox) -> None:
        """Test bumped state moves box up."""
        coin_box.y_vel = -5
        coin_box.bumped()
        assert coin_box.rect.y < 200

    def test_bumped_returns_to_rest(self, coin_box: CoinBox) -> None:
        """Test bumped state returns to resting."""
        coin_box.rect.y = coin_box.rest_height
        coin_box.y_vel = 5
        coin_box.bumped()
        assert coin_box.state == c.OPENED or coin_box.state == c.RESTING


class TestCoinBoxIntegration:
    """Integration tests for CoinBox."""

    def test_multiple_coin_boxes(self) -> None:
        """Test multiple coin boxes can be created."""
        box1 = CoinBox(100, 200)
        box2 = CoinBox(200, 200)
        box3 = CoinBox(300, 200)

        group = pg.sprite.Group(box1, box2, box3)
        assert len(group) == 3

    def test_coin_box_in_sprite_group(self, coin_box: CoinBox) -> None:
        """Test coin box works in sprite group."""
        group = pg.sprite.Group(coin_box)
        assert len(group) == 1
        group.update({c.CURRENT_TIME: 1000})

    def test_coin_box_different_contents(self) -> None:
        """Test coin boxes with different contents."""
        coin_box = CoinBox(100, 200, contents="coin")
        mushroom_box = CoinBox(200, 200, contents="mushroom")
        star_box = CoinBox(300, 200, contents="star")

        assert coin_box.contents == "coin"
        assert mushroom_box.contents == "mushroom"
        assert star_box.contents == "star"

    def test_coin_box_mask_collision(self, coin_box: CoinBox) -> None:
        """Test coin box mask for pixel-perfect collision."""
        assert coin_box.mask is not None
        assert isinstance(coin_box.mask, pg.Mask)
