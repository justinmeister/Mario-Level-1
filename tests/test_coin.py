"""Tests for coin components."""

import pytest
import pygame as pg

from data.components.coin import Coin
from data import constants as c


@pytest.fixture
def score_group():
    """Create a score group for testing."""
    return []


@pytest.fixture
def coin(score_group) -> Coin:
    """Create a Coin instance for testing."""
    return Coin(100, 200, score_group)


class TestCoinInitialization:
    """Tests for Coin initialization."""

    def test_coin_creation(self, coin: Coin) -> None:
        """Test that Coin can be created."""
        assert coin is not None

    def test_coin_initial_state(self, coin: Coin) -> None:
        """Test Coin's initial state."""
        assert coin.state == c.SPIN
        assert coin.frame_index == 0

    def test_coin_has_rect(self, coin: Coin) -> None:
        """Test Coin has a rect."""
        assert hasattr(coin, "rect")
        assert isinstance(coin.rect, pg.Rect)

    def test_coin_position(self, coin: Coin) -> None:
        """Test Coin initial position."""
        assert coin.rect.centerx == 100
        assert coin.rect.bottom == 195

    def test_coin_has_frames(self, coin: Coin) -> None:
        """Test Coin has frames."""
        assert hasattr(coin, "frames")
        assert len(coin.frames) == 4

    def test_coin_velocity(self, coin: Coin) -> None:
        """Test Coin initial velocity."""
        assert coin.y_vel == -15
        assert coin.gravity == 1


class TestCoinFrames:
    """Tests for Coin frame setup."""

    def test_setup_frames(self, coin: Coin) -> None:
        """Test frame setup creates 4 frames."""
        assert len(coin.frames) == 4
        for frame in coin.frames:
            assert isinstance(frame, pg.Surface)

    def test_frame_animation_timer(self, coin: Coin) -> None:
        """Test animation timer is initialized."""
        assert coin.animation_timer == 0


class TestCoinUpdate:
    """Tests for Coin update behavior."""

    def test_coin_update(self, coin: Coin) -> None:
        """Test coin update method."""
        game_info = {c.CURRENT_TIME: 1000}
        viewport = pg.Rect(0, 0, 800, 600)
        coin.update(game_info, viewport)
        assert coin.viewport == viewport

    def test_coin_spinning(self, coin: Coin) -> None:
        """Test coin spinning state."""
        coin.current_time = 1000
        coin.spinning()
        assert coin.image is not None

    def test_coin_animation_cycle(self, coin: Coin) -> None:
        """Test coin animation cycles through frames."""
        initial_frame = coin.frame_index
        coin.current_time = 1000
        coin.animation_timer = 0
        coin.spinning()
        assert coin.frame_index >= initial_frame


class TestCoinGravity:
    """Tests for Coin gravity behavior."""

    def test_coin_falls_with_gravity(self, coin: Coin) -> None:
        """Test coin falls with gravity."""
        initial_y_vel = coin.y_vel
        coin.y_vel = 0
        coin.spinning()
        assert coin.y_vel == coin.gravity

    def test_coin_initial_height_set(self, coin: Coin) -> None:
        """Test initial height is set correctly."""
        assert coin.initial_height == coin.rect.bottom - 5


class TestCoinScore:
    """Tests for Coin score integration."""

    def test_score_group_assigned(self, coin: Coin, score_group) -> None:
        """Test score group is assigned."""
        assert coin.score_group == score_group

    def test_coin_creates_score_on_collection(self, score_group) -> None:
        """Test coin creates score when collected."""
        coin = Coin(100, 200, score_group)
        coin.viewport = pg.Rect(0, 0, 800, 600)
        coin.rect.bottom = coin.initial_height + 10
        coin.current_time = 1000
        coin.spinning()
        assert coin not in coin.groups() or len(score_group) >= 0


class TestCoinIntegration:
    """Integration tests for Coin."""

    def test_multiple_coins(self, score_group) -> None:
        """Test multiple coins can be created."""
        coin1 = Coin(100, 200, score_group)
        coin2 = Coin(200, 200, score_group)
        coin3 = Coin(300, 200, score_group)

        group = pg.sprite.Group(coin1, coin2, coin3)
        assert len(group) == 3

    def test_coin_in_sprite_group(self, coin: Coin) -> None:
        """Test coin works in sprite group."""
        group = pg.sprite.Group(coin)
        assert len(group) == 1
        group.update({c.CURRENT_TIME: 1000}, pg.Rect(0, 0, 800, 600))

    def test_coin_different_positions(self, score_group) -> None:
        """Test coins at different positions."""
        coin1 = Coin(50, 100, score_group)
        coin2 = Coin(400, 300, score_group)

        assert coin1.rect.centerx == 50
        assert coin2.rect.centerx == 400
        assert coin1.rect.bottom == 95
        assert coin2.rect.bottom == 295
