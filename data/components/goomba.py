__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup
from .. import constants as c


class Goomba(pg.sprite.Sprite):

    def __init__(self, x, y, direction, name):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['smb_enemies_sheet']
        self.name = name
        self.frames = []
        self.frame_index = 0
        self.animate_timer = 0
        self.gravity = .4
        self.setup_frames()

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y
        self.direction = direction
        self.state = c.WALK

        if self.direction == c.LEFT:
            self.x_vel = c.GOOMBA_VEL * -1
        else:
            self.x_vel = c.GOOMBA_VEL

        self.y_vel = 0


    def setup_frames(self):
        """Put the image frames in a list to be animated"""

        self.frames.append(
            self.get_image(0, 4, 16, 16))
        self.frames.append(
            self.get_image(30, 4, 16, 16))


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




    def handle_state(self, current_time):
        if self.state == c.WALK:
            self.walking(current_time)
        elif self.state == c.FALL:
            self.falling(current_time)
        elif self.state == c.JUMPED_ON:
            self.jumped_on(current_time)



    def walking(self, current_time):
        if (current_time - self.animate_timer) > 125:
            if self.frame_index == 0:
                self.frame_index += 1
            elif self.frame_index == 1:
                self.frame_index = 0

            self.animate_timer = current_time

    def falling(self, current_time):
        self.y_vel += self.gravity





    def animation(self):
        self.image = self.frames[self.frame_index]


    def update(self, current_time, colliders):
        self.handle_state(current_time)
        self.animation()








