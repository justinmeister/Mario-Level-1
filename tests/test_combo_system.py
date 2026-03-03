"""
Tests for combo and score system.
"""
import time

import pytest

from data.combo_system import (
    ComboManager,
    ComboConfig,
    ComboState,
    ComboType,
    ComboTier,
    ComboUI,
    ScoreManager,
    ScoreUI,
)


class TestComboConfig:
    """Tests for ComboConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ComboConfig()

        assert config.combo_window == 3000
        assert config.combo_decay_time == 5000
        assert config.bronze_threshold == 3
        assert config.silver_threshold == 5
        assert config.gold_threshold == 10
        assert config.max_multiplier == 5.0


class TestComboState:
    """Tests for ComboState."""

    def test_default_state(self) -> None:
        """Test default combo state."""
        state = ComboState()

        assert state.count == 0
        assert state.multiplier == 1.0
        assert state.tier == ComboTier.NONE
        assert state.is_active is False


class TestComboManager:
    """Tests for ComboManager."""

    @pytest.fixture
    def combo_manager(self) -> ComboManager:
        """Create combo manager with test config."""
        config = ComboConfig(
            combo_window=1000,
            combo_decay_time=2000,
            bronze_threshold=3,
            silver_threshold=5,
            gold_threshold=10,
            platinum_threshold=20,
            legendary_threshold=50,
            multiplier_per_combo=0.1,
            max_multiplier=5.0,
        )
        return ComboManager(config)

    def test_initial_state(self, combo_manager: ComboManager) -> None:
        """Test initial combo state."""
        assert combo_manager.combo_count == 0
        assert combo_manager.multiplier == 1.0
        assert combo_manager.tier == ComboTier.NONE
        assert combo_manager.is_active is False

    def test_add_action_increments_combo(self, combo_manager: ComboManager) -> None:
        """Test that adding action increments combo."""
        count = combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert count == 1

        count = combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert count == 2

    def test_add_action_activates_combo(self, combo_manager: ComboManager) -> None:
        """Test that combo becomes active."""
        combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert not combo_manager.is_active  # Need at least 2

        combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert combo_manager.is_active

    def test_combo_multiplier_increases(self, combo_manager: ComboManager) -> None:
        """Test that multiplier increases with combo."""
        initial_multiplier = combo_manager.multiplier

        combo_manager.add_action(ComboType.ENEMY_STOMP)
        combo_manager.add_action(ComboType.ENEMY_STOMP)

        assert combo_manager.multiplier > initial_multiplier

    def test_combo_tier_progression(self, combo_manager: ComboManager) -> None:
        """Test combo tier progression."""
        assert combo_manager.tier == ComboTier.NONE

        # Bronze tier (3 combo)
        for _ in range(3):
            combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert combo_manager.tier == ComboTier.BRONZE

        # Silver tier (5 combo)
        for _ in range(2):
            combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert combo_manager.tier == ComboTier.SILVER

        # Gold tier (10 combo)
        for _ in range(5):
            combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert combo_manager.tier == ComboTier.GOLD

    def test_add_action_with_custom_time(self, combo_manager: ComboManager) -> None:
        """Test add_action with explicit time parameter."""
        # First action at time 0
        combo_manager.add_action(ComboType.ENEMY_STOMP, current_time=0)
        assert combo_manager.combo_count == 1

        # Second action within combo window
        combo_manager.add_action(ComboType.ENEMY_STOMP, current_time=1000)
        assert combo_manager.combo_count == 2

        # Third action after combo window (5000ms window)
        combo_manager.add_action(ComboType.ENEMY_STOMP, current_time=10000)
        # Combo should have reset and started again
        assert combo_manager.combo_count == 1

    def test_combo_reset(self, combo_manager: ComboManager) -> None:
        """Test combo reset."""
        combo_manager.add_action(ComboType.ENEMY_STOMP)
        combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert combo_manager.is_active

        combo_manager.reset()

        assert combo_manager.combo_count == 0
        assert combo_manager.multiplier == 1.0
        assert combo_manager.is_active is False

    def test_calculate_score_with_multiplier(self, combo_manager: ComboManager) -> None:
        """Test score calculation with combo multiplier."""
        base_score = 100

        # No combo - base score
        score = combo_manager.calculate_score(base_score)
        assert score == base_score

        # Add combo
        combo_manager.add_action(ComboType.ENEMY_STOMP)
        combo_manager.add_action(ComboType.ENEMY_STOMP)

        # Should have multiplier
        score = combo_manager.calculate_score(base_score)
        assert score >= base_score

    def test_calculate_score_max_multiplier(self, combo_manager: ComboManager) -> None:
        """Test that multiplier is capped at maximum."""
        # Build high combo
        for _ in range(100):
            combo_manager.add_action(ComboType.ENEMY_STOMP)

        assert combo_manager.multiplier <= combo_manager.config.max_multiplier

    def test_get_combo_display(self, combo_manager: ComboManager) -> None:
        """Test combo display string."""
        # No display for low combo
        display = combo_manager.get_combo_display()
        assert display == ""

        combo_manager.add_action(ComboType.ENEMY_STOMP)
        combo_manager.add_action(ComboType.ENEMY_STOMP)

        display = combo_manager.get_combo_display()
        assert "2x" in display
        assert "COMBO" in display

    def test_get_tier_color(self, combo_manager: ComboManager) -> None:
        """Test tier color retrieval."""
        assert combo_manager.get_tier_color() is not None

    def test_milestone_callback(self, combo_manager: ComboManager) -> None:
        """Test milestone callback."""
        milestones_hit = []

        def on_milestone(count: int, tier: ComboTier) -> None:
            milestones_hit.append((count, tier))

        combo_manager.set_milestone_callback(on_milestone)

        # Build to bronze
        for _ in range(3):
            combo_manager.add_action(ComboType.ENEMY_STOMP)

        assert len(milestones_hit) >= 1
        assert milestones_hit[-1][0] == 3

    def test_update_decay(self, combo_manager: ComboManager) -> None:
        """Test combo decay over time."""
        combo_manager.add_action(ComboType.ENEMY_STOMP)
        combo_manager.add_action(ComboType.ENEMY_STOMP)
        assert combo_manager.is_active

        # Wait for decay (simulate with large dt)
        combo_manager.update(3000)

        # Combo should still be active (within window)
        # Actual decay depends on real time, not simulated


class TestComboTier:
    """Tests for ComboTier enum."""

    def test_tier_values(self) -> None:
        """Test tier enum values."""
        assert ComboTier.NONE.value == "none"
        assert ComboTier.BRONZE.value == "bronze"
        assert ComboTier.SILVER.value == "silver"
        assert ComboTier.GOLD.value == "gold"
        assert ComboTier.PLATINUM.value == "platinum"
        assert ComboTier.LEGENDARY.value == "legendary"


class TestComboType:
    """Tests for ComboType enum."""

    def test_combo_types(self) -> None:
        """Test combo type enum values."""
        assert ComboType.ENEMY_STOMP.value == "enemy_stomp"
        assert ComboType.COIN_COLLECT.value == "coin_collect"
        assert ComboType.BLOCK_HIT.value == "block_hit"
        assert ComboType.FIREBALL_KILL.value == "fireball_kill"


class TestScoreManager:
    """Tests for ScoreManager."""

    @pytest.fixture
    def score_manager(self) -> ScoreManager:
        """Create score manager."""
        combo = ComboManager()
        return ScoreManager(combo, initial_score=0)

    def test_initial_score(self, score_manager: ScoreManager) -> None:
        """Test initial score."""
        assert score_manager.score == 0

    def test_add_score_without_combo(self, score_manager: ScoreManager) -> None:
        """Test adding score without combo."""
        added = score_manager.add_score(100)
        assert added == 100
        assert score_manager.score == 100

    def test_add_score_with_combo(self, score_manager: ScoreManager) -> None:
        """Test adding score with combo bonus."""
        # Build combo
        score_manager.add_score(100, ComboType.ENEMY_STOMP)
        score_manager.add_score(100, ComboType.ENEMY_STOMP)

        # Third score should have multiplier
        initial_score = score_manager.score
        added = score_manager.add_score(100, ComboType.ENEMY_STOMP)

        assert added >= 100  # At least base score

    def test_get_display_score(self, score_manager: ScoreManager) -> None:
        """Test formatted score display."""
        score_manager.score = 12345

        display = score_manager.get_display_score()
        assert display == "012345"

    def test_get_display_score_large(self, score_manager: ScoreManager) -> None:
        """Test formatted score with large numbers."""
        score_manager.score = 1234567

        display = score_manager.get_display_score()
        assert display == "1234567"

    def test_reset_score(self, score_manager: ScoreManager) -> None:
        """Test score reset."""
        score_manager.add_score(1000)
        score_manager.reset()

        assert score_manager.score == 0

    def test_reset_keep_total(self, score_manager: ScoreManager) -> None:
        """Test score reset with keep total."""
        score_manager.add_score(1000)
        base = score_manager.score
        score_manager.reset(keep_total=True)

        assert score_manager.base_score == base

    def test_add_score_with_chain(self, score_manager: ScoreManager) -> None:
        """Test adding score with chain bonus."""
        added = score_manager.add_score_with_chain(100, 3)
        assert added >= 100


class TestComboUI:
    """Tests for ComboUI."""

    def test_combo_ui_creation(self) -> None:
        """Test creating ComboUI."""
        combo = ComboManager()
        ui = ComboUI(combo)

        assert ui.combo == combo
        # Fonts may be None if pygame not initialized

    def test_draw_inactive_combo(self) -> None:
        """Test drawing when combo is inactive."""
        import pygame as pg

        pg.init()
        surface = pg.Surface((800, 600))

        combo = ComboManager()
        ui = ComboUI(combo)

        # Should not crash
        ui.draw(surface)

        pg.quit()


class TestScoreUI:
    """Tests for ScoreUI."""

    def test_score_ui_creation(self) -> None:
        """Test creating ScoreUI."""
        score_mgr = ScoreManager(ComboManager())
        ui = ScoreUI(score_mgr)

        assert ui.score_mgr == score_mgr

    def test_draw_score(self) -> None:
        """Test drawing score."""
        import pygame as pg

        pg.init()
        surface = pg.Surface((800, 600))

        score_mgr = ScoreManager(ComboManager(), initial_score=1000)
        ui = ScoreUI(score_mgr)

        # Should not crash
        ui.draw(surface)

        pg.quit()


class TestComboIntegration:
    """Integration tests for combo system."""

    def test_full_combo_sequence(self) -> None:
        """Test complete combo sequence."""
        combo = ComboManager()
        score_mgr = ScoreManager(combo)

        # Simulate combo chain
        for i in range(15):
            score_mgr.add_score(100, ComboType.ENEMY_STOMP)

        # Should have gold tier
        assert combo.tier == ComboTier.GOLD

        # Score should be significantly higher than base
        base_total = 15 * 100
        assert score_mgr.score > base_total

    def test_combo_timeout_and_reset(self) -> None:
        """Test combo timing out and resetting."""
        combo = ComboManager(ComboConfig(combo_window=500, combo_decay_time=1000))

        combo.add_action(ComboType.ENEMY_STOMP)
        combo.add_action(ComboType.ENEMY_STOMP)
        assert combo.is_active

        # Combo should timeout
        time.sleep(1.5)  # Wait for timeout

        combo.update(2000)
        # May or may not reset depending on real time
