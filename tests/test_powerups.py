"""Tests for powerup components."""

import pytest
import pygame as pg

from data.components.powerups import (
    Powerup,
    Mushroom,
    LifeMushroom,
    FireFlower,
    Star,
    FireBall,
)
from data import constants as c


@pytest.fixture
def powerup() -> Powerup:
    """Create a base Powerup instance for testing."""
    return Powerup(100, 200)


@pytest.fixture
def mushroom() -> Mushroom:
    """Create a Mushroom instance for testing."""
    return Mushroom(100, 200)


@pytest.fixture
def fire_flower() -> FireFlower:
    """Create a FireFlower instance for testing."""
    return FireFlower(100, 200)


@pytest.fixture
def star() -> Star:
    """Create a Star instance for testing."""
    return Star(100, 200)


class TestPowerupInitialization:
    """Tests for Powerup initialization."""

    def test_powerup_creation(self, powerup: Powerup) -> None:
        """Test that Powerup can be created."""
        assert powerup is not None

    def test_powerup_initial_state(self, powerup: Powerup) -> None:
        """Test Powerup's initial state."""
        assert powerup.state == c.REVEAL
        assert powerup.gravity == 1
        assert powerup.frame_index == 0

    def test_powerup_velocity(self, powerup: Powerup) -> None:
        """Test Powerup initial velocity."""
        assert powerup.y_vel == -1
        assert powerup.x_vel == 0

    def test_powerup_direction(self, powerup: Powerup) -> None:
        """Test Powerup initial direction."""
        assert powerup.direction == c.RIGHT

    def test_powerup_has_frames(self, powerup: Powerup) -> None:
        """Test Powerup has frames list."""
        assert hasattr(powerup, "frames")
        assert isinstance(powerup.frames, list)


class TestPowerupSetup:
    """Tests for Powerup setup methods."""

    def test_setup_powerup(self, powerup: Powerup) -> None:
        """Test setup_powerup method."""
        def dummy_setup() -> None:
            powerup.frames.append(pg.Surface((16, 16)))

        powerup.setup_powerup(150, 250, "test_item", dummy_setup)
        assert powerup.name == "test_item"
        assert powerup.rect.centerx == 150
        assert powerup.state == c.REVEAL

    def test_sliding_right(self, powerup: Powerup) -> None:
        """Test sliding state when facing right."""
        powerup.direction = c.RIGHT
        powerup.sliding()
        assert powerup.x_vel == 3

    def test_sliding_left(self, powerup: Powerup) -> None:
        """Test sliding state when facing left."""
        powerup.direction = c.LEFT
        powerup.sliding()
        assert powerup.x_vel == -3

    def test_falling_increases_velocity(self, powerup: Powerup) -> None:
        """Test falling increases y velocity."""
        powerup.y_vel = 0
        powerup.falling()
        assert powerup.y_vel == powerup.gravity


class TestMushroomInitialization:
    """Tests for Mushroom initialization."""

    def test_mushroom_creation(self, mushroom: Mushroom) -> None:
        """Test that Mushroom can be created."""
        assert mushroom is not None

    def test_mushroom_name(self, mushroom: Mushroom) -> None:
        """Test Mushroom name."""
        assert mushroom.name == "mushroom"

    def test_mushroom_has_frames(self, mushroom: Mushroom) -> None:
        """Test Mushroom has frames."""
        assert hasattr(mushroom, "frames")
        assert len(mushroom.frames) > 0


class TestMushroomBehavior:
    """Tests for Mushroom behavior."""

    def test_mushroom_revealing(self, mushroom: Mushroom) -> None:
        """Test Mushroom revealing state."""
        mushroom.state = c.REVEAL
        initial_y = mushroom.rect.y
        mushroom.revealing()
        assert mushroom.rect.y < initial_y

    def test_mushroom_sliding(self, mushroom: Mushroom) -> None:
        """Test Mushroom sliding state."""
        mushroom.state = c.SLIDE
        mushroom.sliding()
        assert mushroom.x_vel != 0


class TestLifeMushroom:
    """Tests for LifeMushroom (1-up)."""

    def test_life_mushroom_creation(self) -> None:
        """Test LifeMushroom can be created."""
        mushroom = LifeMushroom(100, 200)
        assert mushroom is not None
        assert mushroom.name == "1up_mushroom"

    def test_life_mushroom_has_frames(self) -> None:
        """Test LifeMushroom has frames."""
        mushroom = LifeMushroom(100, 200)
        assert len(mushroom.frames) > 0


