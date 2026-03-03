"""
Melee Combat System for Super Mario Bros.

Features:
- Combo attacks
- Hit detection
- Attack animations
- Damage calculation
- Knockback effects
- Parrying/blocking
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pygame as pg


class AttackType(Enum):
    """Attack types."""

    LIGHT = auto()
    HEAVY = auto()
    SPECIAL = auto()
    AERIAL = auto()
    CHARGED = auto()


class AttackState(Enum):
    """Attack states."""

    IDLE = auto()
    WINDUP = auto()
    ACTIVE = auto()
    RECOVERY = auto()
    CANCELLED = auto()


@dataclass
class AttackConfig:
    """Attack configuration."""

    attack_type: AttackType
    damage: int = 10
    knockback: float = 5.0
    hit_stun: float = 0.5  # seconds
    windup_time: float = 0.1
    active_time: float = 0.2
    recovery_time: float = 0.3
    hit_box_width: float = 30.0
    hit_box_height: float = 30.0
    hit_box_offset: Tuple[float, float] = (0, 0)
    can_cancel: bool = True
    cancels_into: List[AttackType] = field(default_factory=list)
    sound_effect: Optional[str] = None


@dataclass
class ComboConfig:
    """Combo configuration."""

    name: str
    attacks: List[AttackType]
    damage_multiplier: float = 1.0
    speed_multiplier: float = 1.0
    special_effect: Optional[str] = None


@dataclass
class HitBox:
    """Hit box for attack."""

    x: float
    y: float
    width: float
    height: float
    damage: int
    knockback: float
    hit_stun: float
    owner_id: str
    attack_type: AttackType
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    hit_entities: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Set expiration."""
        self.expires_at = self.created_at + self.hit_stun

    @property
    def rect(self) -> pg.Rect:
        """Get pygame rect."""
        return pg.Rect(self.x, self.y, self.width, self.height)

    @property
    def is_active(self) -> bool:
        """Check if hitbox is active."""
        return time.time() < self.expires_at

    def contains(self, x: float, y: float) -> bool:
        """Check if point is inside hitbox."""
        return self.rect.collidepoint(x, y)

    def intersects(self, other: "HitBox") -> bool:
        """Check if hitboxes intersect."""
        return self.rect.colliderect(other.rect)


@dataclass
class CombatStats:
    """Combat statistics."""

    total_damage_dealt: int = 0
    total_hits: int = 0
    combos_started: int = 0
    combos_completed: int = 0
    max_combo: int = 0
    enemies_defeated: int = 0
    damage_taken: int = 0
    attacks_blocked: int = 0
    perfect_pars: int = 0


