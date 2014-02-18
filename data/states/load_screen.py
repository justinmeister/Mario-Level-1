__author__ = 'justinarmstrong'

from .. import setup, tools
from .. import constants as c
from ..components import info


class Load_Screen(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persist):
        self.next = self.determine_next_game_state(persist)
        self.start_time = current_time
        self.persist = persist
        self.game_info = self.persist

        self.overhead_info = info.OverheadInfo(self.game_info, c.LOAD_SCREEN)


    def determine_next_game_state(self, game_info):
        """Checks if it's a game over"""
        if game_info[c.LIVES] > 0:
            self.next = c.LEVEL1
        else:
            self.next = c.MAIN_MENU

        return self.next


    def update(self, surface, keys, current_time):
        """Updates the loading screen"""
        if self.next == c.LEVEL1:
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

        elif self.next == c.MAIN_MENU:
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




