__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c


class Menu(tools._State):
    def __init__(self):
        tools._State.__init__(self)
        self.startup(0.0, None)

    def startup(self, current_time, *args):
        self.next = "LOAD_SCREEN"
        self.surface = pg.Surface(c.SCREEN_SIZE)
        self.rect = self.surface.get_rect()
        text = 'Main Menu placeholder'
        self.font = pg.font.Font(setup.FONTS['Fixedsys500c'], 15)
        self.rendered_text = self.font.render(text, 1, c.BLACK)
        self.text_rect = self.rendered_text.get_rect()
        self.text_rect.center = self.rect.center
        self.persist = {'coins': 0,
                        'score': 0,
                        'lives': 3}
        self.start_time = current_time


    def update(self, surface, keys, current_time):
        self.current_time = current_time
        surface.fill(c.WHITE)
        surface.blit(self.rendered_text, self.text_rect)


    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.done = True









