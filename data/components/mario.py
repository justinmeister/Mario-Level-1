__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
import copy


class Mario(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['mario_bros']

        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        self.max_x_vel = 4
        self.x_accel = c.SMALL_ACCEL
        self.jump_vel = c.JUMP_VEL
        self.gravity = c.GRAVITY
        self.state = c.STAND
        self.facing_right = True
        self.walking_timer = 0
        self.allow_jump = True
        self.dead = False
        self.invincible = False
        self.invincible_animation_timer = 0
        self.invincible_start_timer = 0
        self.invincible_index = 0

        self.load_from_sheet()
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()



    def load_from_sheet(self):
        self.right_frames = []
        self.left_frames = []
        self.right_small_normal_frames = []
        self.left_small_normal_frames = []
        self.right_small_green_frames = []
        self.left_small_green_frames = []
        self.right_small_red_frames = []
        self.left_small_red_frames = []
        self.right_small_black_frames = []
        self.left_small_black_frames = []

        self.right_small_normal_frames.append(
            self.get_image(178, 32, 12, 16))  #right
        self.right_small_normal_frames.append(
            self.get_image(80,  32, 15, 16))  #right walking 1
        self.right_small_normal_frames.append(
            self.get_image(99,  32, 15, 16))  #right walking 2
        self.right_small_normal_frames.append(
            self.get_image(114,  32, 15, 16))  #right walking 3
        self.right_small_normal_frames.append(
            self.get_image(144, 32, 16, 16))  #right jump
        self.right_small_normal_frames.append(
            self.get_image(130, 32, 14, 16))  #right skid

        self.right_small_green_frames.append(
            self.get_image(178, 224, 12, 16))
        self.right_small_green_frames.append(
            self.get_image(80, 224, 15, 16))
        self.right_small_green_frames.append(
            self.get_image(99, 224, 15, 16))
        self.right_small_green_frames.append(
            self.get_image(114, 224, 15, 16))
        self.right_small_green_frames.append(
            self.get_image(144, 224, 16, 16))
        self.right_small_green_frames.append(
            self.get_image(130, 224, 14, 16))

        self.right_small_red_frames.append(
            self.get_image(178, 272, 12, 16))
        self.right_small_red_frames.append(
            self.get_image(80, 272, 15, 16))
        self.right_small_red_frames.append(
            self.get_image(99, 272, 15, 16))
        self.right_small_red_frames.append(
            self.get_image(114, 272, 15, 16))
        self.right_small_red_frames.append(
            self.get_image(144, 272, 16, 16))
        self.right_small_red_frames.append(
            self.get_image(130, 272, 14, 16))

        self.right_small_black_frames.append(
            self.get_image(178, 176, 12, 16))
        self.right_small_black_frames.append(
            self.get_image(80, 176, 15, 16))
        self.right_small_black_frames.append(
            self.get_image(99, 176, 15, 16))
        self.right_small_black_frames.append(
            self.get_image(114, 176, 15, 16))
        self.right_small_black_frames.append(
            self.get_image(144, 176, 16, 16))
        self.right_small_black_frames.append(
            self.get_image(130, 176, 14, 16))

        right_frames = [self.right_small_normal_frames,
                        self.right_small_green_frames,
                        self.right_small_red_frames,
                        self.right_small_black_frames]

        #The left image frames are numbered the same as the right
        #frames but are simply reversed.

        for frame in self.right_small_normal_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_normal_frames.append(new_image)

        for frame in self.right_small_green_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_green_frames.append(new_image)

        for frame in self.right_small_red_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_red_frames.append(new_image)

        for frame in self.right_small_black_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_small_black_frames.append(new_image)


        self.normal_frames = [self.right_small_normal_frames,
                              self.left_small_normal_frames]

        self.green_frames = [self.right_small_green_frames,
                             self.left_small_green_frames]

        self.red_frames = [self.right_small_red_frames,
                           self.left_small_red_frames]

        self.black_frames = [self.right_small_black_frames,
                             self.left_small_black_frames]

        self.invincible_frames_list = [self.normal_frames,
                                          self.green_frames,
                                          self.red_frames,
                                          self.black_frames]


        self.right_frames = self.normal_frames[0]
        self.left_frames = self.normal_frames[1]


    def get_image(self, x, y, width, height):
        image = pg.Surface([width, height]).convert()
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width*c.SIZE_MULTIPLIER),
                                    int(rect.height*c.SIZE_MULTIPLIER)))
        return image


    def update(self, keys, current_time):
        self.handle_state(keys, current_time)
        self.animation()


    def handle_state(self, keys, current_time):
        if self.state == c.STAND:
            self.standing(keys, current_time)
        elif self.state == c.WALK:
            self.walking(keys, current_time)
        elif self.state == c.JUMP:
            self.jumping(keys, current_time)
        elif self.state == c.FALL:
            self.falling(keys, current_time)

        self.check_if_invincible(current_time)


    def standing(self, keys, current_time):
        """This function is called if Mario is standing still"""
        self.check_to_allow_jump(keys)
        
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0
        self.gravity = c.GRAVITY

        if keys[pg.K_LEFT]:
            self.facing_right = False
            self.state = c.WALK
        elif keys[pg.K_RIGHT]:
            self.facing_right = True
            self.state = c.WALK
        elif keys[pg.K_a]:
            if self.allow_jump:
                self.state = c.JUMP
                self.y_vel = self.jump_vel
        else:
            self.state = c.STAND


    def walking(self, keys, current_time):
        """This function is called when Mario is in a walking state
        It changes the frame, checks for holding down the run button,
        checks for a jump, then adjusts the state if necessary"""

        self.check_to_allow_jump(keys)

        if self.frame_index == 0:
            self.frame_index += 1
            self.walking_timer = current_time
        else:
            if (current_time - self.walking_timer >
                    self.calculate_animation_speed()):
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 1

                self.walking_timer = current_time


        if keys[pg.K_s]:
            self.max_x_vel = 7
        else:
            self.max_x_vel = 5


        if keys[pg.K_a]:
            if self.allow_jump:
                self.state = c.JUMP
                self.y_vel = c.JUMP_VEL


        if keys[pg.K_LEFT]:
            self.facing_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND
            else:
                self.x_accel = c.SMALL_ACCEL

            if self.x_vel > (self.max_x_vel * -1):
                self.x_vel -= self.x_accel
            elif self.x_vel < (self.max_x_vel * -1):
                self.x_vel += self.x_accel

        elif keys[pg.K_RIGHT]:
            self.facing_right = True
            if self.x_vel < 0:
                self.frame_index = 5
                self.x_accel = c.SMALL_TURNAROUND
            else:
                self.x_accel = c.SMALL_ACCEL

            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel
            elif self.x_vel > self.max_x_vel:
                self.x_vel -= self.x_accel


        else:
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND


    def jumping(self, keys, current_time):
        self.allow_jump = False
        self.frame_index = 4
        self.gravity = c.JUMP_GRAVITY
        self.y_vel += self.gravity
        if self.y_vel >= 0:
            self.gravity += .4
            self.state = c.FALL

        if keys[pg.K_LEFT]:
            if self.x_vel > (self.max_x_vel * - 1):
                self.x_vel -= self.x_accel

        elif keys[pg.K_RIGHT]:
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel


        if not keys[pg.K_a]:
            self.gravity = c.GRAVITY
            self.state = c.FALL


    def falling(self, keys, current_time):
        self.y_vel += self.gravity

        if keys[pg.K_LEFT]:
            if self.x_vel > (self.max_x_vel * - 1):
                self.x_vel -= self.x_accel

        elif keys[pg.K_RIGHT]:
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel


    def check_to_allow_jump(self, keys):
        if not keys[pg.K_a]:
            self.allow_jump = True


    def calculate_animation_speed(self):
        if self.x_vel == 0:
            animation_speed = 130
        elif self.x_vel > 0:
            animation_speed = 130 - (self.x_vel * (10))
        else:
            animation_speed = 130 - (self.x_vel * (10) * -1)

        return animation_speed


    def animation(self):
        if self.facing_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]


    def check_if_invincible(self, current_time):
        if self.invincible == True:
            if ((current_time - self.invincible_start_timer) < 10000):
                self.change_frame_list(current_time, 30)
            elif ((current_time - self.invincible_start_timer) < 12000):
                self.change_frame_list(current_time, 100)
            else:
                self.invincible = False
        else:
            self.right_frames = self.invincible_frames_list[0][0]
            self.left_frames = self.invincible_frames_list[0][1]


    def change_frame_list(self, current_time, frame_switch_speed):
        if (current_time - self.invincible_animation_timer) > frame_switch_speed:
            if self.invincible_index < (len(self.invincible_frames_list) - 1):
                self.invincible_index += 1
            else:
                self.invincible_index = 0

            frames = self.invincible_frames_list[self.invincible_index]
            self.right_frames = frames[0]
            self.left_frames = frames[1]

            self.invincible_animation_timer = current_time
