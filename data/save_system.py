"""
Enhanced Save/Load system for game progress.

Features:
- Multiple save slots
- Auto-save functionality
- Save compression
- Save validation
- Backup creation
"""
from __future__ import annotations

import gzip
import json
import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from . import constants as c

# Configuration
SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
MAX_SAVE_SLOTS = 3
AUTO_SAVE_INTERVAL = 300  # seconds (5 minutes)
MAX_BACKUPS = 3


@dataclass
class SaveMetadata:
    """Metadata for a save file."""

    slot: int
    timestamp: str = ""
    score: int = 0
    coin_total: int = 0
    lives: int = 3
    top_score: int = 0
    current_level: str = c.LEVEL1
    play_time: int = 0
    enemies_defeated: int = 0
    blocks_broken: int = 0
    levels_completed: List[str] = field(default_factory=list)
    is_valid: bool = True
    file_size: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SaveMetadata:
        """Create SaveMetadata from dictionary."""
        return cls(
            slot=data.get("slot", 0),
            timestamp=data.get("timestamp", ""),
            score=data.get("score", 0),
            coin_total=data.get("coin_total", 0),
            lives=data.get("lives", 3),
            top_score=data.get("top_score", 0),
            current_level=data.get("current_level", c.LEVEL1),
            play_time=data.get("play_time", 0),
            enemies_defeated=data.get("enemies_defeated", 0),
            blocks_broken=data.get("blocks_broken", 0),
            levels_completed=data.get("levels_completed", []),
            is_valid=data.get("is_valid", True),
            file_size=data.get("file_size", 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert SaveMetadata to dictionary."""
        return {
            "slot": self.slot,
            "timestamp": self.timestamp,
            "score": self.score,
            "coin_total": self.coin_total,
            "lives": self.lives,
            "top_score": self.top_score,
            "current_level": self.current_level,
            "play_time": self.play_time,
            "enemies_defeated": self.enemies_defeated,
            "blocks_broken": self.blocks_broken,
            "levels_completed": self.levels_completed,
            "is_valid": self.is_valid,
            "file_size": self.file_size,
        }


@dataclass
class GameData:
    """Container for game save data."""

    score: int = 0
    coin_total: int = 0
    lives: int = 3
    top_score: int = 0
    current_level: str = c.LEVEL1
    play_time: int = 0
    enemies_defeated: int = 0
    blocks_broken: int = 0
    levels_completed: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    unlocked_skins: List[str] = field(default_factory=list)
    current_skin: str = "default"
    challenges_completed: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert game data to dictionary."""
        return {
            "score": self.score,
            "coin_total": self.coin_total,
            "lives": self.lives,
            "top_score": self.top_score,
            "current_level": self.current_level,
            "play_time": self.play_time,
            "enemies_defeated": self.enemies_defeated,
            "blocks_broken": self.blocks_broken,
            "levels_completed": self.levels_completed,
            "settings": self.settings,
            "unlocked_skins": self.unlocked_skins,
            "current_skin": self.current_skin,
            "challenges_completed": self.challenges_completed,
            "statistics": self.statistics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GameData:
        """Create GameData from dictionary."""
        return cls(
            score=data.get("score", 0),
            coin_total=data.get("coin_total", 0),
            lives=data.get("lives", 3),
            top_score=data.get("top_score", 0),
            current_level=data.get("current_level", c.LEVEL1),
            play_time=data.get("play_time", 0),
            enemies_defeated=data.get("enemies_defeated", 0),
            blocks_broken=data.get("blocks_broken", 0),
            levels_completed=data.get("levels_completed", []),
            settings=data.get("settings", {}),
            unlocked_skins=data.get("unlocked_skins", []),
            current_skin=data.get("current_skin", "default"),
            challenges_completed=data.get("challenges_completed", []),
            statistics=data.get("statistics", {}),
        )


class SaveManager:
    """
    Manager for game save/load operations.

    Features:
    - Multiple save slots
    - Auto-save with configurable interval
    - Save compression
    - Backup creation
    - Save validation
    - Data caching for performance
    """

    def __init__(self) -> None:
        """Initialize save manager."""
        self.save_dir = SAVE_DIR
        self.metadata_file = os.path.join(self.save_dir, "metadata.json")
        self.metadata: Dict[int, SaveMetadata] = {}
        self._last_auto_save: float = 0
        self._auto_save_enabled: bool = True

        # Cache for loaded game data
        self._data_cache: Dict[int, GameData] = {}
        self._metadata_cache_loaded: bool = False

        self._ensure_save_dir()
        self._load_metadata()

    def _ensure_save_dir(self) -> None:
        """Ensure save directory exists."""
        os.makedirs(self.save_dir, exist_ok=True)

    def _load_metadata(self) -> None:
        """Load metadata from file."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.metadata = {int(k): SaveMetadata.from_dict(v) for k, v in data.items()}
                self._metadata_cache_loaded = True
            except (json.JSONDecodeError, IOError):
                self.metadata = {}
                self._metadata_cache_loaded = True
        else:
            self._metadata_cache_loaded = True

    def _save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(
                    {k: v.to_dict() for k, v in self.metadata.items()},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except IOError:
            pass

    def _invalidate_cache(self, slot: Optional[int] = None) -> None:
        """Invalidate cache for slot or all slots."""
        if slot is not None:
            self._data_cache.pop(slot, None)
        else:
            self._data_cache.clear()

    def _get_save_path(self, slot: int, compressed: bool = True) -> str:
        """Get file path for save slot."""
        ext = ".sav.gz" if compressed else ".sav"
        return os.path.join(self.save_dir, f"save_{slot}{ext}")

    def _get_backup_path(self, slot: int, timestamp: str) -> str:
        """Get backup file path."""
        return os.path.join(self.save_dir, f"save_{slot}_backup_{timestamp}.sav.gz")

    def _create_backup(self, slot: int) -> None:
        """Create backup of save slot."""
        save_path = self._get_save_path(slot)
        if os.path.exists(save_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self._get_backup_path(slot, timestamp)

            # Copy save file to backup
            shutil.copy2(save_path, backup_path)

            # Clean old backups
            self._cleanup_old_backups(slot)

    def _cleanup_old_backups(self, slot: int) -> None:
        """Remove old backups, keeping only MAX_BACKUPS most recent."""
        backups = sorted([f for f in os.listdir(self.save_dir) if f.startswith(f"save_{slot}_backup_")])

        while len(backups) > MAX_BACKUPS:
            oldest = backups.pop(0)
            try:
                os.remove(os.path.join(self.save_dir, oldest))
            except OSError:
                pass

    def save_game(
        self,
        slot: int,
        game_data: GameData,
        force: bool = False,
    ) -> bool:
        """
        Save game to slot.

        Args:
            slot: Save slot number (1-based)
            game_data: GameData object to save
            force: Force save even if auto-save is disabled

        Returns:
            True if save successful, False otherwise
        """
        if slot < 1 or slot > MAX_SAVE_SLOTS:
            return False

        try:
            # Create backup if save exists
            if self.save_exists(slot):
                self._create_backup(slot)

            # Save with compression
            save_path = self._get_save_path(slot)
            data_dict = game_data.to_dict()
            data_dict["version"] = "2.7.0"
            data_dict["saved_at"] = datetime.now().isoformat()

            with gzip.open(save_path, "wt", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)

            # Update metadata
            file_size = os.path.getsize(save_path)
            self.metadata[slot] = SaveMetadata(
                slot=slot,
                timestamp=data_dict["saved_at"],
                score=game_data.score,
                coin_total=game_data.coin_total,
                lives=game_data.lives,
                top_score=game_data.top_score,
                current_level=game_data.current_level,
                play_time=game_data.play_time,
                enemies_defeated=game_data.enemies_defeated,
                blocks_broken=game_data.blocks_broken,
                levels_completed=game_data.levels_completed,
                is_valid=True,
                file_size=file_size,
            )
            self._save_metadata()

            # Update cache
            self._data_cache[slot] = game_data

            return True

        except (IOError, OSError, ValueError) as e:
            logger.warning("Save error: %s", e)
            return False

    def load_game(self, slot: int) -> Optional[GameData]:
        """
        Load game from slot.

        Args:
            slot: Save slot number (1-based)

        Returns:
            GameData object if successful, None otherwise
        """
        if slot < 1 or slot > MAX_SAVE_SLOTS:
            return None

        # Check cache first
        if slot in self._data_cache:
            return self._data_cache[slot]

        save_path = self._get_save_path(slot)
        if not os.path.exists(save_path):
            # Try uncompressed version
            save_path = self._get_save_path(slot, compressed=False)
            if not os.path.exists(save_path):
                return None

        try:
            # Try compressed first
            try:
                with gzip.open(save_path, "rt", encoding="utf-8") as f:
                    data = json.load(f)
            except gzip.BadGzipFile:
                # Fall back to uncompressed
                with open(save_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            game_data = GameData.from_dict(data)

            # Cache the loaded data
            self._data_cache[slot] = game_data

            return game_data

        except (IOError, OSError, json.JSONDecodeError, gzip.BadGzipFile) as e:
            logger.warning("Load error: %s", e)
            # Mark save as invalid
            if slot in self.metadata:
                self.metadata[slot].is_valid = False
                self._save_metadata()
            return None

    def delete_save(self, slot: int) -> bool:
        """
        Delete save from slot.

        Args:
            slot: Save slot number (1-based)

        Returns:
            True if deletion successful, False otherwise
        """
        if slot < 1 or slot > MAX_SAVE_SLOTS:
            return False

        try:
            # Delete main save
            for compressed in [True, False]:
                save_path = self._get_save_path(slot, compressed)
                if os.path.exists(save_path):
                    os.remove(save_path)

            # Delete backups
            for f in os.listdir(self.save_dir):
                if f.startswith(f"save_{slot}_backup_"):
                    os.remove(os.path.join(self.save_dir, f))

            # Remove metadata
            if slot in self.metadata:
                del self.metadata[slot]
                self._save_metadata()

            return True

        except OSError:
            return False

    def save_exists(self, slot: int) -> bool:
        """Check if save exists in slot."""
        if slot in self.metadata:
            return os.path.exists(self._get_save_path(slot))
        return False

    def get_metadata(self, slot: int) -> Optional[SaveMetadata]:
        """Get metadata for save slot."""
        return self.metadata.get(slot)

    def get_all_metadata(self) -> Dict[int, SaveMetadata]:
        """Get metadata for all slots."""
        return self.metadata.copy()

    def enable_auto_save(self, enable: bool = True) -> None:
        """Enable or disable auto-save."""
        self._auto_save_enabled = enable

    def try_auto_save(self, slot: int, game_data: GameData) -> bool:
        """
        Try to auto-save if interval has passed.

        Args:
            slot: Save slot number
            game_data: GameData to save

        Returns:
            True if auto-save was performed, False otherwise
        """
        if not self._auto_save_enabled:
            return False

        current_time = time.time()
        if current_time - self._last_auto_save >= AUTO_SAVE_INTERVAL:
            self._last_auto_save = current_time
            return self.save_game(slot, game_data)

        return False

    def clear_cache(self, slot: Optional[int] = None) -> None:
        """
        Clear cached game data.

        Args:
            slot: Specific slot to clear, or None to clear all
        """
        self._invalidate_cache(slot)

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_slots": len(self._data_cache),
            "max_slots": MAX_SAVE_SLOTS,
            "metadata_loaded": 1 if self._metadata_cache_loaded else 0,
        }


# Backwards-compatible API for tests and simple save file usage
# Provide a simple single-file save API alongside the slot-based SaveManager.
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")


# Simple GameSave alias for historical API
class GameSave(GameData):
    pass


def save_game_file(save: GameSave) -> bool:
    """Save a GameSave to the module-level `SAVE_FILE`. Returns True on success."""
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(save.to_dict(), f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def load_game_file() -> Optional["GameSave"]:
    """Load a GameSave from module-level `SAVE_FILE` or return None."""
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        result = GameSave.from_dict(data)
        return result  # type: ignore[return-value]
    except (IOError, OSError, ValueError):
        return None


def delete_save_file() -> bool:
    """Delete the module-level `SAVE_FILE`."""
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        return True
    except OSError:
        return False


def save_exists_file() -> bool:
    """Return True if module-level `SAVE_FILE` exists."""
    return os.path.exists(SAVE_FILE)


# Alias for backwards compatibility
save_exists = save_exists_file


def get_save_info_file() -> Optional[Dict[str, Any]]:
    """Return basic info about the save file (without full load)."""
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        info = {
            "score": data.get("score", 0),
            "coin_total": data.get("coin_total", 0),
            "lives": data.get("lives", 0),
            "timestamp": data.get("saved_at", ""),
        }
        return info
    except (IOError, json.JSONDecodeError):
        return None


# Alias for backwards compatibility
get_save_info = get_save_info_file


def create_save_from_game_info(game_info: Dict[str, Any]) -> GameSave:
    """Create a GameSave from a lightweight game_info mapping."""
    save = GameSave()
    save.score = game_info.get(c.SCORE, 0)
    save.coin_total = game_info.get(c.COIN_TOTAL, 0)
    save.lives = game_info.get(c.LIVES, 3)
    save.top_score = game_info.get(c.TOP_SCORE, 0)
    return save


def update_game_info_from_save(game_info: Dict[str, Any], save: GameSave) -> None:
    """Update a game_info mapping in-place from a GameSave."""
    game_info[c.SCORE] = save.score
    game_info[c.COIN_TOTAL] = save.coin_total
    game_info[c.LIVES] = save.lives
    game_info[c.TOP_SCORE] = save.top_score

    def get_save_summary(self, slot: int) -> str:
        """
        Get human-readable summary of save.

        Args:
            slot: Save slot number

        Returns:
            Summary string or "Empty slot" if no save
        """
        metadata = self.get_metadata(slot)
        if not metadata or not self.save_exists(slot):
            return "Empty slot"

        return (
            f"Score: {metadata.score} | "
            f"Coins: {metadata.coin_total} | "
            f"Lives: {metadata.lives} | "
            f"Level: {metadata.current_level} | "
            f"Time: {metadata.play_time // 60}m"
        )

    def validate_all_saves(self) -> List[int]:
        """
        Validate all save files.

        Returns:
            List of invalid slot numbers
        """
        invalid_slots = []

        for slot in range(1, MAX_SAVE_SLOTS + 1):
            if self.save_exists(slot):
                try:
                    data = self.load_game(slot)
                    if data is None:
                        invalid_slots.append(slot)
                except Exception:
                    invalid_slots.append(slot)

        return invalid_slots


# Global save manager instance
_save_manager: Optional[SaveManager] = None


def get_save_manager() -> SaveManager:
    """Get global save manager instance."""
    global _save_manager
    if _save_manager is None:
        _save_manager = SaveManager()
    return _save_manager


# Backward compatibility functions
def save_game(game_data: GameData, slot: int = 1) -> bool:
    """Save game (backward compatible)."""
    try:
        if SAVE_FILE:
            return save_game_file(game_data)  # type: ignore[arg-type]
    except Exception:
        pass
    return get_save_manager().save_game(slot, game_data)


def load_game(slot: int = 1) -> Optional[GameData]:
    """Load game (backward compatible)."""
    try:
        if SAVE_FILE:
            loaded = load_game_file()
            if loaded is not None:
                return loaded
    except Exception:
        pass
    return get_save_manager().load_game(slot)


def delete_save(slot: int = 1) -> bool:
    """Delete save (backward compatible)."""
    try:
        if SAVE_FILE:
            return delete_save_file()
    except Exception:
        pass
    return get_save_manager().delete_save(slot)
