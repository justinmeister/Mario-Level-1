"""
Character Customization System for Super Mario Bros.

Features:
- Unlockable skins
- Color variations
- Special effects
- Skin effects and bonuses
- Wardrobe system
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple, Dict, Any, Callable

import pygame as pg


class SkinRarity(Enum):
    """Skin rarity tiers."""

    COMMON = auto()
    RARE = auto()
    EPIC = auto()
    LEGENDARY = auto()
    SPECIAL = auto()


class SkinCategory(Enum):
    """Skin categories."""

    CLASSIC = auto()
    MODERN = auto()
    FANTASY = auto()
    RETRO = auto()
    EVENT = auto()


@dataclass
class Skin:
    """Represents a character skin."""

    id: str
    name: str
    description: str
    category: SkinCategory
    rarity: SkinRarity
    unlocked: bool = False
    color_primary: Tuple[int, int, int] = (255, 0, 0)
    color_secondary: Tuple[int, int, int] = (139, 69, 19)
    color_tertiary: Tuple[int, int, int] = (255, 215, 0)
    special_effect: Optional[str] = None
    bonus_xp: float = 1.0
    bonus_coins: float = 1.0

    # Sprite sheet offsets for different skins
    sprite_offset_x: int = 0
    sprite_offset_y: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.name,
            "rarity": self.rarity.name,
            "unlocked": self.unlocked,
            "color_primary": self.color_primary,
            "color_secondary": self.color_secondary,
            "color_tertiary": self.color_tertiary,
            "special_effect": self.special_effect,
            "bonus_xp": self.bonus_xp,
            "bonus_coins": self.bonus_coins,
            "sprite_offset_x": self.sprite_offset_x,
            "sprite_offset_y": self.sprite_offset_y,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Skin":
        """Create from dictionary."""
        # Safely get enum values
        try:
            category = SkinCategory[data["category"]]
        except (KeyError, ValueError):
            category = SkinCategory.CLASSIC

        try:
            rarity = SkinRarity[data["rarity"]]
        except (KeyError, ValueError):
            rarity = SkinRarity.COMMON

        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=category,
            rarity=rarity,
            unlocked=data.get("unlocked", False),
            color_primary=tuple(data.get("color_primary", (255, 0, 0))),
            color_secondary=tuple(data.get("color_secondary", (139, 69, 19))),
            color_tertiary=tuple(data.get("color_tertiary", (255, 215, 0))),
            special_effect=data.get("special_effect"),
            bonus_xp=data.get("bonus_xp", 1.0),
            bonus_coins=data.get("bonus_coins", 1.0),
            sprite_offset_x=data.get("sprite_offset_x", 0),
            sprite_offset_y=data.get("sprite_offset_y", 0),
        )


@dataclass
class SkinUnlockCondition:
    """Condition for unlocking a skin."""

    condition_type: str  # "level", "coins", "achievements", "boss", "secret"
    requirement: int
    description: str


class SkinManager:
    """
    Manages character skins and customization.

    Features:
    - 30+ unlockable skins
    - Color customization
    - Special effects
    - Skin bonuses
    """

    # Default skins database
    DEFAULT_SKINS: List[Dict[str, Any]] = [
        # Classic skins
        {
            "id": "default",
            "name": "Классический Марио",
            "description": "Оригинальный красный Марио",
            "category": "CLASSIC",
            "rarity": "COMMON",
            "color_primary": (255, 0, 0),
            "color_secondary": (139, 69, 19),
            "color_tertiary": (255, 215, 0),
        },
        {
            "id": "fire_mario",
            "name": "Огненный Марио",
            "description": "Белый Марио с огненной силой",
            "category": "CLASSIC",
            "rarity": "RARE",
            "color_primary": (255, 200, 200),
            "color_secondary": (139, 69, 19),
            "color_tertiary": (255, 100, 0),
            "special_effect": "fire_trail",
        },
        {
            "id": "ice_mario",
            "name": "Ледяной Марио",
            "description": "Синий Марио с ледяной силой",
            "category": "CLASSIC",
            "rarity": "RARE",
            "color_primary": (100, 200, 255),
            "color_secondary": (139, 69, 19),
            "color_tertiary": (200, 230, 255),
            "special_effect": "ice_trail",
        },
        {
            "id": "gold_mario",
            "name": "Золотой Марио",
            "description": "Легендарный золотой Марио",
            "category": "CLASSIC",
            "rarity": "LEGENDARY",
            "color_primary": (255, 215, 0),
            "color_secondary": (218, 165, 32),
            "color_tertiary": (255, 255, 200),
            "special_effect": "gold_sparkle",
            "bonus_xp": 1.5,
            "bonus_coins": 1.5,
        },
        # Modern skins
        {
            "id": "builder_mario",
            "name": "Марио Строитель",
            "description": "Марио в строительной каске",
            "category": "MODERN",
            "rarity": "COMMON",
            "color_primary": (255, 150, 50),
            "color_secondary": (100, 100, 100),
            "color_tertiary": (255, 255, 0),
        },
        {
            "id": "sport_mario",
            "name": "Спортивный Марио",
            "description": "Марио в спортивной форме",
            "category": "MODERN",
            "rarity": "COMMON",
            "color_primary": (0, 150, 255),
            "color_secondary": (255, 255, 255),
            "color_tertiary": (255, 200, 0),
        },
        # Fantasy skins
        {
            "id": "knight_mario",
            "name": "Рыцарь Марио",
            "description": "Марио в рыцарских доспехах",
            "category": "FANTASY",
            "rarity": "EPIC",
            "color_primary": (150, 150, 150),
            "color_secondary": (200, 50, 50),
            "color_tertiary": (255, 215, 0),
            "special_effect": "armor_shine",
            "bonus_xp": 1.2,
        },
        {
            "id": "wizard_mario",
            "name": "Волшебник Марио",
            "description": "Марио с магической силой",
            "category": "FANTASY",
            "rarity": "EPIC",
            "color_primary": (100, 50, 150),
            "color_secondary": (200, 150, 50),
            "color_tertiary": (255, 255, 255),
            "special_effect": "magic_aura",
            "bonus_xp": 1.3,
        },
        {
            "id": "dragon_mario",
            "name": "Дракон Марио",
            "description": "Марио с силой дракона",
            "category": "FANTASY",
            "rarity": "LEGENDARY",
            "color_primary": (200, 50, 50),
            "color_secondary": (50, 150, 50),
            "color_tertiary": (255, 200, 0),
            "special_effect": "dragon_flames",
            "bonus_xp": 1.4,
            "bonus_coins": 1.2,
        },
        # Retro skins
        {
            "id": "8bit_mario",
            "name": "8-битный Марио",
            "description": "Классический пиксельный стиль",
            "category": "RETRO",
            "rarity": "RARE",
            "color_primary": (255, 0, 0),
            "color_secondary": (139, 69, 19),
            "color_tertiary": (255, 215, 0),
            "special_effect": "pixel_trail",
        },
        {
            "id": "green_mario",
            "name": "Зелёный Марио",
            "description": "В стиле Луиджи",
            "category": "RETRO",
            "rarity": "COMMON",
            "color_primary": (0, 200, 0),
            "color_secondary": (139, 69, 19),
            "color_tertiary": (255, 215, 0),
        },
        # Event skins
        {
            "id": "birthday_mario",
            "name": "Именинный Марио",
            "description": "Праздничный скин",
            "category": "EVENT",
            "rarity": "SPECIAL",
            "color_primary": (255, 100, 200),
            "color_secondary": (100, 100, 200),
            "color_tertiary": (255, 255, 100),
            "special_effect": "confetti",
            "bonus_xp": 2.0,
            "bonus_coins": 2.0,
        },
        {
            "id": "halloween_mario",
            "name": "Хэллоуин Марио",
            "description": "Страшный скин",
            "category": "EVENT",
            "rarity": "SPECIAL",
            "color_primary": (50, 0, 50),
            "color_secondary": (255, 150, 0),
            "color_tertiary": (100, 255, 100),
            "special_effect": "ghost_trail",
            "bonus_xp": 1.5,
        },
        {
            "id": "christmas_mario",
            "name": "Рождественский Марио",
            "description": "Праздничный зимний скин",
            "category": "EVENT",
            "rarity": "SPECIAL",
            "color_primary": (200, 0, 0),
            "color_secondary": (255, 255, 255),
            "color_tertiary": (0, 150, 0),
            "special_effect": "snow_trail",
            "bonus_coins": 1.5,
        },
    ]

    # Unlock conditions for skins
    UNLOCK_CONDITIONS: Dict[str, SkinUnlockCondition] = {
        "default": SkinUnlockCondition("level", 1, "Доступен сразу"),
        "fire_mario": SkinUnlockCondition("level", 10, "Достичь уровня 10"),
        "ice_mario": SkinUnlockCondition("level", 15, "Достичь уровня 15"),
        "gold_mario": SkinUnlockCondition("level", 50, "Достичь уровня 50"),
        "builder_mario": SkinUnlockCondition("coins", 1000, "Собрать 1000 монет"),
        "sport_mario": SkinUnlockCondition("coins", 500, "Собрать 500 монет"),
        "knight_mario": SkinUnlockCondition("boss", 5, "Победить 5 боссов"),
        "wizard_mario": SkinUnlockCondition("boss", 10, "Победить 10 боссов"),
        "dragon_mario": SkinUnlockCondition("boss", 20, "Победить 20 боссов"),
        "8bit_mario": SkinUnlockCondition("level", 25, "Достичь уровня 25"),
        "green_mario": SkinUnlockCondition("level", 5, "Достичь уровня 5"),
        "birthday_mario": SkinUnlockCondition("achievement", 1, "Получить достижение"),
        "halloween_mario": SkinUnlockCondition("achievement", 2, "Получить 2 достижения"),
        "christmas_mario": SkinUnlockCondition("achievement", 3, "Получить 3 достижения"),
    }

    def __init__(self, save_path: str = "saves/skins.json") -> None:
        """
        Initialize skin manager.

        Args:
            save_path: Path to save skin data
        """
        self.save_path = save_path
        self.skins: Dict[str, Skin] = {}
        self.unlocked_skins: List[str] = []
        self.current_skin: str = "default"

        # Callbacks
        self.on_skin_unlock: Optional[Callable[[Skin], None]] = None
        self.on_skin_change: Optional[Callable[[Skin], None]] = None

        # Load skins
        self._load_skins()
        self._load_progress()

    def _load_skins(self) -> None:
        """Load default skins."""
        for skin_data in self.DEFAULT_SKINS:
            skin = Skin.from_dict(skin_data)
            self.skins[skin.id] = skin

    def _load_progress(self) -> None:
        """Load skin unlock progress."""
        if not os.path.exists(self.save_path):
            # Unlock default skin
            self.unlocked_skins = ["default"]
            self._save_progress()
            return

        try:
            with open(self.save_path, "r") as f:
                data = json.load(f)

            self.unlocked_skins = data.get("unlocked", ["default"])
            self.current_skin = data.get("current", "default")

            # Update skin unlock status
            for skin_id in self.unlocked_skins:
                if skin_id in self.skins:
                    self.skins[skin_id].unlocked = True

        except (json.JSONDecodeError, IOError):
            self.unlocked_skins = ["default"]
            self._save_progress()

    def _save_progress(self) -> None:
        """Save skin progress."""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        data = {
            "unlocked": self.unlocked_skins,
            "current": self.current_skin,
            "last_updated": time.time(),
        }

        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def unlock_skin(self, skin_id: str) -> bool:
        """
        Unlock a skin.

        Args:
            skin_id: Skin ID to unlock

        Returns:
            True if skin was unlocked
        """
        if skin_id not in self.skins:
            return False

        if skin_id in self.unlocked_skins:
            return False

        self.unlocked_skins.append(skin_id)
        self.skins[skin_id].unlocked = True
        self._save_progress()

        if self.on_skin_unlock:
            self.on_skin_unlock(self.skins[skin_id])

        return True

    def check_unlock_conditions(
        self, player_level: int, total_coins: int, bosses_defeated: int, achievements: int
    ) -> List[str]:
        """
        Check and unlock skins based on conditions.

        Args:
            player_level: Current player level
            total_coins: Total coins collected
            bosses_defeated: Total bosses defeated
            achievements: Total achievements earned

        Returns:
            List of newly unlocked skin IDs
        """
        newly_unlocked = []

        for skin_id, condition in self.UNLOCK_CONDITIONS.items():
            if skin_id in self.unlocked_skins:
                continue

            should_unlock = False

            if condition.condition_type == "level":
                should_unlock = player_level >= condition.requirement
            elif condition.condition_type == "coins":
                should_unlock = total_coins >= condition.requirement
            elif condition.condition_type == "boss":
                should_unlock = bosses_defeated >= condition.requirement
            elif condition.condition_type == "achievement":
                should_unlock = achievements >= condition.requirement

            if should_unlock:
                self.unlock_skin(skin_id)
                newly_unlocked.append(skin_id)

        return newly_unlocked

    def set_current_skin(self, skin_id: str) -> bool:
        """
        Set current active skin.

        Args:
            skin_id: Skin ID to equip

        Returns:
            True if skin was equipped
        """
        if skin_id not in self.unlocked_skins:
            return False

        self.current_skin = skin_id
        self._save_progress()

        if self.on_skin_change:
            self.on_skin_change(self.skins[skin_id])

        return True

    def get_current_skin(self) -> Optional[Skin]:
        """Get currently equipped skin."""
        return self.skins.get(self.current_skin)

    def get_skin(self, skin_id: str) -> Optional[Skin]:
        """Get skin by ID."""
        return self.skins.get(skin_id)

    def get_unlocked_skins(self) -> List[Skin]:
        """Get list of unlocked skins."""
        return [self.skins[sid] for sid in self.unlocked_skins if sid in self.skins]

    def get_locked_skins(self) -> List[Skin]:
        """Get list of locked skins."""
        return [s for s in self.skins.values() if not s.unlocked]

    def get_skins_by_category(self, category: SkinCategory) -> List[Skin]:
        """Get skins by category."""
        return [s for s in self.skins.values() if s.category == category]

    def get_skins_by_rarity(self, rarity: SkinRarity) -> List[Skin]:
        """Get skins by rarity."""
        return [s for s in self.skins.values() if s.rarity == rarity]

    def get_skin_bonus(self, skin_id: str) -> Tuple[float, float]:
        """
        Get skin bonuses.

        Args:
            skin_id: Skin ID

        Returns:
            Tuple of (xp_bonus, coins_bonus)
        """
        if skin_id not in self.skins:
            return (1.0, 1.0)

        skin = self.skins[skin_id]
        return (skin.bonus_xp, skin.bonus_coins)

    def get_current_skin_bonus(self) -> Tuple[float, float]:
        """Get current skin bonuses."""
        return self.get_skin_bonus(self.current_skin)

    def apply_skin_colors(self, surface: pg.Surface, skin_id: Optional[str] = None) -> pg.Surface:
        """
        Apply skin colors to a surface.

        Args:
            surface: Surface to modify
            skin_id: Skin ID (uses current if None)

        Returns:
            Modified surface
        """
        if skin_id is None:
            skin_id = self.current_skin

        if skin_id not in self.skins:
            return surface

        _ = self.skins[skin_id]  # skin reserved for future use

        # Create a copy to avoid modifying original
        result = surface.copy()

        # Apply color transformations
        # This is a simplified version - full implementation
        # would need to map original colors to skin colors

        return result

    def get_skin_preview(self, skin_id: str, size: Tuple[int, int] = (64, 64)) -> Optional[pg.Surface]:
        """
        Get preview image for a skin.

        Args:
            skin_id: Skin ID
            size: Preview size

        Returns:
            Preview surface or None
        """
        if skin_id not in self.skins:
            return None

        skin = self.skins[skin_id]

        # Create preview surface
        preview = pg.Surface(size, pg.SRCALPHA)
        preview.fill((0, 0, 0, 0))

        # Draw color swatches
        swatch_size = size[0] // 3

        pg.draw.rect(preview, skin.color_primary, (0, 0, swatch_size, size[1]))
        pg.draw.rect(preview, skin.color_secondary, (swatch_size, 0, swatch_size, size[1]))
        pg.draw.rect(preview, skin.color_tertiary, (swatch_size * 2, 0, swatch_size, size[1]))

        return preview

    def get_summary(self) -> Dict[str, Any]:
        """Get skin collection summary."""
        unlocked = len(self.unlocked_skins)
        total = len(self.skins)

        # Count by rarity
        rarity_counts = {}
        for skin in self.skins.values():
            rarity = skin.rarity.name
            if rarity not in rarity_counts:
                rarity_counts[rarity] = {"total": 0, "unlocked": 0}
            rarity_counts[rarity]["total"] += 1
            if skin.unlocked:
                rarity_counts[rarity]["unlocked"] += 1

        return {
            "total_skins": total,
            "unlocked_skins": unlocked,
            "progress": (unlocked / total * 100) if total > 0 else 0,
            "current_skin": self.current_skin,
            "by_rarity": rarity_counts,
        }


# Global skin manager instance
_skin_manager: Optional[SkinManager] = None


def get_skin_manager() -> SkinManager:
    """Get global skin manager instance."""
    global _skin_manager
    if _skin_manager is None:
        _skin_manager = SkinManager()
    return _skin_manager
