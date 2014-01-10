__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
from .. components import mario
from .. components import collider
from .. components import break_brick
from .. components import coin_box
from .. components import goomba



class Level1(tools._State):
    def __init__(self):
        tools._State.__init__(self)


    def startup(self, current_time, persistant):
        self.persistant = persistant
        self.camera_adjust = 0

        self.setup_background()
        self.setup_ground()
        self.setup_pipes()
        self.setup_steps()
        self.setup_bricks()
        self.setup_coin_boxes()
        self.setup_enemies()
        self.setup_mario()

        self.collide_group = pg.sprite.Group(self.ground_group,
                                             self.pipe_group,
                                             self.step_group,
                                             self.brick_group,
                                             self.coin_box_group)

        self.all_sprites = pg.sprite.Group(self.mario, self.enemies)


    def setup_background(self):
        self.background = setup.GFX['level_1']
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                  (int(self.back_rect.width*c.BACKGROUND_MULTIPLER),
                                  int(self.back_rect.height*c.BACKGROUND_MULTIPLER)))


    def setup_ground(self):
        """Create collideable rects for each section of the ground"""

        ground_rect1 = collider.Collider(0, c.GROUND_HEIGHT,    2953, 60)
        ground_rect2 = collider.Collider(3048, c.GROUND_HEIGHT,  635, 60)
        ground_rect3 = collider.Collider(3819, c.GROUND_HEIGHT, 2735, 60)
        ground_rect4 = collider.Collider(6647, c.GROUND_HEIGHT, 2300, 60)

        self.ground_group = pg.sprite.Group(ground_rect1,
                                           ground_rect2,
                                           ground_rect3,
                                           ground_rect4)


    def setup_pipes(self):
        """Create collideable rects for all the pipes"""

        pipe1 = collider.Collider(1202, 452, 83, 82)
        pipe2 = collider.Collider(1631, 409, 83, 140)
        pipe3 = collider.Collider(1973, 366, 83, 170)
        pipe4 = collider.Collider(2445, 366, 83, 170)
        pipe5 = collider.Collider(6989, 452, 83, 82)
        pipe6 = collider.Collider(7675, 452, 83, 82)

        self.pipe_group = pg.sprite.Group(pipe1, pipe2,
                                          pipe3, pipe4,
                                          pipe5, pipe6)


    def setup_steps(self):
        """Create collideable rects for all the steps"""

        step1 = collider.Collider(5745, 495, 40, 44)
        step2 = collider.Collider(5788, 452, 40, 44)
        step3 = collider.Collider(5831, 409, 40, 44)
        step4 = collider.Collider(5874, 366, 40, 176)


        step5 = collider.Collider(6001, 366, 40, 176)
        step6 = collider.Collider(6044, 408, 40, 40)
        step7 = collider.Collider(6087, 452, 40, 40)
        step8 = collider.Collider(6130, 495, 40, 40)

        step9 = collider.Collider(6345, 495, 40, 40)
        step10 = collider.Collider(6388, 452, 40, 40)
        step11 = collider.Collider(6431, 409, 40, 40)
        step12 = collider.Collider(6474, 366, 40, 40)
        step13 = collider.Collider(6517, 366, 40, 176)

        step14 = collider.Collider(6644, 366, 40, 176)
        step15 = collider.Collider(6687, 408, 40, 40)
        step16 = collider.Collider(6728, 452, 40, 40)
        step17 = collider.Collider(6771, 495, 40, 40)

        step18 = collider.Collider(7760, 495, 40, 40)
        step19 = collider.Collider(7803, 452, 40, 40)
        step20 = collider.Collider(7845, 409, 40, 40)
        step21 = collider.Collider(7888, 366, 40, 40)
        step22 = collider.Collider(7931, 323, 40, 40)
        step23 = collider.Collider(7974, 280, 40, 40)
        step24 = collider.Collider(8017, 237, 40, 40)
        step25 = collider.Collider(8060, 194, 40, 40)
        step26 = collider.Collider(8103, 194, 40, 360)

        step27 = collider.Collider(8488, 495, 40, 40)



        self.step_group = pg.sprite.Group(step1,  step2,
                                          step3,  step4,
                                          step5,  step6,
                                          step7,  step8,
                                          step9,  step10,
                                          step11, step12,
                                          step13, step14,
                                          step15, step16,
                                          step17, step18,
                                          step19, step20,
                                          step21, step22,
                                          step23, step24,
                                          step25, step26,
                                          step27)


    def setup_bricks(self):
        brick1  = break_brick.Brick(858,  365)
        brick2  = break_brick.Brick(944,  365)
        brick3  = break_brick.Brick(1030, 365)
        brick4  = break_brick.Brick(3299, 365)
        brick5  = break_brick.Brick(3385, 365)
        brick6  = break_brick.Brick(3430, 193)
        brick7  = break_brick.Brick(3473, 193)
        brick8  = break_brick.Brick(3516, 193)
        brick9  = break_brick.Brick(3559, 193)
        brick10 = break_brick.Brick(3602, 193)
        brick11 = break_brick.Brick(3645, 193)
        brick12 = break_brick.Brick(3688, 193)
        brick13 = break_brick.Brick(3731, 193)
        brick14 = break_brick.Brick(3901, 193)
        brick15 = break_brick.Brick(3944, 193)
        brick16 = break_brick.Brick(3987, 193)
        brick17 = break_brick.Brick(4030, 365)
        brick18 = break_brick.Brick(4287, 365)
        brick19 = break_brick.Brick(4330, 365)
        brick20 = break_brick.Brick(5058, 365)
        brick21 = break_brick.Brick(5187, 193)
        brick22 = break_brick.Brick(5230, 193)
        brick23 = break_brick.Brick(5273, 193)
        brick24 = break_brick.Brick(5488, 193)
        brick25 = break_brick.Brick(5574, 193)
        brick26 = break_brick.Brick(5617, 193)
        brick27 = break_brick.Brick(5531, 365)
        brick28 = break_brick.Brick(5574, 365)
        brick29 = break_brick.Brick(7202, 365)
        brick30 = break_brick.Brick(7245, 365)
        brick31 = break_brick.Brick(7331, 365)



        self.brick_group = pg.sprite.Group(brick1,  brick2,
                                           brick3,  brick4,
                                           brick5,  brick6,
                                           brick7,  brick8,
                                           brick9,  brick10,
                                           brick11, brick12,
                                           brick13, brick14,
                                           brick15, brick16,
                                           brick17, brick18,
                                           brick19, brick20,
                                           brick21, brick22,
                                           brick23, brick24,
                                           brick25, brick26,
                                           brick27, brick28,
                                           brick29, brick30,
                                           brick31)


    def setup_coin_boxes(self):
        coin_box1  = coin_box.Coin_box(685, 365)
        coin_box2  = coin_box.Coin_box(901, 365)
        coin_box3  = coin_box.Coin_box(987, 365)
        coin_box4  = coin_box.Coin_box(943, 193)
        coin_box5  = coin_box.Coin_box(3342, 365)
        coin_box6  = coin_box.Coin_box(4030, 193)
        coin_box7  = coin_box.Coin_box(4544, 365)
        coin_box8  = coin_box.Coin_box(4672, 365)
        coin_box9  = coin_box.Coin_box(4672, 193)
        coin_box10 = coin_box.Coin_box(4800, 365)
        coin_box11 = coin_box.Coin_box(5531, 193)
        coin_box12 = coin_box.Coin_box(7288, 365)

        self.coin_box_group = pg.sprite.Group(coin_box1,  coin_box2,
                                              coin_box3,  coin_box4,
                                              coin_box5,  coin_box6,
                                              coin_box7,  coin_box8,
                                              coin_box9,  coin_box10,
                                              coin_box11, coin_box12)


    def setup_enemies(self):
        """Creates a list of Goomba objects that will be added to the
        self.enemies sprite group when Mario gets a certain distance"""

        goomba1 = goomba.Goomba(800, c.GROUND_HEIGHT, c.LEFT)
        goomba2 = goomba.Goomba(800, c.GROUND_HEIGHT, c.LEFT)

        self.goombas = [goomba1, goomba2]

        self.enemies = pg.sprite.Group()


    def setup_mario(self):
        """Places Mario at the beginning of the level"""

        self.mario = mario.Mario()
        self.mario.rect.x = 110
        self.mario.rect.bottom = c.GROUND_HEIGHT



    def update(self, surface, keys, current_time):
        """Updates level"""

        self.mario.update(keys, current_time, self.collide_group)
        self.create_enemies()
        self.enemies.update(current_time, self.collide_group)
        self.coin_box_group.update(current_time)
        self.adjust_camera()

        surface.blit(self.background, self.back_rect)
        self.all_sprites.draw(surface)
        self.brick_group.draw(surface)
        self.coin_box_group.draw(surface)

        self.check_for_reset(keys)


    def create_enemies(self):
        """Enemies are created based on Mario's distance travelled"""
        
        if self.mario.distance > 530:
            self.enemies.add(self.goombas[0])
            self.all_sprites.add(self.enemies)

        if self.mario.distance > 1400:
            self.enemies.add(self.goombas[1])
            self.all_sprites.add(self.enemies)


    def adjust_camera(self):
        if self.mario.rect.right > c.SCREEN_WIDTH / 3:
            self.camera_adjustment = self.mario.rect.right - c.SCREEN_WIDTH / 3
        else:
            self.camera_adjustment = 0

        self.back_rect.x -= self.camera_adjustment

        for collider in self.collide_group:
            collider.rect.x -= self.camera_adjustment

        self.mario.rect.x -= self.camera_adjustment

        for enemy in self.enemies:
            enemy.rect.x -= self.camera_adjustment



    def check_for_reset(self, keys):
        if self.mario.dead:
            self.startup(keys, self.persistant)















        


