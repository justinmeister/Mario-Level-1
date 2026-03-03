"""Game controller module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import pygame as pg

if TYPE_CHECKING:
    from pygame.surface import Surface

    from .states import _State

__all__ = ["Control"]


class Control:
    """
    Control class for entire project.

    Contains the game loop, and contains the event_loop which passes events
    to States as needed. Logic for flipping states is also found here.

    Attributes:
        screen: Main display surface
        done: Flag to indicate game loop should end
        clock: Pygame clock for FPS control
        caption: Window title
        fps: Target frames per second
        show_fps: Whether to display FPS in window title
        current_time: Current game time in milliseconds
        keys: Current state of keyboard
        state_dict: Dictionary of game states
        state_name: Name of current state
        state: Current state object
    """

    def __init__(self, caption: str, enable_profiler: bool = False) -> None:
        """Initialize the game controller."""
        # ensure pygame modules are initialized (tests may not have done so)
        pg.init()
        self.screen: Optional["Surface"] = pg.display.get_surface()
        if not self.screen:
            try:
                # create a tiny hidden surface to allow key functions
                self.screen = pg.display.set_mode((1, 1))
            except pg.error:
                self.screen = None  # headless environment
        self.done: bool = False
        self.clock: pg.time.Clock = pg.time.Clock()
        self.caption: Optional[str] = caption
        self.fps: int = 60
        self.show_fps: bool = False
        self.current_time: float = 0.0
        try:
            self.keys: Tuple[bool, ...] = pg.key.get_pressed()
        except pg.error:
            self.keys = tuple()
        self.state_dict: Dict[str, "_State"] = {}
        self.state_name: str = ""
        self.state: Optional["_State"] = None

        # Profiler integration
        self.profiler = None
        if enable_profiler:
            from ..profiler import Profiler

            self.profiler = Profiler()

    def setup_states(self, state_dict: Dict[str, "_State"], start_state: str) -> None:
        """
        Initialize game states.

        Args:
            state_dict: Dictionary mapping state names to State objects
            start_state: Name of the initial state
        """
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def update(self) -> None:
        """Update current state and check for state transitions."""
        self.current_time = pg.time.get_ticks()
        if self.state is None or self.screen is None:
            return

        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()

        if self.profiler:
            with self.profiler.profile("state_update"):
                self.state.update(self.screen, self.keys, self.current_time)
        else:
            self.state.update(self.screen, self.keys, self.current_time)

    def flip_state(self) -> None:
        """Transition to the next state, passing persistent data."""
        if self.state is None:
            return
        previous = self.state_name
        self.state_name = self.state.next or ""
        persist = self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)
        self.state.previous = previous

    def event_loop(self) -> None:
        """Process pygame events and pass them to the current state."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                self.toggle_show_fps(event.key)
                # Toggle profiler overlay with F3
                if event.key == pg.K_F3 and self.profiler:
                    self.profiler.toggle_overlay()
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            if self.state is not None:
                self.state.get_event(event)

    def toggle_show_fps(self, key: int) -> None:
        """
        Toggle FPS display on/off.

        Args:
            key: The key that was pressed
        """
        if key == pg.K_F5:
            self.show_fps = not self.show_fps
            if not self.show_fps and self.caption:
                pg.display.set_caption(self.caption)

    def main(self) -> None:
        """Main game loop - processes events, updates state, renders."""
        if self.profiler:
            self.profiler.start()

        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)

            if self.profiler:
                self.profiler.end_frame()
                if self.screen:
                    self.profiler.draw_overlay(self.screen)

            if self.show_fps and self.caption:
                fps = self.clock.get_fps()
                with_fps = "{} - {:.2f} FPS".format(self.caption, fps)
                pg.display.set_caption(with_fps)