class MeleeCombat:
    """
    Melee combat system.

    Features:
    - Combo system
    - Hit detection
    - Attack chaining
    - Damage calculation
    """

    # Default attack configs
    DEFAULT_ATTACKS: Dict[AttackType, AttackConfig] = {
        AttackType.LIGHT: AttackConfig(
            attack_type=AttackType.LIGHT,
            damage=10,
            knockback=3.0,
            hit_stun=0.3,
            windup_time=0.05,
            active_time=0.1,
            recovery_time=0.15,
            hit_box_width=25,
            hit_box_height=25,
            can_cancel=True,
            cancels_into=[AttackType.LIGHT, AttackType.HEAVY],
        ),
        AttackType.HEAVY: AttackConfig(
            attack_type=AttackType.HEAVY,
            damage=25,
            knockback=8.0,
            hit_stun=0.6,
            windup_time=0.2,
            active_time=0.3,
            recovery_time=0.4,
            hit_box_width=40,
            hit_box_height=40,
            can_cancel=False,
        ),
        AttackType.AERIAL: AttackConfig(
            attack_type=AttackType.AERIAL,
            damage=15,
            knockback=5.0,
            hit_stun=0.4,
            windup_time=0.1,
            active_time=0.2,
            recovery_time=0.2,
            hit_box_width=35,
            hit_box_height=35,
            can_cancel=True,
            cancels_into=[AttackType.LIGHT],
        ),
        AttackType.CHARGED: AttackConfig(
            attack_type=AttackType.CHARGED,
            damage=40,
            knockback=12.0,
            hit_stun=1.0,
            windup_time=0.5,
            active_time=0.4,
            recovery_time=0.5,
            hit_box_width=50,
            hit_box_height=50,
            can_cancel=False,
        ),
    }

    # Combo definitions
    COMBOS: Dict[str, ComboConfig] = {
        "basic": ComboConfig(
            name="Basic Combo",
            attacks=[AttackType.LIGHT, AttackType.LIGHT, AttackType.HEAVY],
            damage_multiplier=1.2,
        ),
        "quick": ComboConfig(
            name="Quick Combo",
            attacks=[AttackType.LIGHT, AttackType.LIGHT, AttackType.LIGHT, AttackType.LIGHT],
            speed_multiplier=1.3,
        ),
        "power": ComboConfig(
            name="Power Combo",
            attacks=[AttackType.HEAVY, AttackType.CHARGED],
            damage_multiplier=1.5,
        ),
        "aerial": ComboConfig(
            name="Aerial Combo",
            attacks=[AttackType.AERIAL, AttackType.AERIAL, AttackType.HEAVY],
            damage_multiplier=1.3,
        ),
    }

    def __init__(self, owner_id: str) -> None:
        """
        Initialize combat system.

        Args:
            owner_id: Owner entity ID
        """
        self.owner_id = owner_id

        # State
        self.current_attack: Optional[AttackConfig] = None
        self.attack_state = AttackState.IDLE
        self.combo_chain: List[AttackType] = []
        self.combo_index: int = 0
        self.active_combo: Optional[ComboConfig] = None

        # Timing
        self.attack_timer: float = 0
        self.combo_timer: float = 0
        self.combo_window: float = 1.0  # seconds to continue combo

        # Hitboxes
        self.active_hitboxes: List[HitBox] = []
        self.hit_history: List[Dict[str, Any]] = []

        # Stats
        self.stats = CombatStats()

        # Attack configs
        self.attacks = self.DEFAULT_ATTACKS.copy()

        # Callbacks
        self.on_attack_start: Optional[Callable[[AttackConfig], None]] = None
        self.on_hit: Optional[Callable[[HitBox, Any], None]] = None
        self.on_combo_complete: Optional[Callable[[ComboConfig], None]] = None

    def start_attack(self, attack_type: AttackType, position: Tuple[float, float], facing_right: bool = True) -> bool:
        """
        Start an attack.

        Args:
            attack_type: Type of attack
            position: Attacker position
            facing_right: Facing direction

        Returns:
            True if attack started
        """
        if attack_type not in self.attacks:
            return False

        config = self.attacks[attack_type]

        # Check if can cancel current attack
        if self.current_attack and self.attack_state != AttackState.IDLE:
            if not self.current_attack.can_cancel:
                return False
            if attack_type not in self.current_attack.cancels_into:
                return False

        # Check combo continuation
        if self.active_combo:
            if self.combo_index < len(self.active_combo.attacks):
                expected = self.active_combo.attacks[self.combo_index]
                if attack_type != expected:
                    # Reset combo
                    self._reset_combo()

        # Start new attack
        self.current_attack = config
        self.attack_state = AttackState.WINDUP
        self.attack_timer = time.time()

        # Update combo
        self._update_combo(attack_type)

        # Create hitbox
        offset_x = config.hit_box_offset[0] if facing_right else -config.hit_box_offset[0]
        hitbox_x = position[0] + offset_x
        hitbox_y = position[1] + config.hit_box_offset[1]

        hitbox = HitBox(
            x=hitbox_x,
            y=hitbox_y,
            width=config.hit_box_width,
            height=config.hit_box_height,
            damage=config.damage,
            knockback=config.knockback,
            hit_stun=config.hit_stun,
            owner_id=self.owner_id,
            attack_type=attack_type,
            expires_at=self.attack_timer + config.active_time,
        )

        self.active_hitboxes.append(hitbox)

        if self.on_attack_start:
            self.on_attack_start(config)

        return True

    def _update_combo(self, attack_type: AttackType) -> None:
        """Update combo chain."""
        if not self.active_combo:
            # Try to start new combo
            for combo in self.COMBOS.values():
                if combo.attacks[0] == attack_type:
                    self.active_combo = combo
                    self.combo_index = 1
                    self.combo_timer = time.time()
                    self.stats.combos_started += 1
                    return
        else:
            # Continue combo
            if self.combo_index < len(self.active_combo.attacks):
                if attack_type == self.active_combo.attacks[self.combo_index]:
                    self.combo_index += 1
                    self.combo_timer = time.time()

                    # Check if combo complete
                    if self.combo_index >= len(self.active_combo.attacks):
                        if self.on_combo_complete:
                            self.on_combo_complete(self.active_combo)
                        self.stats.combos_completed += 1
                        self._reset_combo()
                    return

            # Wrong attack - reset
            self._reset_combo()

    def _reset_combo(self) -> None:
        """Reset combo chain."""
        self.combo_chain.clear()
        self.combo_index = 0
        self.active_combo = None

    def update(self, dt: float) -> List[Dict[str, Any]]:
        """
        Update combat system.

        Args:
            dt: Delta time

        Returns:
            List of hit events
        """
        current_time = time.time()
        hits: List[Dict[str, Any]] = []

        # Update attack state
        if self.current_attack:
            elapsed = current_time - self.attack_timer

            if self.attack_state == AttackState.WINDUP:
                if elapsed >= self.current_attack.windup_time:
                    self.attack_state = AttackState.ACTIVE

            elif self.attack_state == AttackState.ACTIVE:
                if elapsed >= self.current_attack.active_time:
                    self.attack_state = AttackState.RECOVERY

            elif self.attack_state == AttackState.RECOVERY:
                if elapsed >= self.current_attack.recovery_time:
                    self.attack_state = AttackState.IDLE
                    self.current_attack = None

        # Update combo timer
        if self.active_combo:
            if current_time - self.combo_timer > self.combo_window:
                self._reset_combo()

        # Update hitboxes
        for hitbox in self.active_hitboxes[:]:
            if not hitbox.is_active:
                self.active_hitboxes.remove(hitbox)

        return hits

    def check_hit(self, target_rect: pg.Rect, target_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if attack hits target.

        Args:
            target_rect: Target hitbox
            target_id: Target ID

        Returns:
            Hit info or None
        """
        for hitbox in self.active_hitboxes:
            if target_id in hitbox.hit_entities:
                continue

            if hitbox.rect.colliderect(target_rect):
                hitbox.hit_entities.add(target_id)

                hit_info = {
                    "damage": hitbox.damage,
                    "knockback": hitbox.knockback,
                    "hit_stun": hitbox.hit_stun,
                    "attack_type": hitbox.attack_type,
                    "attacker_id": hitbox.owner_id,
                    "target_id": target_id,
                    "timestamp": time.time(),
                }

                self.hit_history.append(hit_info)
                self.stats.total_damage_dealt += hitbox.damage
                self.stats.total_hits += 1

                if self.on_hit:
                    self.on_hit(hitbox, hit_info)

                return hit_info

        return None

    def apply_damage_modifier(self, multiplier: float) -> None:
        """
        Apply damage multiplier.

        Args:
            multiplier: Damage multiplier
        """
        for attack in self.attacks.values():
            attack.damage = int(attack.damage * multiplier)

    def get_combo_progress(self) -> Tuple[int, int]:
        """
        Get combo progress.

        Returns:
            Tuple of (current, total)
        """
        if self.active_combo:
            return (self.combo_index, len(self.active_combo.attacks))
        return (0, 0)

    def get_current_damage(self) -> int:
        """Get current attack damage."""
        if self.current_attack:
            damage = self.current_attack.damage
            if self.active_combo:
                damage = int(damage * self.active_combo.damage_multiplier)
            return damage
        return 0

    def get_attack_state(self) -> AttackState:
        """Get current attack state."""
        return self.attack_state

    def is_attacking(self) -> bool:
        """Check if currently attacking."""
        return self.attack_state != AttackState.IDLE

    def is_combo_active(self) -> bool:
        """Check if combo is active."""
        return self.active_combo is not None

    def get_stats(self) -> CombatStats:
        """Get combat statistics."""
        return self.stats

    def reset(self) -> None:
        """Reset combat state."""
        self.current_attack = None
        self.attack_state = AttackState.IDLE
        self.combo_chain.clear()
        self.combo_index = 0
        self.active_combo = None
        self.active_hitboxes.clear()


# Global combat instances
_combat_instances: Dict[str, MeleeCombat] = {}


def get_combat(owner_id: str) -> MeleeCombat:
    """Get or create combat instance."""
    if owner_id not in _combat_instances:
        _combat_instances[owner_id] = MeleeCombat(owner_id)
    return _combat_instances[owner_id]


def remove_combat(owner_id: str) -> None:
    """Remove combat instance."""
    if owner_id in _combat_instances:
        del _combat_instances[owner_id]
