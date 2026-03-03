"""
Weather and Day/Night Cycle System for Super Mario Bros.

Provides:
- Dynamic weather effects (rain, snow, clouds)
- Day/night cycle with sky color transitions
- Weather-based gameplay modifiers
- Seasonal themes
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

import pygame as pg

from . import constants as c
from .animation_system import TweenManager, EasingType


class WeatherType(Enum):
    """Types of weather conditions."""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"
    WINDY = "windy"


class TimeOfDay(Enum):
    """Time of day periods."""

    DAWN = "dawn"
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    DUSK = "dusk"
    EVENING = "evening"
    NIGHT = "night"
    MIDNIGHT = "midnight"


@dataclass
class WeatherConfig:
    """Configuration for weather effects."""

    # Rain settings
    rain_drop_count: int = 100
    rain_speed: float = 5.0
    rain_color: tuple[int, int, int] = (100, 150, 200)

    # Snow settings
    snowflake_count: int = 150
    snow_speed: float = 2.0
    snow_color: tuple[int, int, int] = c.WHITE

    # Cloud settings
    cloud_count: int = 10
    cloud_speed: float = 0.5
    cloud_color: tuple[int, int, int] = (220, 220, 220)

    # Wind settings
    wind_strength: float = 0.0
    wind_direction: int = 1  # 1 = right, -1 = left
    wind_speed: float = 1.0

    # Storm settings
    lightning_chance: float = 0.001
    thunder_sound: bool = True


@dataclass
class TimeConfig:
    """Configuration for day/night cycle."""

    # Cycle duration in real seconds
    full_cycle_duration: int = 300  # 5 minutes
    # Start time (0-24 hours)
    start_hour: float = 8.0  # 8 AM
    # Time scale (1 = real-time, 60 = 1 min = 1 hour)
    time_scale: float = 60.0
    # Enable cycle
    enabled: bool = True


@dataclass
class Drop:
    """Rain drop or snowflake."""

    x: float
    y: float
    speed: float
    length: float
    width: float


@dataclass
class Cloud:
    """Cloud particle."""

    x: float
    y: float
    speed: float
    size: float
    opacity: int


class WeatherEffect:
    """
    Weather effect renderer.
    """

    def __init__(self, screen_width: int, screen_height: int, config: Optional[WeatherConfig] = None) -> None:
        """
        Initialize weather effect.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            config: Weather configuration
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config or WeatherConfig()

        self.weather_type = WeatherType.CLEAR
        self.intensity = 0.0  # 0-1

        # Particles
        self.rain_drops: List[Drop] = []
        self.snowflakes: List[Drop] = []
        self.clouds: List[Cloud] = []

        # Lightning
        self.lightning_timer = 0
        self.lightning_alpha: float = 0

        # Wind offset
        self.wind_offset = 0.0

        self._init_particles()

    def _init_particles(self) -> None:
        """Initialize weather particles."""
        # Initialize rain drops
        for _ in range(self.config.rain_drop_count):
            self.rain_drops.append(
                Drop(
                    x=random.randint(0, self.screen_width),
                    y=random.randint(0, self.screen_height),
                    speed=self.config.rain_speed + random.uniform(-1, 1),
                    length=random.randint(10, 20),
                    width=random.randint(1, 2),
                )
            )

        # Initialize snowflakes
        for _ in range(self.config.snowflake_count):
            self.snowflakes.append(
                Drop(
                    x=random.randint(0, self.screen_width),
                    y=random.randint(0, self.screen_height),
                    speed=self.config.snow_speed * 0.5 + random.uniform(-0.5, 0.5),
                    length=random.randint(4, 8),
                    width=random.randint(2, 4),
                )
            )

        # Initialize clouds
        for _ in range(self.config.cloud_count):
            self.clouds.append(
                Cloud(
                    x=random.randint(0, self.screen_width),
                    y=random.randint(0, self.screen_height // 3),
                    speed=self.config.cloud_speed + random.uniform(-0.2, 0.2),
                    size=random.randint(50, 150),
                    opacity=random.randint(100, 200),
                )
            )

    def set_weather(self, weather_type: WeatherType, intensity: float = 1.0) -> None:
        """
        Set weather type and intensity.

        Args:
            weather_type: Type of weather
            intensity: Intensity level (0-1)
        """
        self.weather_type = weather_type
        self.intensity = max(0.0, min(1.0, intensity))

    def update(self, dt: int) -> None:
        """
        Update weather effects.

        Args:
            dt: Delta time in milliseconds
        """
        dt_seconds = dt / 1000.0

        # Update based on weather type
        if self.weather_type == WeatherType.RAINY:
            self._update_rain(dt_seconds)
        elif self.weather_type == WeatherType.SNOWY:
            self._update_snow(dt_seconds)
        elif self.weather_type == WeatherType.CLOUDY:
            self._update_clouds(dt_seconds)
        elif self.weather_type == WeatherType.STORMY:
            self._update_storm(dt_seconds)
        elif self.weather_type == WeatherType.WINDY:
            self._update_wind(dt_seconds)

        # Update lightning
        if self.lightning_alpha > 0:
            self.lightning_alpha -= 50 * (dt / 16)

    def _update_rain(self, dt: float) -> None:
        """Update rain drops."""
        count = int(self.config.rain_drop_count * self.intensity)

        for drop in self.rain_drops[:count]:
            # Apply wind
            wind_x = self.config.wind_strength * self.config.wind_direction * dt * 10

            drop.y += drop.speed * dt * 60
            drop.x += wind_x

            # Reset when off screen
            if drop.y > self.screen_height:
                drop.y = -drop.length
                drop.x = float(random.randint(0, self.screen_width))

            if drop.x > self.screen_width:
                drop.x = 0.0
            elif drop.x < 0:
                drop.x = float(self.screen_width)

    def _update_snow(self, dt: float) -> None:
        """Update snowflakes."""
        count = int(self.config.snowflake_count * self.intensity)

        for flake in self.snowflakes[:count]:
            # Gentle swaying motion
            flake.y += flake.speed * dt * 60
            flake.x += math.sin(flake.y * 0.05) * 0.5

            # Reset when off screen
            if flake.y > self.screen_height:
                flake.y = -10
                flake.x = random.randint(0, self.screen_width)

    def _update_clouds(self, dt: float) -> None:
        """Update clouds."""
        for cloud in self.clouds:
            cloud.x += cloud.speed * dt * 60 * self.config.wind_direction

            # Wrap around
            if cloud.x > self.screen_width + cloud.size:
                cloud.x = -cloud.size
                cloud.y = random.randint(0, self.screen_height // 3)

    def _update_storm(self, dt: float) -> None:
        """Update storm effects."""
        self._update_rain(dt)
        self._update_clouds(dt)

        # Random lightning
        if random.random() < self.config.lightning_chance * self.intensity:
            self.lightning_alpha = 200

    def _update_wind(self, dt: float) -> None:
        """Update wind effects."""
        self.wind_offset += self.config.wind_strength * dt * 100

        # Affect clouds
        for cloud in self.clouds:
            cloud.x += self.config.cloud_speed * dt * 60

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw weather effects.

        Args:
            surface: Surface to draw to
        """
        if self.weather_type == WeatherType.CLEAR:
            return

        if self.weather_type in (WeatherType.RAINY, WeatherType.STORMY):
            self._draw_rain(surface)

        if self.weather_type == WeatherType.SNOWY:
            self._draw_snow(surface)

        if self.weather_type in (WeatherType.CLOUDY, WeatherType.STORMY):
            self._draw_clouds(surface)

        # Lightning flash
        if self.lightning_alpha > 0:
            flash = pg.Surface((self.screen_width, self.screen_height))
            flash.fill(c.WHITE)
            flash.set_alpha(int(self.lightning_alpha))
            surface.blit(flash, (0, 0))

    def _draw_rain(self, surface: pg.Surface) -> None:
        """Draw rain drops."""
        count = int(self.config.rain_drop_count * self.intensity)

        for drop in self.rain_drops[:count]:
            pg.draw.line(
                surface,
                self.config.rain_color,
                (int(drop.x), int(drop.y)),
                (int(drop.x), int(drop.y) + int(drop.length)),
                int(drop.width),
            )

    def _draw_snow(self, surface: pg.Surface) -> None:
        """Draw snowflakes."""
        count = int(self.config.snowflake_count * self.intensity)

        for flake in self.snowflakes[:count]:
            pg.draw.circle(surface, self.config.snow_color, (int(flake.x), int(flake.y)), flake.width)

    def _draw_clouds(self, surface: pg.Surface) -> None:
        """Draw clouds."""
        for cloud in self.clouds:
            cloud_surface = pg.Surface((cloud.size, cloud.size // 2), pg.SRCALPHA)
            pg.draw.ellipse(
                cloud_surface, (*self.config.cloud_color, cloud.opacity), (0, 0, cloud.size, cloud.size // 2)
            )
            surface.blit(cloud_surface, (cloud.x, cloud.y))


class DayNightCycle:
    """
    Day/night cycle manager.
    """

    # Sky colors for different times
    SKY_COLORS = {
        TimeOfDay.MIDNIGHT: (10, 10, 40),
        TimeOfDay.NIGHT: (20, 20, 60),
        TimeOfDay.DAWN: (80, 60, 100),
        TimeOfDay.MORNING: (100, 150, 220),
        TimeOfDay.NOON: (135, 206, 235),
        TimeOfDay.AFTERNOON: (100, 180, 230),
        TimeOfDay.DUSK: (200, 150, 100),
        TimeOfDay.EVENING: (150, 100, 80),
    }

    def __init__(self, screen_width: int, screen_height: int, config: Optional[TimeConfig] = None) -> None:
        """
        Initialize day/night cycle.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            config: Time configuration
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config or TimeConfig()

        self.current_hour = self.config.start_hour
        self.current_time_of_day = TimeOfDay.MORNING
        self.cycle_timer = 0.0

        self.tween_manager = TweenManager()
        self.sky_overlay_alpha = 0

        self._update_time_of_day()

    def update(self, dt: int) -> None:
        """
        Update day/night cycle.

        Args:
            dt: Delta time in milliseconds
        """
        if not self.config.enabled:
            return

        dt_seconds = dt / 1000.0

        # Advance time
        hours_passed = (dt_seconds / self.config.full_cycle_duration) * 24
        self.current_hour = (self.current_hour + hours_passed) % 24

        self._update_time_of_day()
        self._update_sky_overlay()

    def _update_time_of_day(self) -> None:
        """Update current time of day based on hour."""
        if 4 <= self.current_hour < 6:
            self.current_time_of_day = TimeOfDay.DAWN
        elif 6 <= self.current_hour < 10:
            self.current_time_of_day = TimeOfDay.MORNING
        elif 10 <= self.current_hour < 14:
            self.current_time_of_day = TimeOfDay.NOON
        elif 14 <= self.current_hour < 17:
            self.current_time_of_day = TimeOfDay.AFTERNOON
        elif 17 <= self.current_hour < 19:
            self.current_time_of_day = TimeOfDay.DUSK
        elif 19 <= self.current_hour < 22:
            self.current_time_of_day = TimeOfDay.EVENING
        elif 22 <= self.current_hour or self.current_hour < 1:
            self.current_time_of_day = TimeOfDay.MIDNIGHT
        else:
            self.current_time_of_day = TimeOfDay.NIGHT

    def _update_sky_overlay(self) -> None:
        """Update sky overlay for transitions."""
        target_alpha = 0

        # More overlay at night
        if self.current_time_of_day in (TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT):
            target_alpha = 100
        elif self.current_time_of_day in (TimeOfDay.DAWN, TimeOfDay.DUSK):
            target_alpha = 50

        if "overlay" not in self.tween_manager.tweens:
            self.tween_manager.add_tween(
                "overlay", self.sky_overlay_alpha, target_alpha, 1000, EasingType.EASE_IN_OUT_SINE
            )
        else:
            tween = self.tween_manager.get_tween("overlay")
            if tween and abs(tween.end - target_alpha) > 1:
                tween.end = target_alpha
                tween.start_tween()

        results = self.tween_manager.update(16)
        self.sky_overlay_alpha = int(results.get("overlay", self.sky_overlay_alpha))

    def get_sky_color(self) -> tuple[int, int, int]:
        """
        Get current sky color.

        Returns:
            RGB color tuple
        """
        return self.SKY_COLORS.get(self.current_time_of_day, self.SKY_COLORS[TimeOfDay.NOON])

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw sky overlay.

        Args:
            surface: Surface to draw to
        """
        if self.sky_overlay_alpha <= 0:
            return

        overlay = pg.Surface((self.screen_width, self.screen_height))

        # Color based on time
        color = self.get_sky_color()
        overlay.fill(color)
        overlay.set_alpha(self.sky_overlay_alpha // 2)

        surface.blit(overlay, (0, 0))

    def set_hour(self, hour: float) -> None:
        """
        Set current hour.

        Args:
            hour: Hour (0-24)
        """
        self.current_hour = hour % 24
        self._update_time_of_day()

    def set_time_scale(self, scale: float) -> None:
        """
        Set time scale.

        Args:
            scale: Time scale factor
        """
        self.config.time_scale = scale

    def get_time_display(self) -> str:
        """
        Get formatted time display.

        Returns:
            Time string (HH:MM format)
        """
        hours = int(self.current_hour)
        minutes = int((self.current_hour - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def is_daytime(self) -> bool:
        """Check if it's currently daytime."""
        return self.current_time_of_day in (TimeOfDay.MORNING, TimeOfDay.NOON, TimeOfDay.AFTERNOON)

    def is_nighttime(self) -> bool:
        """Check if it's currently nighttime."""
        return self.current_time_of_day in (TimeOfDay.NIGHT, TimeOfDay.MIDNIGHT)


class WeatherManager:
    """
    Central manager for weather and day/night cycle.
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize weather manager.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.weather = WeatherEffect(screen_width, screen_height)
        self.day_night = DayNightCycle(screen_width, screen_height)

        self.weather_enabled = True
        self.day_night_enabled = True

    def update(self, dt: int) -> None:
        """
        Update all weather and time effects.

        Args:
            dt: Delta time in milliseconds
        """
        if self.weather_enabled:
            self.weather.update(dt)

        if self.day_night_enabled:
            self.day_night.update(dt)

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw all effects.

        Args:
            surface: Surface to draw to
        """
        if self.day_night_enabled:
            self.day_night.draw(surface)

        if self.weather_enabled:
            self.weather.draw(surface)

    def set_weather(self, weather_type: WeatherType, intensity: float = 1.0) -> None:
        """
        Set weather type.

        Args:
            weather_type: Weather type
            intensity: Intensity (0-1)
        """
        self.weather.set_weather(weather_type, intensity)

    def set_time(self, hour: float) -> None:
        """
        Set time of day.

        Args:
            hour: Hour (0-24)
        """
        self.day_night.set_hour(hour)

    def get_current_weather(self) -> WeatherType:
        """Get current weather type."""
        return self.weather.weather_type

    def get_current_time(self) -> TimeOfDay:
        """Get current time of day."""
        return self.day_night.current_time_of_day

    def get_time_display(self) -> str:
        """Get formatted time string."""
        return self.day_night.get_time_display()

    def toggle_weather(self) -> None:
        """Toggle weather effects."""
        self.weather_enabled = not self.weather_enabled

    def toggle_day_night(self) -> None:
        """Toggle day/night cycle."""
        self.day_night_enabled = not self.day_night_enabled


class SeasonalTheme:
    """
    Seasonal theme manager.
    """

    THEMES = {
        "spring": {
            "weather": [WeatherType.CLEAR, WeatherType.RAINY],
            "colors": {"grass": (100, 200, 100), "sky": (135, 206, 235)},
            "particles": "flowers",
        },
        "summer": {
            "weather": [WeatherType.CLEAR],
            "colors": {"grass": (80, 180, 80), "sky": (100, 180, 255)},
            "particles": "butterflies",
        },
        "autumn": {
            "weather": [WeatherType.CLOUDY, WeatherType.WINDY],
            "colors": {"grass": (180, 140, 80), "sky": (200, 180, 150)},
            "particles": "leaves",
        },
        "winter": {
            "weather": [WeatherType.SNOWY, WeatherType.CLOUDY],
            "colors": {"grass": (220, 220, 220), "sky": (200, 210, 220)},
            "particles": "snow",
        },
    }

    def __init__(self, weather_manager: WeatherManager, season: str = "spring") -> None:
        """
        Initialize seasonal theme.

        Args:
            weather_manager: Weather manager instance
            season: Initial season
        """
        self.weather_manager = weather_manager
        self.season = season

        if season not in self.THEMES:
            self.season = "spring"

    def apply_theme(self) -> None:
        """Apply current season theme."""
        theme = self.THEMES[self.season]

        # Set random weather from theme
        weather: WeatherType = random.choice(theme["weather"])  # type: ignore[arg-type]
        self.weather_manager.set_weather(weather)

    def change_season(self, season: str) -> None:
        """
        Change to new season.

        Args:
            season: New season name
        """
        if season in self.THEMES:
            self.season = season
            self.apply_theme()

    def get_season_colors(self) -> dict[str, tuple[int, int, int]]:
        """Get color palette for current season."""
        theme = self.THEMES.get(self.season, self.THEMES["spring"])
        return theme["colors"]  # type: ignore[return-value]
