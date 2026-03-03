"""
Player Statistics System for Super Mario Bros.

Provides:
- Comprehensive stats tracking
- Session statistics
- Lifetime statistics
- Achievements integration
- Stats persistence
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

from . import constants as c


@dataclass
class SessionStats:
    """Statistics for current gaming session."""

    start_time: str = ""
    duration_seconds: int = 0
    score: int = 0
    coins_collected: int = 0
    enemies_defeated: int = 0
    powerups_collected: int = 0
    deaths: int = 0
    damage_taken: int = 0
    jumps: int = 0
    distance_traveled: float = 0.0
    blocks_hit: int = 0
    secrets_found: int = 0
    combo_max: int = 0
    accuracy: float = 0.0  # Hit/attempt ratio


@dataclass
class LifetimeStats:
    """Lifetime statistics across all sessions."""

    total_sessions: int = 0
    total_playtime_seconds: int = 0
    total_score: int = 0
    total_coins: int = 0
    total_enemies: int = 0
    total_powerups: int = 0
    total_deaths: int = 0
    total_jumps: int = 0
    total_distance: float = 0.0
    total_blocks_hit: int = 0
    total_secrets_found: int = 0

    # Records
    highest_score: int = 0
    most_coins_in_session: int = 0
    most_enemies_in_session: int = 0
    longest_combo: int = 0
    fastest_level_time: int = 0  # seconds

    # Progression
    levels_completed: int = 0
    worlds_unlocked: int = 1
    achievements_unlocked: int = 0


@dataclass
class EnemyStats:
    """Enemy-specific statistics."""

    goombas_defeated: int = 0
    koopas_defeated: int = 0
    stomps: int = 0
    fireball_kills: int = 0
    shell_kills: int = 0
    other_kills: int = 0


@dataclass
class PowerUpStats:
    """Power-up statistics."""

    mushrooms_collected: int = 0
    fireflowers_collected: int = 0
    stars_collected: int = 0
    one_ups_collected: int = 0
    time_powerup_active: int = 0  # seconds


class StatisticsManager:
    """
    Central manager for player statistics.

    Usage:
        stats_mgr = StatisticsManager()
        stats_mgr.load()
        stats_mgr.session.increment("coins", 5)
        stats_mgr.save()
    """

    DEFAULT_SAVE_PATH = "saves/statistics.json"

    def __init__(self, save_path: Optional[str] = None) -> None:
        """
        Initialize statistics manager.

        Args:
            save_path: Path to save file
        """
        self.save_path = Path(save_path) if save_path else Path(self.DEFAULT_SAVE_PATH)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        self.session = SessionStats()
        self.lifetime = LifetimeStats()
        self.enemies = EnemyStats()
        self.powerups = PowerUpStats()

        self._session_start_time: float = 0
        self._stat_trackers: Dict[str, int] = {}

        self._start_session()

    def _start_session(self) -> None:
        """Start new session."""
        self.session = SessionStats()
        self.session.start_time = datetime.now().isoformat()
        self._session_start_time = time.time()

        # Reset trackers
        self._stat_trackers = {
            "jumps": 0,
            "coins": 0,
            "enemies": 0,
            "damage": 0,
        }

    def _end_session(self) -> None:
        """End current session and update lifetime stats."""
        # Calculate duration
        duration = int(time.time() - self._session_start_time)
        self.session.duration_seconds = duration

        # Update lifetime
        self.lifetime.total_sessions += 1
        self.lifetime.total_playtime_seconds += duration
        self.lifetime.total_score += self.session.score
        self.lifetime.total_coins += self.session.coins_collected
        self.lifetime.total_enemies += self.session.enemies_defeated
        self.lifetime.total_powerups += self.session.powerups_collected
        self.lifetime.total_deaths += self.session.deaths
        self.lifetime.total_jumps += self.session.jumps
        self.lifetime.total_distance += self.session.distance_traveled
        self.lifetime.total_blocks_hit += self.session.blocks_hit
        self.lifetime.total_secrets_found += self.session.secrets_found

        # Update records
        if self.session.score > self.lifetime.highest_score:
            self.lifetime.highest_score = self.session.score

        if self.session.coins_collected > self.lifetime.most_coins_in_session:
            self.lifetime.most_coins_in_session = self.session.coins_collected

        if self.session.enemies_defeated > self.lifetime.most_enemies_in_session:
            self.lifetime.most_enemies_in_session = self.session.enemies_defeated

        if self.session.combo_max > self.lifetime.longest_combo:
            self.lifetime.longest_combo = self.session.combo_max

    def increment(self, stat: str, amount: int = 1) -> None:
        """
        Increment a statistic.

        Args:
            stat: Statistic name
            amount: Amount to add
        """
        # Session stats
        if hasattr(self.session, stat):
            current = getattr(self.session, stat)
            if isinstance(current, (int, float)):
                setattr(self.session, stat, current + amount)

        # Enemy stats
        if stat.startswith("enemy_"):
            enemy_stat = stat.replace("enemy_", "")
            if hasattr(self.enemies, enemy_stat):
                current = getattr(self.enemies, enemy_stat)
                setattr(self.enemies, enemy_stat, current + amount)

        # Power-up stats
        if stat.startswith("powerup_"):
            pup_stat = stat.replace("powerup_", "")
            if hasattr(self.powerups, pup_stat):
                current = getattr(self.powerups, pup_stat)
                setattr(self.powerups, pup_stat, current + amount)

        # Tracker
        if stat in self._stat_trackers:
            self._stat_trackers[stat] += amount

    def set_stat(self, stat: str, value: Any) -> None:
        """
        Set a statistic value.

        Args:
            stat: Statistic name
            value: Value to set
        """
        if hasattr(self.session, stat):
            setattr(self.session, stat, value)

        if hasattr(self.lifetime, stat):
            setattr(self.lifetime, stat, value)

    def get_stat(self, stat: str, default: Any = 0) -> Any:
        """
        Get statistic value.

        Args:
            stat: Statistic name
            default: Default value if not found

        Returns:
            Statistic value
        """
        # Check session
        if hasattr(self.session, stat):
            return getattr(self.session, stat)

        # Check lifetime
        if hasattr(self.lifetime, stat):
            return getattr(self.lifetime, stat)

        # Check enemies
        if hasattr(self.enemies, stat):
            return getattr(self.enemies, stat)

        # Check powerups
        if hasattr(self.powerups, stat):
            return getattr(self.powerups, stat)

        return default

    def get_tracker(self, stat: str) -> int:
        """Get tracker value."""
        return self._stat_trackers.get(stat, 0)

    def reset_tracker(self, stat: str) -> None:
        """Reset tracker."""
        if stat in self._stat_trackers:
            self._stat_trackers[stat] = 0

    def save(self) -> bool:
        """
        Save statistics to file.

        Returns:
            True if saved successfully
        """
        self._end_session()

        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "session": asdict(self.session),
            "lifetime": asdict(self.lifetime),
            "enemies": asdict(self.enemies),
            "powerups": asdict(self.powerups),
        }

        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logger.warning("Could not save statistics: %s", e)
            return False

    def load(self) -> bool:
        """
        Load statistics from file.

        Returns:
            True if loaded successfully
        """
        if not self.save_path.exists():
            return False

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load lifetime
            lifetime_data = data.get("lifetime", {})
            for key, value in lifetime_data.items():
                if hasattr(self.lifetime, key):
                    setattr(self.lifetime, key, value)

            # Load enemies
            enemies_data = data.get("enemies", {})
            for key, value in enemies_data.items():
                if hasattr(self.enemies, key):
                    setattr(self.enemies, key, value)

            # Load powerups
            powerups_data = data.get("powerups", {})
            for key, value in powerups_data.items():
                if hasattr(self.powerups, key):
                    setattr(self.powerups, key, value)

            return True

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Could not load statistics: %s", e)
            return False

    def get_session_summary(self) -> dict:
        """Get session summary."""
        return {
            "duration": self.session.duration_seconds,
            "score": self.session.score,
            "coins": self.session.coins_collected,
            "enemies": self.session.enemies_defeated,
            "deaths": self.session.deaths,
            "kdr": (self.session.enemies_defeated / max(1, self.session.deaths)),
        }

    def get_lifetime_summary(self) -> dict:
        """Get lifetime summary."""
        hours = self.lifetime.total_playtime_seconds / 3600
        return {
            "sessions": self.lifetime.total_sessions,
            "playtime_hours": round(hours, 2),
            "total_score": self.lifetime.total_score,
            "total_coins": self.lifetime.total_coins,
            "total_enemies": self.lifetime.total_enemies,
            "avg_score_per_session": (self.lifetime.total_score / max(1, self.lifetime.total_sessions)),
            "completion_rate": self._calculate_completion_rate(),
        }

    def _calculate_completion_rate(self) -> float:
        """Calculate game completion rate."""
        # Would integrate with achievements
        return 0.0

    def reset_all(self) -> None:
        """Reset all statistics."""
        self._start_session()
        self.lifetime = LifetimeStats()
        self.enemies = EnemyStats()
        self.powerups = PowerUpStats()


class StatsDisplay:
    """
    Display for statistics.
    """

    def __init__(self, stats_manager: StatisticsManager) -> None:
        """
        Initialize stats display.

        Args:
            stats_manager: Statistics manager
        """
        self.stats = stats_manager
        self.font: Optional[pg.font.Font] = None
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initialize fonts."""
        try:
            import pygame as pg

            self.font = pg.font.Font(None, 24)
        except (ImportError, pg.error):
            self.font = None

    def draw_session_stats(self, surface: "pg.Surface", position: tuple[int, int] = (10, 100)) -> None:
        """
        Draw session statistics.

        Args:
            surface: Surface to draw to
            position: Position
        """
        if not self.font:
            return

        x, y = position
        lines = [
            ("=== SESSION ===", c.GOLD),
            (f"Time: {self._format_time(self.stats.session.duration_seconds)}", c.WHITE),
            (f"Score: {self.stats.session.score}", c.WHITE),
            (f"Coins: {self.stats.session.coins_collected}", c.GOLD),
            (f"Enemies: {self.stats.session.enemies_defeated}", c.RED),
            (f"Deaths: {self.stats.session.deaths}", c.RED),
        ]

        for i, (text, color) in enumerate(lines):
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, y + i * 25))

    def draw_lifetime_stats(self, surface: "pg.Surface", position: tuple[int, int] = (10, 250)) -> None:
        """
        Draw lifetime statistics.

        Args:
            surface: Surface to draw to
            position: Position
        """
        if not self.font:
            return

        summary = self.stats.get_lifetime_summary()

        x, y = position
        lines = [
            ("=== LIFETIME ===", c.GOLD),
            (f"Sessions: {summary['sessions']}", c.WHITE),
            (f"Playtime: {summary['playtime_hours']}h", c.WHITE),
            (f"Total Coins: {summary['total_coins']}", c.GOLD),
            (f"Total Enemies: {summary['total_enemies']}", c.RED),
            (f"Avg Score: {summary['avg_score_per_session']:.0f}", c.WHITE),
        ]

        for i, (text, color) in enumerate(lines):
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, y + i * 25))

    def _format_time(self, seconds: int) -> str:
        """Format time as HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"


# Import for type hints
try:
    import pygame as pg
except ImportError:
    pg = None  # type: ignore[assignment]
