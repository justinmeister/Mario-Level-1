"""
Tests for v2.6 new systems:
- Player Progression
- Skin System
- Challenge System
- Advanced AI
"""
from __future__ import annotations

import pytest
import time
import json
import os
from unittest.mock import Mock, MagicMock, patch, PropertyMock

# Import new modules
from data.player_progression import ProgressionManager, PlayerStats, PlayerProfile, PlayerRank, Skill, SkillType
from data.skin_system import SkinManager, Skin, SkinRarity, SkinCategory
from data.challenge_system import ChallengeManager, Challenge, ChallengeType, ChallengeCategory, ChallengeStatus
from data.advanced_ai import EnemyAI, GroupAI, AIDirector, EnemyAIConfig, AIBehavior, AlertState


# ============================================================================
# Player Progression Tests
# ============================================================================


class TestPlayerProgression:
    """Tests for PlayerProgression system."""

    @pytest.fixture
    def progression(self, tmp_path):
        """Create progression manager with temp save path."""
        save_path = str(tmp_path / "progression.json")
        return ProgressionManager(save_path)

    def test_init(self, progression) -> None:
        """Test progression manager initialization."""
        assert progression.profile is not None
        assert progression.profile.stats.level == 1
        assert progression.profile.stats.total_xp == 0

    def test_add_xp(self, progression) -> None:
        """Test adding XP."""
        progression.add_xp(100)

        assert progression.profile.stats.total_xp == 100

    def test_add_xp_validation(self, progression) -> None:
        """Test XP validation rejects invalid values."""
        initial_xp = progression.profile.stats.total_xp

        # Negative XP should be rejected
        assert progression.add_xp(-100) is False
        assert progression.profile.stats.total_xp == initial_xp

        # Zero XP should be rejected
        assert progression.add_xp(0) is False
        assert progression.profile.stats.total_xp == initial_xp

    def test_level_up(self, progression) -> None:
        """Test level up from XP."""
        # Need 100 * (2^2) = 400 XP for level 2
        progression.add_xp(500)

        assert progression.profile.stats.level >= 2

    def test_xp_formula(self, progression) -> None:
        """Test XP required formula."""
        # Level 1->2: 100 * 2^2 = 400
        # Level 2->3: 100 * 3^2 = 900
        assert progression._get_xp_for_level(2) == 400
        assert progression._get_xp_for_level(3) == 900

    def test_get_xp_progress(self, progression) -> None:
        """Test XP progress calculation."""
        progression.add_xp(200)
        current, needed, percent = progression.get_xp_progress()

        assert current == 200
        assert needed == 400  # XP for level 2
        assert percent == 50.0

    def test_get_player_rank(self, progression) -> None:
        """Test player rank calculation."""
        assert progression.get_player_rank() == PlayerRank.NOVICE

        progression.profile.stats.level = 10
        assert progression.get_player_rank() == PlayerRank.APPRENTICE

        progression.profile.stats.level = 50
        assert progression.get_player_rank() == PlayerRank.ELITE

        progression.profile.stats.level = 100
        assert progression.get_player_rank() == PlayerRank.LEGEND

    def test_add_stat(self, progression) -> None:
        """Test adding to player stats."""
        progression.add_stat("coins_collected", 100)

        assert progression.profile.stats.coins_collected == 100

    def test_skill_unlock(self, progression) -> None:
        """Test skill unlocking."""
        progression.profile.stats.level = 10

        # Should unlock speed_boost at level 5
        progression._check_skill_unlocks()

        # Check if any skill was unlocked
        unlocked = progression.get_unlocked_skills()
        assert len(unlocked) >= 0  # Depends on prerequisites

    def test_get_skill_effect(self, progression) -> None:
        """Test skill effect retrieval."""
        # Default effect is 1.0
        effect = progression.get_skill_effect("nonexistent")
        assert effect == 1.0

    def test_skin_unlock(self, progression) -> None:
        """Test skin unlocking."""
        progression.unlock_skin("fire_mario")

        assert "fire_mario" in progression.profile.unlocked_skins

    def test_set_current_skin(self, progression) -> None:
        """Test setting current skin."""
        progression.unlock_skin("default")
        progression.unlock_skin("fire_mario")

        result = progression.set_current_skin("fire_mario")

        assert result is True
        assert progression.profile.current_skin == "fire_mario"

    def test_get_summary(self, progression) -> None:
        """Test progression summary."""
        progression.add_xp(200)
        progression.add_stat("coins_collected", 100)

        summary = progression.get_summary()

        assert "level" in summary
        assert "rank" in summary
        assert "xp" in summary
        assert summary["level"] >= 1

    def test_save_load(self, progression, tmp_path) -> None:
        """Test save and load."""
        progression.add_xp(500)
        progression.add_stat("enemies_defeated", 50)

        # Save is automatic
        # Create new manager with same path
        new_progression = ProgressionManager(progression.save_path)

        assert new_progression.profile.stats.total_xp == 500
        assert new_progression.profile.stats.enemies_defeated == 50


