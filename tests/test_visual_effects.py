"""
Tests for visual effects module.
"""
import pytest
import pygame as pg

from data.visual_effects import (
    Particle,
    ParticleSystem,
    ParallaxBackground,
    ScreenShake,
    FadeTransition,
)


class TestParticle:
    """Tests for Particle class."""

    def test_particle_creation(self) -> None:
        """Test particle initialization."""
        particle = Particle(100, 200, 1.0, -2.0, 1000)

        assert particle.x == 100
        assert particle.y == 200
        assert particle.vx == 1.0
        assert particle.vy == -2.0
        assert particle.lifetime == 1000
        assert particle.age == 0
        assert particle.size == 4
        assert particle.gravity == 0.5
        assert particle.alpha == 255

    def test_particle_custom_params(self) -> None:
        """Test particle with custom parameters."""
        particle = Particle(
            x=50,
            y=50,
            vx=0,
            vy=0,
            lifetime=500,
            color=(255, 0, 0),
            size=8,
            gravity=1.0,
            alpha=128,
        )

        assert particle.x == 50
        assert particle.color == (255, 0, 0)
        assert particle.size == 8
        assert particle.alpha == 128

    def test_particle_update_alive(self) -> None:
        """Test particle update while still alive."""
        particle = Particle(100, 200, 1.0, 0, 1000)

        result = particle.update(500)

        assert result is True
        assert particle.age == 500
        assert particle.x > 100

    def test_particle_update_dead(self) -> None:
        """Test particle update when lifetime expires."""
        particle = Particle(100, 200, 0, 0, 100)

        result = particle.update(150)

        assert result is False

    def test_particle_update_with_gravity(self) -> None:
        """Test particle velocity changes with gravity."""
        particle = Particle(100, 200, 0, 0, 1000, gravity=0.5)

        particle.update(100)

        assert particle.vy > 0

    def test_particle_update_alpha_fade(self) -> None:
        """Test particle alpha fades over time."""
        particle = Particle(100, 200, 0, 0, 1000, alpha=255)

        particle.update(500)

        assert particle.alpha < 255
        assert particle.alpha > 0

    def test_particle_draw(self, init_pygame) -> None:
        """Test particle drawing."""
        particle = Particle(100, 200, 0, 0, 1000)
        surface = pg.Surface((800, 600))

        particle.draw(surface)

        assert surface.get_at((100, 200)) != (0, 0, 0, 0)

    def test_particle_rect_update(self) -> None:
        """Test particle rect updates with position."""
        particle = Particle(100, 200, 10, 0, 1000)

        particle.update(100)

        assert particle.rect.centerx != 100


@pytest.fixture
def init_pygame():
    """Initialize pygame for tests."""
    pg.init()
    yield
    pg.quit()


class TestParticleSystem:
    """Tests for ParticleSystem class."""

    def test_system_creation(self) -> None:
        """Test particle system initialization."""
        system = ParticleSystem()

        assert len(system.particles) == 0

    def test_emit_particle(self, init_pygame) -> None:
        """Test emitting particles."""
        system = ParticleSystem()

        system.emit(400, 300, count=10)

        assert len(system.particles) == 10

    def test_emit_custom_particle(self, init_pygame) -> None:
        """Test emitting particles with custom parameters."""
        system = ParticleSystem()

        system.emit(
            400,
            300,
            count=5,
            vx_range=(-2, 2),
            vy_range=(-5, -3),
            color=(255, 0, 0),
            lifetime_range=(500, 1000),
        )

        assert len(system.particles) == 5
        # Color has variation, check it's close to red
        for p in system.particles:
            assert p.color[0] > 200  # Red component dominant

    def test_update_system(self, init_pygame) -> None:
        """Test updating particle system."""
        system = ParticleSystem()
        system.emit(400, 300, count=10, lifetime_range=(100, 200))

        system.update(300)

        assert len(system.particles) == 0

    def test_update_partial(self, init_pygame) -> None:
        """Test partial update keeps some particles."""
        system = ParticleSystem()
        system.emit(400, 300, count=10, lifetime_range=(500, 1000))

        system.update(100)

        assert len(system.particles) > 0

    def test_clear_system(self, init_pygame) -> None:
        """Test clearing all particles."""
        system = ParticleSystem()
        system.emit(400, 300, count=20)

        system.clear()

        assert len(system.particles) == 0

    def test_update_with_viewport(self, init_pygame) -> None:
        """Test particle update with viewport offset."""
        system = ParticleSystem()
        system.emit(400, 300, count=5)

        system.update(100, viewport_x=100)

        assert len(system.particles) > 0

    def test_draw_system(self, init_pygame) -> None:
        """Test drawing particle system."""
        system = ParticleSystem()
        system.emit(400, 300, count=10)
        surface = pg.Surface((800, 600))

        system.draw(surface)

        assert True

    def test_emit_zero_particles(self, init_pygame) -> None:
        """Test emitting zero particles."""
        system = ParticleSystem()

        system.emit(400, 300, count=0)

        assert len(system.particles) == 0


