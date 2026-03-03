"""
Enhanced UI system with animated menus for Super Mario Bros.

Provides:
- Animated main menu
- Button components with hover effects
- Menu transitions
- UI animations and effects
- Pause menu
- HUD improvements
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, Tuple, Callable

import pygame as pg

from . import constants as c
from .animation_system import TweenManager, EasingType

if TYPE_CHECKING:
    from pygame.font import Font


class UIState(Enum):
    """UI state types."""

    HIDDEN = "hidden"
    VISIBLE = "visible"
    TRANSITIONING = "transitioning"
    DISABLED = "disabled"


class MenuAction(Enum):
    """Menu action types."""

    START_GAME = "start_game"
    OPTIONS = "options"
    ACHIEVEMENTS = "achievements"
    QUIT = "quit"
    BACK = "back"
    SELECT = "select"
    NAVIGATE_UP = "navigate_up"
    NAVIGATE_DOWN = "navigate_down"


@dataclass
class ButtonStyle:
    """Style configuration for buttons."""

    bg_color: tuple[int, int, int] = c.SKY_BLUE
    bg_hover_color: tuple[int, int, int] = c.BLUE
    text_color: tuple[int, int, int] = c.WHITE
    text_hover_color: tuple[int, int, int] = c.GOLD
    border_color: tuple[int, int, int] = c.WHITE
    border_width: int = 2
    font_size: int = 36
    padding_x: int = 20
    padding_y: int = 10
    corner_radius: int = 8


@dataclass
class MenuItem:
    """Menu item data."""

    text: str
    action: MenuAction
    callback: Optional[Callable[[], None]] = None
    enabled: bool = True


class UIButton:
    """
    Interactive button with hover effects and animations.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        style: Optional[ButtonStyle] = None,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize button.

        Args:
            x, y: Button position
            width, height: Button dimensions
            text: Button text
            style: Button style configuration
            callback: Function to call on click
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.style = style or ButtonStyle()
        self.callback = callback

        self.rect = pg.Rect(x, y, width, height)
        self.is_hovered = False
        self.is_pressed = False
        self.is_enabled = True

        # Animation
        self.tween_manager = TweenManager()
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.alpha = 255

        # Font
        self.font: Optional["Font"] = None
        self._init_font()

        # Click animation
        self._click_timer = 0

    def _init_font(self) -> None:
        """Initialize button font."""
        try:
            self.font = pg.font.Font(None, self.style.font_size)
        except pg.error:
            self.font = None

    def update(self, dt: int, mouse_pos: Tuple[int, int]) -> None:
        """
        Update button state.

        Args:
            dt: Delta time in milliseconds
            mouse_pos: Current mouse position
        """
        if not self.is_enabled:
            return

        # Check hover
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # Update animations
        self._update_animations(dt)

        # Update click animation
        if self._click_timer > 0:
            self._click_timer -= dt

    def _update_animations(self, dt: int) -> None:
        """Update button animations."""
        # Scale animation on hover
        target_scale = 1.1 if self.is_hovered else 1.0

        if "scale" not in self.tween_manager.tweens:
            self.tween_manager.add_tween("scale", self.scale_x, target_scale, 150, EasingType.EASE_OUT_QUAD)
        else:
            tween = self.tween_manager.get_tween("scale")
            if tween and abs(tween.end - target_scale) > 0.01:
                tween.end = target_scale
                tween.start_tween()

        results = self.tween_manager.update(dt)
        self.scale_x = results.get("scale", 1.0)
        self.scale_y = self.scale_x

    def handle_event(self, event: pg.event.Event) -> bool:
        """
        Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            True if event was handled
        """
        if not self.is_enabled:
            return False

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                self._click_timer = 200
                return True

        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False

        return False

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw button to surface.

        Args:
            surface: Surface to draw to
        """
        if not self.is_enabled:
            self._draw_disabled(surface)
            return

        # Calculate colors based on state
        if self.is_pressed:
            bg_color = self.style.bg_hover_color
            text_color = self.style.text_hover_color
        elif self.is_hovered:
            bg_color = self.style.bg_hover_color
            text_color = self.style.text_hover_color
        else:
            bg_color = self.style.bg_color
            text_color = self.style.text_color

        # Calculate scaled rect
        scaled_width = int(self.width * self.scale_x)
        scaled_height = int(self.height * self.scale_y)
        offset_x = (self.width - scaled_width) // 2
        offset_y = (self.height - scaled_height) // 2

        draw_rect = pg.Rect(self.x + offset_x, self.y + offset_y, scaled_width, scaled_height)

        # Draw button background with rounded corners
        self._draw_rounded_rect(surface, draw_rect, bg_color)

        # Draw border
        pg.draw.rect(
            surface, self.style.border_color, draw_rect, self.style.border_width, border_radius=self.style.corner_radius
        )

        # Draw text
        if self.font:
            text_surface = self.font.render(self.text, True, text_color)
            text_rect = text_surface.get_rect(center=draw_rect.center)
            surface.blit(text_surface, text_rect)

    def _draw_rounded_rect(self, surface: pg.Surface, rect: pg.Rect, color: tuple[int, int, int]) -> None:
        """Draw rounded rectangle."""
        pg.draw.rect(surface, color, rect, border_radius=self.style.corner_radius)

    def _draw_disabled(self, surface: pg.Surface) -> None:
        """Draw disabled button state."""
        # Gray out the button
        disabled_color = c.GRAY
        pg.draw.rect(surface, disabled_color, self.rect, border_radius=self.style.corner_radius)

        if self.font:
            text_surface = self.font.render(self.text, True, c.NAVYBLUE)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def set_position(self, x: int, y: int) -> None:
        """Set button position."""
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable button."""
        self.is_enabled = enabled


