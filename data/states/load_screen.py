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
                          'current_time': 0}

        self.overhead_info = info.OverheadInfo(True)


    def update(self, surface, keys, current_time):
        self.current_time = current_time

        surface.fill(c.BLACK)

        self.overhead_info.update(self.info_dict)
        self.overhead_info.draw(surface)

        if (self.current_time - self.start_time) > 6000:
            self.done = True




