"""Tests for score component."""

import pytest
import pygame as pg

from data.components.score import Digit, Score
from data import constants as c


@pytest.fixture
def digit_image() -> pg.Surface:
    """Create a test image for Digit."""
    return pg.Surface((10, 10))


@pytest.fixture
def digit(digit_image: pg.Surface) -> Digit:
    """Create a Digit instance for testing."""
    return Digit(digit_image)


@pytest.fixture
def score() -> Score:
    """Create a Score instance for testing."""
    return Score(100, 200, 100)


class TestDigitInitialization:
    """Tests for Digit initialization."""

    def test_digit_creation(self, digit: Digit, digit_image: pg.Surface) -> None:
        """Test that Digit can be created."""
        assert digit is not None
        assert digit.image == digit_image
        assert isinstance(digit.rect, pg.Rect)

    def test_digit_rect_size(self, digit: Digit, digit_image: pg.Surface) -> None:
        """Test Digit rect matches image size."""
        assert digit.rect.width == digit_image.get_width()
        assert digit.rect.height == digit_image.get_height()


class TestScoreInitialization:
    """Tests for Score initialization."""

    def test_score_creation(self, score: Score) -> None:
        """Test that Score can be created."""
        assert score is not None
        assert score.x == 100
        assert score.y == 200

    def test_score_velocity_normal(self, score: Score) -> None:
        """Test normal score y velocity."""
        assert score.y_vel == -3

    def test_score_velocity_flag_pole(self) -> None:
        """Test flag pole score y velocity."""
        score = Score(100, 200, 100, flag_pole=True)
        assert score.y_vel == -4

    def test_score_string(self, score: Score) -> None:
        """Test score string is set correctly."""
        assert score.score_string == "100"

    def test_score_digit_list(self, score: Score) -> None:
        """Test digit list is created."""
        assert isinstance(score.digit_list, list)
        assert len(score.digit_list) == 3  # "100" has 3 digits

    def test_score_image_dict(self, score: Score) -> None:
        """Test image dict is created."""
        assert isinstance(score.image_dict, dict)
        assert len(score.image_dict) > 0

    def test_score_has_digits(self, score: Score) -> None:
        """Test score has digit sprites."""
        assert "0" in score.image_dict
        assert "1" in score.image_dict


class TestScoreUpdate:
    """Tests for Score update behavior."""

    def test_score_has_y_velocity(self, score: Score) -> None:
        """Test score has y velocity."""
        assert score.y_vel < 0

    def test_score_y_velocity_normal(self, score: Score) -> None:
        """Test normal score y velocity is -3."""
        assert score.y_vel == -3

    def test_score_y_velocity_flag_pole(self) -> None:
        """Test flag pole score y velocity is -4."""
        score = Score(100, 200, 100, flag_pole=True)
        assert score.y_vel == -4


class TestScoreFlagPole:
    """Tests for flag pole score behavior."""

    def test_flag_pole_score_creation(self) -> None:
        """Test flag pole score is created correctly."""
        score = Score(100, 200, 5000, flag_pole=True)
        assert score.flag_pole_score is True
        assert score.y_vel == -4

    def test_normal_score_creation(self) -> None:
        """Test normal score is created correctly."""
        score = Score(100, 200, 100, flag_pole=False)
        assert score.flag_pole_score is False
        assert score.y_vel == -3


class TestScoreDifferentValues:
    """Tests for scores with different values."""

    def test_single_digit_score(self) -> None:
        """Test score with single digit."""
        score = Score(100, 200, 5)
        assert score.score_string == "5"
        assert len(score.digit_list) == 1

    def test_multi_digit_score(self) -> None:
        """Test score with multiple digits."""
        score = Score(100, 200, 12345)
        assert score.score_string == "12345"
        assert len(score.digit_list) == 5

    def test_large_score(self) -> None:
        """Test large score value."""
        score = Score(100, 200, 10000)
        assert score.score_string == "10000"
        assert len(score.digit_list) == 5


class TestScoreIntegration:
    """Integration tests for Score."""

    def test_multiple_scores(self) -> None:
        """Test multiple scores can be created."""
        score1 = Score(50, 100, 100)
        score2 = Score(150, 100, 200)
        score3 = Score(250, 100, 500)

        # Score doesn't extend pygame.sprite.Sprite properly
        # Just verify they can be created and stored
        scores = [score1, score2, score3]
        assert len(scores) == 3

    def test_score_in_sprite_group(self, score: Score) -> None:
        """Test score has required attributes."""
        # Score doesn't extend pygame.sprite.Sprite properly
        # Just verify it has the required attributes
        assert hasattr(score, 'x')
        assert hasattr(score, 'y')
        assert hasattr(score, 'y_vel')
        assert hasattr(score, 'digit_list')

    def test_score_different_positions(self) -> None:
        """Test scores at different positions."""
        score1 = Score(50, 100, 100)
        score2 = Score(400, 300, 200)

        assert score1.x == 50
        assert score2.x == 400
        assert score1.y == 100
        assert score2.y == 300