class TestFireFlowerInitialization:
    """Tests for FireFlower initialization."""

    def test_fire_flower_creation(self, fire_flower: FireFlower) -> None:
        """Test that FireFlower can be created."""
        assert fire_flower is not None

    def test_fire_flower_name(self, fire_flower: FireFlower) -> None:
        """Test FireFlower name."""
        assert fire_flower.name == c.FIREFLOWER

    def test_fire_flower_has_frames(self, fire_flower: FireFlower) -> None:
        """Test FireFlower has multiple frames for animation."""
        assert len(fire_flower.frames) >= 4


class TestFireFlowerBehavior:
    """Tests for FireFlower behavior."""

    def test_fire_flower_revealing(self, fire_flower: FireFlower) -> None:
        """Test FireFlower revealing state."""
        fire_flower.state = c.REVEAL
        fire_flower.current_time = 1000
        fire_flower.revealing()

    def test_fire_flower_resting(self, fire_flower: FireFlower) -> None:
        """Test FireFlower resting state."""
        fire_flower.state = c.RESTING
        fire_flower.current_time = 1000
        fire_flower.resting()


class TestStarInitialization:
    """Tests for Star initialization."""

    def test_star_creation(self, star: Star) -> None:
        """Test that Star can be created."""
        assert star is not None

    def test_star_name(self, star: Star) -> None:
        """Test Star name."""
        assert star.name == "star"

    def test_star_has_frames(self, star: Star) -> None:
        """Test Star has multiple frames for animation."""
        assert len(star.frames) >= 4

    def test_star_gravity(self, star: Star) -> None:
        """Test Star has custom gravity."""
        assert star.gravity == 0.4


class TestStarBehavior:
    """Tests for Star behavior."""

    def test_star_revealing(self, star: Star) -> None:
        """Test Star revealing state."""
        star.state = c.REVEAL
        star.current_time = 1000
        star.revealing()

    def test_star_bouncing(self, star: Star) -> None:
        """Test Star bouncing state."""
        star.state = c.BOUNCE
        star.current_time = 1000
        star.bouncing()

    def test_star_start_bounce(self, star: Star) -> None:
        """Test Star start_bounce method."""
        star.start_bounce(-3)
        assert star.y_vel == -3


class TestFireBallInitialization:
    """Tests for FireBall initialization."""

    def test_fireball_creation_right(self) -> None:
        """Test FireBall created facing right."""
        fireball = FireBall(100, 200, facing_right=True)
        assert fireball is not None
        assert fireball.direction == c.RIGHT
        assert fireball.x_vel == 12

    def test_fireball_creation_left(self) -> None:
        """Test FireBall created facing left."""
        fireball = FireBall(100, 200, facing_right=False)
        assert fireball.direction == c.LEFT
        assert fireball.x_vel == -12

    def test_fireball_has_frames(self) -> None:
        """Test FireBall has frames."""
        fireball = FireBall(100, 200, facing_right=True)
        assert len(fireball.frames) >= 4


class TestFireBallBehavior:
    """Tests for FireBall behavior."""

    def test_fireball_handle_state_flying(self) -> None:
        """Test FireBall flying state."""
        fireball = FireBall(100, 200, facing_right=True)
        fireball.state = c.FLYING
        fireball.current_time = 1000
        fireball.handle_state()

    def test_fireball_explode_transition(self) -> None:
        """Test FireBall explode transition."""
        fireball = FireBall(100, 200, facing_right=True)
        fireball.explode_transition()
        assert fireball.state == c.EXPLODING

    def test_fireball_animation_exploding(self) -> None:
        """Test FireBall animation in exploding state."""
        fireball = FireBall(100, 200, facing_right=True)
        fireball.state = c.EXPLODING
        fireball.current_time = 1000
        fireball.animation()


class TestPowerupIntegration:
    """Integration tests for powerups."""

    def test_powerup_update(self, powerup: Powerup) -> None:
        """Test powerup update method."""
        game_info = {c.CURRENT_TIME: 1000}
        powerup.update(game_info)

    def test_mushroom_state_transition(self, mushroom: Mushroom) -> None:
        """Test Mushroom state transitions."""
        mushroom.state = c.REVEAL
        mushroom.current_time = 1000
        mushroom.handle_state()

    def test_fire_flower_animation(self, fire_flower: FireFlower) -> None:
        """Test FireFlower animation frames."""
        fire_flower.current_time = 1000
        initial_frame = fire_flower.frame_index
        fire_flower.animation()

    def test_star_animation(self, star: Star) -> None:
        """Test Star animation frames."""
        star.current_time = 1000
        star.animation()

    def test_multiple_powerups_in_group(self) -> None:
        """Test multiple powerups in a sprite group."""
        mushroom = Mushroom(100, 200)
        fire_flower = FireFlower(200, 200)
        star = Star(300, 200)

        group = pg.sprite.Group(mushroom, fire_flower, star)
        assert len(group) == 3
