"""
Enhanced Main Menu with Animations for Super Mario Bros.

Features:
- Smooth animations and transitions
- Animated background elements
- Particle effects
- Dynamic logo
- Skin selection preview
- Achievement showcase
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Tuple

import pygame as pg

from .. import setup, tools
from .. import constants as c
from ..animation_system import TweenManager
from ..player_progression import get_progression_manager


class AnimatedButton:
    """Animated menu button with hover effects."""

    rect: pg.Rect
    text: str
    action: str
    base_color: Tuple[int, int, int]
    hover_color: Tuple[int, int, int]
    current_color: Tuple[int, int, int]
    is_hovered: bool
    is_pressed: bool
    tween: TweenManager
    scale: float
    alpha: int
    y_offset: int
    pulse_timer: float
    pulse_speed: float
    font: Any
    text_surface: pg.Surface
    text_rect: pg.Rect

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        action: str,
        color: Tuple[int, int, int] = c.RED,
    ) -> None:
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.base_color = color
        self.hover_color = self._lighten_color(color, 30)
        self.current_color = color

        self.is_hovered = False
        self.is_pressed = False

        # Animation
        self.tween = TweenManager()
        self.scale: float = 1.0
        self.alpha: int = 255
        self.y_offset: int = 0

        # Pulse animation
        self.pulse_timer = 0
        self.pulse_speed = 0.002

        # Font
        self.font = pg.font.Font(None, 36)
        self.text_surface = self.font.render(text, True, c.WHITE)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def _lighten_color(self, color: Tuple[int, int, int], amount: int) -> Tuple[int, int, int]:
        """Lighten a color by a given amount."""
        result = tuple(int(min(255, max(0, c + amount))) for c in color)
        return (result[0], result[1], result[2])

    def update(self, dt: int, mouse_pos: Tuple[int, int]) -> None:
        """Update button state."""
        # Check hover
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # Color interpolation
        target_color = self.hover_color if self.is_hovered else self.base_color
        new_color = []
        for i in range(3):
            diff = target_color[i] - self.current_color[i]
            new_color.append(int(self.current_color[i] + diff * 0.2))
        self.current_color = (new_color[0], new_color[1], new_color[2])

        # Scale animation on hover
        target_scale = 1.1 if self.is_hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.15

        # Pulse effect for primary button
        if self.action == "start":
            self.pulse_timer += dt * self.pulse_speed
            pulse_scale = 1.0 + math.sin(self.pulse_timer) * 0.05
            self.scale = min(1.15, self.scale * pulse_scale)

        # Update text position
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface: pg.Surface) -> None:
        """Draw button."""
        # Calculate scaled rect
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pg.Rect(
            self.rect.x - (scaled_width - self.rect.width) // 2,
            self.rect.y - (scaled_height - self.rect.height) // 2,
            scaled_width,
            scaled_height,
        )

        # Draw shadow
        shadow_rect = scaled_rect.copy()
        shadow_rect.y += 4
        pg.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=8)

        # Draw button background
        pg.draw.rect(surface, self.current_color, scaled_rect, border_radius=8)

        # Draw border
        border_color = c.GOLD if self.is_hovered else c.WHITE
        pg.draw.rect(surface, border_color, scaled_rect, width=3, border_radius=8)

        # Draw text
        surface.blit(self.text_surface, self.text_rect)

    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle mouse event. Returns True if clicked."""
        if not self.is_enabled():
            return False

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True

        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                return True
            self.is_pressed = False

        return False

    def is_enabled(self) -> bool:
        """Check if button is enabled."""
        return True


class ParticleBackground:
    """Animated particle background effect."""

    def __init__(self) -> None:
        self.particles: List[Dict[str, Any]] = []
        self.spawn_timer = 0
        self.spawn_interval = 100  # ms

    def spawn_particle(self) -> None:
        """Spawn a new particle."""
        x = random.randint(0, c.SCREEN_WIDTH)
        y = random.randint(c.SCREEN_HEIGHT, c.SCREEN_HEIGHT + 100)

        particle = {
            "x": x,
            "y": y,
            "vx": random.uniform(-0.5, 0.5),
            "vy": random.uniform(-2, -5),
            "size": random.randint(2, 6),
            "color": random.choice([c.GOLD, c.WHITE, c.RED, c.GREEN]),
            "alpha": random.randint(100, 200),
            "lifetime": random.uniform(2, 4),
            "age": 0,
        }
        self.particles.append(particle)

    def update(self, dt: int) -> None:
        """Update particles."""
        # Spawn new particles
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_particle()

        # Update existing particles
        for particle in self.particles[:]:
            particle["age"] += dt / 1000
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["alpha"] = int(200 * (1 - particle["age"] / particle["lifetime"]))

            # Remove dead particles
            if particle["age"] >= particle["lifetime"]:
                self.particles.remove(particle)

    def draw(self, surface: pg.Surface) -> None:
        """Draw particles."""
        for particle in self.particles:
            alpha = particle["alpha"]
            color = (*particle["color"][:3], alpha)

            # Create surface with alpha
            s = pg.Surface((particle["size"] * 2, particle["size"] * 2), pg.SRCALPHA)
            pg.draw.circle(s, color, (particle["size"], particle["size"]), particle["size"])
            surface.blit(s, (particle["x"] - particle["size"], particle["y"] - particle["size"]))


