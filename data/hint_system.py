"""
Hint and Tutorial System for Super Mario Bros.

Provides:
- Context-sensitive hints
- Tutorial messages for new players
- Hint progression system
- Hint display with animations
- Player skill tracking
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set

import pygame as pg

from . import constants as c
from .animation_system import TweenManager, EasingType


class HintCategory(Enum):
    """Categories of hints."""

    MOVEMENT = "movement"
    COMBAT = "combat"
    POWERUPS = "powerups"
    SECRETS = "secrets"
    ENEMIES = "enemies"
    COLLECTION = "collection"
    GENERAL = "general"


class HintPriority(Enum):
    """Hint priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class HintState(Enum):
    """Hint display state."""

    HIDDEN = "hidden"
    FADE_IN = "fade_in"
    VISIBLE = "visible"
    FADE_OUT = "fade_out"


@dataclass
class Hint:
    """
    Hint data structure.

    Attributes:
        id: Unique identifier
        title: Short title
        message: Full hint message
        category: Hint category
        priority: Display priority
        trigger_count: Times trigger condition met before showing
        display_duration: How long to display (ms)
        cooldown: Minimum time before showing again (ms)
        prerequisites: Other hint IDs that must be shown first
        conditions: Functions that determine if hint should show
    """

    id: str
    title: str
    message: str
    category: HintCategory = HintCategory.GENERAL
    priority: HintPriority = HintPriority.NORMAL
    trigger_count: int = 1
    display_duration: int = 5000
    cooldown: int = 30000
    prerequisites: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)

    # Runtime state
    times_triggered: int = 0
    last_shown: float = 0.0
    is_unlocked: bool = True
    is_completed: bool = False


@dataclass
class HintTrigger:
    """Tracks trigger conditions for hints."""

    hint_id: str
    trigger_type: str
    trigger_data: dict
    times_met: int = 0


class HintCondition:
    """
    Base class for hint conditions.
    """

    def check(self, game_state: dict) -> bool:
        """
        Check if condition is met.

        Args:
            game_state: Current game state dictionary

        Returns:
            True if condition is met
        """
        raise NotImplementedError


class PlayerLevelCondition(HintCondition):
    """Condition based on player level/state."""

    def __init__(self, min_level: int = 0, is_big: bool = False) -> None:
        """
        Initialize condition.

        Args:
            min_level: Minimum player level
            is_big: Check if player is big
        """
        self.min_level = min_level
        self.is_big = is_big

    def check(self, game_state: Dict[str, Any]) -> bool:
        """Check player level condition."""
        player = game_state.get("player", {})

        if self.is_big and not player.get("is_big", False):
            return False

        return bool(player.get("level", 0) >= self.min_level)


class EnemyDefeatCondition(HintCondition):
    """Condition based on enemy defeats."""

    def __init__(self, min_defeats: int = 1, enemy_type: Optional[str] = None) -> None:
        """
        Initialize condition.

        Args:
            min_defeats: Minimum defeats required
            enemy_type: Specific enemy type (None = any)
        """
        self.min_defeats = min_defeats
        self.enemy_type = enemy_type

    def check(self, game_state: Dict[str, Any]) -> bool:
        """Check enemy defeat condition."""
        stats = game_state.get("stats", {})

        if self.enemy_type:
            key = f"{self.enemy_type}_defeated"
            return bool(stats.get(key, 0) >= self.min_defeats)

        return bool(stats.get("enemies_defeated", 0) >= self.min_defeats)


class CoinCollectionCondition(HintCondition):
    """Condition based on coin collection."""

    def __init__(self, min_coins: int = 10) -> None:
        """
        Initialize condition.

        Args:
            min_coins: Minimum coins required
        """
        self.min_coins = min_coins

    def check(self, game_state: Dict[str, Any]) -> bool:
        """Check coin collection condition."""
        stats = game_state.get("stats", {})
        return bool(stats.get("coins_collected", 0) >= self.min_coins)


