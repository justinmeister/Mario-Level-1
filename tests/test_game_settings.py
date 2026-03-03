"""
Tests for game settings system.
"""
import json
import tempfile
from pathlib import Path

import pytest
import pygame as pg

from data.game_settings import (
    Difficulty,
    DifficultyConfig,
    VideoSettings,
    AudioSettings,
    ControlSettings,
    GameSettings,
    SettingsManager,
    SettingsUI,
)


class TestDifficulty:
    """Tests for Difficulty enum."""

    def test_difficulty_values(self) -> None:
        """Test difficulty enum values."""
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.NORMAL.value == "normal"
        assert Difficulty.HARD.value == "hard"
        assert Difficulty.EXTREME.value == "extreme"


class TestDifficultyConfig:
    """Tests for DifficultyConfig."""

    def test_easy_config(self) -> None:
        """Test easy difficulty configuration."""
        config = DifficultyConfig.easy()

        assert config.enemy_speed_multiplier < 1.0
        assert config.player_lives > 3
        assert config.invincibility_time > 1000
        assert config.level_time_limit > 400

    def test_normal_config(self) -> None:
        """Test normal difficulty configuration."""
        config = DifficultyConfig.normal()

        assert config.enemy_speed_multiplier == 1.0
        assert config.player_lives == 3
        assert config.level_time_limit == 400

    def test_hard_config(self) -> None:
        """Test hard difficulty configuration."""
        config = DifficultyConfig.hard()

        assert config.enemy_speed_multiplier > 1.0
        assert config.player_lives < 3
        assert config.enemy_damage > 1
        assert config.level_time_limit < 400

    def test_extreme_config(self) -> None:
        """Test extreme difficulty configuration."""
        config = DifficultyConfig.extreme()

        assert config.enemy_speed_multiplier == 1.5
        assert config.player_lives == 1
        assert config.enemy_damage == 3
        assert config.level_time_limit == 200

    def test_difficulty_progression(self) -> None:
        """Test that difficulty increases progressively."""
        easy = DifficultyConfig.easy()
        normal = DifficultyConfig.normal()
        hard = DifficultyConfig.hard()

        # Enemy speed should increase
        assert easy.enemy_speed_multiplier < normal.enemy_speed_multiplier
        assert normal.enemy_speed_multiplier < hard.enemy_speed_multiplier

        # Player lives should decrease
        assert easy.player_lives > normal.player_lives
        assert normal.player_lives > hard.player_lives


class TestVideoSettings:
    """Tests for VideoSettings."""

    def test_default_video_settings(self) -> None:
        """Test default video settings."""
        video = VideoSettings()

        assert video.screen_width == 800
        assert video.screen_height == 600
        assert video.fullscreen is False
        assert video.vsync is True
        assert video.fps_limit == 60

    def test_apply_video_settings(self) -> None:
        """Test applying video settings."""
        video = VideoSettings(screen_width=1024, screen_height=768)
        result = video.apply()

        assert result == (1024, 768)

    def test_custom_video_settings(self) -> None:
        """Test custom video settings."""
        video = VideoSettings(
            screen_width=1920,
            screen_height=1080,
            fullscreen=True,
            fps_limit=144,
        )

        assert video.screen_width == 1920
        assert video.screen_height == 1080
        assert video.fullscreen is True
        assert video.fps_limit == 144


class TestAudioSettings:
    """Tests for AudioSettings."""

    def test_default_audio_settings(self) -> None:
        """Test default audio settings."""
        audio = AudioSettings()

        assert audio.master_volume == 0.7
        assert audio.music_volume == 0.5
        assert audio.sfx_volume == 0.7
        assert audio.mute is False

    def test_get_music_volume(self) -> None:
        """Test music volume calculation."""
        audio = AudioSettings(master_volume=0.8, music_volume=0.5)

        expected = 0.8 * 0.5
        assert audio.get_music_volume() == expected

    def test_get_sfx_volume(self) -> None:
        """Test SFX volume calculation."""
        audio = AudioSettings(master_volume=0.8, sfx_volume=0.7)

        expected = 0.8 * 0.7
        assert audio.get_sfx_volume() == expected

    def test_mute_audio(self) -> None:
        """Test muting audio."""
        audio = AudioSettings(master_volume=0.8, music_volume=0.5)
        assert audio.get_music_volume() > 0

        audio.mute = True
        assert audio.get_music_volume() == 0.0
        assert audio.get_sfx_volume() == 0.0

    def test_disabled_audio(self) -> None:
        """Test disabled audio."""
        audio = AudioSettings(audio_enabled=False)

        assert audio.get_music_volume() == 0.0
        assert audio.get_sfx_volume() == 0.0


