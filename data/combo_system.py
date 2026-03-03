"""
Combo and score multiplier system for Super Mario Bros.

Provides:
- Combo tracking for consecutive actions
- Score multipliers based on combo
- Combo decay over time
- Visual feedback for combo state
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable

import pygame as pg

from . import constants as c


class ComboType(Enum):
    """Types of combo actions."""

    ENEMY_STOMP = "enemy_stomp"
    COIN_COLLECT = "coin_collect"
    BLOCK_HIT = "block_hit"
    FIREBALL_KILL = "fireball_kill"
    POWERUP_COLLECT = "powerup_collect"


class ComboTier(Enum):
    """Combo multiplier tiers."""

    NONE = "none"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    LEGENDARY = "legendary"


@dataclass
class ComboConfig:
    """Configuration for combo system."""

    # Time in milliseconds before combo decays
    combo_window: int = 3000
    # Time in milliseconds for full combo decay
    combo_decay_time: int = 5000
    # Minimum combo count for each tier
    bronze_threshold: int = 3
    silver_threshold: int = 5
    gold_threshold: int = 10
    platinum_threshold: int = 20
    legendary_threshold: int = 50
    # Maximum multiplier
    max_multiplier: float = 5.0
    # Base multiplier increase per combo
    multiplier_per_combo: float = 0.1


@dataclass
class ComboState:
    """Current state of combo system."""

    count: int = 0
    multiplier: float = 1.0
    tier: ComboTier = ComboTier.NONE
    last_action_time: float = 0.0
    is_active: bool = False
    total_combo_score: int = 0


class ComboManager:
    """
    Manages combo system for score multipliers.

    Usage:
        combo = ComboManager()
        combo.add_action(ComboType.ENEMY_STOMP)
        score = combo.calculate_score(base_score=100)
        combo.update(dt)
    """

    def __init__(self, config: Optional[ComboConfig] = None) -> None:
        """
        Initialize combo manager.

        Args:
            config: Combo configuration (uses default if None)
        """
        self.config = config or ComboConfig()
        self.state = ComboState()
        self._combo_timer: float = 0.0
        self._on_combo_milestone: Optional[Callable[[int, ComboTier], None]] = None

    def set_milestone_callback(self, callback: Callable[[int, ComboTier], None]) -> None:
        """
        Set callback for combo milestones.

        Args:
            callback: Function to call on milestone (count, tier)
        """
        self._on_combo_milestone = callback

    def add_action(self, combo_type: ComboType = ComboType.ENEMY_STOMP, current_time: Optional[float] = None) -> int:
        """
        Add combo action and return new combo count.

        Args:
            combo_type: Type of combo action
            current_time: Optional current time in ms (for testing)

        Returns:
            New combo count
        """
        if current_time is None:
            current_time = time.time() * 1000  # Convert to milliseconds

        # Check if combo should reset
        if self.state.is_active:
            time_since_last = current_time - self.state.last_action_time
            if time_since_last > self.config.combo_window:
                self.reset()

        # Add to combo
        self.state.count += 1
        self.state.last_action_time = current_time
        self.state.is_active = True
        self.state.total_combo_score += self.state.count

        # Update multiplier and tier
        self._update_multiplier()
        self._update_tier()

        # Check for milestones
        self._check_milestone()

        return self.state.count

    def _update_multiplier(self) -> None:
        """Update score multiplier based on combo count."""
        increase = (self.state.count - 1) * self.config.multiplier_per_combo
        self.state.multiplier = min(self.config.max_multiplier, 1.0 + increase)

    def _update_tier(self) -> None:
        """Update combo tier based on count."""
        count = self.state.count

        if count >= self.config.legendary_threshold:
            self.state.tier = ComboTier.LEGENDARY
        elif count >= self.config.platinum_threshold:
            self.state.tier = ComboTier.PLATINUM
        elif count >= self.config.gold_threshold:
            self.state.tier = ComboTier.GOLD
        elif count >= self.config.silver_threshold:
            self.state.tier = ComboTier.SILVER
        elif count >= self.config.bronze_threshold:
            self.state.tier = ComboTier.BRONZE
        else:
            self.state.tier = ComboTier.NONE

    def _check_milestone(self) -> None:
        """Check and trigger combo milestone."""
        if self._on_combo_milestone and self.state.count in [
            self.config.bronze_threshold,
            self.config.silver_threshold,
            self.config.gold_threshold,
            self.config.platinum_threshold,
            self.config.legendary_threshold,
        ]:
            self._on_combo_milestone(self.state.count, self.state.tier)

    def reset(self) -> None:
        """Reset combo state."""
        self.state = ComboState()
        self._combo_timer = 0.0

    def update(self, dt: float) -> None:
        """
        Update combo timer and handle decay.

        Args:
            dt: Delta time in milliseconds
        """
        if not self.state.is_active:
            return

        self._combo_timer += dt

        # Check if combo should expire
        time_since_last = (time.time() * 1000) - self.state.last_action_time
        if time_since_last > self.config.combo_decay_time:
            self.reset()

    def calculate_score(self, base_score: int) -> int:
        """
        Calculate score with combo multiplier.

        Args:
            base_score: Base score value

        Returns:
            Multiplied score (rounded down)
        """
        if not self.state.is_active:
            return base_score

        return int(base_score * self.state.multiplier)

    def get_combo_display(self) -> str:
        """
        Get combo display string.

        Returns:
            Formatted combo string (e.g., "5x COMBO!")
        """
        if not self.state.is_active or self.state.count < 2:
            return ""

        return f"{self.state.count}x COMBO!"

    def get_tier_color(self) -> tuple[int, int, int]:
        """
        Get color for current combo tier.

        Returns:
            RGB color tuple
        """
        colors = {
            ComboTier.NONE: c.GRAY,
            ComboTier.BRONZE: (205, 127, 50),
            ComboTier.SILVER: (192, 192, 192),
            ComboTier.GOLD: c.GOLD,
            ComboTier.PLATINUM: (229, 228, 226),
            ComboTier.LEGENDARY: (180, 100, 255),
        }
        return colors.get(self.state.tier, c.WHITE)

    def get_tier_name(self) -> str:
        """Get display name for current tier."""
        names = {
            ComboTier.NONE: "",
            ComboTier.BRONZE: "Бронза",
            ComboTier.SILVER: "Серебро",
            ComboTier.GOLD: "Золото",
            ComboTier.PLATINUM: "Платина",
            ComboTier.LEGENDARY: "Легенда",
        }
        return names.get(self.state.tier, "")

    @property
    def combo_count(self) -> int:
        """Get current combo count."""
        return self.state.count

    @property
    def multiplier(self) -> float:
        """Get current multiplier."""
        return self.state.multiplier

    @property
    def tier(self) -> ComboTier:
        """Get current tier."""
        return self.state.tier

    @property
    def is_active(self) -> bool:
        """Check if combo is currently active."""
        return self.state.is_active and self.state.count >= 2


class ComboUI:
    """
    UI renderer for combo system.
    """

    def __init__(self, combo_manager: ComboManager) -> None:
        """
        Initialize combo UI.

        Args:
            combo_manager: Combo manager instance
        """
        self.combo = combo_manager
        self.font_large: Optional[pg.font.Font] = None
        self.font_medium: Optional[pg.font.Font] = None
        self.font_small: Optional[pg.font.Font] = None
        self._init_fonts()

        # Animation state
        self._scale: float = 1.0
        self._pulse_timer: float = 0.0
        self._fade_alpha: int = 255

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font_large = pg.font.Font(None, 56)
            self.font_medium = pg.font.Font(None, 36)
            self.font_small = pg.font.Font(None, 24)
        except pg.error:
            self.font_large = None
            self.font_medium = None
            self.font_small = None

    def draw(self, surface: pg.Surface, position: tuple[int, int] = (50, 50)) -> None:
        """
        Draw combo display.

        Args:
            surface: Surface to draw to
            position: (x, y) position for combo display
        """
        if not self.combo.is_active:
            return

        x, y = position

        # Update animation
        self._update_animation()

        # Get combo info
        count = self.combo.combo_count
        tier_name = self.combo.get_tier_name()
        color = self.combo.get_tier_color()

        if self.font_large and self.font_medium:
            # Draw combo count with scaling
            combo_text = f"{count}x"
            combo_surface = self.font_large.render(combo_text, True, color)

            # Apply scale effect
            if self._scale != 1.0:
                combo_surface = pg.transform.scale_by(combo_surface, self._scale)

            combo_rect = combo_surface.get_rect(center=(x + 40, y + 20))
            surface.blit(combo_surface, combo_rect)

            # Draw tier name
            if tier_name:
                tier_surface = self.font_medium.render(tier_name, True, color)
                surface.blit(tier_surface, (x, y + 45))

            # Draw multiplier
            if self.font_small:
                mult_text = f"Множитель: {self.combo.multiplier:.1f}x"
                mult_surface = self.font_small.render(mult_text, True, c.WHITE)
                surface.blit(mult_surface, (x, y + 75))

    def _update_animation(self) -> None:
        """Update combo animation effects."""
        # Pulse effect on recent combo
        current_time = time.time() * 1000
        time_since_last = current_time - self.combo.state.last_action_time

        if time_since_last < 500:
            # Recent combo - pulse effect
            self._pulse_timer += 16  # ~60fps
            self._scale = 1.0 + 0.2 * abs(pg.math.Vector2(1, 0).rotate(self._pulse_timer).x)
        else:
            # Return to normal
            self._scale = max(1.0, self._scale - 0.05)

        # Fade effect when combo is about to expire
        decay_time = self.combo.config.combo_decay_time
        time_since_last = current_time - self.combo.state.last_action_time

        if time_since_last > decay_time * 0.7:
            # Fading - combo about to expire
            fade_progress = (time_since_last - decay_time * 0.7) / (decay_time * 0.3)
            self._fade_alpha = int(255 * (1.0 - fade_progress))
        else:
            self._fade_alpha = 255


class ScoreManager:
    """
    Manages score tracking with combo integration.

    Usage:
        score_mgr = ScoreManager(combo_manager)
        score_mgr.add_score(100, ComboType.ENEMY_STOMP)
        score_mgr.update(dt)
    """

    def __init__(self, combo_manager: ComboManager, initial_score: int = 0) -> None:
        """
        Initialize score manager.

        Args:
            combo_manager: Combo manager for multipliers
            initial_score: Starting score
        """
        self.combo = combo_manager
        self.score = initial_score
        self.base_score = initial_score
        self._pending_scores: list[tuple[int, float]] = []  # (score, time_added)

    def add_score(
        self, base_points: int, combo_type: Optional[ComboType] = None, combo_count: Optional[int] = None
    ) -> int:
        """
        Add score with optional combo bonus.

        Args:
            base_points: Base points to add
            combo_type: Type of combo action (triggers combo if provided)
            combo_count: Override combo count (for display)

        Returns:
            Actual points added (with multiplier)
        """
        # Trigger combo if type specified
        if combo_type:
            self.combo.add_action(combo_type)

        # Calculate multiplied score
        multiplied = self.combo.calculate_score(base_points)
        bonus = multiplied - base_points

        # Add to total
        self.score += multiplied
        # update base_score as well (for reset logic)
        self.base_score += multiplied

        # Store for animation
        current_time = time.time()
        self._pending_scores.append((bonus, current_time))

        return multiplied

    def add_score_with_chain(self, base_points: int, chain_count: int) -> int:
        """
        Add score with manual chain bonus.

        Args:
            base_points: Base points
            chain_count: Number of chained actions

        Returns:
            Total points added
        """
        # Bonus for chain
        chain_bonus = base_points * (chain_count - 1) * 0.1
        total_base = base_points + chain_bonus

        return self.add_score(int(total_base))

    def update(self, dt: float) -> None:
        """
        Update score manager.

        Args:
            dt: Delta time in milliseconds
        """
        # Update combo
        self.combo.update(dt)

        # Clean old pending scores (after 2 seconds)
        current_time = time.time()
        self._pending_scores = [(score, t) for score, t in self._pending_scores if current_time - t < 2.0]

    def get_display_score(self) -> str:
        """
        Get formatted score string.

        Returns:
            Zero-padded score string (6 digits)
        """
        return f"{int(self.score):06d}"

    def get_pending_bonuses(self) -> list[tuple[int, float]]:
        """Get list of pending bonus scores for animation."""
        return self._pending_scores.copy()

    def reset(self, keep_total: bool = False) -> None:
        """
        Reset score.

        Args:
            keep_total: If True, keep base_score for next round
        """
        if not keep_total:
            self.base_score = 0
        self.score = self.base_score
        self._pending_scores.clear()


class ScoreUI:
    """
    UI renderer for score display.
    """

    def __init__(self, score_manager: ScoreManager) -> None:
        """
        Initialize score UI.

        Args:
            score_manager: Score manager instance
        """
        self.score_mgr = score_manager
        self.font: Optional[pg.font.Font] = None
        self._init_fonts()

        # Animation for score increase
        self._last_score: int = 0
        self._score_increase: int = 0
        self._increase_timer: float = 0.0

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font = pg.font.Font(None, 36)
        except pg.error:
            self.font = None

    def draw(self, surface: pg.Surface, position: tuple[int, int] = (50, 100)) -> None:
        """
        Draw score display.

        Args:
            surface: Surface to draw to
            position: (x, y) position
        """
        x, y = position

        if self.font:
            # Draw label
            label_surface = self.font.render("СЧЁТ", True, c.WHITE)
            surface.blit(label_surface, (x, y))

            # Draw score
            score_text = self.score_mgr.get_display_score()
            score_surface = self.font.render(score_text, True, c.GOLD)
            surface.blit(score_surface, (x, y + 30))

    def draw_score_increase(self, surface: pg.Surface, position: tuple[int, int], increase: int) -> None:
        """
        Draw floating score increase text.

        Args:
            surface: Surface to draw to
            position: (x, y) position
            increase: Points added
        """
        x, y = position

        if self.font:
            text = f"+{increase}"
            color = c.GOLD if increase >= 100 else c.WHITE

            surface = self.font.render(text, True, color)
            surface.blit(surface, (x, y))
