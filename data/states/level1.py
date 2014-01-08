__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. components import mario
from .. components import collider



class Level1(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persistant):
        self.persistant = persistant
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.collide_group = pg.sprite.Group(self.ground_group,
                                             self.pipe_group,
                                             self.step_group)
        self.background = setup.GFX['level_1']
        self.back_rect = self.background.get_rect()
        self.back_rect.x = 0
        self.back_rect.y = 0
        self.background = pg.transform.scale(self.background,
                                  (int(self.back_rect.width*c.BACK_SIZE_MULTIPLER),
                                  int(self.back_rect.height*c.BACK_SIZE_MULTIPLER)))

        self.mario = mario.Mario()
        self.all_sprites = pg.sprite.Group(self.mario)
        self.setup_mario_location()
        self.camera_adjust = 0




    def setup_mario_location(self):
        """Places Mario at the beginning of the level"""

        self.mario.rect.x = 110
        self.mario.rect.bottom = c.GROUND_HEIGHT


    def setup_ground(self):
        """Create collideable rects for each section of the ground"""

        self.ground_rect1 = collider.Collider(0, c.GROUND_HEIGHT,    2953, 60)
        self.ground_rect2 = collider.Collider(3048, c.GROUND_HEIGHT,  635, 60)
        self.ground_rect3 = collider.Collider(3819, c.GROUND_HEIGHT, 2735, 60)
        self.ground_rect4 = collider.Collider(6647, c.GROUND_HEIGHT, 2300, 60)

        self.ground_group = pg.sprite.Group(self.ground_rect1,
                                           self.ground_rect2,
                                           self.ground_rect3,
                                           self.ground_rect4)

    def setup_pipes(self):
        """Create collideable rects for all the pipes"""

        self.pipe1 = collider.Collider(1202, 452, 83, 82)
        self.pipe2 = collider.Collider(1631, 409, 83, 140)
        self.pipe3 = collider.Collider(1973, 366, 83, 170)
        self.pipe4 = collider.Collider(2445, 366, 83, 170)
        self.pipe5 = collider.Collider(6989, 452, 83, 82)
        self.pipe6 = collider.Collider(7675, 452, 83, 82)

        self.pipe_group = pg.sprite.Group(self.pipe1, self.pipe2,
                                          self.pipe3, self.pipe4,
                                          self.pipe5, self.pipe6)

    def setup_steps(self):
        """Create collideable rects for all the steps"""

        self.step1 = collider.Collider(5745, 495, 40, 44)
        self.step2 = collider.Collider(5788, 452, 40, 44)
        self.step3 = collider.Collider(5831, 409, 40, 44)
        self.step4 = collider.Collider(5874, 366, 40, 176)


        self.step5 = collider.Collider(6001, 366, 40, 176)
        self.step6 = collider.Collider(6044, 408, 40, 40)
        self.step7 = collider.Collider(6087, 452, 40, 40)
        self.step8 = collider.Collider(6130, 495, 40, 40)

        self.step9 = collider.Collider(6345, 495, 40, 40)
        self.step10 = collider.Collider(6388, 452, 40, 40)
        self.step11 = collider.Collider(6431, 409, 40, 40)
        self.step12 = collider.Collider(6474, 366, 40, 40)
        self.step13 = collider.Collider(6517, 366, 40, 176)

        self.step14 = collider.Collider(6644, 366, 40, 176)
        self.step15 = collider.Collider(6687, 408, 40, 40)
        self.step16 = collider.Collider(6728, 452, 40, 40)
        self.step17 = collider.Collider(6771, 495, 40, 40)

        self.step18 = collider.Collider(7760, 495, 40, 40)
        self.step19 = collider.Collider(7803, 452, 40, 40)
        self.step20 = collider.Collider(7845, 409, 40, 40)
        self.step21 = collider.Collider(7888, 366, 40, 40)
        self.step22 = collider.Collider(7931, 323, 40, 40)
        self.step23 = collider.Collider(7974, 280, 40, 40)
        self.step24 = collider.Collider(8017, 237, 40, 40)
        self.step25 = collider.Collider(8060, 194, 40, 40)
        self.step26 = collider.Collider(8103, 194, 40, 360)

        self.step27 = collider.Collider(8488, 495, 40, 40)



        self.step_group = pg.sprite.Group(self.step1, self.step2,
                                          self.step3, self.step4,
                                          self.step5, self.step6,
                                          self.step7, self.step8,
                                          self.step9, self.step10,
                                          self.step11, self.step12,
                                          self.step13, self.step14,
                                          self.step15, self.step16,
                                          self.step17, self.step18,
                                          self.step19, self.step20,
                                          self.step21, self.step22,
                                          self.step23, self.step24,
                                          self.step25, self.step26,
                                          self.step27)


    def camera(self):
        if self.mario.rect.right > c.SCREEN_WIDTH / 3:
            self.camera_adjust = self.mario.rect.right - c.SCREEN_WIDTH / 3
        else:
            self.camera_adjust = 0

        self.back_rect.x -= self.camera_adjust

        for collider in self.collide_group:
            collider.rect.x -= self.camera_adjust

        self.mario.rect.x -= self.camera_adjust


    def update_mario_position(self, keys):
        self.mario.rect.y += self.mario.y_vel

        collider = pg.sprite.spritecollideany(self.mario, self.collide_group)

        if collider:
            if self.mario.y_vel > 0:
                self.mario.y_vel = 0
                self.mario.rect.bottom = collider.rect.top
                self.mario.state = c.WALK
        else:
            test_sprite = copy.deepcopy(self.mario)
            test_sprite.rect.y += 1
            if not pg.sprite.spritecollideany(test_sprite, self.collide_group):
                if self.mario.state != c.JUMP:
                    self.mario.state = c.FALL

        self.mario.rect.x += self.mario.x_vel

        collider = pg.sprite.spritecollideany(self.mario, self.collide_group)

        if collider:
            if self.mario.x_vel > 0:
                self.mario.rect.right = collider.rect.left
            else:
                self.mario.rect.left = collider.rect.right

            self.mario.x_vel = 0

        if self.mario.rect.y > c.SCREEN_HEIGHT:
            self.startup(keys, self.persistant)

        if self.mario.rect.x < 5:
            self.mario.rect.x = 5


    def check_for_reset(self, keys):
        if self.mario.dead:
            self.startup(keys, self.persistant)



    def update(self, surface, keys, current_time):
        """Updates level"""

        self.current_time = current_time
        self.mario.update(keys, current_time, self.collide_group)
        #self.update_mario_position(keys)
        self.camera()
        surface.blit(self.background, self.back_rect)
        self.all_sprites.draw(surface)
        self.check_for_reset(keys)
        #self.ground_group.draw(surface)
        #self.pipe_group.draw(surface)
        #self.step_group.draw(surface)