class TestControlSettings:
    """Tests for ControlSettings."""

    def test_default_controls(self) -> None:
        """Test default control bindings."""
        controls = ControlSettings()

        assert controls.move_left == pg.K_LEFT
        assert controls.move_right == pg.K_RIGHT
        assert controls.jump == pg.K_a
        assert controls.action == pg.K_s

    def test_get_bindings(self) -> None:
        """Test getting bindings as dictionary."""
        controls = ControlSettings()
        bindings = controls.get_bindings()

        assert "left" in bindings
        assert "right" in bindings
        assert "jump" in bindings
        assert "action" in bindings

    def test_wasd_controls(self) -> None:
        """Test WASD control scheme."""
        controls = ControlSettings.wasd()

        assert controls.move_left == pg.K_a
        assert controls.move_right == pg.K_d
        assert controls.move_up == pg.K_w
        assert controls.move_down == pg.K_s


class TestGameSettings:
    """Tests for GameSettings."""

    def test_default_game_settings(self) -> None:
        """Test default game settings."""
        settings = GameSettings()

        assert settings.difficulty == Difficulty.NORMAL
        assert isinstance(settings.video, VideoSettings)
        assert isinstance(settings.audio, AudioSettings)
        assert isinstance(settings.controls, ControlSettings)
        assert settings.auto_save is True

    def test_get_difficulty_config(self) -> None:
        """Test getting difficulty configuration."""
        settings = GameSettings()

        config = settings.get_difficulty_config()
        assert isinstance(config, DifficultyConfig)

    def test_set_difficulty(self) -> None:
        """Test setting difficulty."""
        settings = GameSettings()
        assert settings.difficulty == Difficulty.NORMAL

        settings.set_difficulty(Difficulty.HARD)
        assert settings.difficulty == Difficulty.HARD

    def test_cycle_difficulty(self) -> None:
        """Test cycling difficulty."""
        settings = GameSettings()

        # NORMAL -> HARD
        result = settings.cycle_difficulty()
        assert result == Difficulty.HARD

        # HARD -> EXTREME
        result = settings.cycle_difficulty()
        assert result == Difficulty.EXTREME

        # EXTREME -> EASY
        result = settings.cycle_difficulty()
        assert result == Difficulty.EASY

        # EASY -> NORMAL
        result = settings.cycle_difficulty()
        assert result == Difficulty.NORMAL

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        settings = GameSettings()
        settings.set_difficulty(Difficulty.HARD)
        settings.video.screen_width = 1024

        data = settings.to_dict()

        assert data["difficulty"] == "hard"
        assert data["video"]["screen_width"] == 1024
        assert data["auto_save"] is True

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "difficulty": "hard",
            "video": {"screen_width": 1920, "screen_height": 1080},
            "audio": {"master_volume": 0.5},
            "controls": {},
            "auto_save": False,
        }

        settings = GameSettings.from_dict(data)

        assert settings.difficulty == Difficulty.HARD
        assert settings.video.screen_width == 1920
        assert settings.audio.master_volume == 0.5
        assert settings.auto_save is False

    def test_from_dict_invalid_difficulty(self) -> None:
        """Test deserialization with invalid difficulty."""
        data = {
            "difficulty": "invalid",
            "video": {},
            "audio": {},
            "controls": {},
        }

        settings = GameSettings.from_dict(data)

        # Should default to NORMAL
        assert settings.difficulty == Difficulty.NORMAL


