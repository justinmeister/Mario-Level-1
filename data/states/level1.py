__author__ = 'justinarmstrong'

import pygame as pg
import copy
from .. import setup, tools
from .. import constants as c
from .. components import mario
from .. components import collider
from .. components import break_brick
from .. components import coin_box
from .. components import enemies
from .. components import checkpoint



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
        self.setup_checkpoints()

        self.collide_group = pg.sprite.Group(self.ground_group,
                                             self.pipe_group,
                                             self.step_group,
                                             )

        self.all_sprites = pg.sprite.Group(self.mario, self.enemies)


    def setup_background(self):
        self.background = setup.GFX['level_1']
        self.back_rect = self.background.get_rect()
        self.background = pg.transform.scale(self.background,
                                  (int(self.back_rect.width*c.BACKGROUND_MULTIPLER),
                                  int(self.back_rect.height*c.BACKGROUND_MULTIPLER)))
        self.back_rect = self.background.get_rect()


    def setup_ground(self):
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
        self.powerups = pg.sprite.Group()

        coin_box1  = coin_box.Coin_box(685, 365)
        coin_box2  = coin_box.Coin_box(901, 365, 'powerup', self.powerups)
        coin_box3  = coin_box.Coin_box(987, 365)
        coin_box4  = coin_box.Coin_box(943, 193)
        coin_box5  = coin_box.Coin_box(3342, 365, 'powerup', self.powerups)
        coin_box6  = coin_box.Coin_box(4030, 193)
        coin_box7  = coin_box.Coin_box(4544, 365)
        coin_box8  = coin_box.Coin_box(4672, 365)
        coin_box9  = coin_box.Coin_box(4672, 193, 'powerup', self.powerups)
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

        goomba0 = enemies.Goomba( 800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba1 = enemies.Goomba( 800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba2 = enemies.Goomba( 800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba3 = enemies.Goomba( 860, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba4 = enemies.Goomba( 800, 193,             c.LEFT, 'goomba')
        goomba5 = enemies.Goomba( 900, 193,             c.LEFT, 'goomba')
        goomba6 = enemies.Goomba( 800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba7 = enemies.Goomba( 860, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba8 = enemies.Goomba( 800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba9 = enemies.Goomba( 860, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba10 = enemies.Goomba(800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba11 = enemies.Goomba(869, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba12 = enemies.Goomba(800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba13 = enemies.Goomba(860, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba14 = enemies.Goomba(800, c.GROUND_HEIGHT, c.LEFT, 'goomba')
        goomba15 = enemies.Goomba(860, c.GROUND_HEIGHT, c.LEFT, 'goomba')

        self.goombas = [goomba0, goomba1, goomba2, goomba3,
                        goomba4, goomba5, goomba6, goomba7,
                        goomba8, goomba9, goomba10, goomba11,
                        goomba12, goomba13, goomba14, goomba15]


        koopa0 = enemies.Koopa( 800, c.GROUND_HEIGHT, c.LEFT, 'koopa')

        self.koopas = [koopa0]

        self.enemy_group1 = pg.sprite.Group(goomba0)
        self.enemy_group2 = pg.sprite.Group(goomba1)
        self.enemy_group3 = pg.sprite.Group(goomba2, goomba3)
        self.enemy_group4 = pg.sprite.Group(goomba4, goomba5)
        self.enemy_group5 = pg.sprite.Group(goomba6, goomba7)
        self.enemy_group6 = pg.sprite.Group(koopa0)
        self.enemy_group7 = pg.sprite.Group(goomba8, goomba9)
        self.enemy_group8 = pg.sprite.Group(goomba10, goomba11)
        self.enemy_group9 = pg.sprite.Group(goomba12, goomba13)
        self.enemy_group10 = pg.sprite.Group(goomba14, goomba15)

        self.enemies = pg.sprite.Group()
        self.death_group = pg.sprite.Group()
        self.shell_group = pg.sprite.Group()


    def setup_mario(self):
        """Places Mario at the beginning of the level"""

        self.mario = mario.Mario()
        self.mario.rect.x = 110
        self.mario.rect.bottom = c.GROUND_HEIGHT


    def setup_checkpoints(self):
        check1 = checkpoint.Checkpoint(530, "1")
        check2 = checkpoint.Checkpoint(1350, '2')
        check3 = checkpoint.Checkpoint(1650, '3')
        check4 = checkpoint.Checkpoint(3000, '4')
        check5 = checkpoint.Checkpoint(3750, '5')
        check6 = checkpoint.Checkpoint(4150, '6')
        check7 = checkpoint.Checkpoint(4470, '7')
        check8 = checkpoint.Checkpoint(4950, '8')
        check9 = checkpoint.Checkpoint(5100, '9')
        check10 = checkpoint.Checkpoint(6800, '10')

        self.check_point_group = pg.sprite.Group(check1, check2, check3,
                                                 check4, check5, check6,
                                                 check7, check8, check9,
                                                 check10)


    def update(self, surface, keys, current_time):
        """Updates Entire level"""

        self.update_all_sprites(keys, current_time)
        self.blit_everything(surface)



    def update_all_sprites(self, keys, current_time):
        self.mario.update(keys, current_time)
        self.check_points_check()
        self.enemies.update(current_time)
        self.death_group.update(current_time)
        self.shell_group.update(current_time)
        self.brick_group.update()
        self.coin_box_group.update(current_time)
        self.powerups.update()
        self.adjust_sprite_positions(current_time)
        self.adjust_camera()
        self.check_for_mario_death(keys)


    def check_points_check(self):
        checkpoint = pg.sprite.spritecollideany(self.mario,
                                                 self.check_point_group)

        if checkpoint:
            checkpoint.kill()

            if checkpoint.name == '1':
                self.enemies.add(self.enemy_group1)
            elif checkpoint.name == '2':
                self.enemies.add(self.enemy_group2)
            elif checkpoint.name == '3':
                self.enemies.add(self.enemy_group3)
            elif checkpoint.name == '4':
                self.enemies.add(self.enemy_group4)
            elif checkpoint.name == '5':
                self.enemies.add(self.enemy_group5)
            elif checkpoint.name == '6':
                self.enemies.add(self.enemy_group6)
            elif checkpoint.name == '7':
                self.enemies.add(self.enemy_group7)
            elif checkpoint.name == '8':
                self.enemies.add(self.enemy_group8)
            elif checkpoint.name == '9':
                self.enemies.add(self.enemy_group9)
            elif checkpoint.name == '10':
                self.enemies.add(self.enemy_group10)

            self.all_sprites.add(self.enemies)


    def adjust_sprite_positions(self, current_time):
        self.adjust_mario_position(current_time)
        self.adjust_enemy_position()
        self.adjust_shell_position()
        self.adjust_powerup_position()


    def adjust_mario_position(self, current_time):
        self.mario.rect.x += self.mario.x_vel
        self.check_mario_x_collisions()

        self.mario.rect.y += self.mario.y_vel
        self.check_mario_y_collisions(current_time)

        if self.mario.rect.x < 5:
            self.mario.rect.x = 5


    def check_mario_x_collisions(self):
        collider = pg.sprite.spritecollideany(self.mario, self.collide_group)
        coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)
        brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        enemy = pg.sprite.spritecollideany(self.mario, self.enemies)
        shell = pg.sprite.spritecollideany(self.mario, self.shell_group)


        if coin_box:
            self.adjust_mario_for_x_collisions(coin_box)

        elif brick:
            self.adjust_mario_for_x_collisions(brick)

        elif collider:
            self.adjust_mario_for_x_collisions(collider)

        elif enemy:
            self.mario.dead = True

        elif shell:
            self.adjust_mario_for_x_shell_collisions(shell)


    def adjust_mario_for_x_collisions(self, collider):
        if self.mario.rect.x < collider.rect.x:
            self.mario.rect.right = collider.rect.left
        else:
            self.mario.rect.left = collider.rect.right

        self.mario.x_vel = 0


    def adjust_mario_for_x_shell_collisions(self, shell):
        if shell.state == c.JUMPED_ON:
            if self.mario.rect.x < shell.rect.x:
                self.mario.rect.right = shell.rect.left
                shell.direction = c.RIGHT
                shell.x_vel = 5
                shell.rect.x += 5

            else:
                self.mario.rect.left = shell.rect.right
                shell.direction = c.LEFT
                shell.x_vel = -5
                shell.rect.x += -5

            shell.state = c.SHELL_SLIDE

        elif shell.state == c.SHELL_SLIDE:
            self.mario.dead = True


    def check_mario_y_collisions(self, current_time):
        collider = pg.sprite.spritecollideany(self.mario, self.collide_group)
        enemy = pg.sprite.spritecollideany(self.mario, self.enemies)
        shell = pg.sprite.spritecollideany(self.mario, self.shell_group)
        brick = pg.sprite.spritecollideany(self.mario, self.brick_group)
        coin_box = pg.sprite.spritecollideany(self.mario, self.coin_box_group)


        if coin_box:
            self.adjust_mario_for_y_coin_box_collisions(coin_box)

        elif brick:
            self.adjust_mario_for_y_brick_collisions(brick)

        elif collider:
            self.adjust_mario_for_y_ground_pipe_collisions(collider)

        else:
            self.test_if_mario_is_falling()


        if enemy:
            self.adjust_mario_for_y_enemy_collisions(enemy, current_time)


        elif shell:
            self.adjust_mario_for_y_shell_collisions(shell)


    def adjust_mario_for_y_coin_box_collisions(self, coin_box):
        if self.mario.rect.y > coin_box.rect.y:
            if coin_box.state == c.RESTING:
                coin_box.state = c.BUMPED
                coin_box.start_bump()

            self.mario.y_vel = 7
            self.mario.rect.y = coin_box.rect.bottom
            self.mario.state = c.FALL
        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = coin_box.rect.top
            self.mario.state = c.WALK


    def adjust_mario_for_y_brick_collisions(self, brick):
        if self.mario.rect.y > brick.rect.y:
            brick.state = c.BUMPED
            brick.start_bump()
            self.mario.y_vel = 7
            self.mario.rect.y = brick.rect.bottom
            self.mario.state = c.FALL
        else:
            self.mario.y_vel = 0
            self.mario.rect.bottom = brick.rect.top
            self.mario.state = c.WALK


    def adjust_mario_for_y_ground_pipe_collisions(self, collider):
        if collider.rect.bottom > self.mario.rect.bottom:
            self.mario.y_vel = 0
            self.mario.rect.bottom = collider.rect.top
            self.mario.state = c.WALK
        elif collider.rect.top < self.mario.rect.top:
            self.mario.y_vel = 7
            self.mario.rect.top = collider.rect.bottom
            self.mario.state = c.FALL


    def test_if_mario_is_falling(self):
        test_sprite = copy.deepcopy(self.mario)
        test_sprite.rect.y += 1
        test_collide_group = pg.sprite.Group(self.collide_group,
                                                 self.brick_group,
                                                 self.coin_box_group)


        if not pg.sprite.spritecollideany(test_sprite, test_collide_group):
            if self.mario.state != c.JUMP:
                self.mario.state = c.FALL


    def adjust_mario_for_y_enemy_collisions(self, enemy, current_time):
        if self.mario.y_vel > 0:
            enemy.state = c.JUMPED_ON
            enemy.kill()
            if enemy.name == 'goomba':
                enemy.death_timer = current_time
                self.death_group.add(enemy)
            elif enemy.name == 'koopa':
                self.shell_group.add(enemy)

            self.mario.rect.bottom = enemy.rect.top
            self.mario.state = c.JUMP
            self.mario.y_vel = -5


    def adjust_mario_for_y_shell_collisions(self, shell):
        if self.mario.y_vel > 0:
            if shell.state == c.JUMPED_ON:
                shell.state = c.SHELL_SLIDE
                if self.mario.rect.centerx < shell.rect.centerx:
                    shell.direction = c.RIGHT
                else:
                    shell.direction = c.LEFT
            else:
                shell.state = c.JUMPED_ON

            self.mario.rect.bottom = shell.rect.top
            self.mario.state = c.JUMP
            self.mario.y_vel = -5


    def adjust_enemy_position(self):
        for enemy in self.enemies:
            enemy.rect.x += enemy.x_vel
            self.check_enemy_x_collisions(enemy)
            self.delete_if_off_screen(enemy)

            enemy.rect.y += enemy.y_vel
            self.check_enemy_y_collisions(enemy)


    def adjust_shell_position(self):
        for shell in self.shell_group:
            shell.rect.x += shell.x_vel
            self.check_shell_x_collisions(shell)
            self.delete_if_off_screen(shell)

            shell.rect.y += shell.y_vel
            self.check_shell_y_collisions(shell)


    def adjust_powerup_position(self):
        for powerup in self.powerups:
            if powerup.state != c.REVEAL:
                powerup.rect.x += powerup.x_vel
                self.check_mushroom_x_collisions(powerup)
                self.delete_if_off_screen(powerup)

                powerup.rect.y += powerup.y_vel
                self.check_mushroom_y_collisions(powerup)


    def check_enemy_x_collisions(self, enemy):

        collider = pg.sprite.spritecollideany(enemy, self.collide_group)

        enemy.kill()
        enemy_collider = pg.sprite.spritecollideany(enemy, self.enemies)

        if collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = collider.rect.left
                enemy.direction = c.LEFT
                enemy.x_vel = -2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = collider.rect.right
                enemy.direction = c.RIGHT
                enemy.x_vel = 2


        elif enemy_collider:
            if enemy.direction == c.RIGHT:
                enemy.rect.right = enemy_collider.rect.left
                enemy.direction = c.LEFT
                enemy_collider.direction = c.RIGHT
                enemy.x_vel = -2
                enemy_collider.x_vel = 2
            elif enemy.direction == c.LEFT:
                enemy.rect.left = enemy_collider.rect.right
                enemy.direction = c.RIGHT
                enemy_collider.direction = c.LEFT
                enemy.x_vel = 2
                enemy_collider.x_vel = -2

        self.enemies.add(enemy)
        self.all_sprites.add(self.enemies)


    def check_enemy_y_collisions(self, enemy):
        collider = pg.sprite.spritecollideany(enemy, self.collide_group)
        brick = pg.sprite.spritecollideany(enemy, self.brick_group)
        coin_box = pg.sprite.spritecollideany(enemy, self.coin_box_group)

        if collider:
            if enemy.rect.bottom > collider.rect.bottom:
                enemy.y_vel = 7
                enemy.rect.top = collider.rect.bottom
                enemy.state = c.FALL
            elif enemy.rect.bottom < collider.rect.bottom:

                enemy.y_vel = 0
                enemy.rect.bottom = collider.rect.top
                enemy.state = c.WALK

        elif brick:
            if brick.state == c.BUMPED:
                enemy.kill()
            elif enemy.rect.x > brick.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = brick.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = brick.rect.top
                enemy.state = c.WALK

        elif coin_box:
            if enemy.rect.x > coin_box.rect.x:
                enemy.y_vel = 7
                enemy.rect.top = coin_box.rect.bottom
                enemy.state = c.FALL
            else:
                enemy.y_vel = 0
                enemy.rect.bottom = coin_box.rect.top
                enemy.state = c.WALK


        else:
            test_sprite = copy.deepcopy(enemy)
            test_sprite.rect.y += 1
            test_group = pg.sprite.Group(self.collide_group,
                                         self.coin_box_group,
                                         self.brick_group)
            if pg.sprite.spritecollideany(test_sprite, test_group) is None:
                if enemy.state != c.JUMP:
                    enemy.state = c.FALL


    def check_shell_x_collisions(self, shell):
        collider = pg.sprite.spritecollideany(shell, self.collide_group)
        enemy = pg.sprite.spritecollideany(shell, self.enemies)

        if collider:
            if shell.x_vel > 0:
                shell.direction = c.LEFT
                shell.rect.right = collider.rect.left
            else:
                shell.direction = c.RIGHT
                shell.rect.left = collider.rect.right

        if enemy:
            enemy.kill()



    def check_shell_y_collisions(self, shell):
        collider = pg.sprite.spritecollideany(shell, self.collide_group)

        if collider:
            shell.y_vel = 0
            shell.rect.bottom = collider.rect.top
            shell.state = c.SHELL_SLIDE

        else:
            test_sprite = copy.deepcopy(shell)
            test_sprite.rect.y += 1
            if pg.sprite.spritecollideany(test_sprite, self.collide_group) is None:
                shell.state = c.FALL


    def check_mushroom_x_collisions(self, mushroom):
        collider = pg.sprite.spritecollideany(mushroom, self.collide_group)
        brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)

        if collider:
            self.adjust_for_collision_x(mushroom, collider)

        elif brick:
            self.adjust_for_collision_x(mushroom, brick)

        elif coin_box:
            self.adjust_for_collision_x(mushroom, coin_box)


    def check_mushroom_y_collisions(self, mushroom):
        collider = pg.sprite.spritecollideany(mushroom, self.collide_group)
        brick = pg.sprite.spritecollideany(mushroom, self.brick_group)
        coin_box = pg.sprite.spritecollideany(mushroom, self.coin_box_group)

        if collider:
            self.adjust_for_collision_y(mushroom, collider)
        elif brick:
            self.adjust_for_collision_y(mushroom, brick)
        elif coin_box:
            self.adjust_for_collision_y(mushroom, coin_box)
        else:
            self.check_if_falling(mushroom, self.collide_group)
            self.check_if_falling(mushroom, self.brick_group)
            self.check_if_falling(mushroom, self.coin_box_group)


    def adjust_for_collision_x(self, item, collider):
        if item.rect.x < collider.rect.x:
            item.rect.right = collider.rect.x
            item.direction = c.LEFT
        else:
            item.rect.x = collider.rect.right
            item.direction = c.RIGHT


    def adjust_for_collision_y(self, item, collider):
        item.rect.bottom = collider.rect.y
        item.state = c.SLIDE
        item.y_vel = 0


    def check_if_falling(self, item, sprite_group):
        test_sprite = copy.deepcopy(item)
        test_sprite.rect.y += 1

        if pg.sprite.spritecollideany(item, sprite_group) is None:
            item.state = c.FALL



    def delete_if_off_screen(self, enemy):
        if enemy.rect.x < -500:
            enemy.kill()

        elif enemy.rect.y > 600:
            enemy.kill()

        elif enemy.state == c.SHELL_SLIDE:
            if enemy.rect.x > 1000:
                enemy.kill()


    def adjust_camera(self):
        if self.back_rect.right <= 800:
            self.camera_adjustment = 0
        elif self.mario.rect.right > c.SCREEN_WIDTH / 3:
            self.camera_adjustment = self.mario.rect.right - c.SCREEN_WIDTH / 3
        else:
            self.camera_adjustment = 0

        self.back_rect.x -= self.camera_adjustment

        for collider in self.collide_group:
            collider.rect.x -= self.camera_adjustment

        for coin_box in self.coin_box_group:
            coin_box.rect.x -= self.camera_adjustment

        for brick in self.brick_group:
            brick.rect.x -= self.camera_adjustment

        for enemy in self.enemies:
            enemy.rect.x -= self.camera_adjustment

        for enemy in self.death_group:
            enemy.rect.x -= self.camera_adjustment

        for shell in self.shell_group:
            shell.rect.x -= self.camera_adjustment

        for powerup in self.powerups:
            powerup.rect.x -= self.camera_adjustment

        for checkpoint in self.check_point_group:
            checkpoint.rect.x -= self.camera_adjustment

        self.mario.rect.x -= self.camera_adjustment


    def check_for_mario_death(self, keys):
        if self.mario.rect.y > c.SCREEN_HEIGHT:
            self.mario.dead = True

        if self.mario.dead:
            self.startup(keys, self.persistant)


    def blit_everything(self, surface):
        surface.blit(self.background, self.back_rect)
        self.all_sprites.draw(surface)
        self.powerups.draw(surface)
        self.brick_group.draw(surface)
        self.coin_box_group.draw(surface)
        self.death_group.draw(surface)
        self.shell_group.draw(surface)

