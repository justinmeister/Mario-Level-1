"""
Player Progression System for Super Mario Bros.

Features:
- Player levels and XP
- Skill trees
- Unlockable abilities
- Persistent progression
- Rank system
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any, Callable

logger = logging.getLogger(__name__)


class PlayerRank(Enum):
    """Player rank tiers."""

    NOVICE = auto()  # Level 1-5
    APPRENTICE = auto()  # Level 6-15
    WARRIOR = auto()  # Level 16-30
    VETERAN = auto()  # Level 31-50
    ELITE = auto()  # Level 51-75
    MASTER = auto()  # Level 76-99
    LEGEND = auto()  # Level 100


class SkillType(Enum):
    """Types of skills."""

    PASSIVE = auto()
    ACTIVE = auto()
    STAT_BOOST = auto()


@dataclass
class Skill:
    """Represents a unlockable skill."""

    id: str
    name: str
    description: str
    skill_type: SkillType
    required_level: int
    prerequisites: List[str] = field(default_factory=list)
    unlocked: bool = False
    effect_value: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "skill_type": self.skill_type.name,
            "required_level": self.required_level,
            "prerequisites": self.prerequisites,
            "unlocked": self.unlocked,
            "effect_value": self.effect_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skill":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            skill_type=SkillType[data["skill_type"]],
            required_level=data["required_level"],
            prerequisites=data.get("prerequisites", []),
            unlocked=data.get("unlocked", False),
            effect_value=data.get("effect_value", 1.0),
        )


@dataclass
class PlayerStats:
    """Player statistics."""

    total_xp: int = 0
    level: int = 1
    coins_collected: int = 0
    enemies_defeated: int = 0
    levels_completed: int = 0
    deaths: int = 0
    playtime_seconds: int = 0
    high_score: int = 0
    combos_achieved: int = 0
    bosses_defeated: int = 0
    secrets_found: int = 0
    perfect_runs: int = 0


@dataclass
class PlayerProfile:
    """Player profile with all progression data."""

    username: str = "Player"
    stats: PlayerStats = field(default_factory=PlayerStats)
    skills: Dict[str, Skill] = field(default_factory=dict)
    unlocked_skins: List[str] = field(default_factory=list)
    current_skin: str = "default"
    created_at: float = field(default_factory=time.time)
    last_played: float = field(default_factory=time.time)


class ProgressionManager:
    """
    Manages player progression.

    Features:
    - XP and leveling
    - Skill unlocks
    - Rank system
    - Persistent saves
    """

    # XP required for each level (formula: base * level^2)
    XP_BASE = 100

    # Default skills
    DEFAULT_SKILLS: List[Dict[str, Any]] = [
        {
            "id": "speed_boost",
            "name": "Speed Boost",
            "description": "Увеличивает скорость бега на 10%",
            "skill_type": "PASSIVE",
            "required_level": 5,
            "effect_value": 1.1,
        },
        {
            "id": "jump_boost",
            "name": "Super Jump",
            "description": "Увеличивает высоту прыжка на 15%",
            "skill_type": "PASSIVE",
            "required_level": 10,
            "prerequisites": ["speed_boost"],
            "effect_value": 1.15,
        },
        {
            "id": "coin_magnet",
            "name": "Coin Magnet",
            "description": "Монеты притягиваются с большего расстояния",
            "skill_type": "PASSIVE",
            "required_level": 15,
            "effect_value": 2.0,
        },
        {
            "id": "fire_resistance",
            "name": "Огнестойкость",
            "description": "Снижает урон от огня на 50%",
            "skill_type": "STAT_BOOST",
            "required_level": 20,
            "effect_value": 0.5,
        },
        {
            "id": "combo_master",
            "name": "Комбо Мастер",
            "description": "Комбо множители увеличены на 25%",
            "skill_type": "PASSIVE",
            "required_level": 25,
            "effect_value": 1.25,
        },
        {
            "id": "second_chance",
            "name": "Второй шанс",
            "description": "Шанс выжить после смертельного удара (1 раз за уровень)",
            "skill_type": "ACTIVE",
            "required_level": 30,
            "effect_value": 1.0,
        },
        {
            "id": "treasure_hunter",
            "name": "Охотник за сокровищами",
            "description": "Повышенный шанс нахождения секретов",
            "skill_type": "PASSIVE",
            "required_level": 35,
            "effect_value": 1.5,
        },
        {
            "id": "boss_slayer",
            "name": "Убийца боссов",
            "description": "+20% урона по боссам",
            "skill_type": "STAT_BOOST",
            "required_level": 40,
            "effect_value": 1.2,
        },
    ]

    def __init__(self, save_path: str = "saves/progression.json") -> None:
        """
        Initialize progression manager.

        Args:
            save_path: Path to save progression data
        """
        self.save_path = save_path
        self.profile: Optional[PlayerProfile] = None
        self.skills: Dict[str, Skill] = {}

        # Callbacks
        self.on_level_up: Optional[Callable[[int], None]] = None
        self.on_skill_unlock: Optional[Callable[[Skill], None]] = None
        self.on_rank_up: Optional[Callable[[PlayerRank], None]] = None

        # Load default skills
        self._load_default_skills()

        # Load or create profile
        self._load_or_create_profile()

    def _load_default_skills(self) -> None:
        """Load default skills."""
        for skill_data in self.DEFAULT_SKILLS:
            skill = Skill.from_dict(skill_data)
            self.skills[skill.id] = skill

    def _load_or_create_profile(self) -> None:
        """Load existing profile or create new one."""
        if os.path.exists(self.save_path):
            self._load_profile()
        else:
            self._create_new_profile()

    def _create_new_profile(self) -> None:
        """Create new player profile."""
        self.profile = PlayerProfile()
        self._save_profile()

    def _load_profile(self) -> None:
        """Load profile from save file."""
        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            # Parse stats
            stats_data = data.get("stats", {})
            stats = PlayerStats(
                total_xp=stats_data.get("total_xp", 0),
                level=stats_data.get("level", 1),
                coins_collected=stats_data.get("coins_collected", 0),
                enemies_defeated=stats_data.get("enemies_defeated", 0),
                levels_completed=stats_data.get("levels_completed", 0),
                deaths=stats_data.get("deaths", 0),
                playtime_seconds=stats_data.get("playtime_seconds", 0),
                high_score=stats_data.get("high_score", 0),
                combos_achieved=stats_data.get("combos_achieved", 0),
                bosses_defeated=stats_data.get("bosses_defeated", 0),
                secrets_found=stats_data.get("secrets_found", 0),
                perfect_runs=stats_data.get("perfect_runs", 0),
            )

            # Parse skills
            skills = {}
            for skill_id, skill_data in data.get("skills", {}).items():
                skills[skill_id] = Skill.from_dict(skill_data)

            # Create profile
            self.profile = PlayerProfile(
                username=data.get("username", "Player"),
                stats=stats,
                skills=skills,
                unlocked_skins=data.get("unlocked_skins", ["default"]),
                current_skin=data.get("current_skin", "default"),
                created_at=data.get("created_at", time.time()),
                last_played=data.get("last_played", time.time()),
            )

            # Merge with default skills
            for skill_id, skill in self.skills.items():
                if skill_id not in self.profile.skills:
                    self.profile.skills[skill_id] = skill

        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Error loading profile: %s", e)
            self._create_new_profile()

    def _save_profile(self) -> None:
        """Save profile to file."""
        if not self.profile:
            return

        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        data = {
            "username": self.profile.username,
            "stats": {
                "total_xp": self.profile.stats.total_xp,
                "level": self.profile.stats.level,
                "coins_collected": self.profile.stats.coins_collected,
                "enemies_defeated": self.profile.stats.enemies_defeated,
                "levels_completed": self.profile.stats.levels_completed,
                "deaths": self.profile.stats.deaths,
                "playtime_seconds": self.profile.stats.playtime_seconds,
                "high_score": self.profile.stats.high_score,
                "combos_achieved": self.profile.stats.combos_achieved,
                "bosses_defeated": self.profile.stats.bosses_defeated,
                "secrets_found": self.profile.stats.secrets_found,
                "perfect_runs": self.profile.stats.perfect_runs,
            },
            "skills": {skill_id: skill.to_dict() for skill_id, skill in self.profile.skills.items()},
            "unlocked_skins": self.profile.unlocked_skins,
            "current_skin": self.profile.current_skin,
            "created_at": self.profile.created_at,
            "last_played": self.profile.last_played,
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_xp(self, amount: int, reason: str = "") -> bool:
        """
        Add XP to player.

        Args:
            amount: XP amount
            reason: Reason for XP gain

        Returns:
            True if player leveled up
        """
        if not self.profile:
            return False

        # Validate XP amount
        if amount <= 0:
            return False

        self.profile.stats.total_xp += amount
        self.profile.last_played = time.time()

        # Check for level up
        leveled_up = self._check_level_up()

        if leveled_up and self.on_level_up:
            self.on_level_up(self.profile.stats.level)

        self._save_profile()
        return leveled_up

    def _check_level_up(self) -> bool:
        """Check if player should level up."""
        if not self.profile:
            return False

        current_level = self.profile.stats.level
        xp_needed = self._get_xp_for_level(current_level + 1)

        if self.profile.stats.total_xp >= xp_needed:
            self.profile.stats.level += 1

            # Check for rank up
            new_rank = self.get_player_rank()
            old_rank_value = (current_level - 1) // 25
            new_rank_value = (self.profile.stats.level - 1) // 25

            if new_rank_value > old_rank_value and self.on_rank_up:
                self.on_rank_up(new_rank)

            # Check for skill unlocks
            self._check_skill_unlocks()

            return True

        return False

    def _get_xp_for_level(self, level: int) -> int:
        """Get XP required for a level."""
        return int(self.XP_BASE * (level**2))

    def _check_skill_unlocks(self) -> None:
        """Check for newly unlocked skills."""
        if not self.profile:
            return

        for skill in self.skills.values():
            if skill.unlocked:
                continue

            if self.profile.stats.level >= skill.required_level:
                # Check prerequisites
                prereqs_met = all(
                    self.profile.skills.get(p, Skill("", "", "", SkillType.PASSIVE, 0)).unlocked
                    for p in skill.prerequisites
                )

                if prereqs_met or not skill.prerequisites:
                    skill.unlocked = True
                    self.profile.skills[skill.id] = skill

                    if self.on_skill_unlock:
                        self.on_skill_unlock(skill)

    def unlock_skill(self, skill_id: str) -> bool:
        """
        Manually unlock a skill.

        Args:
            skill_id: Skill ID to unlock

        Returns:
            True if skill was unlocked
        """
        if not self.profile or skill_id not in self.skills:
            return False

        skill = self.skills[skill_id]

        # Check level requirement
        if self.profile.stats.level < skill.required_level:
            return False

        # Check prerequisites
        for prereq_id in skill.prerequisites:
            if prereq_id not in self.profile.skills:
                return False
            if not self.profile.skills[prereq_id].unlocked:
                return False

        skill.unlocked = True
        self.profile.skills[skill_id] = skill

        if self.on_skill_unlock:
            self.on_skill_unlock(skill)

        self._save_profile()
        return True

    def get_player_rank(self) -> PlayerRank:
        """Get current player rank."""
        if not self.profile:
            return PlayerRank.NOVICE

        level = self.profile.stats.level

        if level >= 100:
            return PlayerRank.LEGEND
        elif level >= 76:
            return PlayerRank.MASTER
        elif level >= 50:
            return PlayerRank.ELITE
        elif level >= 31:
            return PlayerRank.VETERAN
        elif level >= 16:
            return PlayerRank.WARRIOR
        elif level >= 6:
            return PlayerRank.APPRENTICE
        else:
            return PlayerRank.NOVICE

    def get_xp_progress(self) -> Tuple[int, int, float]:
        """
        Get XP progress for current level.

        Returns:
            Tuple of (current_xp, needed_xp, progress_percentage)
        """
        if not self.profile:
            return (0, 0, 0.0)

        current_level = self.profile.stats.level
        prev_level_xp = self._get_xp_for_level(max(0, current_level - 1))
        next_level_xp = self._get_xp_for_level(current_level + 1)

        current_xp = self.profile.stats.total_xp - prev_level_xp
        needed_xp = next_level_xp - prev_level_xp

        progress = (current_xp / needed_xp * 100) if needed_xp > 0 else 0

        return (int(current_xp), int(needed_xp), progress)

    def add_stat(self, stat_name: str, amount: int = 1) -> None:
        """
        Add to a player statistic.

        Args:
            stat_name: Name of stat to update
            amount: Amount to add
        """
        if not self.profile:
            return

        if hasattr(self.profile.stats, stat_name):
            setattr(self.profile.stats, stat_name, getattr(self.profile.stats, stat_name) + amount)
            self._save_profile()

    def unlock_skin(self, skin_id: str) -> None:
        """Unlock a player skin."""
        if not self.profile:
            return

        if skin_id not in self.profile.unlocked_skins:
            self.profile.unlocked_skins.append(skin_id)
            self._save_profile()

    def set_current_skin(self, skin_id: str) -> bool:
        """
        Set current player skin.

        Args:
            skin_id: Skin ID to equip

        Returns:
            True if skin was equipped
        """
        if not self.profile:
            return False

        if skin_id not in self.profile.unlocked_skins:
            return False

        self.profile.current_skin = skin_id
        self._save_profile()
        return True

    def get_profile(self) -> Optional[PlayerProfile]:
        """Get current player profile."""
        return self.profile

    def get_stats(self) -> Optional[PlayerStats]:
        """Get player statistics."""
        if not self.profile:
            return None
        return self.profile.stats

    def get_skills(self) -> Dict[str, Skill]:
        """Get all skills."""
        return self.skills.copy()

    def get_unlocked_skills(self) -> List[Skill]:
        """Get list of unlocked skills."""
        if not self.profile:
            return []
        return [s for s in self.profile.skills.values() if s.unlocked]

    def get_available_skills(self) -> List[Skill]:
        """Get skills available to unlock."""
        if not self.profile:
            return []

        available = []
        for skill in self.skills.values():
            if skill.unlocked:
                continue

            if self.profile.stats.level >= skill.required_level:
                available.append(skill)

        return available

    def get_skill_effect(self, skill_id: str) -> float:
        """Get effect value of a skill."""
        if not self.profile:
            return 1.0

        if skill_id not in self.profile.skills:
            return 1.0

        skill = self.profile.skills[skill_id]
        return skill.effect_value if skill.unlocked else 1.0

    def reset_progression(self) -> None:
        """Reset all progression (hard reset)."""
        self._create_new_profile()

    def get_summary(self) -> Dict[str, Any]:
        """Get progression summary."""
        if not self.profile:
            return {}

        rank = self.get_player_rank()
        current_xp, needed_xp, progress = self.get_xp_progress()

        return {
            "username": self.profile.username,
            "level": self.profile.stats.level,
            "rank": rank.name,
            "xp": {
                "current": current_xp,
                "needed": needed_xp,
                "progress": progress,
            },
            "total_xp": self.profile.stats.total_xp,
            "unlocked_skills": len(self.get_unlocked_skills()),
            "total_skills": len(self.skills),
            "unlocked_skins": len(self.profile.unlocked_skins),
            "stats": {
                "coins": self.profile.stats.coins_collected,
                "enemies": self.profile.stats.enemies_defeated,
                "levels": self.profile.stats.levels_completed,
                "deaths": self.profile.stats.deaths,
                "high_score": self.profile.stats.high_score,
                "bosses": self.profile.stats.bosses_defeated,
            },
        }


# Global progression manager instance
_progression_manager: Optional[ProgressionManager] = None


def get_progression_manager() -> ProgressionManager:
    """Get global progression manager instance."""
    global _progression_manager
    if _progression_manager is None:
        _progression_manager = ProgressionManager()
    return _progression_manager