class TestSettingsManager:
    """Tests for SettingsManager."""

    @pytest.fixture
    def temp_settings_path(self) -> str:
        """Create temporary settings file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield str(Path(tmpdir) / "settings.json")

    @pytest.fixture
    def settings_manager(self, temp_settings_path: str) -> SettingsManager:
        """Create settings manager with temp file."""
        return SettingsManager(save_path=temp_settings_path)

    def test_init_creates_default_settings(self, settings_manager: SettingsManager) -> None:
        """Test initialization creates default settings."""
        settings = settings_manager.get_settings()
        assert settings.difficulty == Difficulty.NORMAL

    def test_save_and_load_settings(self, settings_manager: SettingsManager, temp_settings_path: str) -> None:
        """Test saving and loading settings."""
        # Modify settings
        settings = settings_manager.get_settings()
        settings.set_difficulty(Difficulty.HARD)
        settings.video.screen_width = 1920

        # Save
        assert settings_manager.save() is True

        # Load in new manager
        new_manager = SettingsManager(save_path=temp_settings_path)
        new_settings = new_manager.get_settings()

        assert new_settings.difficulty == Difficulty.HARD
        assert new_settings.video.screen_width == 1920

    def test_reset_to_defaults(self, settings_manager: SettingsManager) -> None:
        """Test resetting settings to defaults."""
        settings = settings_manager.get_settings()
        settings.set_difficulty(Difficulty.EXTREME)

        settings_manager.reset_to_defaults()
        settings = settings_manager.get_settings()

        assert settings.difficulty == Difficulty.NORMAL

    def test_backup_and_restore(self, settings_manager: SettingsManager) -> None:
        """Test backing up and restoring settings."""
        # Backup current (NORMAL)
        settings_manager.backup_settings()

        # Change settings
        settings = settings_manager.get_settings()
        settings.set_difficulty(Difficulty.EXTREME)

        # Restore
        settings_manager.restore_backup()
        settings = settings_manager.get_settings()

        assert settings.difficulty == Difficulty.NORMAL

    def test_get_difficulty_display(self, settings_manager: SettingsManager) -> None:
        """Test getting difficulty display name."""
        settings = settings_manager.get_settings()

        settings.set_difficulty(Difficulty.EASY)
        assert settings_manager.get_difficulty_display() == "Легко"

        settings.set_difficulty(Difficulty.NORMAL)
        assert settings_manager.get_difficulty_display() == "Нормально"

        settings.set_difficulty(Difficulty.HARD)
        assert settings_manager.get_difficulty_display() == "Сложно"

    def test_get_difficulty_color(self, settings_manager: SettingsManager) -> None:
        """Test getting difficulty color."""
        settings = settings_manager.get_settings()

        settings.set_difficulty(Difficulty.EASY)
        assert settings_manager.get_difficulty_color() is not None

        settings.set_difficulty(Difficulty.HARD)
        assert settings_manager.get_difficulty_color() is not None


class TestSettingsUI:
    """Tests for SettingsUI."""

    @pytest.fixture
    def settings_manager(self) -> SettingsManager:
        """Create settings manager."""
        return SettingsManager()

    @pytest.fixture
    def settings_ui(self, settings_manager: SettingsManager) -> SettingsUI:
        """Create settings UI."""
        return SettingsUI(settings_manager)

    def test_ui_creation(self, settings_ui: SettingsUI, settings_manager: SettingsManager) -> None:
        """Test UI creation."""
        assert settings_ui.settings_mgr == settings_manager
        assert len(settings_ui.options) > 0

    def test_navigation(self, settings_ui: SettingsUI) -> None:
        """Test menu navigation."""
        initial = settings_ui.selected_option

        settings_ui.navigate_down()
        assert settings_ui.selected_option == (initial + 1) % len(settings_ui.options)

        settings_ui.navigate_up()
        assert settings_ui.selected_option == initial

    def test_select_option(self, settings_ui: SettingsUI) -> None:
        """Test selecting option."""
        settings_ui.selected_option = 0
        selected = settings_ui.select_option()
        assert selected == settings_ui.options[0]

    def test_get_option_value(self, settings_ui: SettingsUI, settings_manager: SettingsManager) -> None:
        """Test getting option value."""
        settings = settings_manager.get_settings()
        settings.set_difficulty(Difficulty.HARD)

        value = settings_ui._get_option_value("Сложность")
        assert value == "Сложно"

    def test_draw_methods_no_crash(self, settings_ui: SettingsUI) -> None:
        """Test that draw methods don't crash without pygame init."""
        # These should handle uninitialized fonts gracefully
        import pygame as pg

        pg.init()

        surface = pg.Surface((800, 600))

        # Should not crash
        settings_ui.draw_settings_menu(surface)
        settings_ui.draw_difficulty_selector(surface)

        pg.quit()


class TestSettingsIntegration:
    """Integration tests for settings system."""

    def test_full_settings_lifecycle(self) -> None:
        """Test complete settings lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            settings_path = str(Path(tmpdir) / "settings.json")

            # Create and modify
            manager = SettingsManager(save_path=settings_path)
            settings = manager.get_settings()
            settings.set_difficulty(Difficulty.EXTREME)
            settings.video.fullscreen = True
            settings.audio.master_volume = 0.9

            # Save
            manager.save()

            # Load in new instance
            new_manager = SettingsManager(save_path=settings_path)
            new_settings = new_manager.get_settings()

            # Verify all changes persisted
            assert new_settings.difficulty == Difficulty.EXTREME
            assert new_settings.video.fullscreen is True
            assert new_settings.audio.master_volume == 0.9

    def test_difficulty_affects_gameplay(self) -> None:
        """Test that difficulty affects gameplay parameters."""
        settings = GameSettings()

        # Get configs for different difficulties
        easy_config = DifficultyConfig.easy()
        hard_config = DifficultyConfig.hard()

        # Verify differences
        assert easy_config.player_lives > hard_config.player_lives
        assert easy_config.enemy_speed_multiplier < hard_config.enemy_speed_multiplier
        assert easy_config.invincibility_time > hard_config.invincibility_time
