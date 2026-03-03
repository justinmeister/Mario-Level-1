"""
Daily Challenges and Achievements System for Super Mario Bros.

Features:
- Daily challenges
- Weekly challenges
- Seasonal events
- Challenge categories
- Reward system
"""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any, Callable

import pygame as pg

from . import constants as c


class ChallengeType(Enum):
    """Types of challenges."""

    DAILY = auto()
    WEEKLY = auto()
    SEASONAL = auto()
    ACHIEVEMENT = auto()
    PERMANENT = auto()


class ChallengeCategory(Enum):
    """Challenge categories."""

    COMBAT = auto()
    COLLECTION = auto()
    EXPLORATION = auto()
    SKILL = auto()
    SPEEDRUN = auto()
    SPECIAL = auto()


class ChallengeStatus(Enum):
    """Challenge completion status."""

    IN_PROGRESS = auto()
    COMPLETED = auto()
    CLAIMED = auto()
    FAILED = auto()


@dataclass
class Challenge:
    """Represents a challenge."""

    id: str
    name: str
    description: str
    challenge_type: ChallengeType
    category: ChallengeCategory
    target: int  # Target value to reach
    current: int = 0
    reward_coins: int = 0
    reward_xp: int = 0
    reward_item: Optional[str] = None
    status: ChallengeStatus = ChallengeStatus.IN_PROGRESS
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "challenge_type": self.challenge_type.name,
            "category": self.category.name,
            "target": self.target,
            "current": self.current,
            "reward_coins": self.reward_coins,
            "reward_xp": self.reward_xp,
            "reward_item": self.reward_item,
            "status": self.status.name,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Challenge":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            challenge_type=ChallengeType[data["challenge_type"]],
            category=ChallengeCategory[data["category"]],
            target=data["target"],
            current=data.get("current", 0),
            reward_coins=data.get("reward_coins", 0),
            reward_xp=data.get("reward_xp", 0),
            reward_item=data.get("reward_item"),
            status=ChallengeStatus[data.get("status", "IN_PROGRESS")],
            created_at=data.get("created_at", time.time()),
            expires_at=data.get("expires_at"),
            completed_at=data.get("completed_at"),
        )

    @property
    def progress(self) -> float:
        """Get progress percentage."""
        if self.target <= 0:
            return 0.0
        return min(100.0, (self.current / self.target) * 100)

    @property
    def is_expired(self) -> bool:
        """Check if challenge is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def update_progress(self, amount: int = 1) -> bool:
        """
        Update challenge progress.

        Args:
            amount: Amount to add

        Returns:
            True if challenge was completed
        """
        if self.status != ChallengeStatus.IN_PROGRESS:
            return False

        self.current += amount

        if self.current >= self.target:
            self.status = ChallengeStatus.COMPLETED
            self.completed_at = time.time()
            return True

        return False


class ChallengeManager:
    """
    Manages daily and weekly challenges.

    Features:
    - Auto-generating challenges
    - Progress tracking
    - Reward distribution
    - Expiration handling
    """

    # Challenge templates
    DAILY_TEMPLATES: List[Dict[str, Any]] = [
        {
            "name": "Победитель врагов",
            "description": "Победите {target} врагов",
            "category": "COMBAT",
            "target_range": (10, 30),
            "reward_coins_range": (50, 100),
            "reward_xp_range": (20, 50),
        },
        {
            "name": "Сборщик монет",
            "description": "Соберите {target} монет",
            "category": "COLLECTION",
            "target_range": (50, 200),
            "reward_coins_range": (30, 80),
            "reward_xp_range": (15, 40),
        },
        {
            "name": "Комбо мастер",
            "description": "Достигните комбо x{target}",
            "category": "SKILL",
            "target_range": (5, 15),
            "reward_coins_range": (40, 90),
            "reward_xp_range": (25, 60),
        },
        {
            "name": "Исследователь",
            "description": "Найдите {target} секретов",
            "category": "EXPLORATION",
            "target_range": (3, 10),
            "reward_coins_range": (60, 120),
            "reward_xp_range": (30, 70),
        },
        {
            "name": "Победитель боссов",
            "description": "Победите {target} боссов",
            "category": "COMBAT",
            "target_range": (1, 5),
            "reward_coins_range": (100, 300),
            "reward_xp_range": (50, 150),
        },
        {
            "name": "Спидраннер",
            "description": "Завершите {target} уровней",
            "category": "SPEEDRUN",
            "target_range": (3, 10),
            "reward_coins_range": (80, 200),
            "reward_xp_range": (40, 100),
        },
    ]

    WEEKLY_TEMPLATES: List[Dict[str, Any]] = [
        {
            "name": "Недельный воин",
            "description": "Победите {target} врагов за неделю",
            "category": "COMBAT",
            "target_range": (100, 300),
            "reward_coins_range": (300, 600),
            "reward_xp_range": (150, 300),
        },
        {
            "name": "Недельный коллекционер",
            "description": "Соберите {target} монет за неделю",
            "category": "COLLECTION",
            "target_range": (500, 1500),
            "reward_coins_range": (200, 500),
            "reward_xp_range": (100, 250),
        },
        {
            "name": "Недельный чемпион",
            "description": "Завершите {target} уровней без смертей",
            "category": "SKILL",
            "target_range": (5, 15),
            "reward_coins_range": (400, 800),
            "reward_xp_range": (200, 400),
        },
    ]

    def __init__(self, save_path: str = "saves/challenges.json") -> None:
        """
        Initialize challenge manager.

        Args:
            save_path: Path to save challenge data
        """
        self.save_path = save_path
        self.challenges: Dict[str, Challenge] = {}
        self.completed_challenges: List[str] = []

        # Callbacks
        self.on_challenge_completed: Optional[Callable[[Challenge], None]] = None
        self.on_challenge_claimed: Optional[Callable[[Challenge], None]] = None

        # Load or create challenges
        self._load_challenges()

        # Check and regenerate if needed
        self._check_regeneration()

    def _load_challenges(self) -> None:
        """Load challenges from save file."""
        if not os.path.exists(self.save_path):
            self._generate_daily_challenges()
            self._generate_weekly_challenges()
            self._save_challenges()
            return

        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            for chal_data in data.get("challenges", []):
                challenge = Challenge.from_dict(chal_data)
                self.challenges[challenge.id] = chal_data["id"]

            self.completed_challenges = data.get("completed", [])

        except (json.JSONDecodeError, IOError):
            self._generate_daily_challenges()
            self._generate_weekly_challenges()

    def _save_challenges(self) -> None:
        """Save challenges to file."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        data = {
            "challenges": [c.to_dict() for c in self.challenges.values()],
            "completed": self.completed_challenges,
            "last_daily": self._get_last_daily_reset(),
            "last_weekly": self._get_last_weekly_reset(),
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def _check_regeneration(self) -> None:
        """Check if challenges need regeneration."""
        now = time.time()

        # Check daily reset (24 hours)
        last_daily = self._get_last_daily_reset()
        if now - last_daily > 86400:  # 24 hours
            self._regenerate_daily_challenges()

        # Check weekly reset (7 days)
        last_weekly = self._get_last_weekly_reset()
        if now - last_weekly > 604800:  # 7 days
            self._regenerate_weekly_challenges()

    def _get_last_daily_reset(self) -> float:
        """Get last daily reset timestamp."""
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
                return float(data.get("last_daily", time.time()))
        except Exception:
            return time.time()

    def _get_last_weekly_reset(self) -> float:
        """Get last weekly reset timestamp."""
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
                return float(data.get("last_weekly", time.time()))
        except Exception:
            return time.time()

    def _generate_daily_challenges(self) -> List[Challenge]:
        """Generate new daily challenges."""
        challenges = []
        now = time.time()
        expires = now + 86400  # 24 hours

        # Select 3 random templates
        selected = random.sample(self.DAILY_TEMPLATES, min(3, len(self.DAILY_TEMPLATES)))

        for i, template in enumerate(selected):
            target = random.randint(*template["target_range"])
            reward_coins = random.randint(*template["reward_coins_range"])
            reward_xp = random.randint(*template["reward_xp_range"])

            challenge = Challenge(
                id=f"daily_{int(now)}_{i}",
                name=template["name"],
                description=template["description"].format(target=target),
                challenge_type=ChallengeType.DAILY,
                category=ChallengeCategory[template["category"]],
                target=target,
                reward_coins=reward_coins,
                reward_xp=reward_xp,
                created_at=now,
                expires_at=expires,
            )
            challenges.append(challenge)
            self.challenges[challenge.id] = challenge

        return challenges

    def _generate_weekly_challenges(self) -> List[Challenge]:
        """Generate new weekly challenges."""
        challenges = []
        now = time.time()
        expires = now + 604800  # 7 days

        # Select 2 random templates
        selected = random.sample(self.WEEKLY_TEMPLATES, min(2, len(self.WEEKLY_TEMPLATES)))

        for i, template in enumerate(selected):
            target = random.randint(*template["target_range"])
            reward_coins = random.randint(*template["reward_coins_range"])
            reward_xp = random.randint(*template["reward_xp_range"])

            challenge = Challenge(
                id=f"weekly_{int(now)}_{i}",
                name=template["name"],
                description=template["description"].format(target=target),
                challenge_type=ChallengeType.WEEKLY,
                category=ChallengeCategory[template["category"]],
                target=target,
                reward_coins=reward_coins,
                reward_xp=reward_xp,
                created_at=now,
                expires_at=expires,
            )
            challenges.append(challenge)
            self.challenges[challenge.id] = challenge

        return challenges

    def _regenerate_daily_challenges(self) -> None:
        """Regenerate daily challenges."""
        # Remove expired daily challenges
        expired = [cid for cid, c in self.challenges.items() if c.challenge_type == ChallengeType.DAILY]

        for cid in expired:
            del self.challenges[cid]

        # Generate new
        self._generate_daily_challenges()

        # Update timestamp
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
            data["last_daily"] = time.time()
            with open(self.save_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

        self._save_challenges()

    def _regenerate_weekly_challenges(self) -> None:
        """Regenerate weekly challenges."""
        # Remove expired weekly challenges
        expired = [cid for cid, c in self.challenges.items() if c.challenge_type == ChallengeType.WEEKLY]

        for cid in expired:
            del self.challenges[cid]

        # Generate new
        self._generate_weekly_challenges()

        # Update timestamp
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)
            data["last_weekly"] = time.time()
            with open(self.save_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

        self._save_challenges()

    def update_progress(self, event_type: str, amount: int = 1) -> List[Challenge]:
        """
        Update challenge progress based on event.

        Args:
            event_type: Type of event
            amount: Amount to add

        Returns:
            List of completed challenges
        """
        completed = []

        for challenge in self.challenges.values():
            if challenge.status != ChallengeStatus.IN_PROGRESS:
                continue

            if challenge.is_expired:
                continue

            # Check if event matches challenge category
            if self._event_matches_challenge(event_type, challenge):
                if challenge.update_progress(amount):
                    completed.append(challenge)
                    if self.on_challenge_completed:
                        self.on_challenge_completed(challenge)

        if completed:
            self._save_challenges()

        return completed

    def _event_matches_challenge(self, event_type: str, challenge: Challenge) -> bool:
        """Check if event matches challenge category."""
        mapping = {
            "enemy_kill": ChallengeCategory.COMBAT,
            "boss_defeat": ChallengeCategory.COMBAT,
            "coin_collect": ChallengeCategory.COLLECTION,
            "powerup_collect": ChallengeCategory.COLLECTION,
            "secret_found": ChallengeCategory.EXPLORATION,
            "level_complete": ChallengeCategory.SPEEDRUN,
            "combo": ChallengeCategory.SKILL,
        }

        event_category = mapping.get(event_type)
        if event_category is None:
            return False

        return event_category == challenge.category

    def claim_reward(self, challenge_id: str) -> Optional[Tuple[int, int]]:
        """
        Claim challenge reward.

        Args:
            challenge_id: Challenge ID

        Returns:
            Tuple of (coins, xp) or None
        """
        if challenge_id not in self.challenges:
            return None

        challenge = self.challenges[challenge_id]

        if challenge.status != ChallengeStatus.COMPLETED:
            return None

        if challenge.is_expired:
            return None

        # Mark as claimed
        challenge.status = ChallengeStatus.CLAIMED
        self.completed_challenges.append(challenge_id)

        if self.on_challenge_claimed:
            self.on_challenge_claimed(challenge)

        self._save_challenges()

        return (challenge.reward_coins, challenge.reward_xp)

    def get_daily_challenges(self) -> List[Challenge]:
        """Get all daily challenges."""
        return [c for c in self.challenges.values() if c.challenge_type == ChallengeType.DAILY]

    def get_weekly_challenges(self) -> List[Challenge]:
        """Get all weekly challenges."""
        return [c for c in self.challenges.values() if c.challenge_type == ChallengeType.WEEKLY]

    def get_active_challenges(self) -> List[Challenge]:
        """Get all active (in-progress) challenges."""
        return [c for c in self.challenges.values() if c.status == ChallengeStatus.IN_PROGRESS and not c.is_expired]

    def get_completed_challenges(self) -> List[Challenge]:
        """Get all completed challenges."""
        return [c for c in self.challenges.values() if c.status == ChallengeStatus.COMPLETED]

    def get_challenge(self, challenge_id: str) -> Optional[Challenge]:
        """Get challenge by ID."""
        return self.challenges.get(challenge_id)

    def get_summary(self) -> Dict[str, Any]:
        """Get challenge summary."""
        daily = self.get_daily_challenges()
        weekly = self.get_weekly_challenges()
        active = self.get_active_challenges()
        completed = self.get_completed_challenges()

        return {
            "daily": {
                "total": len(daily),
                "completed": sum(1 for c in daily if c.status == ChallengeStatus.COMPLETED),
            },
            "weekly": {
                "total": len(weekly),
                "completed": sum(1 for c in weekly if c.status == ChallengeStatus.COMPLETED),
            },
            "active": len(active),
            "total_completed": len(self.completed_challenges),
            "total_rewards_claimed": sum(c.reward_coins for c in completed if c.status == ChallengeStatus.CLAIMED),
        }

    def draw(self, surface: pg.Surface, position: Tuple[int, int] = (10, 10)) -> None:
        """Draw challenges UI."""
        x, y = position

        font = pg.font.Font(None, 20)
        small_font = pg.font.Font(None, 16)

        # Draw active challenges
        active = self.get_active_challenges()[:3]  # Show top 3

        for i, challenge in enumerate(active):
            # Background
            bg_rect = pg.Rect(x, y + i * 60, 300, 55)
            pg.draw.rect(surface, (40, 40, 40), bg_rect)
            pg.draw.rect(surface, c.GOLD, bg_rect, 1)

            # Name
            name_surf = font.render(challenge.name, True, c.WHITE)
            surface.blit(name_surf, (x + 5, y + i * 60 + 5))

            # Progress
            progress_text = f"{challenge.current}/{challenge.target}"
            progress_surf = small_font.render(progress_text, True, c.GRAY)
            surface.blit(progress_surf, (x + 5, y + i * 60 + 25))

            # Progress bar
            bar_width = 290
            bar_height = 8
            progress_width = int(bar_width * challenge.progress / 100)

            pg.draw.rect(surface, (100, 100, 100), (x + 5, y + i * 60 + 42, bar_width, bar_height))
            pg.draw.rect(surface, c.GREEN, (x + 5, y + i * 60 + 42, progress_width, bar_height))

            # Reward
            reward_surf = small_font.render(f"+{challenge.reward_coins} 💰 +{challenge.reward_xp} XP", True, c.GOLD)
            surface.blit(reward_surf, (x + 150, y + i * 60 + 25))


# Global challenge manager instance
_challenge_manager: Optional[ChallengeManager] = None


def get_challenge_manager() -> ChallengeManager:
    """Get global challenge manager instance."""
    global _challenge_manager
    if _challenge_manager is None:
        _challenge_manager = ChallengeManager()
    return _challenge_manager