class UILabel:
    """
    Text label with optional animations.
    """

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        font_size: int = 36,
        color: tuple[int, int, int] = c.WHITE,
        center: bool = False,
    ) -> None:
        """
        Initialize label.

        Args:
            x, y: Position
            text: Label text
            font_size: Font size
            color: Text color
            center: Whether to center the label
        """
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.center = center

        self.font: Optional["Font"] = None
        self._init_font(font_size)
        self.alpha = 255
        self.visible = True

    def _init_font(self, font_size: int) -> None:
        """Initialize font."""
        try:
            self.font = pg.font.Font(None, font_size)
        except pg.error:
            self.font = None

    def update(self, dt: int) -> None:
        """Update label."""
        pass

    def draw(self, surface: pg.Surface) -> None:
        """Draw label to surface."""
        if not self.visible or not self.font:
            return

        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)

        if self.center:
            rect = text_surface.get_rect(center=(self.x, self.y))
        else:
            rect = text_surface.get_rect(topleft=(self.x, self.y))

        surface.blit(text_surface, rect)

    def set_text(self, text: str) -> None:
        """Set label text."""
        self.text = text

    def fade_in(self, duration: int = 500) -> None:
        """Fade in the label."""
        self.alpha = 0
        # Would use tween in full implementation

    def fade_out(self, duration: int = 500) -> None:
        """Fade out the label."""
        self.alpha = 255