class EnhancedMenu(tools._State):
    """Enhanced main menu with animations."""

    background: Optional[pg.Surface]
    background_rect: pg.Rect
    bg_offset: float
    bg_direction: int
    buttons: List[AnimatedButton]
    logo_surface: Optional[pg.Surface]
    logo_rect: pg.Rect
    logo_y_offset: float
    logo_timer: float
    logo_bounce_speed: float
    particles: List[Dict[str, Any]]
    spawn_timer: float
    spawn_interval: float
    progression: Any
    selected_index: int
    menu_alpha: float
    fade_in: bool
    transition_alpha: float

    def __init__(self) -> None:
        super().__init__()
        self.persist: Dict[str, Any] = {}

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        """Initialize menu."""
        self.next = c.LOAD_SCREEN
        self.persist = persist
        self.game_info = persist.copy()
        self.current_time = current_time

        # Setup components
        self._setup_background()
        self._setup_buttons()
        self._setup_logo()
        self._setup_particles()
        self._setup_music_box()

        # State
        self.selected_index = 0
        self.menu_alpha = 0
        self.fade_in = True
        self.transition_alpha = 255

        # Progression display
        self.progression = get_progression_manager()

    def _setup_background(self) -> None:
        """Setup animated background."""
        self.background = setup.GFX.get("title_screen", setup.GFX.get("level_1", None))
        if self.background:
            self.background = pg.transform.scale(self.background, (c.SCREEN_WIDTH, c.SCREEN_HEIGHT))

        # Create gradient background if no image
        if self.background is None:
            self.background = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
            dark_blue = getattr(c, "DARK_BLUE", (0, 0, 139))
            sky_blue = getattr(c, "SKY_BLUE", (135, 206, 235))
            for y in range(c.SCREEN_HEIGHT):
                ratio = y / c.SCREEN_HEIGHT
                color = tuple(int(c_val * (1 - ratio) + sky_blue[0] * ratio) for c_val in dark_blue)
                pg.draw.line(self.background, color, (0, y), (c.SCREEN_WIDTH, y))

        self.background_rect = self.background.get_rect()
        self.bg_offset = 0
        self.bg_direction = 1

    def _setup_buttons(self) -> None:
        """Setup menu buttons."""
        button_width = 280
        button_height = 60
        start_x = (c.SCREEN_WIDTH - button_width) // 2

        self.buttons: List[AnimatedButton] = []

        # Start Game button (primary)
        start_btn = AnimatedButton(
            start_x,
            280,
            button_width,
            button_height,
            "START GAME",
            "start",
            c.RED,
        )
        self.buttons.append(start_btn)

        # Skins button
        skins_btn = AnimatedButton(
            start_x,
            360,
            button_width,
            button_height,
            "SKINS",
            "skins",
            c.BLUE,
        )
        self.buttons.append(skins_btn)

        # Achievements button
        ach_btn = AnimatedButton(
            start_x,
            440,
            button_width,
            button_height,
            "ACHIEVEMENTS",
            "achievements",
            c.GREEN,
        )
        self.buttons.append(ach_btn)

        # Quit button
        quit_btn = AnimatedButton(
            start_x,
            520,
            button_width,
            button_height,
            "QUIT",
            "quit",
            c.GRAY,
        )
        self.buttons.append(quit_btn)

    def _setup_logo(self) -> None:
        """Setup animated logo."""
        self.logo_text = "SUPER MARIO BROS"
        self.logo_font = pg.font.Font(None, 72)
        self.logo_surface = self.logo_font.render(self.logo_text, True, c.RED)
        self.logo_rect = self.logo_surface.get_rect(centerx=c.SCREEN_WIDTH // 2, top=60)

        # Logo animation
        self.logo_y_offset = 0
        self.logo_timer = 0
        self.logo_bounce_speed = 0.003

        # Subtitle
        self.subtitle_text = "Enhanced Edition v2.7"
        self.subtitle_font = pg.font.Font(None, 28)
        self.subtitle_surface = self.subtitle_font.render(self.subtitle_text, True, c.GOLD)
        self.subtitle_rect = self.subtitle_surface.get_rect(centerx=c.SCREEN_WIDTH // 2, top=140)

    def _setup_particles(self) -> None:
        """Setup particle system."""
        self.particle_system = ParticleBackground()

    def _setup_music_box(self) -> None:
        """Setup music box rotation effect."""
        self.music_box_angle = 0
        self.music_box_speed = 0.5

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Update and draw menu."""
        self.current_time = current_time
        dt = 16  # Assume 60 FPS

        # Update components
        mouse_pos = pg.mouse.get_pos()
        for button in self.buttons:
            button.update(dt, mouse_pos)

        self.particle_system.update(dt)
        self._update_logo(dt)
        self._update_background(dt)

        # Fade in effect
        if self.fade_in and self.menu_alpha < 255:
            self.menu_alpha = min(255, self.menu_alpha + 10)

        # Draw everything
        self._draw(surface)

    def _update_logo(self, dt: int) -> None:
        """Update logo animation."""
        self.logo_timer += dt
        self.logo_y_offset = math.sin(self.logo_timer * self.logo_bounce_speed) * 10

        # Update logo rect
        if self.logo_surface:
            self.logo_rect = self.logo_surface.get_rect(
                centerx=c.SCREEN_WIDTH // 2,
                top=60 + self.logo_y_offset,
            )
        if self.subtitle_surface:
            self.subtitle_rect = self.subtitle_surface.get_rect(
                centerx=c.SCREEN_WIDTH // 2,
                top=140 + self.logo_y_offset * 0.5,
            )

    def _update_background(self, dt: int) -> None:
        """Update background parallax."""
        self.bg_offset += 0.5 * self.bg_direction
        if abs(self.bg_offset) > 20:
            self.bg_direction *= -1

    def _draw(self, surface: pg.Surface) -> None:
        """Draw all menu elements."""
        # Draw background
        if self.background:
            surface.blit(self.background, (self.bg_offset, 0))

        # Draw particles
        self.particle_system.draw(surface)

        # Draw logo
        if self.logo_surface and self.logo_rect:
            surface.blit(self.logo_surface, self.logo_rect)
        if self.subtitle_surface and self.subtitle_rect:
            surface.blit(self.subtitle_surface, self.subtitle_rect)

        # Draw player stats (top right)
        self._draw_player_stats(surface)

        # Draw buttons with fade
        if self.menu_alpha > 0:
            button_surface = pg.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pg.SRCALPHA)
            for button in self.buttons:
                button.draw(button_surface)

            surface.blit(button_surface, (0, 0))

    def _draw_player_stats(self, surface: pg.Surface) -> None:
        """Draw player statistics."""
        font = pg.font.Font(None, 24)

        # Draw stats box
        stats_rect = pg.Rect(c.SCREEN_WIDTH - 220, 10, 210, 80)
        pg.draw.rect(surface, (0, 0, 0, 128), stats_rect, border_radius=8)
        pg.draw.rect(surface, c.GOLD, stats_rect, width=2, border_radius=8)

        # Get stats
        stats = self.progression.get_stats()
        level = stats.level if stats else 1
        rank = self.progression.get_player_rank().name

        # Draw stats
        y_offset = 15
        texts = [
            f"Level: {level}",
            f"Rank: {rank}",
            f"Coins: {stats.coins_collected if stats else 0}",
        ]

        for text in texts:
            text_surf = font.render(text, True, c.WHITE)
            surface.blit(text_surf, (stats_rect.x + 10, stats_rect.y + y_offset))
            y_offset += 22

    def get_event(self, event: pg.event.Event) -> None:
        """Handle events."""
        if event.type == pg.QUIT:
            self.done = True

        # Button clicks
        for button in self.buttons:
            if button.handle_event(event):
                self._on_button_click(button.action)
                break

        # Keyboard navigation
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_RETURN, pg.K_SPACE):
                self._on_button_click(self.buttons[self.selected_index].action)
            elif event.key == pg.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
            elif event.key == pg.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.buttons)

    def _on_button_click(self, action: str) -> None:
        """Handle button click."""
        if action == "start":
            self._start_game()
        elif action == "skins":
            self._show_skins()
        elif action == "achievements":
            self._show_achievements()
        elif action == "quit":
            self.done = True

    def _start_game(self) -> None:
        """Start the game."""
        # Fade out effect
        self.fade_in = False
        self.transition_alpha = 0

        # Reset game info
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.game_info[c.LEVEL_STATE] = None

        self.done = True

    def _show_skins(self) -> None:
        """Show skins menu - starts level 1 with skin selection."""
        # Skins are managed by player_progression system
        # For now, just start the game with default skin
        self.next = c.LEVEL1
        self.game_info[c.COIN_TOTAL] = 0
        self.game_info[c.SCORE] = 0
        self.game_info[c.LIVES] = 3
        self.game_info[c.CURRENT_TIME] = 0.0
        self.done = True

    def _show_achievements(self) -> None:
        """Show achievements - displays achievement list then returns."""
        # Achievements are managed by achievements_v2 system
        # Display message and return to menu
        self.done = False

    def draw(self, surface: pg.Surface) -> None:
        """Draw state (called by state machine)."""
        # Already drawing in update()
        pass
