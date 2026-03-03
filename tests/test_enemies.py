"""Tests for enemy sprites."""

import pytest
import pygame as pg

from data.components.enemies import Enemy, Goomba, Koopa
from data import constants as c


@pytest.fixture
def enemy() -> Enemy:
    """Create an Enemy instance for testing."""
    return Enemy()


@pytest.fixture
def goomba() -> Goomba:
    """Create a Goomba instance for testing."""
    return Goomba(100, 200, "left")


@pytest.fixture
def koopa() -> Koopa:
    """Create a Koopa instance for testing."""
    return Koopa(100, 200, "left")


class TestEnemyInitialization:
    """Tests for Enemy initialization."""

    def test_enemy_creation(self, enemy: Enemy) -> None:
        """Test that Enemy can be created."""
        assert enemy is not None

    def test_enemy_initial_state(self, enemy: Enemy) -> None:
        """Test Enemy's initial state."""
        assert enemy.state == c.WALK
        assert enemy.gravity == 1.5
        assert enemy.frame_index == 0

    def test_enemy_has_frames(self, enemy: Enemy) -> None:
        """Test Enemy has frames list."""
        assert hasattr(enemy, "frames")
        assert isinstance(enemy.frames, list)

    def test_enemy_timers(self, enemy: Enemy) -> None:
        """Test Enemy timers are initialized."""
        assert enemy.animate_timer == 0
        assert enemy.death_timer == 0

    def test_enemy_velocity(self, enemy: Enemy) -> None:
        """Test Enemy velocity is initialized."""
        assert enemy.x_vel == 0
        assert enemy.y_vel == 0


class TestEnemySetup:
    """Tests for Enemy setup methods."""

    def test_setup_enemy(self, enemy: Enemy) -> None:
        """Test setup_enemy method."""
        def dummy_setup() -> None:
            enemy.frames.append(pg.Surface((16, 16)))

        enemy.setup_enemy(100, 200, "left", "goomba", dummy_setup)
        assert enemy.name == "goomba"
        assert enemy.direction == "left"
        assert enemy.rect.x == 100
        assert enemy.rect.bottom == 200

    def test_set_velocity_left(self, enemy: Enemy) -> None:
        """Test velocity when facing left."""
        enemy.direction = c.LEFT
        enemy.set_velocity()
        assert enemy.x_vel == -2
        assert enemy.y_vel == 0

    def test_set_velocity_right(self, enemy: Enemy) -> None:
        """Test velocity when facing right."""
        enemy.direction = c.RIGHT
        enemy.set_velocity()
        assert enemy.x_vel == 2
        assert enemy.y_vel == 0


class TestEnemyState:
    """Tests for Enemy state handling."""

    def test_handle_state_walk(self, enemy: Enemy) -> None:
        """Test walking state."""
        enemy.state = c.WALK
        enemy.current_time = 1000
        enemy.handle_state()

    def test_handle_state_fall(self, enemy: Enemy) -> None:
        """Test falling state."""
        enemy.state = c.FALL
        enemy.y_vel = 0
        enemy.handle_state()
        assert enemy.y_vel > 0

    def test_walking_animation(self, enemy: Enemy) -> None:
        """Test walking animation updates frame."""
        enemy.frames = [pg.Surface((16, 16)), pg.Surface((16, 16))]
        enemy.frame_index = 0
        enemy.current_time = 200
        enemy.animate_timer = 0
        enemy.walking()
        assert enemy.frame_index == 1

    def test_falling_increases_velocity(self, enemy: Enemy) -> None:
        """Test falling increases y velocity."""
        enemy.y_vel = 0
        enemy.falling()
        assert enemy.y_vel == enemy.gravity


class TestGoombaInitialization:
    """Tests for Goomba initialization."""

    def test_goomba_creation(self, goomba: Goomba) -> None:
        """Test that Goomba can be created."""
        assert goomba is not None

    def test_goomba_name(self, goomba: Goomba) -> None:
        """Test Goomba name."""
        assert goomba.name == "goomba"

    def test_goomba_has_rect(self, goomba: Goomba) -> None:
        """Test Goomba has a rect."""
        assert hasattr(goomba, "rect")
        assert isinstance(goomba.rect, pg.Rect)

    def test_goomba_state(self, goomba: Goomba) -> None:
        """Test Goomba initial state."""
        assert goomba.state == c.WALK


class TestGoombaBehavior:
    """Tests for Goomba behavior."""

    def test_goomba_falling(self, goomba: Goomba) -> None:
        """Test Goomba falling."""
        goomba.y_vel = 0
        goomba.falling()
        assert goomba.y_vel > 0


class TestKoopaInitialization:
    """Tests for Koopa initialization."""

    def test_koopa_creation(self, koopa: Koopa) -> None:
        """Test that Koopa can be created."""
        assert koopa is not None

    def test_koopa_name(self, koopa: Koopa) -> None:
        """Test Koopa name."""
        assert koopa.name == "koopa"

    def test_koopa_has_rect(self, koopa: Koopa) -> None:
        """Test Koopa has a rect."""
        assert hasattr(koopa, "rect")

    def test_koopa_state(self, koopa: Koopa) -> None:
        """Test Koopa initial state."""
        assert koopa.state == c.WALK


class TestKoopaBehavior:
    """Tests for Koopa behavior."""

    def test_koopa_shell_sliding(self, koopa: Koopa) -> None:
        """Test Koopa shell sliding."""
        koopa.state = c.SHELL_SLIDE
        koopa.handle_state()

    def test_koopa_falling(self, koopa: Koopa) -> None:
        """Test Koopa falling."""
        koopa.y_vel = 0
        koopa.falling()
        assert koopa.y_vel > 0


class TestEnemyIntegration:
    """Integration tests for enemies."""

    def test_goomba_movement_cycle(self, goomba: Goomba) -> None:
        """Test Goomba movement cycle."""
        goomba.current_time = 1000
        goomba.walking()
        assert goomba.frame_index >= 0

    def test_koopa_movement_cycle(self, koopa: Koopa) -> None:
        """Test Koopa movement cycle."""
        koopa.current_time = 1000
        koopa.walking()
        assert koopa.frame_index >= 0

    def test_enemy_direction_change(self, enemy: Enemy) -> None:
        """Test enemy can change direction."""
        enemy.direction = c.LEFT
        enemy.set_velocity()
        assert enemy.x_vel < 0
        enemy.direction = c.RIGHT
        enemy.set_velocity()
        assert enemy.x_vel > 0
