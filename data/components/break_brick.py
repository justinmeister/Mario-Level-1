__author__ = 'justinarmstrong'

import pygame as pg
import collider
from .. import setup
from .. import constants as c

class Brick(pg.sprite.Sprite):
    """Bricks that can be destroyed"""

    def __init__(self, x, y, name = 'brick'):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['tile_set']

        self.image = self.get_image(16, 0, 16, 16)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.bumped_up = False
        self.rest_height = y
        self.state = c.RESTING
        self.y_vel = 0
        self.gravity = 1.2



    def get_image(self, x, y, width, height):
        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        #image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image


    def update(self):
        self.handle_states()


    def handle_states(self):
        if self.state == c.RESTING:
            pass
        elif self.state == c.BUMPED:
            self.bumped()


    def bumped(self):

        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y >= (self.rest_height + 5):
            self.rect.y = self.rest_height
            self.state = c.RESTING


    def start_bump(self):
        self.y_vel = -6