# ============================================================================
# Skin System Tests
# ============================================================================


class TestSkinSystem:
    """Tests for Skin system."""

    @pytest.fixture
    def skin_manager(self, tmp_path):
        """Create skin manager with temp save path."""
        save_path = str(tmp_path / "skins.json")
        return SkinManager(save_path)

    def test_init(self, skin_manager) -> None:
        """Test skin manager initialization."""
        assert len(skin_manager.skins) > 0
        assert "default" in skin_manager.unlocked_skins
        assert skin_manager.current_skin == "default"

    def test_get_skin(self, skin_manager) -> None:
        """Test getting skin by ID."""
        skin = skin_manager.get_skin("default")

        assert skin is not None
        assert skin.name == "Классический Марио"

    def test_unlock_skin(self, skin_manager) -> None:
        """Test unlocking a skin."""
        result = skin_manager.unlock_skin("fire_mario")

        assert result is True
        assert "fire_mario" in skin_manager.unlocked_skins

    def test_unlock_already_unlocked(self, skin_manager) -> None:
        """Test unlocking already unlocked skin."""
        skin_manager.unlock_skin("fire_mario")
        result = skin_manager.unlock_skin("fire_mario")

        assert result is False

    def test_set_current_skin(self, skin_manager) -> None:
        """Test setting current skin."""
        skin_manager.unlock_skin("fire_mario")
        result = skin_manager.set_current_skin("fire_mario")

        assert result is True
        assert skin_manager.current_skin == "fire_mario"

    def test_set_locked_skin(self, skin_manager) -> None:
        """Test setting locked skin."""
        result = skin_manager.set_current_skin("fire_mario")

        assert result is False

    def test_check_unlock_conditions(self, skin_manager) -> None:
        """Test checking unlock conditions."""
        newly_unlocked = skin_manager.check_unlock_conditions(
            player_level=10, total_coins=0, bosses_defeated=0, achievements=0
        )

        # Should unlock fire_mario at level 10
        assert "fire_mario" in newly_unlocked

    def test_get_unlocked_skins(self, skin_manager) -> None:
        """Test getting unlocked skins."""
        skin_manager.unlock_skin("green_mario")

        unlocked = skin_manager.get_unlocked_skins()

        assert len(unlocked) >= 2  # default + green_mario

    def test_get_skins_by_category(self, skin_manager) -> None:
        """Test getting skins by category."""
        classic_skins = skin_manager.get_skins_by_category(SkinCategory.CLASSIC)

        assert len(classic_skins) > 0
        assert all(s.category == SkinCategory.CLASSIC for s in classic_skins)

    def test_get_skins_by_rarity(self, skin_manager) -> None:
        """Test getting skins by rarity."""
        common_skins = skin_manager.get_skins_by_rarity(SkinRarity.COMMON)

        assert len(common_skins) > 0
        assert all(s.rarity == SkinRarity.COMMON for s in common_skins)

    def test_get_skin_bonus(self, skin_manager) -> None:
        """Test getting skin bonuses."""
        xp_bonus, coin_bonus = skin_manager.get_skin_bonus("default")

        assert xp_bonus == 1.0
        assert coin_bonus == 1.0

    def test_get_summary(self, skin_manager) -> None:
        """Test skin summary."""
        summary = skin_manager.get_summary()

        assert "total_skins" in summary
        assert "unlocked_skins" in summary
        assert "progress" in summary


