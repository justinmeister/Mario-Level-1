"""Settings menu state for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..components import info
from ..game_settings import get_settings_manager


class Settings(tools._State):
    """Settings menu state"""

    def __init__(self) -> None:
        tools._State.__init__(self)
        persist: Dict[str, Any] = {
            c.COIN_TOTAL: 0,
            c.SCORE: 0,
            c.LIVES: 3,
            c.TOP_SCORE: 0,
            c.CURRENT_TIME: 0.0,
            c.LEVEL_STATE: None,
            c.CAMERA_START_X: 0,
            c.MARIO_DEAD: False,
        }
        self.startup(0.0, persist)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called every time the game's state becomes this one"""
        self.next = c.MAIN_MENU
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)

        self.background: pg.Surface = None  # type: ignore[assignment]
        self.selected_option = 0
        self.input_timer = 0
        self.input_delay = 200

        # Load settings from manager
        settings_mgr = get_settings_manager()
        self.settings = {
            "music_volume": settings_mgr.get("music_volume", 70),
            "sfx_volume": settings_mgr.get("sfx_volume", 80),
            "fullscreen": settings_mgr.get("fullscreen", False),
            "show_fps": settings_mgr.get("show_fps", False),
        }

        # Apply loaded settings
        pg.mixer.music.set_volume(self.settings["music_volume"] / 100)
        for sound in setup.SFX.values():
            if sound:
                sound.set_volume(self.settings["sfx_volume"] / 100)

        self.menu_options = ["Music Volume", "SFX Volume", "Fullscreen", "Show FPS", "Back"]
        self.setup_background()

    def setup_background(self) -> None:
        """Setup the background"""
        try:
            # Try to load custom background image
            bg_image = pg.image.load("img/sky_background.jpg")
            self.background = pg.transform.scale(bg_image, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        except (pg.error, FileNotFoundError):
            # Fallback to black background
            self.background = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
            self.background.fill(c.BLACK)

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Updates the state every refresh"""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        # Draw background
        surface.blit(self.background, (0, 0))

        # Draw very light semi-transparent overlay
        overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        overlay.set_alpha(60)  # Very light
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Draw title
        self._draw_text(surface, "SETTINGS", 400, 70, c.YELLOW, 55)

        # Draw settings options with visual indicators
        menu_start_y = 180
        option_descriptions = [
            "Adjust background music volume",
            "Adjust sound effects volume",
            "Toggle fullscreen mode",
            "Show FPS counter (F5)",
            "Return to main menu",
        ]

        for i, option in enumerate(self.menu_options):
            y_pos = menu_start_y + (i * 70)

            # Get value for display
            if option == "Music Volume":
                value = f"{self.settings['music_volume']}%"
                show_bar = True
                bar_value = self.settings["music_volume"]
            elif option == "SFX Volume":
                value = f"{self.settings['sfx_volume']}%"
                show_bar = True
                bar_value = self.settings["sfx_volume"]
            elif option == "Fullscreen":
                value = "ON" if self.settings["fullscreen"] else "OFF"
                show_bar = False
                bar_value = 0
            elif option == "Show FPS":
                value = "ON" if self.settings["show_fps"] else "OFF"
                show_bar = False
                bar_value = 0
            else:
                value = ""
                show_bar = False
                bar_value = 0

            # Highlight selected option
            if i == self.selected_option:
                color = c.YELLOW
                size = 36
                # Draw selection box with background
                box_rect = pg.Rect(100, y_pos - 25, 600, 60)
                box_bg = pg.Surface((600, 60))
                box_bg.set_alpha(140)
                box_bg.fill((60, 60, 80))
                surface.blit(box_bg, (100, y_pos - 25))
                pg.draw.rect(surface, c.GOLD, box_rect, 4, border_radius=8)
            else:
                color = c.WHITE
                size = 30
                # Draw subtle border with background
                box_rect = pg.Rect(100, y_pos - 25, 600, 60)
                box_bg = pg.Surface((600, 60))
                box_bg.set_alpha(80)
                box_bg.fill((40, 40, 50))
                surface.blit(box_bg, (100, y_pos - 25))
                pg.draw.rect(surface, (100, 100, 100), box_rect, 2, border_radius=8)

            # Draw option name
            self._draw_text(surface, option, 200, y_pos - 5, color, size)

            # Draw value or toggle
            if value:
                value_color = c.GREEN if value == "ON" else c.RED if value == "OFF" else color
                self._draw_text(surface, value, 580, y_pos - 5, value_color, size)

            # Draw volume bar
            if show_bar:
                bar_x = 120
                bar_y = y_pos + 18
                bar_width = 560
                bar_height = 8

                # Background bar
                pg.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

                # Filled bar
                filled_width = int(bar_width * (bar_value / 100))
                if filled_width > 0:
                    bar_color = c.GREEN if bar_value > 50 else c.YELLOW if bar_value > 25 else c.RED
                    pg.draw.rect(surface, bar_color, (bar_x, bar_y, filled_width, bar_height), border_radius=4)

            # Draw description for selected option
            if i == self.selected_option:
                desc_color = (220, 220, 220)
                self._draw_text(surface, option_descriptions[i], 400, y_pos + 30, desc_color, 18)

        # Draw instructions
        self._draw_text(surface, "↑↓ Select  |  ←→ Change  |  ENTER/ESC Back", 400, 560, c.WHITE, 22)

        self.overhead_info.draw(surface)

    def _draw_text(
        self, surface: pg.Surface, text: str, x: int, y: int, color: Tuple[int, int, int], size: int = 30
    ) -> None:
        """Draw text on surface with shadow"""
        font = pg.font.Font(None, size)

        # Draw shadow
        shadow_surface = font.render(text, True, c.BLACK)
        shadow_rect = shadow_surface.get_rect(center=(x + 2, y + 2))
        surface.blit(shadow_surface, shadow_rect)

        # Draw text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)

    def update_cursor(self, keys: Tuple[bool, ...]) -> None:
        """Update the position of the cursor"""
        current_time = pg.time.get_ticks()
        can_input = current_time - self.input_timer > self.input_delay

        # Navigation
        if can_input and keys[pg.K_DOWN]:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            self.input_timer = current_time
            # Play navigation sound
            if setup.SFX.get("coin"):
                setup.SFX["coin"].play()

        elif can_input and keys[pg.K_UP]:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            self.input_timer = current_time
            # Play navigation sound
            if setup.SFX.get("coin"):
                setup.SFX["coin"].play()

        # Change values
        if can_input and keys[pg.K_RIGHT]:
            self._change_setting(1)
            self.input_timer = current_time
            # Play change sound
            if setup.SFX.get("powerup"):
                setup.SFX["powerup"].play()

        elif can_input and keys[pg.K_LEFT]:
            self._change_setting(-1)
            self.input_timer = current_time
            # Play change sound
            if setup.SFX.get("powerup"):
                setup.SFX["powerup"].play()

        # Handle selection
        if keys[pg.K_RETURN] or keys[pg.K_a] or keys[pg.K_s]:
            if self.selected_option == len(self.menu_options) - 1:  # Back
                # Play back sound
                if setup.SFX.get("pipe"):
                    setup.SFX["pipe"].play()
                self.done = True

        # Handle ESC to go back
        if keys[pg.K_ESCAPE]:
            # Play back sound
            if setup.SFX.get("pipe"):
                setup.SFX["pipe"].play()
            self.done = True

    def _change_setting(self, direction: int) -> None:
        """Change the selected setting"""
        option = self.menu_options[self.selected_option]
        settings_mgr = get_settings_manager()

        if option == "Music Volume":
            self.settings["music_volume"] = max(0, min(100, self.settings["music_volume"] + direction * 10))
            pg.mixer.music.set_volume(self.settings["music_volume"] / 100)
            settings_mgr.set("music_volume", self.settings["music_volume"])

        elif option == "SFX Volume":
            self.settings["sfx_volume"] = max(0, min(100, self.settings["sfx_volume"] + direction * 10))
            # Update all sound effects volume
            for sound in setup.SFX.values():
                if sound:
                    sound.set_volume(self.settings["sfx_volume"] / 100)
            settings_mgr.set("sfx_volume", self.settings["sfx_volume"])

        elif option == "Fullscreen":
            self.settings["fullscreen"] = not self.settings["fullscreen"]
            if self.settings["fullscreen"]:
                setup.SCREEN = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.FULLSCREEN)
            else:
                setup.SCREEN = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
            settings_mgr.set("fullscreen", self.settings["fullscreen"])

        elif option == "Show FPS":
            self.settings["show_fps"] = not self.settings["show_fps"]
            settings_mgr.set("show_fps", self.settings["show_fps"])
