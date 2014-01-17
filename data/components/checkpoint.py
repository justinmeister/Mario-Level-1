__author__ = 'justinarmstrong'

import pygame as pg
from .. import constants as c



class Checkpoint(pg.sprite.Sprite):
    def __init__(self, x, name):
        super(Checkpoint, self).__init__()
        self.image = pg.Surface((10, 600))
        self.image.fill(c.BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.name = name