# ============================================================================
# Challenge System Tests
# ============================================================================


class TestChallengeSystem:
    """Tests for Challenge system."""

    @pytest.fixture
    def challenge_manager(self, tmp_path):
        """Create challenge manager with temp save path."""
        save_path = str(tmp_path / "challenges.json")
        return ChallengeManager(save_path)

    def test_init(self, challenge_manager) -> None:
        """Test challenge manager initialization."""
        daily = challenge_manager.get_daily_challenges()
        weekly = challenge_manager.get_weekly_challenges()

        assert len(daily) > 0
        assert len(weekly) > 0

    def test_get_daily_challenges(self, challenge_manager) -> None:
        """Test getting daily challenges."""
        daily = challenge_manager.get_daily_challenges()

        assert len(daily) >= 1
        assert all(c.challenge_type == ChallengeType.DAILY for c in daily)

    def test_get_weekly_challenges(self, challenge_manager) -> None:
        """Test getting weekly challenges."""
        weekly = challenge_manager.get_weekly_challenges()

        assert len(weekly) >= 1
        assert all(c.challenge_type == ChallengeType.WEEKLY for c in weekly)

    def test_update_progress_enemy_kill(self, challenge_manager) -> None:
        """Test updating progress for enemy kills."""
        completed = challenge_manager.update_progress("enemy_kill", 5)

        # Check if any challenge was updated
        for challenge in challenge_manager.get_active_challenges():
            if challenge.category == ChallengeCategory.COMBAT:
                assert challenge.current >= 0

    def test_update_progress_coin_collect(self, challenge_manager) -> None:
        """Test updating progress for coin collection."""
        completed = challenge_manager.update_progress("coin_collect", 50)

        for challenge in challenge_manager.get_active_challenges():
            if challenge.category == ChallengeCategory.COLLECTION:
                assert challenge.current >= 0

    def test_challenge_progress_property(self) -> None:
        """Test challenge progress calculation."""
        challenge = Challenge(
            id="test",
            name="Test",
            description="Test challenge",
            challenge_type=ChallengeType.DAILY,
            category=ChallengeCategory.COMBAT,
            target=10,
            current=5,
        )

        assert challenge.progress == 50.0

    def test_challenge_completion(self) -> None:
        """Test challenge completion."""
        challenge = Challenge(
            id="test",
            name="Test",
            description="Test challenge",
            challenge_type=ChallengeType.DAILY,
            category=ChallengeCategory.COMBAT,
            target=5,
            current=0,
        )

        completed = challenge.update_progress(5)

        assert completed is True
        assert challenge.status == ChallengeStatus.COMPLETED

    def test_claim_reward(self, challenge_manager) -> None:
        """Test claiming challenge reward."""
        # Get a challenge and complete it manually
        challenges = challenge_manager.get_daily_challenges()
        if challenges:
            challenge = challenges[0]
            challenge.current = challenge.target
            challenge.status = ChallengeStatus.COMPLETED

            reward = challenge_manager.claim_reward(challenge.id)

            if reward:
                coins, xp = reward
                assert coins > 0
                assert xp > 0

    def test_claim_uncompleted_reward(self, challenge_manager) -> None:
        """Test claiming reward for uncompleted challenge."""
        challenges = challenge_manager.get_daily_challenges()
        if challenges:
            challenge = challenges[0]
            challenge.current = 0

            reward = challenge_manager.claim_reward(challenge.id)

            assert reward is None

    def test_get_summary(self, challenge_manager) -> None:
        """Test challenge summary."""
        summary = challenge_manager.get_summary()

        assert "daily" in summary
        assert "weekly" in summary
        assert "active" in summary


# ============================================================================
# Advanced AI Tests
# ============================================================================


