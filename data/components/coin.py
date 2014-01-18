__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup
from .. import constants as c


class Coin(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['item_objects']
        self.frames = []
        self.frame_index = 0
        self.animation_timer = 0
        self.state = c.SPIN
        self.setup_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y - 5
        self.gravity = 1
        self.y_vel = -15
        self.initial_height = self.rect.bottom - 5


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


    def setup_frames(self):
        self.frames.append(self.get_image(52, 113, 8, 14))
        self.frames.append(self.get_image(4, 113, 8, 14))
        self.frames.append(self.get_image(20, 113, 8, 14))
        self.frames.append(self.get_image(36, 113, 8, 14))


    def update(self, current_time):
        if self.state == c.SPIN:
            self.spinning(current_time)


    def spinning(self, current_time):
        self.image = self.frames[self.frame_index]
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if (current_time - self.animation_timer) > 80:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.animation_timer = current_time

        if self.rect.bottom > self.initial_height:
            self.kill()






