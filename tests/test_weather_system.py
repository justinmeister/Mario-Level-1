"""
Tests for weather and day/night cycle system.
"""
import random

import pytest
import pygame as pg

from data.weather_system import (
    WeatherType,
    TimeOfDay,
    WeatherConfig,
    TimeConfig,
    Drop,
    Cloud,
    WeatherEffect,
    DayNightCycle,
    WeatherManager,
    SeasonalTheme,
)


class TestWeatherType:
    """Tests for WeatherType enum."""

    def test_weather_types(self) -> None:
        """Test weather type enum values."""
        assert WeatherType.CLEAR.value == "clear"
        assert WeatherType.RAINY.value == "rainy"
        assert WeatherType.SNOWY.value == "snowy"
        assert WeatherType.STORMY.value == "stormy"
        assert WeatherType.CLOUDY.value == "cloudy"
        assert WeatherType.WINDY.value == "windy"


class TestTimeOfDay:
    """Tests for TimeOfDay enum."""

    def test_time_of_day_values(self) -> None:
        """Test time of day enum values."""
        assert TimeOfDay.DAWN.value == "dawn"
        assert TimeOfDay.MORNING.value == "morning"
        assert TimeOfDay.NOON.value == "noon"
        assert TimeOfDay.NIGHT.value == "night"


class TestWeatherConfig:
    """Tests for WeatherConfig."""

    def test_default_config(self) -> None:
        """Test default weather config."""
        config = WeatherConfig()

        assert config.rain_drop_count == 100
        assert config.snowflake_count == 150
        assert config.cloud_count == 10
        assert config.rain_speed == 5.0
        assert config.snow_speed == 2.0

    def test_custom_config(self) -> None:
        """Test custom weather config."""
        config = WeatherConfig(rain_drop_count=200, rain_speed=10.0, rain_color=(50, 50, 100))

        assert config.rain_drop_count == 200
        assert config.rain_speed == 10.0
        assert config.rain_color == (50, 50, 100)


class TestTimeConfig:
    """Tests for TimeConfig."""

    def test_default_time_config(self) -> None:
        """Test default time config."""
        config = TimeConfig()

        assert config.full_cycle_duration == 300
        assert config.start_hour == 8.0
        assert config.time_scale == 60.0
        assert config.enabled is True


class TestDrop:
    """Tests for Drop dataclass."""

    def test_drop_creation(self) -> None:
        """Test creating rain/snow drop."""
        drop = Drop(x=100, y=200, speed=5.0, length=15, width=2)

        assert drop.x == 100
        assert drop.y == 200
        assert drop.speed == 5.0
        assert drop.length == 15
        assert drop.width == 2


class TestCloud:
    """Tests for Cloud dataclass."""

    def test_cloud_creation(self) -> None:
        """Test creating cloud."""
        cloud = Cloud(x=50, y=30, speed=1.0, size=100, opacity=150)

        assert cloud.x == 50
        assert cloud.y == 30
        assert cloud.size == 100
        assert cloud.opacity == 150


class TestWeatherEffect:
    """Tests for WeatherEffect."""

    @pytest.fixture
    def weather_effect(self) -> WeatherEffect:
        """Create weather effect instance."""
        return WeatherEffect(800, 600)

    def test_weather_effect_creation(self, weather_effect: WeatherEffect) -> None:
        """Test weather effect initialization."""
        assert weather_effect.weather_type == WeatherType.CLEAR
        assert weather_effect.intensity == 0.0
        assert len(weather_effect.rain_drops) > 0
        assert len(weather_effect.clouds) > 0

    def test_set_weather(self, weather_effect: WeatherEffect) -> None:
        """Test setting weather type."""
        weather_effect.set_weather(WeatherType.RAINY, 0.8)

        assert weather_effect.weather_type == WeatherType.RAINY
        assert weather_effect.intensity == 0.8

    def test_set_weather_intensity_clamped(self, weather_effect: WeatherEffect) -> None:
        """Test that intensity is clamped to 0-1."""
        weather_effect.set_weather(WeatherType.SNOWY, 1.5)
        assert weather_effect.intensity == 1.0

        weather_effect.set_weather(WeatherType.SNOWY, -0.5)
        assert weather_effect.intensity == 0.0

    def test_update_rain(self, weather_effect: WeatherEffect) -> None:
        """Test rain update."""
        weather_effect.set_weather(WeatherType.RAINY, 1.0)

        initial_y = weather_effect.rain_drops[0].y
        weather_effect.update(100)

        # Rain should fall
        assert weather_effect.rain_drops[0].y > initial_y

    def test_update_snow(self, weather_effect: WeatherEffect) -> None:
        """Test snow update."""
        weather_effect.set_weather(WeatherType.SNOWY, 1.0)

        initial_y = weather_effect.snowflakes[0].y
        weather_effect.update(100)

        # Snow should fall (slower than rain)
        assert weather_effect.snowflakes[0].y > initial_y

    def test_update_clouds(self, weather_effect: WeatherEffect) -> None:
        """Test cloud update."""
        weather_effect.set_weather(WeatherType.CLOUDY, 1.0)

        initial_x = weather_effect.clouds[0].x
        weather_effect.update(100)

        # Clouds should move
        assert weather_effect.clouds[0].x != initial_x

    def test_draw_no_crash(self, weather_effect: WeatherEffect) -> None:
        """Test weather draw doesn't crash."""
        pg.init()
        surface = pg.Surface((800, 600))

        weather_effect.set_weather(WeatherType.RAINY, 1.0)
        weather_effect.update(100)

        # Should not crash
        weather_effect.draw(surface)

        pg.quit()

    def test_clear_weather_no_draw(self, weather_effect: WeatherEffect) -> None:
        """Test that clear weather doesn't draw anything."""
        pg.init()
        surface = pg.Surface((800, 600))

        # Clear weather should not draw
        weather_effect.draw(surface)

        pg.quit()