class DeathCondition(HintCondition):
    """Condition based on player deaths."""

    def __init__(self, min_deaths: int = 1, in_area: Optional[str] = None) -> None:
        """
        Initialize condition.

        Args:
            min_deaths: Minimum deaths required
            in_area: Specific area (None = any)
        """
        self.min_deaths = min_deaths
        self.in_area = in_area

    def check(self, game_state: Dict[str, Any]) -> bool:
        """Check death condition."""
        stats = game_state.get("stats", {})

        if self.in_area:
            key = f"deaths_in_{self.in_area}"
            return bool(stats.get(key, 0) >= self.min_deaths)

        return bool(stats.get("deaths", 0) >= self.min_deaths)


class HintManager:
    """
    Central manager for hint system.

    Usage:
        hint_mgr = HintManager()
        hint_mgr.register_default_hints()
        hint_mgr.update(game_state, dt)
        hint_mgr.trigger("player_jump")
        current_hint = hint_mgr.get_current_hint()
    """

    def __init__(self) -> None:
        """Initialize hint manager."""
        self.hints: Dict[str, Hint] = {}
        self.triggers: Dict[str, HintTrigger] = {}
        self.shown_hints: Set[str] = set()
        self.current_hint: Optional[Hint] = None
        self.hint_queue: List[Hint] = []

        self.tween_manager = TweenManager()
        self.display_timer = 0.0
        self.state = HintState.HIDDEN
        self.alpha = 0

        self.enabled = True
        self.show_tutorial_hints = True
        self.hint_frequency = 1.0  # 0-1 scale

        self._game_state: dict = {}

    def register_hint(self, hint: Hint) -> None:
        """
        Register a hint.

        Args:
            hint: Hint to register
        """
        self.hints[hint.id] = hint

    def register_default_hints(self) -> None:
        """Register all default hints."""
        # Movement hints
        self.register_hint(
            Hint(
                id="move_basic",
                title="Перемещение",
                message="Используйте стрелки ← → для движения Марио",
                category=HintCategory.MOVEMENT,
                priority=HintPriority.CRITICAL,
                trigger_count=1,
                prerequisites=[],
            )
        )

        self.register_hint(
            Hint(
                id="jump_basic",
                title="Прыжок",
                message="Нажмите A для прыжка. Прыгайте на врагов, чтобы победить их!",
                category=HintCategory.MOVEMENT,
                priority=HintPriority.CRITICAL,
                trigger_count=3,
                prerequisites=["move_basic"],
            )
        )

        self.register_hint(
            Hint(
                id="jump_hold",
                title="Высокий прыжок",
                message="Удерживайте A для более высокого прыжка",
                category=HintCategory.MOVEMENT,
                priority=HintPriority.NORMAL,
                trigger_count=5,
                prerequisites=["jump_basic"],
            )
        )

        self.register_hint(
            Hint(
                id="run_jump",
                title="Прыжок с разбега",
                message="Разбегитесь перед прыжком для большей дальности",
                category=HintCategory.MOVEMENT,
                priority=HintPriority.LOW,
                trigger_count=10,
                prerequisites=["jump_hold"],
            )
        )

        # Combat hints
        self.register_hint(
            Hint(
                id="stomp_enemy",
                title="Победа над врагами",
                message="Прыгайте на врагов сверху, чтобы победить их",
                category=HintCategory.COMBAT,
                priority=HintPriority.HIGH,
                trigger_count=1,
                prerequisites=["jump_basic"],
            )
        )

        self.register_hint(
            Hint(
                id="koopa_shell",
                title="Панцирь Купы",
                message="Нажмите S рядом с панцирем, чтобы пнуть его",
                category=HintCategory.COMBAT,
                priority=HintPriority.NORMAL,
                trigger_count=1,
                prerequisites=["stomp_enemy"],
            )
        )

        # Power-up hints
        self.register_hint(
            Hint(
                id="mushroom_powerup",
                title="Супер-гриб",
                message="Соберите гриб, чтобы стать большим Марио!",
                category=HintCategory.POWERUPS,
                priority=HintPriority.HIGH,
                trigger_count=1,
                prerequisites=[],
            )
        )

        self.register_hint(
            Hint(
                id="fireflower_powerup",
                title="Огненный цветок",
                message="Огненный цветок позволяет бросать огненные шары!",
                category=HintCategory.POWERUPS,
                priority=HintPriority.NORMAL,
                trigger_count=1,
                prerequisites=["mushroom_powerup"],
            )
        )

        self.register_hint(
            Hint(
                id="star_invincibility",
                title="Звезда неуязвимости",
                message="Звезда делает вас неуязвимым на короткое время!",
                category=HintCategory.POWERUPS,
                priority=HintPriority.NORMAL,
                trigger_count=1,
                prerequisites=["mushroom_powerup"],
            )
        )

        # Collection hints
        self.register_hint(
            Hint(
                id="coin_collection",
                title="Монеты",
                message="Собирайте монеты для очков. 100 монет = дополнительная жизнь!",
                category=HintCategory.COLLECTION,
                priority=HintPriority.NORMAL,
                trigger_count=10,
                prerequisites=[],
            )
        )

        self.register_hint(
            Hint(
                id="block_hit",
                title="Блоки с предметами",
                message="Прыгайте снизу под блоки, чтобы получить предметы",
                category=HintCategory.COLLECTION,
                priority=HintPriority.NORMAL,
                trigger_count=3,
                prerequisites=[],
            )
        )

        self.register_hint(
            Hint(
                id="secret_blocks",
                title="Секретные блоки",
                message="Некоторые невидимые блоки содержат секреты!",
                category=HintCategory.SECRETS,
                priority=HintPriority.LOW,
                trigger_count=5,
                prerequisites=["block_hit"],
            )
        )

        # Enemy-specific hints
        self.register_hint(
            Hint(
                id="goomba_weakness",
                title="Гумбы",
                message="Гумбы медленные. Прыгайте на них сверху!",
                category=HintCategory.ENEMIES,
                priority=HintPriority.NORMAL,
                trigger_count=1,
                prerequisites=["stomp_enemy"],
            )
        )

        self.register_hint(
            Hint(
                id="koopa_weakness",
                title="Купы",
                message="Купы отступают в панцирь при прыжке. Осторожно!",
                category=HintCategory.ENEMIES,
                priority=HintPriority.NORMAL,
                trigger_count=1,
                prerequisites=["stomp_enemy"],
            )
        )

        # General hints
        self.register_hint(
            Hint(
                id="flagpole_goal",
                title="Цель уровня",
                message="Доберитесь до флага в конце уровня!",
                category=HintCategory.GENERAL,
                priority=HintPriority.HIGH,
                trigger_count=1,
                prerequisites=[],
            )
        )

        self.register_hint(
            Hint(
                id="time_limit",
                title="Ограничение времени",
                message="Не дайте времени истечь, или вы потеряете жизнь!",
                category=HintCategory.GENERAL,
                priority=HintPriority.NORMAL,
                trigger_count=1,
                display_duration=4000,
            )
        )

        self.register_hint(
            Hint(
                id="pit_death",
                title="Опасные ямы",
                message="Избегайте падения в ямы!",
                category=HintCategory.GENERAL,
                priority=HintPriority.HIGH,
                trigger_count=1,
                prerequisites=[],
            )
        )

    def trigger(self, trigger_name: str) -> None:
        """
        Trigger a hint event.

        Args:
            trigger_name: Name of trigger event
        """
        if not self.enabled:
            return

        # Map trigger names to hint IDs
        trigger_map = {
            "player_move": "move_basic",
            "player_jump": "jump_basic",
            "player_jump_high": "jump_hold",
            "player_run_jump": "run_jump",
            "enemy_stomp": "stomp_enemy",
            "koopa_shell_kick": "koopa_shell",
            "mushroom_collect": "mushroom_powerup",
            "fireflower_collect": "fireflower_powerup",
            "star_collect": "star_invincibility",
            "coin_collect": "coin_collection",
            "block_hit": "block_hit",
            "secret_found": "secret_blocks",
            "goomba_defeat": "goomba_weakness",
            "koopa_defeat": "koopa_weakness",
            "flagpole_reach": "flagpole_goal",
            "time_low": "time_limit",
            "pit_death": "pit_death",
        }

        hint_id = trigger_map.get(trigger_name)
        if hint_id and hint_id in self.hints:
            self._trigger_hint(hint_id)

    def _trigger_hint(self, hint_id: str) -> None:
        """
        Internal method to trigger a hint.

        Args:
            hint_id: ID of hint to trigger
        """
        hint = self.hints.get(hint_id)
        if not hint or not hint.is_unlocked:
            return

        # Check prerequisites
        for prereq_id in hint.prerequisites:
            if prereq_id not in self.shown_hints:
                return  # Prerequisite not shown yet

        # Increment trigger count
        hint.times_triggered += 1

        # Check if enough triggers
        if hint.times_triggered < hint.trigger_count:
            return

        # Check cooldown
        current_time = time.time() * 1000
        if current_time - hint.last_shown < hint.cooldown:
            return

        # Add to queue
        if hint not in self.hint_queue and hint_id not in self.shown_hints:
            self.hint_queue.append(hint)

    def update(self, game_state: dict, dt: int) -> None:
        """
        Update hint system.

        Args:
            game_state: Current game state
            dt: Delta time in milliseconds
        """
        self._game_state = game_state

        if not self.enabled:
            return

        # Update display timer
        if self.state == HintState.VISIBLE:
            self.display_timer -= dt
            if self.display_timer <= 0:
                self._start_fade_out()

        # Update tweens
        self.tween_manager.update(dt)

        # Process hint queue
        self._process_hint_queue()

    def _process_hint_queue(self) -> None:
        """Process the hint queue."""
        if self.current_hint is not None:
            return  # Already showing a hint

        if not self.hint_queue:
            return

        # Sort by priority
        self.hint_queue.sort(key=lambda h: h.priority.value, reverse=True)

        # Get highest priority hint
        hint = self.hint_queue.pop(0)

        # Check conditions
        if not self._check_conditions(hint):
            return

        # Show hint
        self._show_hint(hint)

    def _check_conditions(self, hint: Hint) -> bool:
        """
        Check if hint conditions are met.

        Args:
            hint: Hint to check

        Returns:
            True if conditions are met
        """
        for condition_name in hint.conditions:
            # Would evaluate condition strings
            pass

        return True

    def _show_hint(self, hint: Hint) -> None:
        """
        Show a hint.

        Args:
            hint: Hint to show
        """
        self.current_hint = hint
        self.state = HintState.FADE_IN
        self.display_timer = hint.display_duration

        # Fade in animation
        self.tween_manager.add_tween("alpha", self.alpha, 255, 300, EasingType.EASE_OUT_SINE)
        self.alpha = 255
        self.state = HintState.VISIBLE

    def _start_fade_out(self) -> None:
        """Start fade out animation."""
        self.state = HintState.FADE_OUT

        self.tween_manager.add_tween("alpha", self.alpha, 0, 300, EasingType.EASE_IN_SINE)
        self.alpha = 0

        # Mark hint as shown
        if self.current_hint:
            self.current_hint.last_shown = time.time() * 1000
            self.shown_hints.add(self.current_hint.id)

        self.current_hint = None
        self.state = HintState.HIDDEN

    def get_current_hint(self) -> Optional[Hint]:
        """Get currently displayed hint."""
        return self.current_hint

    def get_alpha(self) -> int:
        """Get current alpha for rendering."""
        return int(self.alpha)

    def is_visible(self) -> bool:
        """Check if hint is currently visible."""
        return self.state == HintState.VISIBLE

    def force_show_hint(self, hint_id: str) -> bool:
        """
        Force show a specific hint.

        Args:
            hint_id: ID of hint to show

        Returns:
            True if hint was shown
        """
        if hint_id not in self.hints:
            return False

        hint = self.hints[hint_id]
        if hint not in self.hint_queue:
            self.hint_queue.append(hint)

        return True

    def reset(self) -> None:
        """Reset hint system."""
        self.hint_queue.clear()
        self.current_hint = None
        self.state = HintState.HIDDEN
        self.alpha = 0

    def get_hint_progress(self) -> dict:
        """
        Get hint system progress.

        Returns:
            Dictionary with progress info
        """
        total = len(self.hints)
        shown = len(self.shown_hints)

        by_category: Dict[str, int] = {}
        for hint in self.hints.values():
            cat = hint.category.value
            if cat not in by_category:
                by_category[cat] = 0
            if hint.id in self.shown_hints:
                by_category[cat] += 1

        return {
            "total_hints": total,
            "shown_hints": shown,
            "hidden_hints": total - shown,
            "completion_percent": (shown / total * 100) if total > 0 else 0,
            "by_category": by_category,
        }


