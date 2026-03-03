"""
Game settings and difficulty system for Super Mario Bros.

Provides:
- Difficulty levels (Easy, Normal, Hard)
- Game settings (audio, video, controls)
- Settings persistence
- Runtime settings adjustment
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import pygame as pg

from . import constants as c

logger = logging.getLogger(__name__)


class Difficulty(Enum):
    """Game difficulty levels."""

    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    EXTREME = "extreme"


@dataclass
class DifficultyConfig:
    """Configuration for a specific difficulty level."""

    # Enemy behavior
    enemy_speed_multiplier: float = 1.0
    enemy_damage: int = 1
    enemy_health: int = 1
    enemy_spawn_rate: float = 1.0

    # Player behavior
    player_speed: float = 1.0
    player_jump_force: float = 1.0
    player_health: int = 1
    player_lives: int = 3

    # Game mechanics
    powerup_duration: float = 1.0  # Duration multiplier
    invincibility_time: int = 1000  # ms after hit
    combo_window: int = 3000  # ms

    # Scoring
    score_multiplier: float = 1.0
    coin_bonus: float = 1.0

    # Time
    level_time_limit: int = 400  # seconds

    @classmethod
    def easy(cls) -> "DifficultyConfig":
        """Easy difficulty settings."""
        return cls(
            enemy_speed_multiplier=0.7,
            enemy_damage=1,
            enemy_health=1,
            enemy_spawn_rate=0.8,
            player_speed=1.2,
            player_jump_force=1.1,
            player_health=3,
            player_lives=5,
            invincibility_time=2000,
            combo_window=4000,
            score_multiplier=1.2,
            coin_bonus=1.5,
            level_time_limit=600,
        )

    @classmethod
    def normal(cls) -> "DifficultyConfig":
        """Normal difficulty settings (default)."""
        return cls(
            enemy_speed_multiplier=1.0,
            enemy_damage=1,
            enemy_health=1,
            enemy_spawn_rate=1.0,
            player_speed=1.0,
            player_jump_force=1.0,
            player_health=1,
            player_lives=3,
            invincibility_time=1000,
            combo_window=3000,
            score_multiplier=1.0,
            coin_bonus=1.0,
            level_time_limit=400,
        )

    @classmethod
    def hard(cls) -> "DifficultyConfig":
        """Hard difficulty settings."""
        return cls(
            enemy_speed_multiplier=1.3,
            enemy_damage=2,
            enemy_health=2,
            enemy_spawn_rate=1.2,
            player_speed=0.9,
            player_jump_force=0.95,
            player_health=1,
            player_lives=2,
            invincibility_time=500,
            combo_window=2500,
            score_multiplier=1.5,
            coin_bonus=0.8,
            level_time_limit=300,
        )

    @classmethod
    def extreme(cls) -> "DifficultyConfig":
        """Extreme difficulty (for experts)."""
        return cls(
            enemy_speed_multiplier=1.5,
            enemy_damage=3,
            enemy_health=3,
            enemy_spawn_rate=1.5,
            player_speed=0.8,
            player_jump_force=0.9,
            player_health=1,
            player_lives=1,
            invincibility_time=300,
            combo_window=2000,
            score_multiplier=2.0,
            coin_bonus=0.5,
            level_time_limit=200,
        )


@dataclass
class VideoSettings:
    """Video/graphical settings."""

    screen_width: int = 800
    screen_height: int = 600
    fullscreen: bool = False
    vsync: bool = True
    fps_limit: int = 60
    show_fps: bool = False
    particle_effects: bool = True
    parallax_background: bool = True
    screen_shake: bool = True
    frame_skip: bool = False

    def apply(self) -> tuple[int, int]:
        """
        Apply video settings and return screen size.

        Returns:
            (width, height) tuple
        """
        return (self.screen_width, self.screen_height)


@dataclass
class AudioSettings:
    """Audio settings."""

    master_volume: float = 0.7
    music_volume: float = 0.5
    sfx_volume: float = 0.7
    mute: bool = False
    audio_enabled: bool = True

    def get_music_volume(self) -> float:
        """Get effective music volume."""
        if self.mute or not self.audio_enabled:
            return 0.0
        return self.master_volume * self.music_volume

    def get_sfx_volume(self) -> float:
        """Get effective SFX volume."""
        if self.mute or not self.audio_enabled:
            return 0.0
        return self.master_volume * self.sfx_volume


@dataclass
class ControlSettings:
    """Control key bindings."""

    move_left: int = pg.K_LEFT
    move_right: int = pg.K_RIGHT
    move_up: int = pg.K_UP
    move_down: int = pg.K_DOWN
    jump: int = pg.K_a
    action: int = pg.K_s
    pause: int = pg.K_ESCAPE
    toggle_fps: int = pg.K_F5
    quick_save: int = pg.K_F9
    quick_load: int = pg.K_F10

    def get_bindings(self) -> Dict[str, int]:
        """Get key bindings as dictionary."""
        return {
            "left": self.move_left,
            "right": self.move_right,
            "up": self.move_up,
            "down": self.move_down,
            "jump": self.jump,
            "action": self.action,
            "pause": self.pause,
            "toggle_fps": self.toggle_fps,
            "quick_save": self.quick_save,
            "quick_load": self.quick_load,
        }

    @classmethod
    def wasd(cls) -> "ControlSettings":
        """WASD control scheme."""
        return cls(
            move_left=pg.K_a,
            move_right=pg.K_d,
            move_up=pg.K_w,
            move_down=pg.K_s,
            jump=pg.K_SPACE,
            action=pg.K_LSHIFT,
        )


@dataclass
class GameSettings:
    """
    Complete game settings container.

    Usage:
        settings = GameSettings()
        settings.load()
        settings.difficulty = Difficulty.HARD
        settings.save()
    """

    difficulty: Difficulty = Difficulty.NORMAL
    video: VideoSettings = field(default_factory=VideoSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    controls: ControlSettings = field(default_factory=ControlSettings)

    # Gameplay options
    auto_save: bool = True
    auto_save_interval: int = 30  # seconds
    show_hints: bool = True
    skip_intro: bool = False

    # Statistics
    total_playtime: int = 0  # seconds
    games_played: int = 0
    games_won: int = 0

    def get_difficulty_config(self) -> DifficultyConfig:
        """Get configuration for current difficulty."""
        configs = {
            Difficulty.EASY: DifficultyConfig.easy(),
            Difficulty.NORMAL: DifficultyConfig.normal(),
            Difficulty.HARD: DifficultyConfig.hard(),
            Difficulty.EXTREME: DifficultyConfig.extreme(),
        }
        return configs.get(self.difficulty, DifficultyConfig.normal())

    def set_difficulty(self, difficulty: Difficulty) -> None:
        """
        Set difficulty level.

        Args:
            difficulty: New difficulty level
        """
        self.difficulty = difficulty

    def cycle_difficulty(self) -> Difficulty:
        """
        Cycle to next difficulty.

        Returns:
            New difficulty
        """
        difficulties = list(Difficulty)
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.difficulty = difficulties[next_index]
        return self.difficulty

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for JSON serialization."""
        return {
            "difficulty": self.difficulty.value,
            "video": asdict(self.video),
            "audio": asdict(self.audio),
            "controls": asdict(self.controls),
            "auto_save": self.auto_save,
            "auto_save_interval": self.auto_save_interval,
            "show_hints": self.show_hints,
            "skip_intro": self.skip_intro,
            "total_playtime": self.total_playtime,
            "games_played": self.games_played,
            "games_won": self.games_won,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameSettings":
        """Create GameSettings from dictionary."""
        settings = cls()

        if "difficulty" in data:
            try:
                settings.difficulty = Difficulty(data["difficulty"])
            except ValueError:
                settings.difficulty = Difficulty.NORMAL

        if "video" in data:
            video_data = data["video"]
            settings.video = VideoSettings(**video_data)

        if "audio" in data:
            audio_data = data["audio"]
            settings.audio = AudioSettings(**audio_data)

        if "controls" in data:
            controls_data = data["controls"]
            settings.controls = ControlSettings(**controls_data)

        for key in [
            "auto_save",
            "auto_save_interval",
            "show_hints",
            "skip_intro",
            "total_playtime",
            "games_played",
            "games_won",
        ]:
            if key in data:
                setattr(settings, key, data[key])

        return settings


class SettingsManager:
    """
    Manages game settings with persistence.

    Usage:
        settings_mgr = SettingsManager()
        settings = settings_mgr.get_settings()
        settings.set_difficulty(Difficulty.HARD)
        settings_mgr.save()
    """

    DEFAULT_SAVE_PATH = "saves/settings.json"

    def __init__(self, save_path: Optional[str] = None) -> None:
        """
        Initialize settings manager.

        Args:
            save_path: Path to settings file (uses default if None)
        """
        self.save_path = Path(save_path) if save_path else Path(self.DEFAULT_SAVE_PATH)
        self.settings = GameSettings()
        self._original_settings: Optional[GameSettings] = None

        # Create save directory
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing settings
        self.load()

    def get_settings(self) -> GameSettings:
        """Get current settings."""
        return self.settings

    def save(self) -> bool:
        """
        Save settings to file.

        Returns:
            True if save was successful
        """
        try:
            data = self.settings.to_dict()
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logger.warning("Could not save settings: %s", e)
            return False

    def load(self) -> bool:
        """
        Load settings from file.

        Returns:
            True if load was successful
        """
        if not self.save_path.exists():
            return False

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.settings = GameSettings.from_dict(data)
            return True
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Could not load settings: %s", e)
            return False

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = GameSettings()

    def backup_settings(self) -> None:
        """Create backup of current settings."""
        self._original_settings = GameSettings.from_dict(self.settings.to_dict())

    def restore_backup(self) -> None:
        """Restore settings from backup."""
        if self._original_settings:
            self.settings = self._original_settings

    def apply_video_settings(self) -> tuple[int, int]:
        """
        Apply current video settings.

        Returns:
            (width, height) tuple
        """
        return self.settings.video.apply()

    def apply_audio_settings(self) -> None:
        """Apply current audio settings to pygame mixer."""
        if pg.mixer.get_init():
            _ = self.settings.audio.get_music_volume()  # music_vol reserved
            _ = self.settings.audio.get_sfx_volume()  # sfx_vol reserved
            # Note: Actual volume application depends on audio system

    def get_difficulty_display(self) -> str:
        """
        Get display name for current difficulty.

        Returns:
            Localized difficulty name
        """
        names = {
            Difficulty.EASY: "Легко",
            Difficulty.NORMAL: "Нормально",
            Difficulty.HARD: "Сложно",
            Difficulty.EXTREME: "Экстрим",
        }
        return names.get(self.settings.difficulty, "Нормально")

    def get_difficulty_color(self) -> tuple[int, int, int]:
        """
        Get color for current difficulty.

        Returns:
            RGB color tuple
        """
        colors = {
            Difficulty.EASY: c.GREEN,
            Difficulty.NORMAL: c.SKY_BLUE,
            Difficulty.HARD: c.ORANGE,
            Difficulty.EXTREME: c.RED,
        }
        return colors.get(self.settings.difficulty, c.WHITE)


class SettingsUI:
    """
    UI for settings menu.
    """

    def __init__(self, settings_manager: SettingsManager) -> None:
        """
        Initialize settings UI.

        Args:
            settings_manager: Settings manager instance
        """
        self.settings_mgr = settings_manager
        self.font_large: Optional[pg.font.Font] = None
        self.font_medium: Optional[pg.font.Font] = None
        self.font_small: Optional[pg.font.Font] = None
        self._init_fonts()

        # Menu state
        self.selected_option: int = 0
        self.options: List[str] = [
            "Сложность",
            "Видео",
            "Аудио",
            "Управление",
            "Сохранить",
            "По умолчанию",
            "Назад",
        ]

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

    def draw_settings_menu(self, surface: pg.Surface, position: tuple[int, int] = (100, 50)) -> None:
        """
        Draw settings menu.

        Args:
            surface: Surface to draw to
            position: (x, y) position
        """
        x, y = position
        _ = self.settings_mgr.get_settings()  # settings reserved

        if self.font_large:
            # Title
            title = "НАСТРОЙКИ"
            title_surface = self.font_large.render(title, True, c.WHITE)
            surface.blit(title_surface, (x + 100, y))

        if self.font_medium:
            # Draw options
            option_y = y + 80
            for i, option in enumerate(self.options):
                color = c.GOLD if i == self.selected_option else c.WHITE
                is_selected = i == self.selected_option

                # Draw option name
                prefix = "► " if is_selected else ""
                text = f"{prefix}{option}"
                text_surface = self.font_medium.render(text, True, color)
                surface.blit(text_surface, (x, option_y))

                # Draw current value
                value = self._get_option_value(option)
                value_surface = self.font_medium.render(value, True, c.GRAY)
                surface.blit(value_surface, (x + 300, option_y))

                option_y += 40

    def _get_option_value(self, option: str) -> str:
        """
        Get current value string for option.

        Args:
            option: Option name

        Returns:
            Value display string
        """
        settings = self.settings_mgr.get_settings()

        if option == "Сложность":
            return self.settings_mgr.get_difficulty_display()
        elif option == "Видео":
            return f"{settings.video.screen_width}x{settings.video.screen_height}"
        elif option == "Аудио":
            vol = int(settings.audio.master_volume * 100)
            return f"{vol}%"
        elif option == "Управление":
            return "Клавиатура"
        elif option == "Сохранить":
            return "Enter"
        elif option == "По умолчанию":
            return "R"
        elif option == "Назад":
            return "Esc"

        return ""

    def draw_difficulty_selector(self, surface: pg.Surface, position: tuple[int, int] = (200, 200)) -> None:
        """
        Draw difficulty selection UI.

        Args:
            surface: Surface to draw to
            position: (x, y) position
        """
        x, y = position
        settings = self.settings_mgr.get_settings()

        if self.font_medium:
            # Draw difficulty options
            difficulties = list(Difficulty)
            for i, diff in enumerate(difficulties):
                is_selected = settings.difficulty == diff
                color = self.settings_mgr.get_difficulty_color() if is_selected else c.GRAY

                diff_name = self.settings_mgr.get_difficulty_display()
                text = f"[{diff_name}]" if is_selected else diff_name
                text_surface = self.font_medium.render(text, True, color)
                surface.blit(text_surface, (x + i * 150, y))

    def navigate_up(self) -> None:
        """Navigate to previous menu option."""
        self.selected_option = (self.selected_option - 1) % len(self.options)

    def navigate_down(self) -> None:
        """Navigate to next menu option."""
        self.selected_option = (self.selected_option + 1) % len(self.options)

    def select_option(self) -> str:
        """
        Select current option.

        Returns:
            Selected option name
        """
        return self.options[self.selected_option]
