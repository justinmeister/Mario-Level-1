__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup
from .. import constants as c
import powerups
import coin



class Coin_box(pg.sprite.Sprite):
    """Coin box sprite"""

    def __init__(self, x, y, contents='coin', group=None):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['tile_set']
        self.frames = []
        self.setup_frames()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.animation_timer = 0
        self.first_half = True   # First half of animation cycle
        self.state = c.RESTING
        self.rest_height = y
        self.gravity = 1.2
        self.y_vel = 0
        self.contents = contents
        self.group = group



    def get_image(self, x, y, width, height):
        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image


    def setup_frames(self):
        self.frames.append(
            self.get_image(384, 0, 16, 16))
        self.frames.append(
            self.get_image(400, 0, 16, 16))
        self.frames.append(
            self.get_image(416, 0, 16, 16))
        self.frames.append(
            self.get_image(432, 0, 16, 16))


    def update(self, current_time):
        self.handle_states(current_time)


    def handle_states(self, current_time):
        if self.state == c.RESTING:
            self.resting(current_time)
        elif self.state == c.BUMPED:
            self.bumped()
        elif self.state == c.OPENED:
            self.opened()


    def resting(self, current_time):
        if self.first_half:
            if self.frame_index == 0:
                if (current_time - self.animation_timer) > 375:
                    self.frame_index += 1
                    self.animation_timer = current_time
            elif self.frame_index < 2:
                if (current_time - self.animation_timer) > 125:
                    self.frame_index += 1
                    self.animation_timer = current_time
            elif self.frame_index == 2:
                if (current_time - self.animation_timer) > 125:
                    self.frame_index -= 1
                    self.first_half = False
                    self.animation_timer = current_time
        else:
            if self.frame_index == 1:
                if (current_time - self.animation_timer) > 125:
                    self.frame_index -= 1
                    self.first_half = True
                    self.animation_timer = current_time

        self.image = self.frames[self.frame_index]


    def bumped(self):

        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y > self.rest_height + 5:
            self.rect.y = self.rest_height
            self.state = c.OPENED
            if self.contents == 'powerup':
                self.group.add(powerups.Mushroom(self.rect.centerx, self.rect.y))


        self.frame_index = 3
        self.image = self.frames[self.frame_index]


    def start_bump(self):
        self.y_vel = -6
        self.state = c.BUMPED

        if self.contents == 'coin':
            self.group.add(coin.Coin(self.rect.centerx, self.rect.y))


    def opened(self):
        pass