class HintDisplay:
    """
    Renderer for hint UI.
    """

    def __init__(self, hint_manager: HintManager) -> None:
        """
        Initialize hint display.

        Args:
            hint_manager: Hint manager instance
        """
        self.hint_manager = hint_manager
        self.font_title: Optional[pg.font.Font] = None
        self.font_message: Optional[pg.font.Font] = None
        self._init_fonts()

        # Display position
        self.x = 50
        self.y = 400
        self.width = 400
        self.height = 120

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            self.font_title = pg.font.Font(None, 36)
            self.font_message = pg.font.Font(None, 24)
        except pg.error:
            self.font_title = None
            self.font_message = None

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw hint to surface.

        Args:
            surface: Surface to draw to
        """
        hint = self.hint_manager.get_current_hint()
        if not hint:
            return

        alpha = self.hint_manager.get_alpha()
        if alpha <= 0:
            return

        # Draw background
        bg_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        bg_color = (*c.NAVYBLUE, int(alpha * 0.9))
        pg.draw.rect(bg_surface, bg_color, (0, 0, self.width, self.height), border_radius=8)
        pg.draw.rect(bg_surface, (*c.GOLD, int(alpha)), (0, 0, self.width, self.height), 2, border_radius=8)

        surface.blit(bg_surface, (self.x, self.y))

        # Draw title
        if self.font_title:
            title_surface = self.font_title.render(hint.title, True, c.GOLD)
            title_surface.set_alpha(alpha)
            surface.blit(title_surface, (self.x + 15, self.y + 10))

        # Draw message
        if self.font_message:
            # Word wrap message
            words = hint.message.split()
            lines = []
            current_line = ""

            for word in words:
                test_line = current_line + word + " "
                test_surface = self.font_message.render(test_line, True, c.WHITE)
                if test_surface.get_width() <= self.width - 30:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "

            if current_line:
                lines.append(current_line)

            for i, line in enumerate(lines[:3]):  # Max 3 lines
                line_surface = self.font_message.render(line, True, c.WHITE)
                line_surface.set_alpha(alpha)
                surface.blit(line_surface, (self.x + 15, self.y + 45 + i * 25))

        # Draw hint icon based on category
        self._draw_icon(surface, hint.category, alpha)

    def _draw_icon(self, surface: pg.Surface, category: HintCategory, alpha: int) -> None:
        """Draw category icon."""
        icon_colors = {
            HintCategory.MOVEMENT: c.SKY_BLUE,
            HintCategory.COMBAT: c.RED,
            HintCategory.POWERUPS: c.ORANGE,
            HintCategory.SECRETS: c.PURPLE,
            HintCategory.ENEMIES: c.GREEN,
            HintCategory.COLLECTION: c.GOLD,
            HintCategory.GENERAL: c.WHITE,
        }

        color = icon_colors.get(category, c.WHITE)
        icon_rect = pg.Rect(self.x + self.width - 40, self.y + 10, 24, 24)
        pg.draw.rect(surface, (*color, alpha), icon_rect)


class HintTriggerSystem:
    """
    System for tracking game events that trigger hints.
    """

    def __init__(self, hint_manager: HintManager) -> None:
        """
        Initialize trigger system.

        Args:
            hint_manager: Hint manager instance
        """
        self.hint_manager = hint_manager
        self.event_counts: Dict[str, int] = {}
        self.listeners: Dict[str, List[Callable]] = {}

    def register_event(self, event_name: str) -> None:
        """Register an event type."""
        if event_name not in self.event_counts:
            self.event_counts[event_name] = 0

    def trigger_event(self, event_name: str, data: Optional[dict] = None) -> None:
        """
        Trigger an event.

        Args:
            event_name: Name of event
            data: Event data
        """
        if event_name not in self.event_counts:
            self.register_event(event_name)

        self.event_counts[event_name] += 1

        # Notify hint manager
        self.hint_manager.trigger(event_name)

        # Notify listeners
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(data)

    def add_listener(self, event_name: str, callback: Callable[[Optional[dict]], None]) -> None:
        """
        Add event listener.

        Args:
            event_name: Event to listen for
            callback: Function to call on event
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def get_event_count(self, event_name: str) -> int:
        """Get count of event occurrences."""
        return self.event_counts.get(event_name, 0)

    def reset(self) -> None:
        """Reset all event counts."""
        self.event_counts.clear()
