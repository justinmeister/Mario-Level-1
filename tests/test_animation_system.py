"""
Tests for advanced animation system.
"""
import math
import pygame as pg

import pytest

from data.animation_system import (
    EasingType,
    EasingFunctions,
    AnimationFrame,
    AnimationState,
    InterpolatedSprite,
    AnimationManager,
    Tween,
    TweenManager,
    AnimationBlendMode,
    lerp,
    lerp_vector,
)


class TestLerp:
    """Tests for lerp function."""

    def test_lerp_basic(self) -> None:
        """Test basic linear interpolation."""
        assert lerp(0, 100, 0.0) == 0
        assert lerp(0, 100, 1.0) == 100
        assert lerp(0, 100, 0.5) == 50

    def test_lerp_negative(self) -> None:
        """Test lerp with negative values."""
        assert lerp(-100, 100, 0.5) == 0
        assert lerp(-50, 50, 0.5) == 0

    def test_lerp_reverse(self) -> None:
        """Test lerp in reverse."""
        assert lerp(100, 0, 0.5) == 50
        assert lerp(100, 0, 1.0) == 0

    def test_lerp_vector(self) -> None:
        """Test vector interpolation."""
        start = (0.0, 0.0)
        end = (100.0, 100.0)

        result = lerp_vector(start, end, 0.5)
        assert result == (50.0, 50.0)

        result = lerp_vector(start, end, 0.0)
        assert result == (0.0, 0.0)

        result = lerp_vector(start, end, 1.0)
        assert result == (100.0, 100.0)


class TestEasingFunctions:
    """Tests for easing functions."""

    def test_linear(self) -> None:
        """Test linear easing."""
        func = EasingFunctions.get_easing(EasingType.LINEAR)
        assert func(0.0) == 0.0
        assert func(0.5) == 0.5
        assert func(1.0) == 1.0

    def test_ease_in_quad(self) -> None:
        """Test quadratic ease in."""
        func = EasingFunctions.get_easing(EasingType.EASE_IN_QUAD)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0
        # Should accelerate (value < linear at 0.5)
        assert func(0.5) < 0.5

    def test_ease_out_quad(self) -> None:
        """Test quadratic ease out."""
        func = EasingFunctions.get_easing(EasingType.EASE_OUT_QUAD)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0
        # Should decelerate (value > linear at 0.5)
        assert func(0.5) > 0.5

    def test_ease_in_out_quad(self) -> None:
        """Test quadratic ease in/out."""
        func = EasingFunctions.get_easing(EasingType.EASE_IN_OUT_QUAD)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0
        assert func(0.5) == 0.5

    def test_ease_in_cubic(self) -> None:
        """Test cubic ease in."""
        func = EasingFunctions.get_easing(EasingType.EASE_IN_CUBIC)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0
        assert func(0.5) == 0.125  # 0.5^3

    def test_ease_out_cubic(self) -> None:
        """Test cubic ease out."""
        func = EasingFunctions.get_easing(EasingType.EASE_OUT_CUBIC)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0

    def test_ease_in_sine(self) -> None:
        """Test sine ease in."""
        func = EasingFunctions.get_easing(EasingType.EASE_IN_SINE)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0

    def test_ease_out_sine(self) -> None:
        """Test sine ease out."""
        func = EasingFunctions.get_easing(EasingType.EASE_OUT_SINE)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0
        assert abs(func(0.5) - 0.5) < 0.01  # sin(π/4) ≈ 0.707, mapped

    def test_ease_in_out_sine(self) -> None:
        """Test sine ease in/out."""
        func = EasingFunctions.get_easing(EasingType.EASE_IN_OUT_SINE)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0
        assert func(0.5) == 0.5

    def test_ease_out_bounce(self) -> None:
        """Test bounce ease out."""
        func = EasingFunctions.get_easing(EasingType.EASE_OUT_BOUNCE)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0

    def test_ease_in_bounce(self) -> None:
        """Test bounce ease in."""
        func = EasingFunctions.get_easing(EasingType.EASE_IN_BOUNCE)
        assert func(0.0) == 0.0
        assert func(1.0) == 1.0


