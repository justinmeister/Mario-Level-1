__author__ = 'justinarmstrong'

import pygame as pg
import collider
from .. import setup
from .. import constants as c

class Brick(pg.sprite.Sprite):
    """Bricks that can be destroyed"""

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['tile_set']

        self.image = self.get_image(15, 0, 17, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



    def get_image(self, x, y, width, height):
        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        #image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image