class TestDayNightCycle:
    """Tests for DayNightCycle."""

    @pytest.fixture
    def day_night(self) -> DayNightCycle:
        """Create day/night cycle instance."""
        return DayNightCycle(800, 600)

    def test_day_night_creation(self, day_night: DayNightCycle) -> None:
        """Test day/night cycle initialization."""
        assert day_night.current_hour == 8.0
        assert day_night.current_time_of_day == TimeOfDay.MORNING
        assert day_night.config.enabled is True

    def test_get_sky_color(self, day_night: DayNightCycle) -> None:
        """Test getting sky color."""
        color = day_night.get_sky_color()
        assert isinstance(color, tuple)
        assert len(color) == 3

    def test_set_hour(self, day_night: DayNightCycle) -> None:
        """Test setting hour."""
        day_night.set_hour(12.0)
        assert day_night.current_hour == 12.0
        assert day_night.current_time_of_day == TimeOfDay.NOON

    def test_set_hour_wraps(self, day_night: DayNightCycle) -> None:
        """Test that hour wraps around 24."""
        day_night.set_hour(25.0)
        assert day_night.current_hour == 1.0

        day_night.set_hour(-1.0)
        assert day_night.current_hour == 23.0

    def test_time_of_day_transitions(self, day_night: DayNightCycle) -> None:
        """Test time of day transitions."""
        # Dawn (4-6)
        day_night.set_hour(5.0)
        assert day_night.current_time_of_day == TimeOfDay.DAWN

        # Noon (10-14)
        day_night.set_hour(12.0)
        assert day_night.current_time_of_day == TimeOfDay.NOON

        # Dusk (17-19)
        day_night.set_hour(18.0)
        assert day_night.current_time_of_day == TimeOfDay.DUSK

        # Night (22-1)
        day_night.set_hour(23.0)
        assert day_night.current_time_of_day == TimeOfDay.MIDNIGHT

    def test_is_daytime(self, day_night: DayNightCycle) -> None:
        """Test daytime check."""
        day_night.set_hour(12.0)
        assert day_night.is_daytime() is True

        day_night.set_hour(23.0)
        assert day_night.is_daytime() is False

    def test_is_nighttime(self, day_night: DayNightCycle) -> None:
        """Test nighttime check."""
        day_night.set_hour(23.0)
        assert day_night.is_nighttime() is True

        day_night.set_hour(12.0)
        assert day_night.is_nighttime() is False

    def test_get_time_display(self, day_night: DayNightCycle) -> None:
        """Test time display format."""
        day_night.set_hour(14.5)  # 14:30
        display = day_night.get_time_display()
        assert display == "14:30"

    def test_update_time(self, day_night: DayNightCycle) -> None:
        """Test time advancement."""
        initial_hour = day_night.current_hour
        day_night.update(10000)  # 10 seconds

        # Time should advance
        assert day_night.current_hour > initial_hour

    def test_update_disabled(self, day_night: DayNightCycle) -> None:
        """Test that disabled cycle doesn't update."""
        day_night.config.enabled = False
        initial_hour = day_night.current_hour

        day_night.update(10000)

        assert day_night.current_hour == initial_hour

    def test_draw_no_crash(self, day_night: DayNightCycle) -> None:
        """Test day/night draw doesn't crash."""
        pg.init()
        surface = pg.Surface((800, 600))

        day_night.update(100)
        day_night.draw(surface)

        pg.quit()

    def test_set_time_scale(self, day_night: DayNightCycle) -> None:
        """Test setting time scale."""
        day_night.set_time_scale(120.0)
        assert day_night.config.time_scale == 120.0