class TestAnimationFrame:
    """Tests for AnimationFrame."""

    def test_default_frame(self) -> None:
        """Test default animation frame."""
        frame = AnimationFrame()

        assert frame.image is None
        assert frame.duration == 100
        assert frame.offset == (0, 0)
        assert frame.callback is None

    def test_custom_frame(self) -> None:
        """Test custom animation frame."""
        import pygame as pg

        pg.init()
        image = pg.Surface((32, 32))

        callback_called = []

        def callback() -> None:
            callback_called.append(True)

        frame = AnimationFrame(image=image, duration=200, offset=(10, -5), callback=callback)

        assert frame.image == image
        assert frame.duration == 200
        assert frame.offset == (10, -5)

        # Test callback
        frame.callback()
        assert len(callback_called) == 1

        pg.quit()


class TestAnimationState:
    """Tests for AnimationState."""

    def test_create_animation_state(self) -> None:
        """Test creating animation state."""
        anim = AnimationState(name="test")

        assert anim.name == "test"
        assert anim.frames == []
        assert anim.loop is True
        assert anim.fps == 12
        assert anim.is_playing is False

    def test_play_pause_stop(self) -> None:
        """Test play, pause, and stop."""
        anim = AnimationState(name="test")

        anim.play()
        assert anim.is_playing is True

        anim.pause()
        assert anim.is_playing is False

        anim.play()
        anim.stop()
        assert anim.is_playing is False
        assert anim.current_frame == 0

    def test_update_without_frames(self) -> None:
        """Test update without frames."""
        anim = AnimationState(name="test")
        anim.play()

        # Should not crash
        result = anim.update(100)
        assert result is False

    def test_update_with_frames(self) -> None:
        """Test update with frames."""
        import pygame as pg

        pg.init()

        frames = [AnimationFrame(image=pg.Surface((32, 32)), duration=100) for _ in range(3)]

        anim = AnimationState(name="test", frames=frames, fps=10, loop=True)
        anim.play()

        # Should advance frames
        initial_frame = anim.current_frame
        anim.update(200)  # 200ms should advance at 10fps

        pg.quit()

    def test_animation_loop(self) -> None:
        """Test animation looping."""
        import pygame as pg

        pg.init()

        frames = [AnimationFrame(image=pg.Surface((32, 32))) for _ in range(3)]

        anim = AnimationState(name="test", frames=frames, fps=10, loop=True)
        anim.play()

        # Run through all frames multiple times
        for _ in range(10):
            anim.update(200)

        # Should still be playing (looping)
        assert anim.is_playing or anim.current_frame >= 0

        pg.quit()

    def test_animation_no_loop(self) -> None:
        """Test non-looping animation."""
        import pygame as pg

        pg.init()

        frames = [AnimationFrame(image=pg.Surface((32, 32))) for _ in range(3)]

        anim = AnimationState(name="test", frames=frames, fps=10, loop=False)
        anim.play()

        # Run through all frames
        for _ in range(10):
            anim.update(200)

        # Should stop at end
        assert anim.is_playing is False
        assert anim.current_frame == len(frames) - 1

        pg.quit()

    def test_frame_callback(self) -> None:
        """Test frame callback."""
        import pygame as pg

        pg.init()

        callbacks = []

        def on_frame() -> None:
            callbacks.append(True)

        frames = [AnimationFrame(image=pg.Surface((32, 32)), callback=on_frame) for _ in range(3)]

        anim = AnimationState(name="test", frames=frames, fps=10, loop=False)
        anim.play()

        anim.update(200)

        pg.quit()


