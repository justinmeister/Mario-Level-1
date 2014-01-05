__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c


class Load_Screen(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persistant):
        self.next = "LEVEL1"
        self.surface = pg.Surface(c.SCREEN_SIZE)
        self.rect = self.surface.get_rect()
        self.color = c.WHITE
        text = "Loading Screen Place Holder"
        self.font = pg.font.Font(setup.FONTS['Fixedsys500c'], 15)
        self.rendered_text = self.font.render(text, 1, c.BLACK)
        self.text_rect = self.rendered_text.get_rect()
        self.text_rect.center = self.rect.center

    def update(self, surface, keys, current_time):
        self.current_time = current_time
        surface.fill(c.WHITE)
        surface.blit(self.rendered_text, self.text_rect)

        if (self.current_time - self.start_time) > 5000:
            self.done = True


    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.done = True


