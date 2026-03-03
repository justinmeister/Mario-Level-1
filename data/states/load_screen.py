"""Load screen states for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pygame as pg

from .. import tools
from .. import constants as c
from .. import game_sound
from ..components import info


class LoadScreen(tools._State):
    def __init__(self) -> None:
        tools._State.__init__(self)

    def startup(self, current_time: float, persist: Dict[str, Any]) -> None:
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist
        self.next = self.set_next_state()

        info_state = self.set_overhead_info_state()

        self.overhead_info = info.OverheadInfo(self.game_info, info_state)
        self.sound_manager: Optional[game_sound.Sound] = None

    def set_next_state(self) -> str:
        """Sets the next state based on current level"""
        current_level = self.persist.get(c.CURRENT_LEVEL, c.LEVEL1)

        if current_level == c.LEVEL1:
            return c.LEVEL1
        elif current_level == c.LEVEL2:
            return c.LEVEL2
        elif current_level == c.LEVEL3:
            return c.LEVEL3
        elif current_level == c.LEVEL4:
            return c.LEVEL4
        elif current_level == c.LEVEL5:
            return c.LEVEL5
        elif current_level == c.LEVEL6:
            return c.LEVEL6
        elif current_level == c.LEVEL7:
            return c.LEVEL7
        elif current_level == c.LEVEL8:
            return c.LEVEL8
        else:
            return c.LEVEL1

    def set_overhead_info_state(self) -> str:
        """sets the state to send to the overhead info object"""
        return c.LOAD_SCREEN

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        """Updates the loading screen"""
        if (current_time - self.start_time) < 2400:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)

        elif (current_time - self.start_time) < 2600:
            surface.fill(c.BLACK)

        elif (current_time - self.start_time) < 2635:
            surface.fill((106, 150, 252))

        else:
            self.done = True


class GameOver(LoadScreen):
    """A loading screen with Game Over"""

    def __init__(self) -> None:
        super(GameOver, self).__init__()

    def set_next_state(self) -> str:
        """Sets next state"""
        return c.MAIN_MENU

    def set_overhead_info_state(self) -> str:
        """sets the state to send to the overhead info object"""
        return c.GAME_OVER

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        self.current_time = current_time
        if self.sound_manager:
            self.sound_manager.update(self.persist, None)

        if (self.current_time - self.start_time) < 7000:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        elif (self.current_time - self.start_time) < 7200:
            surface.fill(c.BLACK)
        elif (self.current_time - self.start_time) < 7235:
            surface.fill((106, 150, 252))
        else:
            self.done = True


class TimeOut(LoadScreen):
    """Loading Screen with Time Out"""

    def __init__(self) -> None:
        super(TimeOut, self).__init__()

    def set_next_state(self) -> str:
        """Sets next state"""
        if self.persist[c.LIVES] == 0:
            return c.GAME_OVER
        else:
            return c.LOAD_SCREEN

    def set_overhead_info_state(self) -> str:
        """Sets the state to send to the overhead info object"""
        return c.TIME_OUT

    def update(self, surface: pg.Surface, keys: Tuple[bool, ...], current_time: float) -> None:
        self.current_time = current_time

        if (self.current_time - self.start_time) < 2400:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.game_info)
            self.overhead_info.draw(surface)
        else:
            self.done = True
