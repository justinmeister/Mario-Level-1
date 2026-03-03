"""
Effect System for Super Mario Bros.

Features:
- Buffs and debuffs
- Timed effects
- Effect stacking
- Visual indicators
- Effect categories
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame as pg

from . import constants as c


class EffectType(Enum):
    """Type of effect."""

    BUFF = auto()
    DEBUFF = auto()
    POWERUP = auto()
    STATUS = auto()
    SPECIAL = auto()


class EffectCategory(Enum):
    """Effect category for grouping."""

    MOVEMENT = auto()
    COMBAT = auto()
    DEFENSE = auto()
    UTILITY = auto()
    SPECIAL = auto()


class EffectStackType(Enum):
    """How effects stack."""

    NONE = auto()  # No stacking, refresh duration
    STACK = auto()  # Stack magnitude
    EXTEND = auto()  # Extend duration


@dataclass
class EffectConfig:
    """Configuration for an effect."""

    name: str
    effect_type: EffectType
    category: EffectCategory
    duration: float  # milliseconds, 0 = permanent
    stack_type: EffectStackType = EffectStackType.NONE
    max_stacks: int = 1
    icon_color: Tuple[int, int, int] = (255, 255, 255)
    description: str = ""


@dataclass
class ActiveEffect:
    """An active effect instance."""

    config: EffectConfig
    magnitude: float = 1.0
    stacks: int = 1
    applied_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    modifiers: Dict[str, float] = field(default_factory=dict)
    on_tick: Optional[Callable[[Any], None]] = None
    on_expire: Optional[Callable[[Any], None]] = None

    def __post_init__(self) -> None:
        """Initialize expires_at if duration is set."""
        if self.expires_at is None and self.config.duration > 0:
            self.expires_at = self.applied_at + (self.config.duration / 1000)

    @property
    def remaining_time(self) -> float:
        """Get remaining time in milliseconds."""
        if self.expires_at is None:
            return float("inf")
        return max(0, (self.expires_at - time.time()) * 1000)

    @property
    def is_expired(self) -> bool:
        """Check if effect is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def progress(self) -> float:
        """Get effect progress (0-100)."""
        if self.expires_at is None:
            return 100.0
        total = self.expires_at - self.applied_at
        if total <= 0:
            return 100.0
        elapsed = time.time() - self.applied_at
        return max(0, min(100, (elapsed / total) * 100))

    def tick(self, target: Any, delta_ms: float) -> bool:
        """
        Tick the effect.

        Args:
            target: Effect target (e.g., Mario)
            delta_ms: Delta time in milliseconds

        Returns:
            True if effect should be removed
        """
        if self.is_expired:
            if self.on_expire:
                self.on_expire(target)
            return True

        if self.on_tick:
            self.on_tick(target)

        return False

    def add_stack(self) -> int:
        """
        Add a stack.

        Returns:
            New stack count
        """
        if self.config.stack_type != EffectStackType.STACK:
            return self.stacks

        self.stacks = min(self.stacks + 1, self.config.max_stacks)
        self.magnitude = self.stacks
        return self.stacks

    def extend(self, duration_ms: float) -> None:
        """Extend effect duration."""
        if self.expires_at:
            self.expires_at += duration_ms / 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.config.name,
            "type": self.config.effect_type.name,
            "category": self.config.category.name,
            "duration": self.config.duration,
            "magnitude": self.magnitude,
            "stacks": self.stacks,
            "remaining": self.remaining_time,
            "progress": self.progress,
        }


