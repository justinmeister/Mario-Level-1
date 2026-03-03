"""Level selection menu state for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, List

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..components import info, mario


class LevelSelect(tools._State):
    """Level selection menu state"""

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
            c.CURRENT_LEVEL: c.LEVEL1,
        }
        self.startup(0.0, persist)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Called every time the game's state becomes this one"""
        self.next = c.MAIN_MENU  # Default to main menu, will change to LOAD_SCREEN when level selected
        self.persist = persist
        self.game_info = persist
        self.overhead_info = info.OverheadInfo(self.game_info, c.MAIN_MENU)

        self.sprite_sheet = setup.GFX.get("title_screen")
        self.background: pg.Surface = None  # type: ignore[assignment]
        self.background_rect: pg.Rect = None  # type: ignore[assignment]
        self.viewport: pg.Rect = None  # type: ignore[assignment]
        self.image_dict: Dict[str, Tuple[pg.Surface, pg.Rect]] = {}
        self.mario: Optional[mario.Mario] = None
        self.cursor: Optional[pg.sprite.Sprite] = None
        self.selected_level: int = 0
        self.input_timer = 0
        self.input_delay = 200  # milliseconds between inputs
        self.level_names: List[str] = [
            "LEVEL 1-1",
            "LEVEL 1-2",
            "LEVEL 1-3",
            "LEVEL 1-4",
            "LEVEL 2-1",
            "LEVEL 2-2",
            "LEVEL 2-3",
            "LEVEL 2-4",
        ]
        self.level_constants: List[str] = [
            c.LEVEL1,
            c.LEVEL2,
            c.LEVEL3,
            c.LEVEL4,
            c.LEVEL5,
            c.LEVEL6,
            c.LEVEL7,
            c.LEVEL8,
        ]
        self.setup_background()
        self.setup_mario()
        self.setup_cursor()

    def cleanup(self) -> Dict[str, Any]:
        """Clean up and return game info with selected level"""
        self.done = False
        return self.game_info

    def setup_cursor(self) -> None:
        """Creates the cursor to select level"""
        self.cursor = pg.sprite.Sprite()
        image = pg.Surface([16, 16])
        image.fill(c.RED)
        rect = image.get_rect()
        self.cursor.image = image
        self.cursor.rect = rect
        self.cursor.state = c.PLAYER1  # type: ignore[attr-defined]
        self._update_cursor_position()

    def _update_cursor_position(self) -> None:
        """Updates cursor position based on selected level"""
        if self.cursor and self.cursor.rect:
            self.cursor.rect.x = 220
            self.cursor.rect.y = 280 + (self.selected_level * 40)

    def setup_mario(self) -> None:
        """Places Mario at the side"""
        self.mario = mario.Mario()
        if self.mario and self.mario.rect:
            self.mario.rect.x = 500
            self.mario.rect.bottom = c.GROUND_HEIGHT - 50

    def setup_background(self) -> None:
        """Setup the background image"""
        try:
            # Try to load custom background image
            bg_image = pg.image.load("img/sky_background.jpg")
            self.background = pg.transform.scale(bg_image, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
            self.background_rect = self.background.get_rect()
            self.viewport = pg.Rect(0, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT)
        except (pg.error, FileNotFoundError):
            # Fallback to level_1 image
            level_1_img = setup.GFX.get("level_1")
            if level_1_img is None:
                level_1_img = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
            self.background = level_1_img
            self.background_rect = self.background.get_rect()
            scaled_background = pg.transform.scale(
                self.background,
                (
                    int(self.background_rect.width * c.BACKGROUND_MULTIPLIER),
                    int(self.background_rect.height * c.BACKGROUND_MULTIPLIER),
                ),
            )
            if scaled_background:
                self.background = scaled_background
                self.background_rect = self.background.get_rect()

            if self.background_rect and setup.SCREEN is not None:
                screen_rect = setup.SCREEN.get_rect(bottom=setup.SCREEN_RECT.bottom if setup.SCREEN_RECT else 0)
                if screen_rect:
                    self.viewport = screen_rect

        self.image_dict = {}
        title_screen = setup.GFX.get("title_screen")
        if title_screen:
            self.image_dict["GAME_NAME_BOX"] = self.get_image(1, 60, 176, 88, (170, 100), title_screen)

    def get_image(
        self, x: int, y: int, width: int, height: int, dest: Tuple[int, int], sprite_sheet: Optional[pg.Surface]
    ) -> Tuple[pg.Surface, pg.Rect]:
        """Returns images and rects to blit onto the screen"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        if sprite_sheet:
            image.blit(sprite_sheet, (0, 0), (x, y, width, height))
            image.set_colorkey((255, 0, 220))
            image = pg.transform.scale(
                image, (int(rect.width * c.SIZE_MULTIPLIER), int(rect.height * c.SIZE_MULTIPLIER))
            )
        else:
            image.fill(c.WHITE)

        rect = image.get_rect()
        rect.x = dest[0]
        rect.y = dest[1]
        return (image, rect)

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Updates the state every refresh"""
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.update_cursor(keys)
        self.overhead_info.update(self.game_info)

        # Clear and draw background
        surface.fill(c.BLACK)
        if self.background:
            surface.blit(self.background, (0, 0))

        # Draw very light semi-transparent overlay
        overlay = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
        overlay.set_alpha(60)  # Very light
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Draw title
        self._draw_text(surface, "SELECT LEVEL", 400, 80, c.YELLOW, 50)

        # Draw level descriptions
        level_descriptions = [
            "Classic overworld - Goombas & Koopas",
            "Underground - Pipes & secret areas",
            "Tree platforms - Koopa Paratroopas",
            "Castle - Fire Bars & fake Bowser",
            "Overworld - Spring board challenge",
            "Underwater - Bloobers & Cheep-Cheeps",
            "Bridge - Jumping Cheep-Cheeps",
            "Castle - Podoboos & fake Bowser",
        ]

        # Draw level grid (2 columns)
        levels_per_column = 4
        column_width = 350
        start_x = 150
        start_y = 180

        for i, level_name in enumerate(self.level_names):
            col = i // levels_per_column
            row = i % levels_per_column

            x_pos = start_x + (col * column_width)
            y_pos = start_y + (row * 100)

            # Highlight selected level
            if i == self.selected_level:
                color = c.YELLOW
                size = 33
                # Draw selection box with glow effect
                box_rect = pg.Rect(x_pos - 10, y_pos - 15, 320, 80)
                # Background for better visibility
                box_bg = pg.Surface((320, 80))
                box_bg.set_alpha(120)
                box_bg.fill((60, 60, 80))
                surface.blit(box_bg, (x_pos - 10, y_pos - 15))

                pg.draw.rect(surface, c.GOLD, box_rect, 4, border_radius=8)
            else:
                color = c.WHITE
                size = 28
                # Draw subtle border with background
                box_rect = pg.Rect(x_pos - 10, y_pos - 15, 320, 80)
                box_bg = pg.Surface((320, 80))
                box_bg.set_alpha(80)
                box_bg.fill((40, 40, 50))
                surface.blit(box_bg, (x_pos - 10, y_pos - 15))
                pg.draw.rect(surface, (120, 120, 120), box_rect, 2, border_radius=8)

            # Draw level name
            self._draw_text(surface, level_name, x_pos + 150, y_pos, color, size)

            # Draw description
            desc_color = c.YELLOW if i == self.selected_level else (210, 210, 210)
            self._draw_text(surface, level_descriptions[i], x_pos + 150, y_pos + 30, desc_color, 17)

        # Draw instructions with icons
        self._draw_text(surface, "↑↓←→ Navigate  |  ENTER Start  |  ESC Back", 400, 550, c.WHITE, 22)

        # Don't draw overhead_info - it causes issues

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
        # Check if enough time has passed since last input
        current_time = pg.time.get_ticks()
        can_input = current_time - self.input_timer > self.input_delay

        levels_per_column = 4

        if can_input and keys[pg.K_DOWN]:
            # Move down in current column
            if self.selected_level % levels_per_column < levels_per_column - 1:
                self.selected_level += 1
                # Play navigation sound
                if setup.SFX.get("coin"):
                    setup.SFX["coin"].play()
            self.input_timer = current_time

        elif can_input and keys[pg.K_UP]:
            # Move up in current column
            if self.selected_level % levels_per_column > 0:
                self.selected_level -= 1
                # Play navigation sound
                if setup.SFX.get("coin"):
                    setup.SFX["coin"].play()
            self.input_timer = current_time

        elif can_input and keys[pg.K_RIGHT]:
            # Move to next column
            if self.selected_level < levels_per_column:
                self.selected_level += levels_per_column
                # Play navigation sound
                if setup.SFX.get("coin"):
                    setup.SFX["coin"].play()
            self.input_timer = current_time

        elif can_input and keys[pg.K_LEFT]:
            # Move to previous column
            if self.selected_level >= levels_per_column:
                self.selected_level -= levels_per_column
                # Play navigation sound
                if setup.SFX.get("coin"):
                    setup.SFX["coin"].play()
            self.input_timer = current_time

        elif can_input and (keys[pg.K_RETURN] or keys[pg.K_a] or keys[pg.K_s]):
            # Play selection sound
            if setup.SFX.get("bump"):
                setup.SFX["bump"].play()
            self.game_info[c.CURRENT_LEVEL] = self.level_constants[self.selected_level]
            self.next = c.LOAD_SCREEN
            self.done = True
            self.input_timer = current_time

        elif can_input and keys[pg.K_ESCAPE]:
            # Play back sound
            if setup.SFX.get("pipe"):
                setup.SFX["pipe"].play()
            self.next = c.MAIN_MENU
            self.done = True
            self.input_timer = current_time

    def get_event(self, event: pg.event.Event) -> None:
        """Handle events"""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_DOWN:
                self.selected_level = (self.selected_level + 1) % len(self.level_names)
                self._update_cursor_position()
            elif event.key == pg.K_UP:
                self.selected_level = (self.selected_level - 1) % len(self.level_names)
                self._update_cursor_position()
            elif event.key == pg.K_RETURN or event.key == pg.K_a or event.key == pg.K_s:
                # Play selection sound
                if setup.SFX.get("bump"):
                    setup.SFX["bump"].play()
                self.game_info[c.CURRENT_LEVEL] = self.level_constants[self.selected_level]
                self.next = c.LOAD_SCREEN
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.next = c.MAIN_MENU
                self.done = True
