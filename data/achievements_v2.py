"""
Enhanced Achievements System v2 for Super Mario Bros.

Features:
- Achievement categories and rarity
- Achievement chains
- Progress tracking with milestones
- Hidden achievements
- Achievement points
- Visual notifications
- Statistics integration
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame as pg

from . import constants as c


class AchievementRarity(Enum):
    """Achievement rarity levels."""

    COMMON = auto()      # 50%+ players unlock
    UNCOMMON = auto()    # 25-50% players unlock
    RARE = auto()        # 10-25% players unlock
    VERY_RARE = auto()   # 5-10% players unlock
    LEGENDARY = auto()   # 1-5% players unlock
    MYTHIC = auto()      # <1% players unlock


class AchievementCategory(Enum):
    """Achievement categories."""

    COMBAT = auto()         # Enemy defeats
    COLLECTION = auto()     # Collecting items
    EXPLORATION = auto()    # Finding secrets
    PLATFORMING = auto()    # Jumping, movement
    SPEEDRUN = auto()       # Time-based challenges
    SURVIVAL = auto()       # Endurance, no-death runs
    COMBO = auto()          # Combo-based
    BOSS = auto()           # Boss defeats
    SPECIAL = auto()        # Easter eggs, secrets


class AchievementTier(Enum):
    """Achievement tiers for chains."""

    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()
    PLATINUM = auto()
    DIAMOND = auto()


@dataclass
class AchievementReward:
    """Reward for unlocking achievement."""

    coins: int = 0
    xp: int = 0
    points: int = 10  # Achievement points
    unlockables: List[str] = field(default_factory=list)
    title: Optional[str] = None
    skin: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "coins": self.coins,
            "xp": self.xp,
            "points": self.points,
            "unlockables": self.unlockables,
            "title": self.title,
            "skin": self.skin,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AchievementReward":
        """Create from dictionary."""
        return cls(
            coins=data.get("coins", 0),
            xp=data.get("xp", 0),
            points=data.get("points", 10),
            unlockables=data.get("unlockables", []),
            title=data.get("title"),
            skin=data.get("skin"),
        )


@dataclass
class Achievement:
    """Achievement data."""

    id: str
    name: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    tier: AchievementTier = AchievementTier.BRONZE
    reward: AchievementReward = field(default_factory=AchievementReward)

    # Progress tracking
    target: int = 1
    current: int = 0
    milestones: List[int] = field(default_factory=list)  # For partial progress

    # Metadata
    hidden: bool = False
    hidden_description: str = ""
    prerequisites: List[str] = field(default_factory=list)
    chain_id: Optional[str] = None  # For achievement chains
    chain_order: int = 0

    # State
    unlocked: bool = False
    unlocked_at: Optional[float] = None
    progress_percent: float = 0.0

    # Statistics
    global_unlock_rate: float = 0.0  # Percentage of players who unlocked

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.name,
            "rarity": self.rarity.name,
            "tier": self.tier.name,
            "reward": self.reward.to_dict(),
            "target": self.target,
            "current": self.current,
            "milestones": self.milestones,
            "hidden": self.hidden,
            "hidden_description": self.hidden_description,
            "prerequisites": self.prerequisites,
            "chain_id": self.chain_id,
            "chain_order": self.chain_order,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at,
            "progress_percent": self.progress_percent,
            "global_unlock_rate": self.global_unlock_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=AchievementCategory[data["category"]],
            rarity=AchievementRarity[data["rarity"]],
            tier=AchievementTier[data.get("tier", "BRONZE")],
            reward=AchievementReward.from_dict(data.get("reward", {})),
            target=data.get("target", 1),
            current=data.get("current", 0),
            milestones=data.get("milestones", []),
            hidden=data.get("hidden", False),
            hidden_description=data.get("hidden_description", ""),
            prerequisites=data.get("prerequisites", []),
            chain_id=data.get("chain_id"),
            chain_order=data.get("chain_order", 0),
            unlocked=data.get("unlocked", False),
            unlocked_at=data.get("unlocked_at"),
            progress_percent=data.get("progress_percent", 0.0),
            global_unlock_rate=data.get("global_unlock_rate", 0.0),
        )

    @property
    def display_name(self) -> str:
        """Get display name (hidden if not unlocked)."""
        if self.hidden and not self.unlocked:
            return "???"
        return self.name

    @property
    def display_description(self) -> str:
        """Get display description (hidden if not unlocked)."""
        if self.hidden and not self.unlocked:
            return self.hidden_description or "Секретное достижение"
        return self.description

    @property
    def is_complete(self) -> bool:
        """Check if achievement is complete."""
        return self.current >= self.target

    @property
    def progress(self) -> float:
        """Get progress percentage."""
        if self.target <= 0:
            return 100.0
        return min(100.0, (self.current / self.target) * 100)

    def update_progress(self, amount: int = 1) -> bool:
        """
        Update achievement progress.

        Returns:
            True if achievement was unlocked
        """
        if self.unlocked:
            return False

        self.current += amount
        self.progress_percent = self.progress

        if self.is_complete:
            self.unlocked = True
            self.unlocked_at = time.time()
            return True

        return False

    def get_rarity_color(self) -> Tuple[int, int, int]:
        """Get color based on rarity."""
        colors = {
            AchievementRarity.COMMON: (150, 150, 150),
            AchievementRarity.UNCOMMON: (50, 200, 50),
            AchievementRarity.RARE: (50, 100, 255),
            AchievementRarity.VERY_RARE: (150, 50, 255),
            AchievementRarity.LEGENDARY: (255, 200, 50),
            AchievementRarity.MYTHIC: (255, 50, 50),
        }
        return colors.get(self.rarity, c.WHITE)

    def get_tier_color(self) -> Tuple[int, int, int]:
        """Get color based on tier."""
        colors = {
            AchievementTier.BRONZE: (205, 127, 50),
            AchievementTier.SILVER: (192, 192, 192),
            AchievementTier.GOLD: (255, 215, 0),
            AchievementTier.PLATINUM: (224, 224, 224),
            AchievementTier.DIAMOND: (185, 242, 255),
        }
        return colors.get(self.tier, c.WHITE)


class AchievementManager:
    """
    Manages achievements and tracking.

    Features:
    - Unlock tracking
    - Progress monitoring
    - Achievement chains
    - Statistics integration
    - Visual notifications
    """

    # Default achievements
    DEFAULT_ACHIEVEMENTS: List[Dict[str, Any]] = [
        # Combat achievements
        {
            "id": "first_blood",
            "name": "Первая кровь",
            "description": "Победите первого врага",
            "category": "COMBAT",
            "rarity": "COMMON",
            "tier": "BRONZE",
            "target": 1,
            "reward": {"coins": 10, "xp": 20, "points": 5},
        },
        {
            "id": "enemy_slayer",
            "name": "Убийца врагов",
            "description": "Победите 100 врагов",
            "category": "COMBAT",
            "rarity": "UNCOMMON",
            "tier": "SILVER",
            "target": 100,
            "milestones": [10, 25, 50],
            "reward": {"coins": 100, "xp": 200, "points": 20},
        },
        {
            "id": "goomba_stomper",
            "name": "Гумба-топтер",
            "description": "Победите 50 Гумба",
            "category": "COMBAT",
            "rarity": "UNCOMMON",
            "tier": "SILVER",
            "target": 50,
            "reward": {"coins": 75, "xp": 150, "points": 15},
        },
        {
            "id": "boss_hunter",
            "name": "Охотник на боссов",
            "description": "Победите всех боссов",
            "category": "BOSS",
            "rarity": "LEGENDARY",
            "tier": "GOLD",
            "target": 5,
            "hidden": True,
            "hidden_description": "Победите ???",
            "reward": {"coins": 500, "xp": 1000, "points": 100, "unlockables": ["golden_mario"]},
        },
        # Collection achievements
        {
            "id": "coin_collector",
            "name": "Коллекционер монет",
            "description": "Соберите 1000 монет",
            "category": "COLLECTION",
            "rarity": "UNCOMMON",
            "tier": "SILVER",
            "target": 1000,
            "milestones": [100, 250, 500],
            "reward": {"coins": 200, "xp": 300, "points": 25},
        },
        {
            "id": "powerup_master",
            "name": "Мастер усилений",
            "description": "Соберите все типы усилений",
            "category": "COLLECTION",
            "rarity": "RARE",
            "tier": "GOLD",
            "target": 6,
            "hidden": True,
            "reward": {"coins": 300, "xp": 500, "points": 50},
        },
        # Exploration achievements
        {
            "id": "secret_finder",
            "name": "Искатель секретов",
            "description": "Найдите 25 секретов",
            "category": "EXPLORATION",
            "rarity": "RARE",
            "tier": "GOLD",
            "target": 25,
            "milestones": [5, 10, 15],
            "reward": {"coins": 250, "xp": 400, "points": 40},
        },
        {
            "id": "explorer",
            "name": "Исследователь",
            "description": "Исследуйте весь уровень",
            "category": "EXPLORATION",
            "rarity": "UNCOMMON",
            "tier": "BRONZE",
            "target": 1,
            "reward": {"coins": 50, "xp": 100, "points": 10},
        },
        # Platforming achievements
        {
            "id": "high_jumper",
            "name": "Высокий прыжок",
            "description": "Прыгните на максимальную высоту",
            "category": "PLATFORMING",
            "rarity": "COMMON",
            "tier": "BRONZE",
            "target": 1,
            "reward": {"coins": 25, "xp": 50, "points": 5},
        },
        {
            "id": "perfect_landing",
            "name": "Идеальная посадка",
            "description": "Приземлитесь на платформу с точностью до пикселя",
            "category": "PLATFORMING",
            "rarity": "VERY_RARE",
            "tier": "PLATINUM",
            "target": 10,
            "hidden": True,
            "reward": {"coins": 150, "xp": 250, "points": 35},
        },
        # Speedrun achievements
        {
            "id": "speedrunner",
            "name": "Спидраннер",
            "description": "Завершите уровень за 2 минуты",
            "category": "SPEEDRUN",
            "rarity": "VERY_RARE",
            "tier": "GOLD",
            "target": 1,
            "hidden": False,
            "reward": {"coins": 400, "xp": 600, "points": 75},
        },
        {
            "id": "no_death_run",
            "name": "Бессмертный",
            "description": "Завершите уровень без смертей",
            "category": "SURVIVAL",
            "rarity": "LEGENDARY",
            "tier": "DIAMOND",
            "target": 1,
            "reward": {"coins": 1000, "xp": 2000, "points": 200, "title": "Бессмертный"},
        },
        # Combo achievements
        {
            "id": "combo_novice",
            "name": "Комбо-новичок",
            "description": "Достигните комбо x10",
            "category": "COMBO",
            "rarity": "COMMON",
            "tier": "BRONZE",
            "target": 10,
            "reward": {"coins": 30, "xp": 60, "points": 10},
        },
        {
            "id": "combo_master",
            "name": "Комбо-мастер",
            "description": "Достигните комбо x50",
            "category": "COMBO",
            "rarity": "RARE",
            "tier": "GOLD",
            "target": 50,
            "reward": {"coins": 200, "xp": 400, "points": 50},
        },
        {
            "id": "combo_legend",
            "name": "Легенда комбо",
            "description": "Достигните комбо x100",
            "category": "COMBO",
            "rarity": "MYTHIC",
            "tier": "DIAMOND",
            "target": 100,
            "reward": {"coins": 500, "xp": 1000, "points": 150, "skin": "combo_mario"},
        },
        # Special achievements
        {
            "id": "first_steps",
            "name": "Первые шаги",
            "description": "Начните игру",
            "category": "SPECIAL",
            "rarity": "COMMON",
            "tier": "BRONZE",
            "target": 1,
            "reward": {"coins": 10, "xp": 10, "points": 5},
        },
        {
            "id": "dedicated_player",
            "name": "Преданный игрок",
            "description": "Играйте 10 часов",
            "category": "SPECIAL",
            "rarity": "RARE",
            "tier": "GOLD",
            "target": 36000,  # seconds
            "reward": {"coins": 500, "xp": 1000, "points": 100},
        },
    ]

    def __init__(self, save_path: str = "saves/achievements_v2.json") -> None:
        """
        Initialize achievement manager.

        Args:
            save_path: Path to save achievement data
        """
        self.save_path = save_path
        self.achievements: Dict[str, Achievement] = {}
        self.total_points: int = 0
        self.player_stats: Dict[str, Any] = {}

        # Callbacks
        self.on_achievement_unlocked: Optional[Callable[[Achievement], None]] = None
        self.on_milestone_reached: Optional[Callable[[Achievement, int], None]] = None

        # Load achievements
        self._load_achievements()

    def _load_achievements(self) -> None:
        """Load achievements from save file."""
        if not os.path.exists(self.save_path):
            self._initialize_default_achievements()
            self._save_achievements()
            return

        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            for ach_data in data.get("achievements", []):
                achievement = Achievement.from_dict(ach_data)
                self.achievements[achievement.id] = achievement

            self.total_points = data.get("total_points", 0)
            self.player_stats = data.get("player_stats", {})

        except (json.JSONDecodeError, IOError):
            self._initialize_default_achievements()

    def _save_achievements(self) -> None:
        """Save achievements to file."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        data = {
            "achievements": [a.to_dict() for a in self.achievements.values()],
            "total_points": self.total_points,
            "player_stats": self.player_stats,
            "last_updated": time.time(),
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def _initialize_default_achievements(self) -> None:
        """Initialize default achievements."""
        for ach_data in self.DEFAULT_ACHIEVEMENTS:
            achievement = Achievement.from_dict(ach_data)
            self.achievements[achievement.id] = achievement

    def update_progress(self, event_type: str, amount: int = 1, **kwargs: Any) -> List[Achievement]:
        """
        Update achievement progress based on event.

        Args:
            event_type: Type of event
            amount: Amount to add
            **kwargs: Additional event data

        Returns:
            List of newly unlocked achievements
        """
        unlocked = []
        event_mapping = self._get_event_mapping()

        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue

            # Check if event matches achievement
            achievement_events = event_mapping.get(achievement.id, [])
            if event_type not in achievement_events:
                continue

            # Check prerequisites
            if not self._check_prerequisites(achievement):
                continue

            # Update progress
            if achievement.update_progress(amount):
                unlocked.append(achievement)
                self.total_points += achievement.reward.points

                if self.on_achievement_unlocked:
                    self.on_achievement_unlocked(achievement)

            # Check milestones
            elif achievement.milestones:
                for milestone in achievement.milestones:
                    if achievement.current >= milestone > (achievement.current - amount):
                        if self.on_milestone_reached:
                            self.on_milestone_reached(achievement, milestone)

        if unlocked:
            self._save_achievements()

        return unlocked

    def _get_event_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of events to achievements."""
        return {
            "enemy_kill": ["first_blood", "enemy_slayer"],
            "goomba_kill": ["goomba_stomper"],
            "boss_defeat": ["boss_hunter"],
            "coin_collect": ["coin_collector"],
            "powerup_collect": ["powerup_master"],
            "secret_found": ["secret_finder", "explorer"],
            "level_complete": ["explorer", "speedrunner", "no_death_run"],
            "combo": ["combo_novice", "combo_master", "combo_legend"],
            "high_jump": ["high_jumper"],
            "perfect_landing": ["perfect_landing"],
            "play_time": ["dedicated_player"],
            "game_start": ["first_steps"],
        }

    def _check_prerequisites(self, achievement: Achievement) -> bool:
        """Check if prerequisites are met."""
        for prereq_id in achievement.prerequisites:
            if prereq_id not in self.achievements:
                return False
            if not self.achievements[prereq_id].unlocked:
                return False
        return True

    def unlock_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """
        Manually unlock an achievement.

        Args:
            achievement_id: Achievement ID

        Returns:
            Unlocked achievement or None
        """
        if achievement_id not in self.achievements:
            return None

        achievement = self.achievements[achievement_id]

        if achievement.unlocked:
            return None

        achievement.unlocked = True
        achievement.unlocked_at = time.time()
        achievement.progress_percent = 100.0
        self.total_points += achievement.reward.points

        if self.on_achievement_unlocked:
            self.on_achievement_unlocked(achievement)

        self._save_achievements()
        return achievement

    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID."""
        return self.achievements.get(achievement_id)

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]

    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements."""
        return [a for a in self.achievements.values() if not a.unlocked]

    def get_achievements_by_category(self, category: AchievementCategory) -> List[Achievement]:
        """Get achievements by category."""
        return [a for a in self.achievements.values() if a.category == category]

    def get_achievements_by_rarity(self, rarity: AchievementRarity) -> List[Achievement]:
        """Get achievements by rarity."""
        return [a for a in self.achievements.values() if a.rarity == rarity]

    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if not self.achievements:
            return 0.0
        unlocked = len(self.get_unlocked_achievements())
        return (unlocked / len(self.achievements)) * 100

    def get_summary(self) -> Dict[str, Any]:
        """Get achievement summary."""
        unlocked = self.get_unlocked_achievements()

        return {
            "total": len(self.achievements),
            "unlocked": len(unlocked),
            "locked": len(self.achievements) - len(unlocked),
            "completion": self.get_completion_percentage(),
            "total_points": self.total_points,
            "by_category": self._get_category_breakdown(),
            "by_rarity": self._get_rarity_breakdown(),
        }

    def _get_category_breakdown(self) -> Dict[str, int]:
        """Get unlocked count by category."""
        breakdown: Dict[str, int] = {}
        for category in AchievementCategory:
            unlocked = len([a for a in self.get_unlocked_achievements() if a.category == category])
            breakdown[category.name] = unlocked
        return breakdown

    def _get_rarity_breakdown(self) -> Dict[str, int]:
        """Get unlocked count by rarity."""
        breakdown: Dict[str, int] = {}
        for rarity in AchievementRarity:
            unlocked = len([a for a in self.get_unlocked_achievements() if a.rarity == rarity])
            breakdown[rarity.name] = unlocked
        return breakdown

    def draw_notification(self, surface: pg.Surface, achievement: Achievement) -> None:
        """
        Draw achievement unlock notification.

        Args:
            surface: Surface to draw on
            achievement: Unlocked achievement
        """
        # Notification dimensions
        width = 400
        height = 100
        x = (surface.get_width() - width) // 2
        y = 50

        # Background
        bg_rect = pg.Rect(x, y, width, height)
        pg.draw.rect(surface, (20, 20, 40), bg_rect, border_radius=10)

        # Border with rarity color
        border_color = achievement.get_rarity_color()
        pg.draw.rect(surface, border_color, bg_rect, width=3, border_radius=10)

        # Icon
        icon_size = 60
        icon_rect = pg.Rect(x + 20, y + 20, icon_size, icon_size)
        pg.draw.rect(surface, achievement.get_tier_color(), icon_rect, border_radius=8)

        # Trophy symbol
        font_large = pg.font.Font(None, 48)
        trophy_text = "🏆"
        trophy_surf = font_large.render(trophy_text, True, c.GOLD)
        trophy_rect = trophy_surf.get_rect(center=icon_rect.center)
        surface.blit(trophy_surf, trophy_rect)

        # Text
        font_title = pg.font.Font(None, 28)
        font_desc = pg.font.Font(None, 20)

        # Title
        title_text = "Достижение разблокировано!"
        title_surf = font_title.render(title_text, True, c.GOLD)
        surface.blit(title_surf, (x + 100, y + 15))

        # Achievement name
        name_surf = font_title.render(achievement.display_name, True, c.WHITE)
        surface.blit(name_surf, (x + 100, y + 45))

        # Description
        desc_surf = font_desc.render(achievement.display_description, True, c.GRAY)
        surface.blit(desc_surf, (x + 100, y + 70))

        # Points
        points_text = f"+{achievement.reward.points} очков"
        points_surf = font_desc.render(points_text, True, border_color)
        surface.blit(points_surf, (x + width - 100, y + 70))

    def draw(self, surface: pg.Surface, position: Tuple[int, int] = (10, 10)) -> None:
        """
        Draw achievement tracker UI.

        Args:
            surface: Surface to draw on
            position: Top-left position
        """
        x, y = position

        font = pg.font.Font(None, 24)
        small_font = pg.font.Font(None, 18)

        # Draw recent unlocked achievements
        unlocked = sorted(
            self.get_unlocked_achievements(),
            key=lambda a: a.unlocked_at or 0,
            reverse=True,
        )[:3]

        for i, achievement in enumerate(unlocked):
            # Background
            bg_rect = pg.Rect(x, y + i * 70, 350, 65)
            pg.draw.rect(surface, (40, 40, 40), bg_rect)

            # Border with rarity color
            border_color = achievement.get_rarity_color()
            pg.draw.rect(surface, border_color, bg_rect, width=2)

            # Name
            name_surf = font.render(achievement.display_name, True, c.WHITE)
            surface.blit(name_surf, (x + 10, y + i * 70 + 5))

            # Progress or description
            if not achievement.unlocked:
                progress_text = f"{achievement.progress:.0f}%"
                progress_surf = small_font.render(progress_text, True, c.GRAY)
                surface.blit(progress_surf, (x + 10, y + i * 70 + 30))

                # Progress bar
                bar_width = 330
                bar_height = 6
                progress = achievement.progress / 100
                pg.draw.rect(surface, (100, 100, 100), (x + 10, y + i * 70 + 50, bar_width, bar_height))
                pg.draw.rect(surface, border_color, (x + 10, y + i * 70 + 50, int(bar_width * progress), bar_height))
            else:
                desc_surf = small_font.render(achievement.display_description[:50], True, c.GRAY)
                surface.blit(desc_surf, (x + 10, y + i * 70 + 30))

                # Tier icon
                tier_text = achievement.tier.name
                tier_surf = small_font.render(tier_text, True, achievement.get_tier_color())
                surface.blit(tier_surf, (x + 280, y + i * 70 + 30))


# Global achievement manager instance
_achievement_manager: Optional[AchievementManager] = None


def get_achievement_manager() -> AchievementManager:
    """Get global achievement manager instance."""
    global _achievement_manager
    if _achievement_manager is None:
        _achievement_manager = AchievementManager()
    return _achievement_manager