class EffectManager:
    """
    Manages effects on entities.

    Features:
    - Apply/remove effects
    - Effect stacking
    - Duration tracking
    - Modifier application
    - Visual indicators
    """

    def __init__(self, target: Any) -> None:
        """
        Initialize effect manager.

        Args:
            target: Entity that receives effects
        """
        self.target = target
        self.effects: Dict[str, ActiveEffect] = {}
        self.modifiers: Dict[str, float] = {}

        # Callbacks
        self.on_effect_applied: Optional[Callable[[ActiveEffect], None]] = None
        self.on_effect_removed: Optional[Callable[[ActiveEffect], None]] = None
        self.on_effect_expired: Optional[Callable[[ActiveEffect], None]] = None

    def apply_effect(
        self,
        config: EffectConfig,
        magnitude: float = 1.0,
        modifiers: Optional[Dict[str, float]] = None,
        on_tick: Optional[Callable[[Any], None]] = None,
        on_expire: Optional[Callable[[Any], None]] = None,
    ) -> ActiveEffect:
        """
        Apply an effect to the target.

        Args:
            config: Effect configuration
            magnitude: Effect magnitude
            modifiers: Stat modifiers
            on_tick: Callback per tick
            on_expire: Callback on expiration

        Returns:
            Applied effect
        """
        effect_id = config.name.lower()

        # Check if effect already exists
        if effect_id in self.effects:
            existing = self.effects[effect_id]
            return self._handle_existing_effect(existing, config, magnitude)

        # Create new effect
        expires_at = None
        if config.duration > 0:
            expires_at = time.time() + (config.duration / 1000)

        effect = ActiveEffect(
            config=config,
            magnitude=magnitude,
            applied_at=time.time(),
            expires_at=expires_at,
            modifiers=modifiers or {},
            on_tick=on_tick,
            on_expire=on_expire,
        )

        self.effects[effect_id] = effect
        self._recalculate_modifiers()

        if self.on_effect_applied:
            self.on_effect_applied(effect)

        return effect

    def _handle_existing_effect(self, existing: ActiveEffect, config: EffectConfig, magnitude: float) -> ActiveEffect:
        """Handle applying effect that already exists."""
        if config.stack_type == EffectStackType.NONE:
            # Refresh duration
            if config.duration > 0:
                existing.expires_at = time.time() + (config.duration / 1000)
            existing.magnitude = magnitude

        elif config.stack_type == EffectStackType.STACK:
            existing.add_stack()
            if config.duration > 0:
                existing.expires_at = time.time() + (config.duration / 1000)

        elif config.stack_type == EffectStackType.EXTEND:
            existing.extend(config.duration)

        self._recalculate_modifiers()
        return existing

    def remove_effect(self, effect_id: str) -> bool:
        """
        Remove an effect by ID.

        Args:
            effect_id: Effect identifier

        Returns:
            True if effect was removed
        """
        if effect_id not in self.effects:
            return False

        effect = self.effects.pop(effect_id)
        self._recalculate_modifiers()

        if self.on_effect_removed:
            self.on_effect_removed(effect)

        return True

    def remove_effects_by_type(self, effect_type: EffectType) -> int:
        """
        Remove all effects of a type.

        Args:
            effect_type: Type to remove

        Returns:
            Number of effects removed
        """
        to_remove = [eid for eid, eff in self.effects.items() if eff.config.effect_type == effect_type]

        for effect_id in to_remove:
            self.remove_effect(effect_id)

        return len(to_remove)

    def remove_effects_by_category(self, category: EffectCategory) -> int:
        """
        Remove all effects of a category.

        Args:
            category: Category to remove

        Returns:
            Number of effects removed
        """
        to_remove = [eid for eid, eff in self.effects.items() if eff.config.category == category]

        for effect_id in to_remove:
            self.remove_effect(effect_id)

        return len(to_remove)

    def clear_all(self) -> None:
        """Clear all effects."""
        for effect in list(self.effects.values()):
            if self.on_effect_removed:
                self.on_effect_removed(effect)

        self.effects.clear()
        self.modifiers.clear()

    def update(self, delta_ms: float = 16) -> List[ActiveEffect]:
        """
        Update all effects.

        Args:
            delta_ms: Delta time in milliseconds

        Returns:
            List of expired effects
        """
        expired = []

        for effect_id, effect in list(self.effects.items()):
            if effect.tick(self.target, delta_ms):
                expired.append(effect)
                del self.effects[effect_id]

                if self.on_effect_expired:
                    self.on_effect_expired(effect)

        if expired:
            self._recalculate_modifiers()

        return expired

    def _recalculate_modifiers(self) -> None:
        """Recalculate all stat modifiers."""
        self.modifiers.clear()

        for effect in self.effects.values():
            for stat, value in effect.modifiers.items():
                if stat not in self.modifiers:
                    self.modifiers[stat] = 0.0
                self.modifiers[stat] += value * effect.magnitude

    def get_modifier(self, stat_name: str) -> float:
        """
        Get total modifier for a stat.

        Args:
            stat_name: Stat name

        Returns:
            Modifier value (1.0 = no change)
        """
        return 1.0 + self.modifiers.get(stat_name, 0.0)

    def get_effects(self) -> List[ActiveEffect]:
        """Get all active effects."""
        return list(self.effects.values())

    def get_effects_by_type(self, effect_type: EffectType) -> List[ActiveEffect]:
        """Get effects by type."""
        return [e for e in self.effects.values() if e.config.effect_type == effect_type]

    def get_effects_by_category(self, category: EffectCategory) -> List[ActiveEffect]:
        """Get effects by category."""
        return [e for e in self.effects.values() if e.config.category == category]

    def get_buffs(self) -> List[ActiveEffect]:
        """Get all buffs."""
        return self.get_effects_by_type(EffectType.BUFF)

    def get_debuffs(self) -> List[ActiveEffect]:
        """Get all debuffs."""
        return self.get_effects_by_type(EffectType.DEBUFF)

    def has_effect(self, effect_id: str) -> bool:
        """Check if effect is active."""
        return effect_id.lower() in self.effects

    def get_effect(self, effect_id: str) -> Optional[ActiveEffect]:
        """Get effect by ID."""
        return self.effects.get(effect_id.lower())

    def draw(self, surface: pg.Surface, position: Tuple[int, int] = (10, 550)) -> None:
        """
        Draw effect indicators.

        Args:
            surface: Surface to draw on
            position: Top-left position
        """
        x, y = position
        icon_size = 32
        spacing = 5

        effects = self.get_effects()[:6]  # Show max 6 effects

        for i, effect in enumerate(effects):
            # Draw icon background
            icon_rect = pg.Rect(x + i * (icon_size + spacing), y, icon_size, icon_size)
            pg.draw.rect(surface, (40, 40, 40), icon_rect)
            pg.draw.rect(surface, effect.config.icon_color, icon_rect, 2)

            # Draw progress bar
            if effect.config.duration > 0:
                bar_height = 4
                progress = effect.progress / 100
                bar_rect = pg.Rect(x + i * (icon_size + spacing), y + icon_size - bar_height, icon_size, bar_height)
                pg.draw.rect(surface, (100, 100, 100), bar_rect)

                if effect.config.effect_type == EffectType.BUFF:
                    color = c.GREEN
                elif effect.config.effect_type == EffectType.DEBUFF:
                    color = c.RED
                else:
                    color = c.GOLD

                pg.draw.rect(surface, color, (bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_height))

            # Draw stack count
            if effect.stacks > 1:
                font = pg.font.Font(None, 20)
                stack_text = f"x{effect.stacks}"
                stack_surf = font.render(stack_text, True, c.WHITE)
                surface.blit(stack_surf, (x + i * (icon_size + spacing) + 20, y + 20))