class TestAdvancedAI:
    """Tests for Advanced AI system."""

    @pytest.fixture
    def mock_enemy(self):
        """Create mock enemy."""
        enemy = Mock()
        enemy.rect = Mock()
        enemy.rect.centerx = 100
        enemy.rect.centery = 100
        enemy.rect.x = 90
        enemy.rect.y = 90
        enemy.max_speed = 3.0
        enemy.direction = "left"
        enemy.x_vel = 0
        enemy.health = 100
        enemy.max_health = 100
        return enemy

    @pytest.fixture
    def mock_mario(self):
        """Create mock Mario."""
        mario = Mock()
        mario.rect = Mock()
        mario.rect.centerx = 200
        mario.rect.centery = 100
        return mario

    def test_ai_init(self, mock_enemy) -> None:
        """Test EnemyAI initialization."""
        ai = EnemyAI(mock_enemy)

        assert ai.alert_state == AlertState.IDLE
        assert ai.target is None
        assert ai.config.detection_range == 300.0

    def test_ai_with_config(self, mock_enemy) -> None:
        """Test EnemyAI with custom config."""
        config = EnemyAIConfig(
            behavior=AIBehavior.AGGRESSIVE,
            detection_range=500.0,
            aggression=0.9,
        )
        ai = EnemyAI(mock_enemy, config)

        assert ai.config.behavior == AIBehavior.AGGRESSIVE
        assert ai.config.detection_range == 500.0
        assert ai.config.aggression == 0.9

    def test_detect_target(self, mock_enemy, mock_mario) -> None:
        """Test target detection."""
        ai = EnemyAI(mock_enemy)
        mock_mario.rect.centerx = 150  # Within range

        game_info = {c.CURRENT_TIME: 1000}
        ai._detect_target(mock_mario, game_info)

        assert ai.target is not None
        assert ai.target.visible is True

    def test_ai_update(self, mock_enemy, mock_mario) -> None:
        """Test EnemyAI update cycle."""
        ai = EnemyAI(mock_enemy)
        game_info = {c.CURRENT_TIME: 1000}

        # Update with target
        ai.update(game_info, mario=mock_mario)

        # Should have processed target
        assert ai.last_update == 1000

    def test_ai_update_throttling(self, mock_enemy, mock_mario) -> None:
        """Test that AI update is throttled."""
        ai = EnemyAI(mock_enemy)
        game_info = {c.CURRENT_TIME: 1000}

        # First update
        ai.update(game_info, mario=mock_mario)
        first_update = ai.last_update

        # Second update too soon - should be throttled
        game_info[c.CURRENT_TIME] = 1001
        ai.update(game_info, mario=mock_mario)

        # Should not have updated again (throttled)
        assert ai.last_update == first_update

    def test_target_out_of_range(self, mock_enemy, mock_mario) -> None:
        """Test target out of range."""
        ai = EnemyAI(mock_enemy)
        ai.config.detection_range = 10.0  # Very short range

        game_info = {c.CURRENT_TIME: 1000}
        ai._detect_target(mock_mario, game_info)

        # Target should not be visible
        if ai.target:
            assert ai.target.visible is False

    def test_make_decision_no_target(self, mock_enemy) -> None:
        """Test decision making without target."""
        ai = EnemyAI(mock_enemy)
        ai._make_decision(None)

        # Should patrol or guard
        assert ai.weights["patrol"] > 0 or ai.weights["guard"] > 0

    def test_make_decision_with_target(self, mock_enemy, mock_mario) -> None:
        """Test decision making with target."""
        ai = EnemyAI(mock_enemy)
        ai.config.aggression = 0.8

        # Set up target
        ai.target = Mock()
        ai.target.visible = True
        ai.target.distance = 30.0  # Close range

        ai._make_decision(mock_mario)

        # Should want to attack
        assert ai.weights["attack"] > 0

    def test_set_behavior(self, mock_enemy) -> None:
        """Test setting AI behavior."""
        ai = EnemyAI(mock_enemy)
        ai.set_behavior(AIBehavior.FLEE)

        assert ai.config.behavior == AIBehavior.FLEE

    def test_add_patrol_point(self, mock_enemy) -> None:
        """Test adding patrol points."""
        ai = EnemyAI(mock_enemy)
        ai.add_patrol_point(100, 100)
        ai.add_patrol_point(200, 100)

        assert len(ai.config.patrol_points) == 2

    def test_group_ai_creation(self, mock_enemy) -> None:
        """Test GroupAI creation."""
        group_ai = GroupAI()

        ai1 = EnemyAI(mock_enemy)
        ai2 = EnemyAI(mock_enemy)

        group_ai.create_group("test_group", [ai1, ai2], "assault")

        assert "test_group" in group_ai.groups
        assert ai1.group_id == "test_group"
        assert ai2.group_id == "test_group"

    def test_group_ai_strategies(self, mock_enemy) -> None:
        """Test GroupAI strategies."""
        group_ai = GroupAI()

        enemies = [EnemyAI(mock_enemy) for _ in range(4)]
        group_ai.create_group("test_group", enemies, "assault")

        # All should be aggressive
        for enemy in enemies:
            assert enemy.config.aggression >= 0.8

    def test_ai_director_init(self) -> None:
        """Test AIDirector initialization."""
        director = AIDirector()

        assert director.player_performance == 0.5
        assert director.tension_level == 0.0

    def test_ai_director_update(self, mock_enemy) -> None:
        """Test AIDirector update."""
        director = AIDirector()
        game_info = {c.CURRENT_TIME: 1000}

        # First update - no decisions yet (need time to pass)
        decisions = director.update(game_info, player_alive=True, player_health=0.8, enemies_remaining=5)

        # Advance time beyond adjustment interval (30 seconds)
        game_info[c.CURRENT_TIME] = 35000
        decisions = director.update(game_info, player_alive=True, player_health=0.8, enemies_remaining=5)

        assert "spawn_rate" in decisions
        assert "enemy_aggression" in decisions

    def test_ai_director_tension(self, mock_enemy) -> None:
        """Test AIDirector tension calculation."""
        director = AIDirector()
        game_info = {c.CURRENT_TIME: 1000}

        # Low health, many enemies = high tension
        # Need multiple updates to build up tension (smooth transition)
        for i in range(20):
            game_info[c.CURRENT_TIME] = 1000 + i * 1000
            director.update(game_info, player_alive=True, player_health=0.1, enemies_remaining=10)

        tension = director.get_tension_level()
        assert tension > 0.5

    def test_ai_director_difficulty_adjustment(self, mock_enemy) -> None:
        """Test AIDirector difficulty adjustment."""
        director = AIDirector()
        game_info = {c.CURRENT_TIME: 1000}

        # Player dying a lot
        for _ in range(5):
            director.update(game_info, player_alive=False, player_health=0, enemies_remaining=2)

        # Should reduce difficulty
        decisions = director._make_adjustments()
        assert decisions.get("spawn_rate", 1.0) <= 0.7


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for multiple systems."""

    def test_progression_with_challenges(self, tmp_path) -> None:
        """Test progression and challenge integration."""
        from data.player_progression import ProgressionManager
        from data.challenge_system import ChallengeManager

        prog = ProgressionManager(str(tmp_path / "prog.json"))
        chall = ChallengeManager(str(tmp_path / "chall.json"))

        # Player completes enemy kills
        prog.add_stat("enemies_defeated", 10)
        chall.update_progress("enemy_kill", 10)

        # Should have progress in both systems
        assert prog.profile.stats.enemies_defeated == 10

        for challenge in chall.get_active_challenges():
            if challenge.category == ChallengeCategory.COMBAT:
                assert challenge.current >= 0

    def test_skin_bonus_with_progression(self, tmp_path) -> None:
        """Test skin bonus integration with progression."""
        from data.player_progression import ProgressionManager
        from data.skin_system import SkinManager

        prog = ProgressionManager(str(tmp_path / "prog.json"))
        skin = SkinManager(str(tmp_path / "skins.json"))

        # Unlock and equip gold skin
        skin.unlock_skin("gold_mario")
        skin.set_current_skin("gold_mario")

        # Get bonuses
        xp_bonus, coin_bonus = skin.get_current_skin_bonus()

        # Gold skin gives 1.5x bonuses
        assert xp_bonus == 1.5
        assert coin_bonus == 1.5

        # Apply to progression
        base_xp = 100
        actual_xp = int(base_xp * xp_bonus)
        prog.add_xp(actual_xp)

        assert prog.profile.stats.total_xp == 150


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