class TestWeatherManager:
    """Tests for WeatherManager."""

    @pytest.fixture
    def weather_manager(self) -> WeatherManager:
        """Create weather manager instance."""
        return WeatherManager(800, 600)

    def test_weather_manager_creation(self, weather_manager: WeatherManager) -> None:
        """Test weather manager initialization."""
        assert weather_manager.weather_enabled is True
        assert weather_manager.day_night_enabled is True

    def test_set_weather(self, weather_manager: WeatherManager) -> None:
        """Test setting weather through manager."""
        weather_manager.set_weather(WeatherType.STORMY, 0.9)

        assert weather_manager.get_current_weather() == WeatherType.STORMY

    def test_set_time(self, weather_manager: WeatherManager) -> None:
        """Test setting time through manager."""
        weather_manager.set_time(15.0)

        assert weather_manager.get_current_time() == TimeOfDay.AFTERNOON

    def test_toggle_weather(self, weather_manager: WeatherManager) -> None:
        """Test toggling weather."""
        initial = weather_manager.weather_enabled
        weather_manager.toggle_weather()
        assert weather_manager.weather_enabled != initial

    def test_toggle_day_night(self, weather_manager: WeatherManager) -> None:
        """Test toggling day/night."""
        initial = weather_manager.day_night_enabled
        weather_manager.toggle_day_night()
        assert weather_manager.day_night_enabled != initial

    def test_update(self, weather_manager: WeatherManager) -> None:
        """Test manager update."""
        # Should not crash
        weather_manager.update(16)

    def test_draw(self, weather_manager: WeatherManager) -> None:
        """Test manager draw."""
        pg.init()
        surface = pg.Surface((800, 600))

        weather_manager.update(16)
        weather_manager.draw(surface)

        pg.quit()

    def test_get_time_display(self, weather_manager: WeatherManager) -> None:
        """Test getting time display."""
        display = weather_manager.get_time_display()
        assert isinstance(display, str)
        assert ":" in display


class TestSeasonalTheme:
    """Tests for SeasonalTheme."""

    @pytest.fixture
    def weather_manager(self) -> WeatherManager:
        """Create weather manager for seasonal theme."""
        return WeatherManager(800, 600)

    def test_seasonal_theme_creation(self, weather_manager: WeatherManager) -> None:
        """Test seasonal theme initialization."""
        theme = SeasonalTheme(weather_manager, "summer")

        assert theme.season == "summer"

    def test_invalid_season_defaults(self, weather_manager: WeatherManager) -> None:
        """Test that invalid season defaults to spring."""
        theme = SeasonalTheme(weather_manager, "invalid")

        assert theme.season == "spring"

    def test_apply_theme(self, weather_manager: WeatherManager) -> None:
        """Test applying seasonal theme."""
        theme = SeasonalTheme(weather_manager, "winter")
        theme.apply_theme()

        # Should set weather
        weather = weather_manager.get_current_weather()
        assert weather in [WeatherType.SNOWY, WeatherType.CLOUDY]

    def test_change_season(self, weather_manager: WeatherManager) -> None:
        """Test changing season."""
        theme = SeasonalTheme(weather_manager, "spring")
        theme.change_season("autumn")

        assert theme.season == "autumn"

    def test_get_season_colors(self, weather_manager: WeatherManager) -> None:
        """Test getting season colors."""
        theme = SeasonalTheme(weather_manager, "summer")
        colors = theme.get_season_colors()

        assert "grass" in colors
        assert "sky" in colors

    def test_all_seasons_exist(self, weather_manager: WeatherManager) -> None:
        """Test that all seasons are defined."""
        for season in ["spring", "summer", "autumn", "winter"]:
            theme = SeasonalTheme(weather_manager, season)
            assert theme.season == season


class TestWeatherIntegration:
    """Integration tests for weather system."""

    def test_full_weather_cycle(self) -> None:
        """Test complete weather cycle."""
        pg.init()

        manager = WeatherManager(800, 600)
        surface = pg.Surface((800, 600))

        # Cycle through weather types
        for weather in WeatherType:
            manager.set_weather(weather, 1.0)
            manager.update(100)
            manager.draw(surface)

        pg.quit()

    def test_day_night_full_cycle(self) -> None:
        """Test full day/night cycle."""
        manager = WeatherManager(800, 600)

        # Test all hours
        for hour in range(24):
            manager.set_time(float(hour))
            manager.update(16)

        # Should complete full cycle
        assert manager.get_current_time() is not None

    def test_seasonal_weather_changes(self) -> None:
        """Test that seasons affect weather."""
        manager = WeatherManager(800, 600)
        theme = SeasonalTheme(manager, "spring")

        # Apply each season
        for season in ["spring", "summer", "autumn", "winter"]:
            theme.change_season(season)
            theme.apply_theme()

            weather = manager.get_current_weather()
            assert weather is not None

    def test_weather_with_time_progression(self) -> None:
        """Test weather system with time passing."""
        pg.init()

        manager = WeatherManager(800, 600)
        surface = pg.Surface((800, 600))

        # Simulate extended gameplay
        for _ in range(100):
            manager.update(100)
            manager.draw(surface)

        # Should still be working
        assert manager.get_current_weather() is not None
        assert manager.get_current_time() is not None

        pg.quit()
