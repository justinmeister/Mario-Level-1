"""Tests for collider component."""

import pytest
import pygame as pg

from data.components.collider import Collider


@pytest.fixture
def collider() -> Collider:
    """Create a Collider instance for testing."""
    return Collider(100, 200, 50, 60)


class TestColliderInitialization:
    """Tests for Collider initialization."""

    def test_collider_creation(self, collider: Collider) -> None:
        """Test that Collider can be created."""
        assert collider is not None

    def test_collider_rect(self, collider: Collider) -> None:
        """Test Collider has correct rect."""
        assert isinstance(collider.rect, pg.Rect)
        assert collider.rect.x == 100
        assert collider.rect.y == 200
        assert collider.rect.width == 50
        assert collider.rect.height == 60

    def test_collider_name(self, collider: Collider) -> None:
        """Test Collider default name."""
        assert collider.name == "collider"

    def test_collider_state(self, collider: Collider) -> None:
        """Test Collider initial state."""
        assert collider.state is None

    def test_collider_image_transparent(self, collider: Collider) -> None:
        """Test Collider image is transparent surface."""
        assert isinstance(collider.image, pg.Surface)
        assert collider.image.get_flags() & pg.SRCALPHA


class TestColliderCustomization:
    """Tests for Collider customization."""

    def test_custom_name(self) -> None:
        """Test Collider with custom name."""
        collider = Collider(0, 0, 10, 10, name="pipe")
        assert collider.name == "pipe"

    def test_different_sizes(self) -> None:
        """Test Collider with different sizes."""
        collider1 = Collider(0, 0, 100, 20)
        assert collider1.rect.width == 100
        assert collider1.rect.height == 20

        collider2 = Collider(0, 0, 20, 100)
        assert collider2.rect.width == 20
        assert collider2.rect.height == 100

    def test_negative_position(self) -> None:
        """Test Collider with negative position."""
        collider = Collider(-50, -100, 10, 10)
        assert collider.rect.x == -50
        assert collider.rect.y == -100


class TestColliderState:
    """Tests for Collider state."""

    def test_set_state(self, collider: Collider) -> None:
        """Test setting collider state."""
        collider.state = "active"
        assert collider.state == "active"

    def test_change_state(self, collider: Collider) -> None:
        """Test changing collider state."""
        collider.state = "state1"
        collider.state = "state2"
        assert collider.state == "state2"


class TestColliderCollision:
    """Tests for Collider collision behavior."""

    def test_collider_rect_collision(self, collider: Collider) -> None:
        """Test collider rect collision detection."""
        other_rect = pg.Rect(120, 220, 50, 50)
        assert collider.rect.colliderect(other_rect)

    def test_collider_no_collision(self, collider: Collider) -> None:
        """Test collider when not colliding."""
        other_rect = pg.Rect(500, 500, 50, 50)
        assert not collider.rect.colliderect(other_rect)

    def test_collider_contains_point(self, collider: Collider) -> None:
        """Test if collider rect contains a point."""
        assert collider.rect.collidepoint(125, 230)
        assert not collider.rect.collidepoint(0, 0)


class TestColliderIntegration:
    """Integration tests for Collider."""

    def test_multiple_colliders(self) -> None:
        """Test multiple colliders in a group."""
        collider1 = Collider(0, 0, 50, 50)
        collider2 = Collider(100, 100, 50, 50)
        collider3 = Collider(25, 25, 50, 50)

        group = pg.sprite.Group(collider1, collider2, collider3)
        assert len(group) == 3

    def test_collider_with_sprite_collision(self, collider: Collider) -> None:
        """Test collider collision with actual sprite."""
        sprite = pg.sprite.Sprite()
        sprite.image = pg.Surface((20, 20))
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = 110
        sprite.rect.y = 210

        assert collider.rect.colliderect(sprite.rect)

    def test_ground_collider(self) -> None:
        """Test typical ground collider setup."""
        ground = Collider(0, 500, 2000, 60, name="ground")
        assert ground.rect.width == 2000
        assert ground.rect.height == 60
        assert ground.name == "ground"

    def test_pipe_collider(self) -> None:
        """Test typical pipe collider setup."""
        pipe = Collider(500, 400, 60, 100, name="pipe")
        assert pipe.rect.width == 60
        assert pipe.rect.height == 100
        assert pipe.name == "pipe"

    def test_step_collider(self) -> None:
        """Test typical step collider setup."""
        step = Collider(300, 350, 30, 30, name="step")
        assert step.rect.width == 30
        assert step.rect.height == 30
        assert step.name == "step"