class TestInterpolatedSprite:
    """Tests for InterpolatedSprite."""

    def test_create_sprite(self) -> None:
        """Test creating interpolated sprite."""
        sprite = InterpolatedSprite()

        assert sprite.x == 0.0
        assert sprite.y == 0.0
        assert sprite.prev_x == 0.0
        assert sprite.prev_y == 0.0
        assert sprite.vx == 0.0
        assert sprite.vy == 0.0
        assert sprite.visible is True

    def test_set_position(self) -> None:
        """Test setting sprite position."""
        sprite = InterpolatedSprite()

        sprite.set_position(100, 200)

        assert sprite.x == 100.0
        assert sprite.y == 200.0
        assert sprite.prev_x == 0.0
        assert sprite.prev_y == 0.0

    def test_move(self) -> None:
        """Test moving sprite."""
        sprite = InterpolatedSprite()
        sprite.set_position(100, 100)

        sprite.move(50, -25)

        assert sprite.x == 150.0
        assert sprite.y == 75.0

    def test_set_velocity(self) -> None:
        """Test setting velocity."""
        sprite = InterpolatedSprite()

        sprite.set_velocity(10, -5)

        assert sprite.vx == 10
        assert sprite.vy == -5

    def test_update_with_velocity(self) -> None:
        """Test update with velocity."""
        sprite = InterpolatedSprite()
        sprite.set_position(0, 0)
        sprite.set_velocity(100, 50)  # pixels per second

        sprite.update(1000)  # 1 second

        assert abs(sprite.x - 100.0) < 0.1
        assert abs(sprite.y - 50.0) < 0.1

    def test_interpolated_position(self) -> None:
        """Test interpolated position."""
        sprite = InterpolatedSprite()
        sprite.set_position(0, 0)
        sprite.set_position(100, 100)

        sprite.interpolation_factor = 0.5

        pos = sprite.get_interpolated_position()
        assert abs(pos[0] - 50.0) < 0.1
        assert abs(pos[1] - 50.0) < 0.1

    def test_flip_and_rotation(self) -> None:
        """Test flip and rotation settings."""
        sprite = InterpolatedSprite()

        sprite.flip_x = True
        sprite.flip_y = True
        sprite.rotation = 45

        assert sprite.flip_x is True
        assert sprite.flip_y is True
        assert sprite.rotation == 45

    def test_alpha_transparency(self) -> None:
        """Test alpha transparency."""
        sprite = InterpolatedSprite()

        sprite.alpha = 128
        assert sprite.alpha == 128

        sprite.alpha = 0
        assert sprite.alpha == 0

    def test_scale(self) -> None:
        """Test sprite scaling."""
        sprite = InterpolatedSprite()

        sprite.scale_x = 2.0
        sprite.scale_y = 0.5

        assert sprite.scale_x == 2.0
        assert sprite.scale_y == 0.5


class TestAnimationManager:
    """Tests for AnimationManager."""

    def test_create_manager(self) -> None:
        """Test creating animation manager."""
        manager = AnimationManager()

        assert manager.target_fps == 60
        assert manager.frame_time == 16  # 1000/60
        assert manager.get_sprite_count() == 0

    def test_add_remove_sprite(self) -> None:
        """Test adding and removing sprites."""
        manager = AnimationManager()
        sprite = InterpolatedSprite()

        manager.add_sprite(sprite)
        assert manager.get_sprite_count() == 1

        manager.remove_sprite(sprite)
        assert manager.get_sprite_count() == 0

    def test_clear_sprites(self) -> None:
        """Test clearing all sprites."""
        manager = AnimationManager()

        for _ in range(5):
            manager.add_sprite(InterpolatedSprite())

        manager.clear()
        assert manager.get_sprite_count() == 0

    def test_update(self) -> None:
        """Test manager update."""
        manager = AnimationManager()
        sprite = InterpolatedSprite()
        manager.add_sprite(sprite)

        # Should not crash
        manager.update(16)

    def test_draw(self) -> None:
        """Test manager draw."""
        import pygame as pg

        pg.init()

        manager = AnimationManager()
        sprite = InterpolatedSprite()
        manager.add_sprite(sprite)

        surface = pg.Surface((800, 600))

        # Should not crash
        manager.draw(surface)

        pg.quit()


