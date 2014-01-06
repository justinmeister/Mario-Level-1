__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. components import mario



class Level1(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persistant):
        self.setup_ground()
        self.background = setup.GFX['level_1']
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                   (int(self.back_rect.width*c.BACK_SIZE_MULTIPLER),
                                    int(self.back_rect.height*c.BACK_SIZE_MULTIPLER)))
        self.mario = mario.Mario()
        self.setup_mario_location()
        self.all_sprites = pg.sprite.Group(self.mario)
        self.camera_adjust = 0


    def setup_mario_location(self):
        self.mario.rect.x = 10
        self.mario.rect.bottom = c.SCREEN_HEIGHT - c.GROUND_HEIGHT

    def setup_ground(self):
        pass

    def camera(self):
        if self.mario.rect.right > c.SCREEN_WIDTH / 3:
            self.camera_adjust = self.mario.rect.right - c.SCREEN_WIDTH / 3
        else:
            self.camera_adjust = 0

        self.back_rect.x -= self.camera_adjust
        for sprite in self.all_sprites:
            sprite.rect.x -= self.camera_adjust

    def update(self, surface, keys, current_time):
        """Updates level"""
        self.current_time = current_time
        surface.blit(self.background, self.back_rect)
        self.all_sprites.update(keys, current_time)
        self.camera()
        self.all_sprites.draw(surface)

