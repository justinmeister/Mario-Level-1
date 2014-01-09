__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. components import mario
from .. components import collider
from .. components import break_brick
from .. components import coin_box



class Level1(tools._State):
    def __init__(self):
        tools._State.__init__(self)

    def startup(self, current_time, persistant):
        self.persistant = persistant
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.setup_bricks()
        self.setup_coin_boxes()
        self.collide_group = pg.sprite.Group(self.ground_group,
                                             self.pipe_group,
                                             self.step_group,
                                             self.brick_group,
                                             self.coin_box_group)

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

    def setup_bricks(self):
        self.brick1  = break_brick.Brick(858,  365)
        self.brick2  = break_brick.Brick(944,  365)
        self.brick3  = break_brick.Brick(1030, 365)
        self.brick4  = break_brick.Brick(3299, 365)
        self.brick5  = break_brick.Brick(3385, 365)
        self.brick6  = break_brick.Brick(3430, 193)
        self.brick7  = break_brick.Brick(3473, 193)
        self.brick8  = break_brick.Brick(3516, 193)
        self.brick9  = break_brick.Brick(3559, 193)
        self.brick10 = break_brick.Brick(3602, 193)
        self.brick11 = break_brick.Brick(3645, 193)
        self.brick12 = break_brick.Brick(3688, 193)
        self.brick13 = break_brick.Brick(3731, 193)
        self.brick14 = break_brick.Brick(3901, 193)
        self.brick15 = break_brick.Brick(3944, 193)
        self.brick16 = break_brick.Brick(3987, 193)
        self.brick17 = break_brick.Brick(4030, 365)
        self.brick18 = break_brick.Brick(4287, 365)
        self.brick19 = break_brick.Brick(4330, 365)
        self.brick20 = break_brick.Brick(5058, 365)
        self.brick21 = break_brick.Brick(5187, 193)
        self.brick22 = break_brick.Brick(5230, 193)
        self.brick23 = break_brick.Brick(5273, 193)
        self.brick24 = break_brick.Brick(5488, 193)
        self.brick25 = break_brick.Brick(5574, 193)
        self.brick26 = break_brick.Brick(5617, 193)
        self.brick27 = break_brick.Brick(5531, 365)
        self.brick28 = break_brick.Brick(5574, 365)
        self.brick29 = break_brick.Brick(7202, 365)
        self.brick30 = break_brick.Brick(7245, 365)
        self.brick31 = break_brick.Brick(7331, 365)



        self.brick_group = pg.sprite.Group(self.brick1,  self.brick2,
                                           self.brick3,  self.brick4,
                                           self.brick5,  self.brick6,
                                           self.brick7,  self.brick8,
                                           self.brick9,  self.brick10,
                                           self.brick11, self.brick12,
                                           self.brick13, self.brick14,
                                           self.brick15, self.brick16,
                                           self.brick17, self.brick18,
                                           self.brick19, self.brick20,
                                           self.brick21, self.brick22,
                                           self.brick23, self.brick24,
                                           self.brick25, self.brick26,
                                           self.brick27, self.brick28,
                                           self.brick29, self.brick30,
                                           self.brick31)


    def setup_coin_boxes(self):
        self.coin_box1  = coin_box.Coin_box(685, 365)
        self.coin_box2  = coin_box.Coin_box(901, 365)
        self.coin_box3  = coin_box.Coin_box(987, 365)
        self.coin_box4  = coin_box.Coin_box(943, 193)
        self.coin_box5  = coin_box.Coin_box(3342, 365)
        self.coin_box6  = coin_box.Coin_box(4030, 193)
        self.coin_box7  = coin_box.Coin_box(4544, 365)
        self.coin_box8  = coin_box.Coin_box(4672, 365)
        self.coin_box9  = coin_box.Coin_box(4672, 193)
        self.coin_box10 = coin_box.Coin_box(4800, 365)
        self.coin_box11 = coin_box.Coin_box(5531, 193)
        self.coin_box12 = coin_box.Coin_box(7288, 365)

        self.coin_box_group = pg.sprite.Group(self.coin_box1, self.coin_box2,
                                              self.coin_box3, self.coin_box4,
                                              self.coin_box5, self.coin_box6,
                                              self.coin_box7, self.coin_box8,
                                              self.coin_box9, self.coin_box10,
                                              self.coin_box11, self.coin_box12)



    def camera(self):
        if self.mario.rect.right > c.SCREEN_WIDTH / 3:
            self.camera_adjust = self.mario.rect.right - c.SCREEN_WIDTH / 3
        else:
            self.camera_adjust = 0

        self.back_rect.x -= self.camera_adjust

        for collider in self.collide_group:
            collider.rect.x -= self.camera_adjust

        self.mario.rect.x -= self.camera_adjust



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
        self.brick_group.draw(surface)
        self.coin_box_group.draw(surface)