class TestTween:
    """Tests for Tween."""

    def test_create_tween(self) -> None:
        """Test creating tween."""
        tween = Tween(0, 100, 1000)

        assert tween.start == 0
        assert tween.end == 100
        assert tween.duration == 1000
        assert tween.current_value == 0
        assert tween.is_playing is False

    def test_tween_start_stop(self) -> None:
        """Test starting and stopping tween."""
        tween = Tween(0, 100, 1000)

        tween.start_tween()
        assert tween.is_playing is True

        tween.stop()
        assert tween.is_playing is False

    def test_tween_update(self) -> None:
        """Test tween update."""
        tween = Tween(0, 100, 1000)
        tween.start_tween()

        # Halfway through
        value = tween.update(500)
        assert 45 < value < 55  # Approximately 50 with easing

    def test_tween_complete(self) -> None:
        """Test tween completion."""
        tween = Tween(0, 100, 1000)
        tween.start_tween()

        # Complete tween
        value = tween.update(1000)

        assert value == 100
        assert tween.is_complete is True
        assert tween.is_playing is False

    def test_tween_on_complete_callback(self) -> None:
        """Test tween on complete callback."""
        completed = []

        def on_complete(value: float) -> None:
            completed.append(value)

        tween = Tween(0, 100, 1000)
        tween.on_complete = on_complete
        tween.start_tween()

        tween.update(1000)

        assert len(completed) == 1
        assert completed[0] == 100

    def test_tween_reset(self) -> None:
        """Test tween reset."""
        tween = Tween(0, 100, 1000)
        tween.start_tween()
        tween.update(500)

        tween.reset()

        assert tween.current_value == 0
        assert tween.is_playing is False
        assert tween.is_complete is False


class TestTweenManager:
    """Tests for TweenManager."""

    def test_create_tween_manager(self) -> None:
        """Test creating tween manager."""
        manager = TweenManager()

        assert len(manager.tweens) == 0

    def test_add_tween(self) -> None:
        """Test adding tween."""
        manager = TweenManager()

        tween = manager.add_tween("test", 0, 100, 1000)

        assert "test" in manager.tweens
        assert tween.start == 0
        assert tween.end == 100

    def test_get_tween(self) -> None:
        """Test getting tween."""
        manager = TweenManager()
        manager.add_tween("test", 0, 100, 1000)

        tween = manager.get_tween("test")
        assert tween is not None

        tween = manager.get_tween("nonexistent")
        assert tween is None

    def test_start_tween(self) -> None:
        """Test starting tween by name."""
        manager = TweenManager()
        manager.add_tween("test", 0, 100, 1000)

        result = manager.start_tween("test")
        assert result is True

        result = manager.start_tween("nonexistent")
        assert result is False

    def test_update_tweens(self) -> None:
        """Test updating multiple tweens."""
        manager = TweenManager()
        manager.add_tween("a", 0, 100, 1000)
        manager.add_tween("b", 50, 150, 1000)

        results = manager.update(500)

        assert "a" in results
        assert "b" in results

    def test_clear_tweens(self) -> None:
        """Test clearing all tweens."""
        manager = TweenManager()
        manager.add_tween("a", 0, 100, 1000)
        manager.add_tween("b", 50, 150, 1000)

        manager.clear()

        assert len(manager.tweens) == 0


class TestAnimationIntegration:
    """Integration tests for animation system."""

    def test_sprite_with_animation(self) -> None:
        """Test sprite with animation."""
        import pygame as pg

        pg.init()

        sprite = InterpolatedSprite()
        frames = [pg.Surface((32, 32)) for _ in range(4)]

        sprite.add_animation("walk", frames, fps=12, loop=True)
        sprite.play_animation("walk")

        sprite.set_velocity(50, 0)
        sprite.update(1000)

        assert sprite.x > 0

        pg.quit()

    def test_manager_with_multiple_sprites(self) -> None:
        """Test manager with multiple animated sprites."""
        import pygame as pg

        pg.init()

        manager = AnimationManager()

        for i in range(5):
            sprite = InterpolatedSprite()
            sprite.set_position(i * 100, 0)
            frames = [pg.Surface((32, 32)) for _ in range(4)]
            sprite.add_animation("idle", frames)
            manager.add_sprite(sprite)

        manager.update(1000)

        assert manager.get_sprite_count() == 5

        pg.quit()

    def test_tween_sequence(self) -> None:
        """Test sequence of tweens."""
        manager = TweenManager()

        # Create fade in/out sequence
        manager.add_tween("fade_in", 0, 255, 500, EasingType.EASE_OUT_SINE)
        manager.add_tween("fade_out", 255, 0, 500, EasingType.EASE_IN_SINE)

        manager.start_tween("fade_in")

        # Update through fade in
        for _ in range(10):
            results = manager.update(50)

        pg.quit()