class TestParallaxBackground:
    """Tests for ParallaxBackground class."""

    def test_background_creation(self, init_pygame) -> None:
        """Test parallax background initialization."""
        bg = ParallaxBackground(800, 600)

        assert bg.width == 800
        assert bg.height == 600
        assert bg.layers == 3
        assert len(bg.layer_surfaces) == 3

    def test_custom_layers(self, init_pygame) -> None:
        """Test custom number of layers."""
        bg = ParallaxBackground(800, 600, layers=2)

        assert bg.layers == 2
        assert len(bg.layer_surfaces) == 2

    def test_custom_scroll_speeds(self, init_pygame) -> None:
        """Test custom scroll speeds."""
        bg = ParallaxBackground(800, 600, scroll_speeds=[0.2, 0.5, 0.8])

        assert bg.scroll_speeds == [0.2, 0.5, 0.8]

    def test_update(self, init_pygame) -> None:
        """Test background update."""
        bg = ParallaxBackground(800, 600)

        bg.update(0)

        assert bg.layer_positions[0] == 0

    def test_update_with_camera(self, init_pygame) -> None:
        """Test update with camera position."""
        bg = ParallaxBackground(800, 600)

        bg.update(500)

        assert bg.layer_positions[0] != 0

    def test_draw(self, init_pygame) -> None:
        """Test drawing background."""
        bg = ParallaxBackground(800, 600)
        target = pg.Surface((800, 600))

        bg.draw(target)

        assert True


class TestScreenShake:
    """Tests for ScreenShake class."""

    def test_shake_creation(self) -> None:
        """Test screen shake initialization."""
        shake = ScreenShake(intensity=10.0, decay=0.9)

        assert shake.intensity == 10.0
        assert shake.decay == 0.9
        assert shake.current_intensity == 0.0

    def test_shake_trigger(self) -> None:
        """Test triggering screen shake."""
        shake = ScreenShake(intensity=10.0)

        shake.trigger()

        assert shake.current_intensity == 10.0

    def test_shake_trigger_custom(self) -> None:
        """Test triggering with custom intensity."""
        shake = ScreenShake(intensity=10.0)

        shake.trigger(intensity=20.0)

        assert shake.current_intensity == 20.0

    def test_shake_update_active(self) -> None:
        """Test shake update while active."""
        shake = ScreenShake(intensity=10.0, decay=0.9)
        shake.trigger()

        offset = shake.update()

        assert offset[0] != 0 or offset[1] != 0
        assert shake.current_intensity < 10.0

    def test_shake_update_inactive(self) -> None:
        """Test shake update when inactive."""
        shake = ScreenShake(intensity=10.0)

        offset = shake.update()

        assert offset == (0, 0)
        assert shake.is_active() is False

    def test_shake_decay(self) -> None:
        """Test shake intensity decays."""
        shake = ScreenShake(intensity=10.0, decay=0.5)
        shake.trigger()

        initial = shake.current_intensity
        shake.update()

        assert shake.current_intensity < initial

    def test_shake_is_active(self) -> None:
        """Test shake active check."""
        shake = ScreenShake(intensity=10.0)

        assert shake.is_active() is False

        shake.trigger()

        assert shake.is_active() is True


class TestFadeTransition:
    """Tests for FadeTransition class."""

    def test_fade_creation(self) -> None:
        """Test fade transition initialization."""
        fade = FadeTransition()

        assert fade.alpha == 0
        assert fade.target_alpha == 0
        assert fade.speed == 10

    def test_fade_in(self) -> None:
        """Test fade in."""
        fade = FadeTransition()

        fade.fade_in()

        assert fade.alpha == 255
        assert fade.target_alpha == 0

    def test_fade_out(self) -> None:
        """Test fade out."""
        fade = FadeTransition()

        fade.fade_out()

        assert fade.alpha == 0
        assert fade.target_alpha == 255

    def test_fade_update_fading_in(self) -> None:
        """Test update while fading in."""
        fade = FadeTransition()
        fade.fade_in()

        result = fade.update()

        assert result is False
        assert fade.alpha < 255

    def test_fade_update_fading_out(self) -> None:
        """Test update while fading out."""
        fade = FadeTransition()
        fade.fade_out()

        result = fade.update()

        assert result is False
        assert fade.alpha > 0

    def test_fade_update_complete_in(self) -> None:
        """Test fade in completion."""
        fade = FadeTransition()
        fade.fade_in()
        fade.alpha = 0

        result = fade.update()

        assert result is True
        assert fade.alpha == 0

    def test_fade_update_complete_out(self) -> None:
        """Test fade out completion."""
        fade = FadeTransition()
        fade.fade_out()
        fade.alpha = 255

        result = fade.update()

        assert result is True
        assert fade.alpha == 255

    def test_fade_draw(self, init_pygame) -> None:
        """Test fade drawing."""
        fade = FadeTransition()
        fade.fade_out()
        surface = pg.Surface((800, 600))

        fade.update()
        fade.draw(surface)

        assert True

    def test_fade_surface_cache(self, init_pygame) -> None:
        """Test surface caching."""
        fade = FadeTransition()
        fade.fade_out()
        surface = pg.Surface((800, 600))

        fade.update()
        fade.draw(surface)

        assert fade.surface is not None
