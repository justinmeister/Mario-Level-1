"""
Quest System for Super Mario Bros.

Features:
- Quest chains and prerequisites
- Multiple quest types
- Quest tracking and progress
- Reward distribution
- Quest categories (main, side, daily)
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


class QuestType(Enum):
    """Quest types."""

    MAIN = auto()  # Main story quests
    SIDE = auto()  # Side quests
    DAILY = auto()  # Daily quests
    WEEKLY = auto()  # Weekly quests
    ACHIEVEMENT = auto()  # Achievement-based
    HIDDEN = auto()  # Hidden/secret quests


class QuestCategory(Enum):
    """Quest categories."""

    COMBAT = auto()
    COLLECTION = auto()
    EXPLORATION = auto()
    PLATFORMING = auto()
    BOSS = auto()
    NPC = auto()
    SPECIAL = auto()


class QuestState(Enum):
    """Quest states."""

    LOCKED = auto()  # Prerequisites not met
    AVAILABLE = auto()  # Can be accepted
    ACTIVE = auto()  # In progress
    COMPLETED = auto()  # Completed, not claimed
    CLAIMED = auto()  # Rewards claimed
    FAILED = auto()  # Failed
    EXPIRED = auto()  # Time limit expired


@dataclass
class QuestObjective:
    """Quest objective."""

    id: str
    description: str
    target_type: str  # enemy, coin, location, etc.
    target_id: Optional[str]
    target_count: int
    current_count: int = 0
    completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "target_count": self.target_count,
            "current_count": self.current_count,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestObjective":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            description=data["description"],
            target_type=data["target_type"],
            target_id=data.get("target_id"),
            target_count=data["target_count"],
            current_count=data.get("current_count", 0),
            completed=data.get("completed", False),
        )

    @property
    def progress(self) -> float:
        """Get objective progress percentage."""
        if self.target_count <= 0:
            return 100.0
        return min(100.0, (self.current_count / self.target_count) * 100)


@dataclass
class QuestReward:
    """Quest reward."""

    coins: int = 0
    xp: int = 0
    items: List[str] = field(default_factory=list)
    unlockables: List[str] = field(default_factory=list)
    stat_bonus: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "coins": self.coins,
            "xp": self.xp,
            "items": self.items,
            "unlockables": self.unlockables,
            "stat_bonus": self.stat_bonus,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestReward":
        """Create from dictionary."""
        return cls(
            coins=data.get("coins", 0),
            xp=data.get("xp", 0),
            items=data.get("items", []),
            unlockables=data.get("unlockables", []),
            stat_bonus=data.get("stat_bonus"),
        )


@dataclass
class Quest:
    """Quest data."""

    id: str
    name: str
    description: str
    quest_type: QuestType
    category: QuestCategory
    objectives: List[QuestObjective]
    reward: QuestReward
    prerequisites: List[str] = field(default_factory=list)
    state: QuestState = QuestState.LOCKED
    time_limit: Optional[float] = None  # milliseconds, None = no limit
    created_at: float = field(default_factory=time.time)
    accepted_at: Optional[float] = None
    completed_at: Optional[float] = None
    npc_giver: Optional[str] = None
    is_repeatable: bool = False
    min_level: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type.name,
            "category": self.category.name,
            "objectives": [o.to_dict() for o in self.objectives],
            "reward": self.reward.to_dict(),
            "prerequisites": self.prerequisites,
            "state": self.state.name,
            "time_limit": self.time_limit,
            "created_at": self.created_at,
            "accepted_at": self.accepted_at,
            "completed_at": self.completed_at,
            "npc_giver": self.npc_giver,
            "is_repeatable": self.is_repeatable,
            "min_level": self.min_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            quest_type=QuestType[data["quest_type"]],
            category=QuestCategory[data["category"]],
            objectives=[QuestObjective.from_dict(o) for o in data.get("objectives", [])],
            reward=QuestReward.from_dict(data.get("reward", {})),
            prerequisites=data.get("prerequisites", []),
            state=QuestState[data.get("state", "LOCKED")],
            time_limit=data.get("time_limit"),
            created_at=data.get("created_at", time.time()),
            accepted_at=data.get("accepted_at"),
            completed_at=data.get("completed_at"),
            npc_giver=data.get("npc_giver"),
            is_repeatable=data.get("is_repeatable", False),
            min_level=data.get("min_level", 1),
        )

    @property
    def is_available(self) -> bool:
        """Check if quest is available to accept."""
        return self.state == QuestState.AVAILABLE

    @property
    def is_active(self) -> bool:
        """Check if quest is active."""
        return self.state == QuestState.ACTIVE

    @property
    def is_completed(self) -> bool:
        """Check if quest is completed."""
        return self.state == QuestState.COMPLETED

    @property
    def all_objectives_complete(self) -> bool:
        """Check if all objectives are complete."""
        return all(obj.completed for obj in self.objectives)

    @property
    def overall_progress(self) -> float:
        """Get overall quest progress."""
        if not self.objectives:
            return 100.0
        return sum(obj.progress for obj in self.objectives) / len(self.objectives)

    def update_objective(self, objective_id: str, amount: int = 1) -> bool:
        """
        Update objective progress.

        Args:
            objective_id: Objective ID
            amount: Amount to add

        Returns:
            True if quest was completed
        """
        for obj in self.objectives:
            if obj.id == objective_id and not obj.completed:
                obj.current_count += amount
                if obj.current_count >= obj.target_count:
                    obj.completed = True
                    obj.current_count = obj.target_count

                # Check if all objectives complete
                if self.all_objectives_complete and self.state == QuestState.ACTIVE:
                    self.state = QuestState.COMPLETED
                    self.completed_at = time.time()
                    return True

        return False


class QuestManager:
    """
    Manages quests and quest progression.

    Features:
    - Quest tracking
    - Prerequisite checking
    - Reward distribution
    - Quest chains
    - Persistence
    """

    # Default quest templates
    DEFAULT_QUESTS: List[Dict[str, Any]] = [
        {
            "id": "first_steps",
            "name": "Первые шаги",
            "description": "Начните своё приключение!",
            "quest_type": "MAIN",
            "category": "PLATFORMING",
            "objectives": [
                {
                    "id": "move",
                    "description": "Пройдите вперёд",
                    "target_type": "distance",
                    "target_id": None,
                    "target_count": 100,
                }
            ],
            "reward": {"coins": 50, "xp": 100},
            "prerequisites": [],
            "min_level": 1,
        },
        {
            "id": "goomba_slayer",
            "name": "Убийца Гумба",
            "description": "Победите врагов в первом уровне",
            "quest_type": "SIDE",
            "category": "COMBAT",
            "objectives": [
                {
                    "id": "kill_goombas",
                    "description": "Победите Гумба",
                    "target_type": "enemy",
                    "target_id": "goomba",
                    "target_count": 10,
                }
            ],
            "reward": {"coins": 100, "xp": 200, "items": ["mushroom"]},
            "prerequisites": ["first_steps"],
            "min_level": 1,
        },
        {
            "id": "coin_collector",
            "name": "Коллекционер монет",
            "description": "Соберите монеты по всему уровню",
            "quest_type": "SIDE",
            "category": "COLLECTION",
            "objectives": [
                {
                    "id": "collect_coins",
                    "description": "Соберите монеты",
                    "target_type": "coin",
                    "target_id": None,
                    "target_count": 50,
                }
            ],
            "reward": {"coins": 150, "xp": 250},
            "prerequisites": [],
            "min_level": 1,
        },
        {
            "id": "daily_warrior",
            "name": "Ежедневный воин",
            "description": "Победите врагов сегодня",
            "quest_type": "DAILY",
            "category": "COMBAT",
            "objectives": [
                {
                    "id": "daily_kills",
                    "description": "Победите врагов",
                    "target_type": "enemy",
                    "target_id": None,
                    "target_count": 20,
                }
            ],
            "reward": {"coins": 80, "xp": 150},
            "prerequisites": [],
            "min_level": 1,
            "time_limit": 86400000,  # 24 hours
            "is_repeatable": True,
        },
        {
            "id": "boss_hunter",
            "name": "Охотник на боссов",
            "description": "Победите босса",
            "quest_type": "MAIN",
            "category": "BOSS",
            "objectives": [
                {
                    "id": "defeat_boss",
                    "description": "Победите босса",
                    "target_type": "boss",
                    "target_id": "bowser",
                    "target_count": 1,
                }
            ],
            "reward": {"coins": 500, "xp": 1000, "unlockables": ["fire_mario"]},
            "prerequisites": ["goomba_slayer", "coin_collector"],
            "min_level": 5,
        },
    ]

    def __init__(self, save_path: str = "saves/quests.json") -> None:
        """
        Initialize quest manager.

        Args:
            save_path: Path to save quest data
        """
        self.save_path = save_path
        self.quests: Dict[str, Quest] = {}
        self.completed_quests: List[str] = []
        self.player_level: int = 1

        # Callbacks
        self.on_quest_accepted: Optional[Callable[[Quest], None]] = None
        self.on_quest_completed: Optional[Callable[[Quest], None]] = None
        self.on_quest_updated: Optional[Callable[[Quest], None]] = None

        # Load quests
        self._load_quests()

    def _load_quests(self) -> None:
        """Load quests from save file."""
        if not os.path.exists(self.save_path):
            self._initialize_default_quests()
            self._save_quests()
            return

        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            for quest_data in data.get("quests", []):
                quest = Quest.from_dict(quest_data)
                self.quests[quest.id] = quest

            self.completed_quests = data.get("completed", [])
            self.player_level = data.get("player_level", 1)

        except (json.JSONDecodeError, IOError):
            self._initialize_default_quests()

    def _save_quests(self) -> None:
        """Save quests to file."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        data = {
            "quests": [q.to_dict() for q in self.quests.values()],
            "completed": self.completed_quests,
            "player_level": self.player_level,
            "last_daily_reset": self._get_last_daily_reset(),
            "last_weekly_reset": self._get_last_weekly_reset(),
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def _initialize_default_quests(self) -> None:
        """Initialize default quests."""
        for quest_data in self.DEFAULT_QUESTS:
            quest = Quest.from_dict(quest_data)

            # Check if player meets requirements
            if self.player_level >= quest.min_level:
                quest.state = QuestState.AVAILABLE
            else:
                quest.state = QuestState.LOCKED

            self.quests[quest.id] = quest

    def _get_last_daily_reset(self) -> float:
        """Get last daily reset timestamp."""
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
                return float(data.get("last_daily_reset", 0))
        except Exception:
            return 0.0

    def _get_last_weekly_reset(self) -> float:
        """Get last weekly reset timestamp."""
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
                return float(data.get("last_weekly_reset", 0))
        except Exception:
            return 0.0

    def accept_quest(self, quest_id: str) -> bool:
        """
        Accept a quest.

        Args:
            quest_id: Quest ID

        Returns:
            True if quest was accepted
        """
        if quest_id not in self.quests:
            return False

        quest = self.quests[quest_id]

        # Check state
        if quest.state != QuestState.AVAILABLE:
            return False

        # Check level
        if self.player_level < quest.min_level:
            return False

        # Accept quest
        quest.state = QuestState.ACTIVE
        quest.accepted_at = time.time()

        if self.on_quest_accepted:
            self.on_quest_accepted(quest)

        self._save_quests()
        return True

    def update_quest_progress(self, event_type: str, target_id: Optional[str] = None, amount: int = 1) -> List[Tuple[str, str]]:
        """
        Update quest progress based on event.

        Args:
            event_type: Type of event (enemy_kill, coin_collect, etc.)
            target_id: Target identifier
            amount: Amount to add

        Returns:
            List of (quest_id, objective_id) tuples that were updated
        """
        updated: List[Tuple[str, str]] = []

        for quest in self.quests.values():
            if quest.state != QuestState.ACTIVE:
                continue

            # Check time limit
            if quest.time_limit and quest.accepted_at:
                elapsed = (time.time() - quest.accepted_at) * 1000
                if elapsed > quest.time_limit:
                    quest.state = QuestState.EXPIRED
                    continue

            # Update matching objectives
            for obj in quest.objectives:
                if obj.completed:
                    continue

                if self._event_matches_objective(event_type, target_id, obj):
                    was_completed = obj.completed
                    if quest.update_objective(obj.id, amount):
                        # Quest completed
                        if self.on_quest_completed:
                            self.on_quest_completed(quest)

                    if not was_completed and obj.completed:
                        updated.append((quest.id, obj.id))

                        if self.on_quest_updated:
                            self.on_quest_updated(quest, obj.id)

        if updated:
            self._save_quests()

        return updated

    def _event_matches_objective(self, event_type: str, target_id: Optional[str], obj: QuestObjective) -> bool:
        """Check if event matches objective."""
        mapping = {
            "enemy_kill": "enemy",
            "boss_defeat": "boss",
            "coin_collect": "coin",
            "powerup_collect": "powerup",
            "distance_traveled": "distance",
            "secret_found": "secret",
            "level_complete": "level",
        }

        event_target = mapping.get(event_type)
        if event_target is None:
            return False

        if obj.target_type != event_target:
            return False

        # Check specific target if required
        if obj.target_id and target_id != obj.target_id:
            return False

        return True

    def claim_reward(self, quest_id: str) -> Optional[QuestReward]:
        """
        Claim quest reward.

        Args:
            quest_id: Quest ID

        Returns:
            Reward or None
        """
        if quest_id not in self.quests:
            return None

        quest = self.quests[quest_id]

        if quest.state != QuestState.COMPLETED:
            return None

        reward = quest.reward

        # Mark as claimed
        quest.state = QuestState.CLAIMED
        self.completed_quests.append(quest_id)

        # Handle repeatable quests
        if quest.is_repeatable:
            self._reset_quest(quest_id)

        self._save_quests()
        return reward

    def _reset_quest(self, quest_id: str) -> None:
        """Reset a repeatable quest."""
        quest = self.quests[quest_id]
        quest.state = QuestState.AVAILABLE
        quest.accepted_at = None
        quest.completed_at = None

        for obj in quest.objectives:
            obj.current_count = 0
            obj.completed = False

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get quest by ID."""
        return self.quests.get(quest_id)

    def get_available_quests(self) -> List[Quest]:
        """Get quests available to accept."""
        return [q for q in self.quests.values() if q.state == QuestState.AVAILABLE]

    def get_active_quests(self) -> List[Quest]:
        """Get active quests."""
        return [q for q in self.quests.values() if q.state == QuestState.ACTIVE]

    def get_completed_quests(self) -> List[Quest]:
        """Get completed quests."""
        return [q for q in self.quests.values() if q.state == QuestState.COMPLETED]

    def get_quests_by_type(self, quest_type: QuestType) -> List[Quest]:
        """Get quests by type."""
        return [q for q in self.quests.values() if q.quest_type == quest_type]

    def get_quests_by_category(self, category: QuestCategory) -> List[Quest]:
        """Get quests by category."""
        return [q for q in self.quests.values() if q.category == category]

    def check_prerequisites(self, quest_id: str) -> bool:
        """Check if prerequisites are met for a quest."""
        if quest_id not in self.quests:
            return False

        quest = self.quests[quest_id]

        # Check level
        if self.player_level < quest.min_level:
            return False

        # Check completed prerequisites
        for prereq_id in quest.prerequisites:
            if prereq_id not in self.completed_quests:
                return False

        return True

    def update_prerequisites(self) -> None:
        """Update quest availability based on prerequisites."""
        for quest in self.quests.values():
            if quest.state == QuestState.LOCKED:
                if self.check_prerequisites(quest.id):
                    quest.state = QuestState.AVAILABLE

    def set_player_level(self, level: int) -> None:
        """Set player level."""
        self.player_level = level
        self.update_prerequisites()
        self._save_quests()

    def get_summary(self) -> Dict[str, Any]:
        """Get quest summary."""
        active = self.get_active_quests()
        available = self.get_available_quests()
        completed = self.get_completed_quests()

        return {
            "total": len(self.quests),
            "active": len(active),
            "available": len(available),
            "completed": len(completed),
            "completed_ids": self.completed_quests,
        }

    def draw(self, surface: pg.Surface, position: Tuple[int, int] = (10, 10)) -> None:
        """Draw quest tracker UI."""
        x, y = position

        font = pg.font.Font(None, 24)
        small_font = pg.font.Font(None, 18)

        # Draw active quests
        active = self.get_active_quests()[:3]  # Show top 3

        for i, quest in enumerate(active):
            # Background
            bg_rect = pg.Rect(x, y + i * 100, 350, 95)
            pg.draw.rect(surface, (40, 40, 40), bg_rect)
            pg.draw.rect(surface, c.GOLD, bg_rect, 2)

            # Quest name
            name_surf = font.render(quest.name, True, c.WHITE)
            surface.blit(name_surf, (x + 8, y + i * 100 + 5))

            # Objectives
            for j, obj in enumerate(quest.objectives[:2]):
                status = "✓" if obj.completed else "○"
                obj_text = f"{status} {obj.description}: {obj.current_count}/{obj.target_count}"
                obj_surf = small_font.render(obj_text, True, c.GRAY)
                surface.blit(obj_surf, (x + 8, y + i * 100 + 30 + j * 20))

            # Progress bar
            bar_width = 340
            bar_height = 6
            progress = quest.overall_progress / 100
            bar_rect = pg.Rect(x + 5, y + i * 100 + 85, bar_width, bar_height)

            pg.draw.rect(surface, (100, 100, 100), bar_rect)
            pg.draw.rect(surface, c.GREEN, (bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_height))


# Global quest manager instance
_quest_manager: Optional[QuestManager] = None


def get_quest_manager() -> QuestManager:
    """Get global quest manager instance."""
    global _quest_manager
    if _quest_manager is None:
        _quest_manager = QuestManager()
    return _quest_manager
