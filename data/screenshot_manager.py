"""
Screenshot System for Super Mario Bros.

Features:
- Automatic screenshot capture
- Custom naming with timestamps
- Metadata embedding
- Screenshot directory management
- Auto-cleanup of old screenshots
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pygame as pg

logger = logging.getLogger(__name__)


@dataclass
class ScreenshotMetadata:
    """Screenshot metadata."""

    filename: str
    timestamp: str
    resolution: tuple[int, int]
    game_state: str
    level: str
    score: int
    coin_total: int
    fps: float
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "timestamp": self.timestamp,
            "resolution": self.resolution,
            "game_state": self.game_state,
            "level": self.level,
            "score": self.score,
            "coin_total": self.coin_total,
            "fps": round(self.fps, 2),
            "notes": self.notes,
        }


class ScreenshotManager:
    """
    Screenshot management system.

    Features:
    - Capture screenshots with F12
    - Automatic naming and organization
    - Metadata tracking
    - Cleanup old screenshots

    Usage:
        screenshot_mgr = ScreenshotManager()

        # In game loop
        if key_pressed(F12):
            screenshot_mgr.capture(screen, game_info)
    """

    def __init__(
        self,
        output_dir: str = "screenshots",
        max_screenshots: int = 100,
        auto_cleanup: bool = True,
    ) -> None:
        """
        Initialize screenshot manager.

        Args:
            output_dir: Directory for screenshots
            max_screenshots: Maximum screenshots to keep
            auto_cleanup: Auto-remove old screenshots
        """
        self.output_dir = output_dir
        self.max_screenshots = max_screenshots
        self.auto_cleanup = auto_cleanup

        self._ensure_output_dir()
        self._metadata_file = os.path.join(self.output_dir, "metadata.json")
        self._metadata: List[Dict[str, Any]] = self._load_metadata()

    def _ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_metadata(self) -> List[Dict[str, Any]]:
        """Load metadata from file."""
        if os.path.exists(self._metadata_file):
            try:
                with open(self._metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def _save_metadata(self) -> None:
        """Save metadata to file."""
        try:
            with open(self._metadata_file, "w", encoding="utf-8") as f:
                json.dump(self._metadata, f, indent=2, ensure_ascii=False)
        except (IOError, OSError):
            pass

    def _generate_filename(self) -> str:
        """Generate unique filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"screenshot_{timestamp}.png"

    def capture(
        self,
        surface: pg.Surface,
        game_info: Optional[Dict[str, Any]] = None,
        notes: str = "",
    ) -> Optional[str]:
        """
        Capture screenshot.

        Args:
            surface: Surface to capture
            game_info: Game state information
            notes: Optional notes

        Returns:
            Filename if successful, None otherwise
        """
        filename = self._generate_filename()
        filepath = os.path.join(self.output_dir, filename)

        try:
            # Save screenshot
            pg.image.save(surface, filepath)

            # Create metadata
            metadata = ScreenshotMetadata(
                filename=filename,
                timestamp=datetime.now().isoformat(),
                resolution=(surface.get_width(), surface.get_height()),
                game_state=game_info.get("level_state", "unknown") if game_info else "unknown",
                level=game_info.get("current_level", "unknown") if game_info else "unknown",
                score=game_info.get("score", 0) if game_info else 0,
                coin_total=game_info.get("coin_total", 0) if game_info else 0,
                fps=game_info.get("fps", 0.0) if game_info else 0.0,
                notes=notes,
            )

            # Save metadata
            self._metadata.append(metadata.to_dict())
            self._save_metadata()

            # Cleanup if needed
            if self.auto_cleanup:
                self._cleanup()

            return filename

        except (pg.error, IOError) as e:
            logger.warning("Screenshot error: %s", e)
            return None

    def _cleanup(self) -> None:
        """Remove old screenshots."""
        if len(self._metadata) <= self.max_screenshots:
            return

        # Sort by timestamp
        sorted_screens = sorted(self._metadata, key=lambda x: x.get("timestamp", ""))

        # Remove oldest
        to_remove = sorted_screens[: len(self._metadata) - self.max_screenshots]
        for screen in to_remove:
            filepath = os.path.join(self.output_dir, screen["filename"])
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except OSError:
                pass

        # Update metadata
        self._metadata = sorted_screens[len(to_remove) :]
        self._save_metadata()

    def get_screenshots(self) -> List[Dict[str, Any]]:
        """Get list of all screenshots with metadata."""
        return self._metadata.copy()

    def get_screenshot_path(self, filename: str) -> str:
        """Get full path for screenshot."""
        return os.path.join(self.output_dir, filename)

    def delete_screenshot(self, filename: str) -> bool:
        """
        Delete screenshot.

        Args:
            filename: Screenshot filename

        Returns:
            True if deleted
        """
        filepath = os.path.join(self.output_dir, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)

            # Remove from metadata
            self._metadata = [m for m in self._metadata if m["filename"] != filename]
            self._save_metadata()

            return True

        except OSError:
            return False

    def clear_all(self) -> int:
        """
        Clear all screenshots.

        Returns:
            Number of screenshots deleted
        """
        count = 0
        for screen in self._metadata:
            filepath = os.path.join(self.output_dir, screen["filename"])
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    count += 1
            except OSError:
                pass

        self._metadata.clear()
        self._save_metadata()

        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get screenshot statistics."""
        if not self._metadata:
            return {
                "count": 0,
                "total_size": 0,
                "oldest": None,
                "newest": None,
            }

        total_size = 0
        for screen in self._metadata:
            filepath = os.path.join(self.output_dir, screen["filename"])
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)

        sorted_screens = sorted(self._metadata, key=lambda x: x.get("timestamp", ""))

        return {
            "count": len(self._metadata),
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "oldest": sorted_screens[0]["timestamp"] if sorted_screens else None,
            "newest": sorted_screens[-1]["timestamp"] if sorted_screens else None,
        }


# Global screenshot manager
_screenshot_manager: Optional[ScreenshotManager] = None


def get_screenshot_manager() -> ScreenshotManager:
    """Get global screenshot manager."""
    global _screenshot_manager
    if _screenshot_manager is None:
        _screenshot_manager = ScreenshotManager()
    return _screenshot_manager


def capture_screenshot(
    surface: pg.Surface,
    game_info: Optional[Dict[str, Any]] = None,
    notes: str = "",
) -> Optional[str]:
    """Capture screenshot using global manager."""
    return get_screenshot_manager().capture(surface, game_info, notes)
