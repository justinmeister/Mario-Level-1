__author__ = 'justinarmstrong'

import pygame as pg
from .. import constants as c
from .. import setup

class Mushroom(pg.sprite.Sprite):

    def __init__(self, x, y):
        super(Mushroom, self).__init__()
        self.sprite_sheet = setup.GFX['item_objects']
        self.frames = []
        self.frame_index = 0
        self.set_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.state = c.REVEAL
        self.y_vel = -1
        self.x_vel = 0
        self.direction = c.RIGHT
        self.box_height = y
        self.gravity = 1
        self.max_y_vel = 8


    def set_frames(self):
        self.frames.append(self.get_image(0, 0, 16, 16))


    def get_image(self, x, y, width, height):
        """Get the image frames from the sprite sheet"""

        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)


        image = pg.transform.scale(image,
                                   (int(rect.width*c.SIZE_MULTIPLIER),
                                    int(rect.height*c.SIZE_MULTIPLIER)))
        return image


    def update(self):
        self.handle_state()

    def handle_state(self):
        if self.state == c.REVEAL:
            self.revealing()
        elif self.state == c.SLIDE:
            self.sliding()
        elif self.state == c.FALL:
            self.falling()

    def revealing(self):
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.y_vel = 0
            self.state = c.SLIDE


    def sliding(self):
        if self.direction == c.RIGHT:
            self.x_vel = 3
        else:
            self.x_vel = -3


    def falling(self):
        if self.y_vel < self.max_y_vel:
            self.y_vel += self.gravity