class AnimatedMenu:
    """
    Animated menu with transitions.
    """

    def __init__(self, screen_width: int, screen_height: int, title: str = "MENU") -> None:
        """
        Initialize animated menu.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            title: Menu title
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title

        self.buttons: List[UIButton] = []
        self.labels: List[UILabel] = []
        self.selected_index = 0

        self.state = UIState.HIDDEN
        self.alpha = 0

        # Transitions
        self.tween_manager = TweenManager()

        # Title label
        self._init_title()

    def _init_title(self) -> None:
        """Initialize title label."""
        self.title_label = UILabel(self.screen_width // 2, 80, self.title, font_size=72, color=c.GOLD, center=True)

    def add_button(
        self, text: str, action: MenuAction, callback: Optional[Callable[[], None]] = None, y_offset: int = 0
    ) -> UIButton:
        """
        Add button to menu.

        Args:
            text: Button text
            action: Menu action
            callback: Click callback
            y_offset: Vertical offset from base position

        Returns:
            Created button
        """
        button_width = 300
        button_height = 60
        button_x = (self.screen_width - button_width) // 2
        base_y = self.screen_height // 2

        # Calculate y position based on number of buttons
        y = base_y + y_offset + len(self.buttons) * 70

        button = UIButton(button_x, y, button_width, button_height, text, callback=callback)

        self.buttons.append(button)
        return button

    def add_label(
        self, text: str, font_size: int = 24, color: tuple[int, int, int] = c.GRAY, y_offset: int = 0
    ) -> UILabel:
        """Add label to menu."""
        label = UILabel(
            self.screen_width // 2,
            self.screen_height - 50 + y_offset,
            text,
            font_size=font_size,
            color=color,
            center=True,
        )
        self.labels.append(label)
        return label

    def update(self, dt: int, mouse_pos: Tuple[int, int]) -> None:
        """
        Update menu state.

        Args:
            dt: Delta time in milliseconds
            mouse_pos: Mouse position
        """
        if self.state == UIState.HIDDEN:
            return

        # Update title
        self.title_label.update(dt)

        # Update buttons
        for button in self.buttons:
            button.update(dt, mouse_pos)

        # Update labels
        for label in self.labels:
            label.update(dt)

        # Update transitions
        self.tween_manager.update(dt)

    def draw(self, surface: pg.Surface) -> None:
        """Draw menu to surface."""
        if self.state == UIState.HIDDEN:
            return

        # Draw semi-transparent background
        overlay = pg.Surface((self.screen_width, self.screen_height))
        overlay.fill(c.BLACK)
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))

        # Draw title
        self.title_label.draw(surface)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

        # Draw labels
        for label in self.labels:
            label.draw(surface)

    def handle_event(self, event: pg.event.Event) -> Optional[MenuAction]:
        """
        Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            MenuAction if triggered, None otherwise
        """
        if self.state == UIState.HIDDEN:
            return None

        # Handle button events
        for button in self.buttons:
            if button.handle_event(event):
                # Find and return the action for this button
                idx = self.buttons.index(button)
                if idx < len(self.buttons):
                    # Get action from menu items if available
                    pass
                return MenuAction.SELECT

        # Handle keyboard navigation
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                return MenuAction.NAVIGATE_UP
            elif event.key == pg.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                return MenuAction.NAVIGATE_DOWN
            elif event.key in (pg.K_RETURN, pg.K_SPACE):
                if self.buttons and self.selected_index < len(self.buttons):
                    btn = self.buttons[self.selected_index]
                    if btn and btn.callback:
                        btn.callback()
                    return MenuAction.SELECT

        return None

    def show(self, transition_duration: int = 300) -> None:
        """Show menu with transition."""
        self.state = UIState.TRANSITIONING
        self.tween_manager.add_tween("alpha", self.alpha, 255, transition_duration)
        self.alpha = 255
        self.state = UIState.VISIBLE

    def hide(self, transition_duration: int = 300) -> None:
        """Hide menu with transition."""
        self.state = UIState.TRANSITIONING
        self.alpha = 0
        self.state = UIState.HIDDEN

    def clear(self) -> None:
        """Clear all menu items."""
        self.buttons.clear()
        self.labels.clear()


class MainMenu(AnimatedMenu):
    """
    Main menu with game-specific options.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        on_start: Optional[Callable[[], None]] = None,
        on_options: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize main menu.

        Args:
            screen_width: Screen width
            screen_height: Screen height
            on_start: Callback for start game
            on_options: Callback for options
            on_quit: Callback for quit
        """
        super().__init__(screen_width, screen_height, "SUPER MARIO BROS")

        self.on_start = on_start
        self.on_options = on_options
        self.on_quit = on_quit

        self._setup_menu()

    def _setup_menu(self) -> None:
        """Setup main menu buttons."""
        # Title with shadow
        self.title_label = UILabel(
            self.screen_width // 2, 60, "SUPER MARIO BROS", font_size=64, color=c.RED, center=True
        )

        # Subtitle
        subtitle = UILabel(self.screen_width // 2, 120, "Level 1-1", font_size=32, color=c.WHITE, center=True)
        self.labels.append(subtitle)

        # Menu buttons
        self.add_button("НАЧАТЬ ИГРУ", MenuAction.START_GAME, self.on_start, -60)
        self.add_button("НАСТРОЙКИ", MenuAction.OPTIONS, self.on_options, 10)
        self.add_button("ВЫХОД", MenuAction.QUIT, self.on_quit, 80)

        # Copyright/info label
        self.add_label("Нажмите ENTER для выбора", font_size=20)


class PauseMenu(AnimatedMenu):
    """
    Pause menu overlay.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        on_resume: Optional[Callable[[], None]] = None,
        on_restart: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize pause menu."""
        super().__init__(screen_width, screen_height, "ПАУЗА")

        self.on_resume = on_resume
        self.on_restart = on_restart
        self.on_quit = on_quit

        self._setup_menu()

    def _setup_menu(self) -> None:
        """Setup pause menu buttons."""
        self.add_button("ПРОДОЛЖИТЬ", MenuAction.START_GAME, self.on_resume, -30)
        self.add_button("НАЧАТЬ ЗАНОВО", MenuAction.SELECT, self.on_restart, 40)
        self.add_button("В МЕНЮ", MenuAction.BACK, self.on_quit, 110)


class HUD:
    """
    Heads-up display for game information.
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize HUD.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        self._init_fonts()
        self._init_labels()

        # Game state
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.world = "1-1"
        self.time = 400
        self.combo_text = ""

    def _init_fonts(self) -> None:
        """Initialize HUD fonts."""
        try:
            self.font_large: Optional["Font"] = pg.font.Font(None, 48)
            self.font_medium: Optional["Font"] = pg.font.Font(None, 36)
            self.font_small: Optional["Font"] = pg.font.Font(None, 24)
        except pg.error:
            self.font_large = None
            self.font_medium = None
            self.font_small = None

    def _init_labels(self) -> None:
        """Initialize static labels."""
        self.labels = {
            "score_label": UILabel(50, 20, "СЧЁТ", font_size=24, color=c.WHITE),
            "coins_label": UILabel(250, 20, "МОНЕТЫ", font_size=24, color=c.WHITE),
            "world_label": UILabel(450, 20, "МИР", font_size=24, color=c.WHITE),
            "time_label": UILabel(600, 20, "ВРЕМЯ", font_size=24, color=c.WHITE),
            "lives_label": UILabel(50, 80, "ЖИЗНИ", font_size=24, color=c.WHITE),
        }

    def update(self, dt: int) -> None:
        """Update HUD."""
        for label in self.labels.values():
            label.update(dt)

    def draw(self, surface: pg.Surface) -> None:
        """Draw HUD to surface."""
        # Draw background bar
        bar_rect = pg.Rect(0, 0, self.screen_width, 100)
        pg.draw.rect(surface, (0, 0, 0, 128), bar_rect)

        # Draw labels
        for label in self.labels.values():
            label.draw(surface)

        # Draw values
        self._draw_values(surface)

    def _draw_values(self, surface: pg.Surface) -> None:
        """Draw dynamic values."""
        y_offset = 45

        if self.font_medium:
            # Score
            score_text = f"{self.score:06d}"
            score_surface = self.font_medium.render(score_text, True, c.WHITE)
            surface.blit(score_surface, (50, y_offset))

            # Coins
            coins_text = f"x {self.coins:02d}"
            coins_surface = self.font_medium.render(coins_text, True, c.GOLD)
            surface.blit(coins_surface, (250, y_offset))

            # World
            world_surface = self.font_medium.render(self.world, True, c.WHITE)
            surface.blit(world_surface, (450, y_offset))

            # Time
            time_surface = self.font_medium.render(f"{self.time:03d}", True, c.WHITE)
            surface.blit(time_surface, (600, y_offset))

            # Lives
            lives_surface = self.font_medium.render(f"x {self.lives}", True, c.WHITE)
            surface.blit(lives_surface, (50, y_offset + 60))

        # Draw combo if active
        if self.combo_text and self.font_small:
            combo_surface = self.font_small.render(self.combo_text, True, c.GOLD)
            surface.blit(combo_surface, (self.screen_width // 2 - 50, 120))

    def set_score(self, score: int) -> None:
        """Set current score."""
        self.score = score

    def set_coins(self, coins: int) -> None:
        """Set coin count."""
        self.coins = coins

    def set_lives(self, lives: int) -> None:
        """Set lives count."""
        self.lives = lives

    def set_world(self, world: str) -> None:
        """Set world/level."""
        self.world = world

    def set_time(self, time: int) -> None:
        """Set remaining time."""
        self.time = time

    def set_combo(self, combo_text: str) -> None:
        """Set combo display text."""
        self.combo_text = combo_text


class UIManager:
    """
    Central manager for all UI elements.
    """

    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize UI manager.

        Args:
            screen_width: Screen width
            screen_height: Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.main_menu: Optional[MainMenu] = None
        self.pause_menu: Optional[PauseMenu] = None
        self.hud: Optional[HUD] = None

        self.current_menu: Optional[AnimatedMenu] = None
        self.active_menus: List[AnimatedMenu] = []

        self._init_menus()

    def _init_menus(self) -> None:
        """Initialize all menus."""
        self.main_menu = MainMenu(
            self.screen_width,
            self.screen_height,
            on_start=self._on_start_game,
            on_options=self._on_options,
            on_quit=self._on_quit,
        )

        self.pause_menu = PauseMenu(
            self.screen_width,
            self.screen_height,
            on_resume=self._on_resume,
            on_restart=self._on_restart,
            on_quit=self._on_quit_to_menu,
        )

        self.hud = HUD(self.screen_width, self.screen_height)

    def _on_start_game(self) -> None:
        """Handle start game action."""
        pass  # Override in game

    def _on_options(self) -> None:
        """Handle options action."""
        pass

    def _on_quit(self) -> None:
        """Handle quit action."""
        pass

    def _on_resume(self) -> None:
        """Handle resume action."""
        pass

    def _on_restart(self) -> None:
        """Handle restart action."""
        pass

    def _on_quit_to_menu(self) -> None:
        """Handle quit to menu action."""
        pass

    def update(self, dt: int, mouse_pos: Tuple[int, int]) -> None:
        """
        Update all UI.

        Args:
            dt: Delta time in milliseconds
            mouse_pos: Mouse position
        """
        if self.current_menu:
            self.current_menu.update(dt, mouse_pos)

        if self.hud:
            self.hud.update(dt)

    def draw(self, surface: pg.Surface) -> None:
        """
        Draw all UI.

        Args:
            surface: Surface to draw to
        """
        if self.current_menu:
            self.current_menu.draw(surface)

        if self.hud:
            self.hud.draw(surface)

    def handle_event(self, event: pg.event.Event) -> Optional[MenuAction]:
        """
        Handle pygame event.

        Args:
            event: Pygame event

        Returns:
            MenuAction if triggered
        """
        if self.current_menu:
            return self.current_menu.handle_event(event)
        return None

    def show_main_menu(self) -> None:
        """Show main menu."""
        self.current_menu = self.main_menu
        if self.main_menu:
            self.main_menu.show()

    def show_pause_menu(self) -> None:
        """Show pause menu."""
        self.current_menu = self.pause_menu
        if self.pause_menu:
            self.pause_menu.show()

    def hide_menu(self) -> None:
        """Hide current menu."""
        if self.current_menu:
            self.current_menu.hide()
        self.current_menu = None

    def show_hud(self) -> None:
        """Show HUD."""
        if self.hud:
            self.hud.labels["score_label"].visible = True

    def hide_hud(self) -> None:
        """Hide HUD."""
        if self.hud:
            for label in self.hud.labels.values():
                label.visible = False
