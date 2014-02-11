__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from ..components import info


class Load_Screen(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persistant):
        self.start_time = current_time
        self.next = "LEVEL1"

        self.persist = persistant

        self.info_dict = {'coin_total': self.persist['coins'],
                          'score': self.persist['score'],
                          'current_time': 0,
                          'state': None}

        self.overhead_info = info.OverheadInfo(True, self.persist['lives'])


    def update(self, surface, keys, current_time):
        self.current_time = current_time

        if (self.current_time - self.start_time) < 2400:
            surface.fill(c.BLACK)
            self.overhead_info.update(self.info_dict)
            self.overhead_info.draw(surface)

        elif (self.current_time - self.start_time) < 2600:
            surface.fill(c.BLACK)

        elif (self.current_time - self.start_time) < 2635:
            surface.fill((106, 150, 252))

        else:
            self.done = True




