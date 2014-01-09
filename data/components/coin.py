__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['tile_sheet']