# Pre-defined effects
EFFECT_PRESETS: Dict[str, EffectConfig] = {
    "speed_boost": EffectConfig(
        name="Speed Boost",
        effect_type=EffectType.BUFF,
        category=EffectCategory.MOVEMENT,
        duration=10000,  # 10 seconds
        icon_color=(0, 255, 0),
        description="Увеличивает скорость на 25%",
    ),
    "slow": EffectConfig(
        name="Slow",
        effect_type=EffectType.DEBUFF,
        category=EffectCategory.MOVEMENT,
        duration=5000,
        icon_color=(255, 0, 0),
        description="Уменьшает скорость на 30%",
    ),
    "invincibility": EffectConfig(
        name="Invincibility",
        effect_type=EffectType.POWERUP,
        category=EffectCategory.DEFENSE,
        duration=8000,
        icon_color=(255, 255, 0),
        description="Полная неуязвимость",
    ),
    "poison": EffectConfig(
        name="Poison",
        effect_type=EffectType.DEBUFF,
        category=EffectCategory.COMBAT,
        duration=3000,
        stack_type=EffectStackType.STACK,
        max_stacks=5,
        icon_color=(128, 0, 128),
        description="Постепенная потеря здоровья",
    ),
    "mushroom_power": EffectConfig(
        name="Mushroom Power",
        effect_type=EffectType.POWERUP,
        category=EffectCategory.SPECIAL,
        duration=0,  # Permanent until hit
        icon_color=(255, 128, 0),
        description="Увеличенный размер и сила",
    ),
    "fire_power": EffectConfig(
        name="Fire Power",
        effect_type=EffectType.POWERUP,
        category=EffectCategory.COMBAT,
        duration=0,
        icon_color=(255, 64, 0),
        description="Способность метать огненные шары",
    ),
    "ice_power": EffectConfig(
        name="Ice Power",
        effect_type=EffectType.POWERUP,
        category=EffectCategory.COMBAT,
        duration=0,
        icon_color=(0, 128, 255),
        description="Способность замораживать врагов",
    ),
}


def create_effect(effect_name: str, magnitude: float = 1.0) -> Optional[ActiveEffect]:
    """
    Create an effect from preset.

    Args:
        effect_name: Name of preset effect
        magnitude: Effect magnitude

    Returns:
        Created effect or None
    """
    if effect_name not in EFFECT_PRESETS:
        return None

    config = EFFECT_PRESETS[effect_name]
    expires_at = None
    if config.duration > 0:
        expires_at = time.time() + (config.duration / 1000)

    return ActiveEffect(
        config=config,
        magnitude=magnitude,
        applied_at=time.time(),
        expires_at=expires_at,
    )


# Global effect registry
_effect_registry: Dict[str, EffectConfig] = {}


def register_effect(config: EffectConfig) -> None:
    """Register a custom effect."""
    _effect_registry[config.name.lower()] = config


def get_effect_config(effect_name: str) -> Optional[EffectConfig]:
    """Get effect config by name."""
    return EFFECT_PRESETS.get(effect_name) or _effect_registry.get(effect_name.lower())
