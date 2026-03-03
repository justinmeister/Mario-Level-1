"""
Tests for constants module.
"""
from __future__ import annotations

import pytest
from data import constants as c


class TestConstantsExistence:
    """Tests that required constants exist."""

    def test_screen_constants(self):
        """Test screen-related constants exist."""
        assert hasattr(c, "SCREEN_WIDTH")
        assert hasattr(c, "SCREEN_HEIGHT")
        assert hasattr(c, "SCREEN_SIZE")
        assert c.SCREEN_WIDTH == 800
        assert c.SCREEN_HEIGHT == 600

    def test_color_constants(self):
        """Test color constants exist and are valid RGB tuples."""
        colors = ["WHITE", "BLACK", "RED", "GREEN", "BLUE", "YELLOW"]
        for color in colors:
            assert hasattr(c, color)
            value = getattr(c, color)
            assert isinstance(value, tuple)
            assert len(value) == 3
            assert all(0 <= v <= 255 for v in value)

    def test_mario_physics_constants(self):
        """Test Mario physics constants exist."""
        assert hasattr(c, "GRAVITY")
        assert hasattr(c, "JUMP_VEL")
        assert hasattr(c, "WALK_ACCEL")
        assert c.GRAVITY > 0
        assert c.JUMP_VEL < 0  # Negative = upward

    def test_mario_states(self):
        """Test Mario state constants exist."""
        states = ["STAND", "WALK", "JUMP", "FALL", "FLAGPOLE"]
        for state in states:
            assert hasattr(c, state)
            assert isinstance(getattr(c, state), str)

    def test_enemy_states(self):
        """Test enemy state constants exist."""
        assert hasattr(c, "LEFT")
        assert hasattr(c, "RIGHT")
        assert hasattr(c, "JUMPED_ON")
        assert hasattr(c, "DEATH_JUMP")

    def test_game_states(self):
        """Test game state constants exist."""
        states = ["MAIN_MENU", "LOAD_SCREEN", "LEVEL1", "GAME_OVER"]
        for state in states:
            assert hasattr(c, state)


class TestTimingConstants:
    """Tests for timing-related constants."""

    def test_timing_constants_exist(self):
        """Test that timing constants are defined."""
        assert hasattr(c, "ENEMY_ANIMATION_INTERVAL")
        assert hasattr(c, "FIREBALL_INTERVAL")
        assert c.ENEMY_ANIMATION_INTERVAL > 0
        assert c.FIREBALL_INTERVAL > 0


class TestScoreConstants:
    """Tests for score-related constants."""

    def test_score_constants_exist(self):
        """Test that score constants are defined."""
        assert hasattr(c, "SCORE_GOOMBA_STOMP")
        assert hasattr(c, "SCORE_STAR")
        assert c.SCORE_GOOMBA_STOMP > 0
        assert c.SCORE_STAR > 0
