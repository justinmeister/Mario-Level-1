"""
Tests for Effect System.

Tests cover:
- Effect creation and application
- Effect stacking
- Duration and expiration
- Modifiers
- Effect manager functionality
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from data.effect_system import (
    ActiveEffect,
    EffectCategory,
    EffectConfig,
    EffectManager,
    EffectStackType,
    EffectType,
    EFFECT_PRESETS,
    create_effect,
    get_effect_config,
    register_effect,
)


class MockEntity:
    """Mock entity for testing effects."""

    def __init__(self) -> None:
        self.health = 100
        self.speed = 5.0
        self.damage = 10
        self.effects_applied = []
        self.effects_removed = []
        self.effects_expired = []


class TestEffectConfig:
    """Test EffectConfig."""

    def test_create_buff_config(self) -> None:
        """Test creating buff configuration."""
        config = EffectConfig(
            name="Speed Boost",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
            icon_color=(0, 255, 0),
            description="Increases speed",
        )

        assert config.name == "Speed Boost"
        assert config.effect_type == EffectType.BUFF
        assert config.category == EffectCategory.MOVEMENT
        assert config.duration == 10000
        assert config.stack_type == EffectStackType.NONE
        assert config.max_stacks == 1

    def test_create_debuff_config(self) -> None:
        """Test creating debuff configuration."""
        config = EffectConfig(
            name="Slow",
            effect_type=EffectType.DEBUFF,
            category=EffectCategory.MOVEMENT,
            duration=5000,
            icon_color=(255, 0, 0),
        )

        assert config.effect_type == EffectType.DEBUFF
        assert config.duration == 5000


class TestActiveEffect:
    """Test ActiveEffect."""

    def test_create_permanent_effect(self) -> None:
        """Test creating permanent effect."""
        config = EffectConfig(
            name="Permanent Power",
            effect_type=EffectType.POWERUP,
            category=EffectCategory.SPECIAL,
            duration=0,
        )

        effect = ActiveEffect(config=config, magnitude=1.5)

        assert effect.magnitude == 1.5
        assert effect.stacks == 1
        assert effect.expires_at is None
        assert not effect.is_expired
        assert effect.remaining_time == float("inf")
        assert effect.progress == 100.0

    def test_create_timed_effect(self) -> None:
        """Test creating timed effect."""
        config = EffectConfig(
            name="Temporary Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.COMBAT,
            duration=5000,
        )

        effect = ActiveEffect(
            config=config,
            magnitude=2.0,
            modifiers={"damage": 0.5},
        )

        assert effect.expires_at is not None
        assert effect.remaining_time <= 5000
        assert effect.modifiers["damage"] == 0.5

    def test_effect_expiration(self) -> None:
        """Test effect expiration."""
        config = EffectConfig(
            name="Short Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=100,  # 100ms
        )

        effect = ActiveEffect(config=config)
        assert not effect.is_expired

        # Wait for expiration
        time.sleep(0.15)
        assert effect.is_expired
        assert effect.remaining_time == 0

    @pytest.mark.flaky(reruns=2)
    def test_add_stack(self) -> None:
        """Test adding stacks to effect."""
        config = EffectConfig(
            name="Stacking Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.COMBAT,
            duration=10000,
            stack_type=EffectStackType.STACK,
            max_stacks=5,
        )

        effect = ActiveEffect(config=config, magnitude=1.0)

        assert effect.stacks == 1
        assert effect.magnitude == 1.0

        effect.add_stack()
        assert effect.stacks == 2
        assert effect.magnitude == 2.0

        # Stack to max
        for _ in range(4):
            effect.add_stack()

        assert effect.stacks == 5
        assert effect.magnitude == 5.0

        # Can't exceed max
        effect.add_stack()
        assert effect.stacks == 5

    @pytest.mark.flaky(reruns=2)
    def test_extend_duration(self) -> None:
        """Test extending effect duration."""
        config = EffectConfig(
            name="Extendable Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.UTILITY,
            duration=1000,
        )

        effect = ActiveEffect(config=config)
        initial_expires = effect.expires_at

        time.sleep(0.05)
        effect.extend(500)

        assert effect.expires_at is not None
        assert initial_expires is not None
        assert effect.expires_at > initial_expires

    def test_tick_with_callbacks(self) -> None:
        """Test effect tick with callbacks."""
        entity = MockEntity()
        config = EffectConfig(
            name="Tick Test",
            effect_type=EffectType.BUFF,
            category=EffectCategory.SPECIAL,
            duration=10000,
        )

        tick_called = False
        expire_called = False

        def on_tick(target: Any) -> None:
            nonlocal tick_called
            tick_called = True
            target.effects_applied.append("tick")

        def on_expire(target: Any) -> None:
            nonlocal expire_called
            expire_called = True
            target.effects_removed.append("expire")

        effect = ActiveEffect(
            config=config,
            on_tick=on_tick,
            on_expire=on_expire,
        )

        # Tick should call on_tick
        result = effect.tick(entity, 16)
        assert not result  # Not expired
        assert tick_called
        assert "tick" in entity.effects_applied

        # Expire should call on_expire
        effect.expires_at = time.time() - 1
        result = effect.tick(entity, 16)
        assert result  # Expired
        assert expire_called


class TestEffectManager:
    """Test EffectManager."""

    def test_apply_effect(self) -> None:
        """Test applying effect."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Test Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
        )

        effect = manager.apply_effect(config, magnitude=1.5)

        assert effect is not None
        assert manager.has_effect("test buff")
        assert len(manager.get_effects()) == 1

    def test_apply_effect_with_modifiers(self) -> None:
        """Test applying effect with modifiers."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Damage Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.COMBAT,
            duration=10000,
        )

        manager.apply_effect(config, modifiers={"damage": 0.5})

        modifier = manager.get_modifier("damage")
        assert modifier == 1.5  # Base 1.0 + 0.5

    def test_remove_effect(self) -> None:
        """Test removing effect."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Temporary",
            effect_type=EffectType.BUFF,
            category=EffectCategory.UTILITY,
            duration=10000,
        )

        manager.apply_effect(config)
        assert manager.has_effect("temporary")

        manager.remove_effect("temporary")
        assert not manager.has_effect("temporary")

    def test_remove_effects_by_type(self) -> None:
        """Test removing effects by type."""
        entity = MockEntity()
        manager = EffectManager(entity)

        buff_config = EffectConfig(
            name="Buff 1",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
        )

        debuff_config = EffectConfig(
            name="Debuff 1",
            effect_type=EffectType.DEBUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
        )

        manager.apply_effect(buff_config)
        manager.apply_effect(debuff_config)

        removed = manager.remove_effects_by_type(EffectType.BUFF)

        assert removed == 1
        assert not manager.has_effect("buff 1")
        assert manager.has_effect("debuff 1")

    def test_clear_all_effects(self) -> None:
        """Test clearing all effects."""
        entity = MockEntity()
        manager = EffectManager(entity)

        for i in range(5):
            config = EffectConfig(
                name=f"Effect {i}",
                effect_type=EffectType.BUFF,
                category=EffectCategory.UTILITY,
                duration=10000,
            )
            manager.apply_effect(config)

        assert len(manager.get_effects()) == 5

        manager.clear_all()

        assert len(manager.get_effects()) == 0

    def test_update_expires_effects(self) -> None:
        """Test updating effects expires them."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Short Effect",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=50,  # 50ms
        )

        manager.apply_effect(config)
        assert len(manager.get_effects()) == 1

        time.sleep(0.1)
        expired = manager.update(16)

        assert len(expired) == 1
        assert len(manager.get_effects()) == 0

    def test_effect_stacking_none(self) -> None:
        """Test effect stacking with NONE type."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Non-stacking",
            effect_type=EffectType.BUFF,
            category=EffectCategory.COMBAT,
            duration=10000,
            stack_type=EffectStackType.NONE,
        )

        manager.apply_effect(config, magnitude=1.5)
        manager.apply_effect(config, magnitude=2.0)

        effects = manager.get_effects()
        assert len(effects) == 1
        assert effects[0].magnitude == 2.0  # Refreshed

    def test_effect_stacking_stack(self) -> None:
        """Test effect stacking with STACK type."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Stacking Effect",
            effect_type=EffectType.BUFF,
            category=EffectCategory.COMBAT,
            duration=10000,
            stack_type=EffectStackType.STACK,
            max_stacks=3,
        )

        manager.apply_effect(config)
        manager.apply_effect(config)
        manager.apply_effect(config)

        effects = manager.get_effects()
        assert len(effects) == 1
        assert effects[0].stacks == 3
        assert effects[0].magnitude == 3.0

    def test_effect_stacking_extend(self) -> None:
        """Test effect stacking with EXTEND type."""
        entity = MockEntity()
        manager = EffectManager(entity)

        config = EffectConfig(
            name="Extendable",
            effect_type=EffectType.BUFF,
            category=EffectCategory.UTILITY,
            duration=1000,
            stack_type=EffectStackType.EXTEND,
        )

        effect = manager.apply_effect(config)
        initial_expires = effect.expires_at

        time.sleep(0.1)
        manager.apply_effect(config)

        # Duration should be extended
        assert effect.expires_at > initial_expires

    def test_callbacks(self) -> None:
        """Test effect manager callbacks."""
        entity = MockEntity()
        manager = EffectManager(entity)

        applied = []
        removed = []
        expired = []

        manager.on_effect_applied = lambda e: applied.append(e.config.name)
        manager.on_effect_removed = lambda e: removed.append(e.config.name)
        manager.on_effect_expired = lambda e: expired.append(e.config.name)

        config = EffectConfig(
            name="Callback Test",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=50,
        )

        manager.apply_effect(config)
        assert "Callback Test" in applied

        manager.remove_effect("callback test")
        assert "Callback Test" in removed

        # Test expired callback
        manager.apply_effect(config)
        time.sleep(0.1)
        manager.update(16)
        assert "Callback Test" in expired

    def test_get_effects_by_type(self) -> None:
        """Test getting effects by type."""
        entity = MockEntity()
        manager = EffectManager(entity)

        buff_config = EffectConfig(
            name="Buff",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
        )

        debuff_config = EffectConfig(
            name="Debuff",
            effect_type=EffectType.DEBUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
        )

        manager.apply_effect(buff_config)
        manager.apply_effect(debuff_config)

        buffs = manager.get_buffs()
        debuffs = manager.get_debuffs()

        assert len(buffs) == 1
        assert buffs[0].config.name == "Buff"
        assert len(debuffs) == 1
        assert debuffs[0].config.name == "Debuff"


class TestEffectPresets:
    """Test predefined effect presets."""

    def test_preset_effects_exist(self) -> None:
        """Test that preset effects are defined."""
        assert "speed_boost" in EFFECT_PRESETS
        assert "slow" in EFFECT_PRESETS
        assert "invincibility" in EFFECT_PRESETS
        assert "poison" in EFFECT_PRESETS
        assert "mushroom_power" in EFFECT_PRESETS
        assert "fire_power" in EFFECT_PRESETS
        assert "ice_power" in EFFECT_PRESETS

    def test_create_effect_from_preset(self) -> None:
        """Test creating effect from preset."""
        effect = create_effect("speed_boost", magnitude=1.5)

        assert effect is not None
        assert effect.config.name == "Speed Boost"
        assert effect.magnitude == 1.5

    def test_create_invalid_preset(self) -> None:
        """Test creating effect from invalid preset."""
        effect = create_effect("nonexistent_effect")
        assert effect is None

    def test_get_effect_config(self) -> None:
        """Test getting effect config."""
        config = get_effect_config("speed_boost")
        assert config is not None
        assert config.name == "Speed Boost"

        config = get_effect_config("invalid_effect")
        assert config is None


class TestEffectRegistry:
    """Test effect registry."""

    def test_register_custom_effect(self) -> None:
        """Test registering custom effect."""
        config = EffectConfig(
            name="Custom Test Effect",
            effect_type=EffectType.SPECIAL,
            category=EffectCategory.SPECIAL,
            duration=10000,
        )

        register_effect(config)

        retrieved = get_effect_config("custom test effect")
        assert retrieved is not None
        assert retrieved.name == "Custom Test Effect"


class TestEffectCategory:
    """Test effect categories."""

    def test_get_effects_by_category(self) -> None:
        """Test getting effects by category."""
        entity = MockEntity()
        manager = EffectManager(entity)

        movement_config = EffectConfig(
            name="Speed",
            effect_type=EffectType.BUFF,
            category=EffectCategory.MOVEMENT,
            duration=10000,
        )

        combat_config = EffectConfig(
            name="Damage",
            effect_type=EffectType.BUFF,
            category=EffectCategory.COMBAT,
            duration=10000,
        )

        manager.apply_effect(movement_config)
        manager.apply_effect(combat_config)

        movement_effects = manager.get_effects_by_category(EffectCategory.MOVEMENT)
        combat_effects = manager.get_effects_by_category(EffectCategory.COMBAT)

        assert len(movement_effects) == 1
        assert len(combat_effects) == 1
