__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup, tools
from .. import constants as c
import powerups


class Mario(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.sprite_sheet = setup.GFX['mario_bros']

        self.setup_timers()
        self.setup_state_booleans()
        self.setup_forces()
        self.setup_counters()
        self.load_images_from_sheet()

        self.state = c.STAND
        self.image = self.right_frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)


    def setup_timers(self):
        """Sets up timers for animations"""
        self.walking_timer = 0
        self.invincible_animation_timer = 0
        self.invincible_start_timer = 0
        self.fire_transition_timer = 0
        self.death_timer = 0
        self.transition_timer = 0
        self.last_fireball_time = 0
        self.hurt_invisible_timer = 0
        self.hurt_invisible_timer2 = 0
        self.flag_pole_timer = 0


    def setup_state_booleans(self):
        """Sets up booleans that affect Mario's behavior"""
        self.facing_right = True
        self.allow_jump = True
        self.dead = False
        self.invincible = False
        self.big = False
        self.fire = False
        self.allow_fireball = True
        self.in_transition_state = False
        self.hurt_invisible = False


    def setup_forces(self):
        """Sets up forces that affect Mario's velocity"""
        self.x_vel = 0
        self.y_vel = 0
        self.max_x_vel = 4
        self.x_accel = c.SMALL_ACCEL
        self.jump_vel = c.JUMP_VEL
        self.gravity = c.GRAVITY


    def setup_counters(self):
        """These keep track of various total for important values"""
        self.frame_index = 0
        self.invincible_index = 0
        self.fire_transition_index = 0
        self.fireball_count = 0
        self.flag_pole_right = 0


    def load_images_from_sheet(self):
        """Extracts Mario images from his sprite sheet and assigns
        them to appropriate lists"""
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

        self.right_big_normal_frames = []
        self.left_big_normal_frames = []
        self.right_big_green_frames = []
        self.left_big_green_frames = []
        self.right_big_red_frames = []
        self.left_big_red_frames = []
        self.right_big_black_frames = []
        self.left_big_black_frames = []

        self.right_fire_frames = []
        self.left_fire_frames = []


        #Images for normal small mario#

        self.right_small_normal_frames.append(
            self.get_image(178, 32, 12, 16))  # Right [0]
        self.right_small_normal_frames.append(
            self.get_image(80,  32, 15, 16))  # Right walking 1 [1]
        self.right_small_normal_frames.append(
            self.get_image(98,  32, 16, 16))  # Right walking 2 [2]
        self.right_small_normal_frames.append(
            self.get_image(114,  32, 15, 16))  # Right walking 3 [3]
        self.right_small_normal_frames.append(
            self.get_image(144, 32, 16, 16))  # Right jump [4]
        self.right_small_normal_frames.append(
            self.get_image(130, 32, 14, 16))  # Right skid [5]
        self.right_small_normal_frames.append(
            self.get_image(160, 32, 15, 16))  # Death frame [6]
        self.right_small_normal_frames.append(
            self.get_image(320, 8, 16, 24))  # Transition small to big [7]
        self.right_small_normal_frames.append(
            self.get_image(241, 33, 16, 16))  # Transition big to small [8]
        self.right_small_normal_frames.append(
            self.get_image(194, 32, 12, 16))  # Frame 1 of flag pole Slide [9]
        self.right_small_normal_frames.append(
            self.get_image(210, 33, 12, 16))  # Frame 2 of flag pole slide [10]


        #Images for small green mario (for invincible animation)#

        self.right_small_green_frames.append(
            self.get_image(178, 224, 12, 16))  # Right standing [0]
        self.right_small_green_frames.append(
            self.get_image(80, 224, 15, 16))  # Right walking 1 [1]
        self.right_small_green_frames.append(
            self.get_image(98, 224, 16, 16))  # Right walking 2 [2]
        self.right_small_green_frames.append(
            self.get_image(114, 224, 15, 16))  # Right walking 3 [3]
        self.right_small_green_frames.append(
            self.get_image(144, 224, 16, 16))  # Right jump [4]
        self.right_small_green_frames.append(
            self.get_image(130, 224, 14, 16))  # Right skid [5]

        #Images for red mario (for invincible animation)#

        self.right_small_red_frames.append(
            self.get_image(178, 272, 12, 16))  # Right standing [0]
        self.right_small_red_frames.append(
            self.get_image(80, 272, 15, 16))  # Right walking 1 [1]
        self.right_small_red_frames.append(
            self.get_image(98, 272, 16, 16))  # Right walking 2 [2]
        self.right_small_red_frames.append(
            self.get_image(114, 272, 15, 16))  # Right walking 3 [3]
        self.right_small_red_frames.append(
            self.get_image(144, 272, 16, 16))  # Right jump [4]
        self.right_small_red_frames.append(
            self.get_image(130, 272, 14, 16))  # Right skid [5]

        #Images for black mario (for invincible animation)#

        self.right_small_black_frames.append(
            self.get_image(178, 176, 12, 16))  # Right standing [0]
        self.right_small_black_frames.append(
            self.get_image(80, 176, 15, 16))  # Right walking 1 [1]
        self.right_small_black_frames.append(
            self.get_image(98, 176, 16, 16))  # Right walking 2 [2]
        self.right_small_black_frames.append(
            self.get_image(114, 176, 15, 16))  # Right walking 3 [3]
        self.right_small_black_frames.append(
            self.get_image(144, 176, 16, 16))  # Right jump [4]
        self.right_small_black_frames.append(
            self.get_image(130, 176, 14, 16))  # Right skid [5]


        #Images for normal big Mario

        self.right_big_normal_frames.append(
            self.get_image(176, 0, 16, 32))  # Right standing [0]
        self.right_big_normal_frames.append(
            self.get_image(80, 0, 16, 32))  # Right walking 1 [1]
        self.right_big_normal_frames.append(
            self.get_image(97, 0, 15, 32))  # Right walking 2 [2]
        self.right_big_normal_frames.append(
            self.get_image(112, 0, 16, 32))  # Right walking 3 [3]
        self.right_big_normal_frames.append(
            self.get_image(144, 0, 16, 32))  # Right jump [4]
        self.right_big_normal_frames.append(
            self.get_image(128, 0, 16, 32))  # Right skid [5]
        self.right_big_normal_frames.append(
            self.get_image(160, 10, 16, 22))  # Right crouching [6]
        self.right_big_normal_frames.append(
            self.get_image(336, 0, 16, 32))  # Right throwing [7]
        self.right_big_normal_frames.append(
            self.get_image(272, 2, 16, 29))  # Transition big to small [8]
        self.right_big_normal_frames.append(
            self.get_image(193, 2, 16, 30))  # Frame 1 of flag pole slide [9]
        self.right_big_normal_frames.append(
            self.get_image(209, 2, 16, 29))  # Frame 2 of flag pole slide [10]

        #Images for green big Mario#

        self.right_big_green_frames.append(
            self.get_image(176, 192, 16, 32))  # Right standing [0]
        self.right_big_green_frames.append(
            self.get_image(80, 192, 16, 32))  # Right walking 1 [1]
        self.right_big_green_frames.append(
            self.get_image(97, 192, 15, 32))  # Right walking 2 [2]
        self.right_big_green_frames.append(
            self.get_image(112, 192, 16, 32))  # Right walking 3 [3]
        self.right_big_green_frames.append(
            self.get_image(144, 192, 16, 32))  # Right jump [4]
        self.right_big_green_frames.append(
            self.get_image(128, 192, 16, 32))  # Right skid [5]
        self.right_big_green_frames.append(
            self.get_image(160, 202, 16, 22))  # Right throwing
        self.right_big_green_frames.append(
            self.get_image(336, 192, 16, 32))  # Transition big to small [8]

        #Images for red big Mario#

        self.right_big_red_frames.append(
            self.get_image(176, 240, 16, 32))  # Right standing [0]
        self.right_big_red_frames.append(
            self.get_image(80, 240, 16, 32))  # Right walking 1 [1]
        self.right_big_red_frames.append(
            self.get_image(97, 240, 15, 32))  # Right walking 2 [2]
        self.right_big_red_frames.append(
            self.get_image(112, 240, 16, 32))  # Right walking 3 [3]
        self.right_big_red_frames.append(
            self.get_image(144, 240, 16, 32))  # Right jump [4]
        self.right_big_red_frames.append(
            self.get_image(128, 240, 16, 32))  # Right skid [5]
        self.right_big_red_frames.append(
            self.get_image(160, 250, 16, 22))  # Right throwing [6]
        self.right_big_red_frames.append(
            self.get_image(336, 240, 16, 32))  # Transition big to small [8]

        #Images for black big Mario#

        self.right_big_black_frames.append(
            self.get_image(176, 144, 16, 32))  # Right standing [0]
        self.right_big_black_frames.append(
            self.get_image(80, 144, 16, 32))  # Right walking 1 [1]
        self.right_big_black_frames.append(
            self.get_image(97, 144, 15, 32))  # Right walking 2 [2]
        self.right_big_black_frames.append(
            self.get_image(112, 144, 16, 32))  # Right walking 3 [3]
        self.right_big_black_frames.append(
            self.get_image(144, 144, 16, 32))  # Right jump [4]
        self.right_big_black_frames.append(
            self.get_image(128, 144, 16, 32))  # Right skid [5]
        self.right_big_black_frames.append(
            self.get_image(160, 154, 16, 22))  # Right throwing [6]
        self.right_big_black_frames.append(
            self.get_image(336, 144, 16, 32))  # Transition big to small [7]


        #Images for Fire Mario#

        self.right_fire_frames.append(
            self.get_image(176, 48, 16, 32))  # Right standing [0]
        self.right_fire_frames.append(
            self.get_image(80, 48, 16, 32))  # Right walking 1 [1]
        self.right_fire_frames.append(
            self.get_image(97, 48, 15, 32))  # Right walking 2 [2]
        self.right_fire_frames.append(
            self.get_image(112, 48, 16, 32))  # Right walking 3 [3]
        self.right_fire_frames.append(
            self.get_image(144, 48, 16, 32))  # Right jump [4]
        self.right_fire_frames.append(
            self.get_image(128, 48, 16, 32))  # Right skid [5]
        self.right_fire_frames.append(
            self.get_image(336, 48, 16, 32))  # Right throwing [6]
        self.right_fire_frames.append(
            self.get_image(160, 58, 16, 22))  # Right crouching [7]
        self.right_fire_frames.append(
            self.get_image(0, 0, 0, 0))  # Place holder [8]
        self.right_fire_frames.append(
            self.get_image(193, 50, 16, 29))  # Frame 1 of flag pole slide [9]
        self.right_fire_frames.append(
            self.get_image(209, 50, 16, 29))  # Frame 2 of flag pole slide [10]


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

        for frame in self.right_big_normal_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_normal_frames.append(new_image)

        for frame in self.right_big_green_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_green_frames.append(new_image)

        for frame in self.right_big_red_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_red_frames.append(new_image)

        for frame in self.right_big_black_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_big_black_frames.append(new_image)

        for frame in self.right_fire_frames:
            new_image = pg.transform.flip(frame, True, False)
            self.left_fire_frames.append(new_image)


        self.normal_small_frames = [self.right_small_normal_frames,
                              self.left_small_normal_frames]

        self.green_small_frames = [self.right_small_green_frames,
                             self.left_small_green_frames]

        self.red_small_frames = [self.right_small_red_frames,
                           self.left_small_red_frames]

        self.black_small_frames = [self.right_small_black_frames,
                             self.left_small_black_frames]

        self.invincible_small_frames_list = [self.normal_small_frames,
                                          self.green_small_frames,
                                          self.red_small_frames,
                                          self.black_small_frames]

        self.normal_big_frames = [self.right_big_normal_frames,
                                  self.left_big_normal_frames]

        self.green_big_frames = [self.right_big_green_frames,
                                 self.left_big_green_frames]

        self.red_big_frames = [self.right_big_red_frames,
                               self.left_big_red_frames]

        self.black_big_frames = [self.right_big_black_frames,
                                 self.left_big_black_frames]

        self.fire_frames = [self.right_fire_frames,
                            self.left_fire_frames]

        self.invincible_big_frames_list = [self.normal_big_frames,
                                           self.green_big_frames,
                                           self.red_big_frames,
                                           self.black_big_frames]

        self.all_images = [self.right_big_normal_frames,
                           self.right_big_black_frames,
                           self.right_big_red_frames,
                           self.right_big_green_frames,
                           self.right_small_normal_frames,
                           self.right_small_green_frames,
                           self.right_small_red_frames,
                           self.right_small_black_frames,
                           self.left_big_normal_frames,
                           self.left_big_black_frames,
                           self.left_big_red_frames,
                           self.left_big_green_frames,
                           self.left_small_normal_frames,
                           self.left_small_red_frames,
                           self.left_small_green_frames,
                           self.left_small_black_frames]


        self.right_frames = self.normal_small_frames[0]
        self.left_frames = self.normal_small_frames[1]


    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width*c.SIZE_MULTIPLIER),
                                    int(rect.height*c.SIZE_MULTIPLIER)))
        return image


    def update(self, keys, current_time, fire_group):
        """Updates Mario's states and animations once per frame"""
        self.handle_state(keys, current_time, fire_group)
        self.check_for_special_state(current_time)
        self.animation()


    def handle_state(self, keys, current_time, fire_group):
        """Determines Mario's behavior based on his state"""
        if self.state == c.STAND:
            self.standing(keys, current_time, fire_group)
        elif self.state == c.WALK:
            self.walking(keys, current_time, fire_group)
        elif self.state == c.JUMP:
            self.jumping(keys, current_time, fire_group)
        elif self.state == c.FALL:
            self.falling(keys, current_time, fire_group)
        elif self.state == c.DEATH_JUMP:
            self.jumping_to_death(current_time)
        elif self.state == c.SMALL_TO_BIG:
            self.changing_to_big(current_time)
        elif self.state == c.BIG_TO_FIRE:
            self.changing_to_fire(current_time)
        elif self.state == c.BIG_TO_SMALL:
            self.changing_to_small(current_time)
        elif self.state == c.FLAGPOLE:
            self.flag_pole_sliding(current_time)
        elif self.state == c.BOTTOM_OF_POLE:
            self.sitting_at_bottom_of_pole(current_time)


    def standing(self, keys, current_time, fire_group):
        """This function is called if Mario is standing still"""
        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)
        
        self.frame_index = 0
        self.x_vel = 0
        self.y_vel = 0

        if keys[pg.K_s]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group, current_time)

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


    def check_to_allow_jump(self, keys):
        """Check to allow Mario to jump"""
        if not keys[pg.K_a]:
            self.allow_jump = True


    def check_to_allow_fireball(self, keys):
        """Check to allow the shooting of a fireball"""
        if not keys[pg.K_s]:
            self.allow_fireball = True


    def shoot_fireball(self, powerup_group, current_time):
        """Shoots fireball, allowing no more than two to exist at once"""
        self.fireball_count = self.count_number_of_fireballs(powerup_group)

        if (current_time - self.last_fireball_time) > 200:
            if self.fireball_count < 2:
                self.allow_fireball = False
                powerup_group.add(
                    powerups.FireBall(self.rect.right, self.rect.y, self.facing_right))
                self.last_fireball_time = current_time

                self.frame_index = 6
                if self.facing_right:
                    self.image = self.right_frames[self.frame_index]
                else:
                    self.image = self.left_frames[self.frame_index]


    def count_number_of_fireballs(self, powerup_group):
        """Count number of fireballs that exist in the level"""
        fireball_list = []

        for powerup in powerup_group:
            if powerup.name == c.FIREBALL:
                fireball_list.append(powerup)

        return len(fireball_list)


    def walking(self, keys, current_time, fire_group):
        """This function is called when Mario is in a walking state
        It changes the frame, checks for holding down the run button,
        checks for a jump, then adjusts the state if necessary"""

        self.check_to_allow_jump(keys)
        self.check_to_allow_fireball(keys)

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
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group, current_time)
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


    def calculate_animation_speed(self):
        """Used to make walking animation speed be in relation to
        Mario's x-vel"""
        if self.x_vel == 0:
            animation_speed = 130
        elif self.x_vel > 0:
            animation_speed = 130 - (self.x_vel * (10))
        else:
            animation_speed = 130 - (self.x_vel * (10) * -1)

        return animation_speed


    def jumping(self, keys, current_time, fire_group):
        """Called when Mario is in a JUMP state."""
        self.allow_jump = False
        self.frame_index = 4
        self.gravity = c.JUMP_GRAVITY
        self.y_vel += self.gravity
        self.check_to_allow_fireball(keys)

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

        if keys[pg.K_s]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group, current_time)


    def falling(self, keys, current_time, fire_group):
        """Called when Mario is in a FALL state"""
        self.check_to_allow_fireball(keys)
        self.y_vel += self.gravity

        if keys[pg.K_LEFT]:
            if self.x_vel > (self.max_x_vel * - 1):
                self.x_vel -= self.x_accel

        elif keys[pg.K_RIGHT]:
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel

        if keys[pg.K_s]:
            if self.fire and self.allow_fireball:
                self.shoot_fireball(fire_group, current_time)


    def jumping_to_death(self, current_time):
        """Called when Mario is in a DEATH_JUMP state"""
        if self.death_timer == 0:
            self.death_timer = current_time
        elif (current_time - self.death_timer) > 500:
            self.rect.y += self.y_vel
            self.y_vel += self.gravity


    def start_death_jump(self):
        """Used to put Mario in a DEATH_JUMP state"""
        self.y_vel = -11
        self.gravity = .5
        self.frame_index = 6
        self.image = self.right_frames[self.frame_index]
        self.state = c.DEATH_JUMP
        self.in_transition_state = True


    def changing_to_big(self, current_time):
        """Changes Mario's image attribute based on time while
        transitioning to big"""
        self.in_transition_state = True

        if self.transition_timer == 0:
            self.transition_timer = current_time
        elif self.timer_between_these_two_times(current_time, 135, 200):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(current_time, 200, 365):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(current_time, 365, 430):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(current_time, 430, 495):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(current_time, 495, 560):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(current_time, 560, 625):
            self.set_mario_to_big_image()
        elif self.timer_between_these_two_times(current_time, 625, 690):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(current_time, 690, 755):
            self.set_mario_to_middle_image()
        elif self.timer_between_these_two_times(current_time, 755, 820):
            self.set_mario_to_big_image()
        elif self.timer_between_these_two_times(current_time, 820, 885):
            self.set_mario_to_small_image()
        elif self.timer_between_these_two_times(current_time, 885, 950):
            self.set_mario_to_big_image()
            self.state = c.WALK
            self.in_transition_state = False
            self.transition_timer = 0
            self.become_big()


    def timer_between_these_two_times(self, current_time, start_time, end_time):
        """Checks if the timer is at the right time for the action. Reduces
        the ugly code."""
        if (current_time - self.transition_timer) >= start_time\
            and (current_time - self.transition_timer) < end_time:
            return True


    def set_mario_to_middle_image(self):
        """During a change from small to big, sets mario's image to the
        transition/middle size"""
        if self.facing_right:
            self.image = self.normal_small_frames[0][7]
        else:
            self.image = self.normal_small_frames[1][7]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx


    def set_mario_to_small_image(self):
        """During a change from small to big, sets mario's image to small"""
        if self.facing_right:
            self.image = self.normal_small_frames[0][0]
        else:
            self.image = self.normal_small_frames[1][0]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx


    def set_mario_to_big_image(self):
        """During a change from small to big, sets mario's image to big"""
        if self.facing_right:
            self.image = self.normal_big_frames[0][0]
        else:
            self.image = self.normal_big_frames[1][0]
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx


    def become_big(self):
        self.big = True
        self.right_frames = self.right_big_normal_frames
        self.left_frames = self.left_big_normal_frames
        bottom = self.rect.bottom
        left = self.rect.x
        image = self.right_frames[0]
        self.rect = image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left


    def changing_to_fire(self, current_time):
        """Called when Mario is in a BIG_TO_FIRE state (i.e. when
        he obtains a fire flower"""
        self.in_transition_state = True

        if self.facing_right:
            frames = [self.right_fire_frames[3],
                      self.right_big_green_frames[3],
                      self.right_big_red_frames[3],
                      self.right_big_black_frames[3]]
        else:
            frames = [self.left_fire_frames[3],
                      self.left_big_green_frames[3],
                      self.left_big_red_frames[3],
                      self.left_big_black_frames[3]]

        if self.fire_transition_timer == 0:
            self.fire_transition_timer = current_time
        elif (current_time - self.fire_transition_timer) > 65 and (current_time - self.fire_transition_timer) < 130:
            self.image = frames[0]
        elif (current_time - self.fire_transition_timer) < 195:
            self.image = frames[1]
        elif (current_time - self.fire_transition_timer) < 260:
            self.image = frames[2]
        elif (current_time - self.fire_transition_timer) < 325:
            self.image = frames[3]
        elif (current_time - self.fire_transition_timer) < 390:
            self.image = frames[0]
        elif (current_time - self.fire_transition_timer) < 455:
            self.image = frames[1]
        elif (current_time - self.fire_transition_timer) < 520:
            self.image = frames[2]
        elif (current_time - self.fire_transition_timer) < 585:
            self.image = frames[3]
        elif (current_time - self.fire_transition_timer) < 650:
            self.image = frames[0]
        elif (current_time - self.fire_transition_timer) < 715:
            self.image = frames[1]
        elif (current_time - self.fire_transition_timer) < 780:
            self.image = frames[2]
        elif (current_time - self.fire_transition_timer) < 845:
            self.image = frames[3]
        elif (current_time - self.fire_transition_timer) < 910:
            self.image = frames[0]
        elif (current_time - self.fire_transition_timer) < 975:
            self.image = frames[1]
        elif (current_time - self.fire_transition_timer) < 1040:
            self.image = frames[2]
            self.fire = True
            self.in_transition_state = False
            self.state = c.WALK
            self.transition_timer = 0


    def changing_to_small(self, current_time):
        """Mario's state and animation when he shrinks from big to small
        after colliding with an enemy"""
        self.in_transition_state = True
        self.hurt_invisible = True
        self.state = c.BIG_TO_SMALL

        if self.facing_right:
            frames = [self.right_big_normal_frames[4],
                      self.right_big_normal_frames[8],
                      self.right_small_normal_frames[8]
                      ]
        else:
            frames = [self.left_big_normal_frames[4],
                      self.left_big_normal_frames[8],
                      self.left_small_normal_frames[8]
                     ]

        if self.transition_timer == 0:
            self.transition_timer = current_time
        elif (current_time - self.transition_timer) < 265:
            self.image = frames[0]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 330:
            self.image = frames[1]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 395:
            self.image = frames[2]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 460:
            self.image = frames[1]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 525:
            self.image = frames[2]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 590:
            self.image = frames[1]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 655:
            self.image = frames[2]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 720:
            self.image = frames[1]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 785:
            self.image = frames[2]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 850:
            self.image = frames[1]
            self.hurt_invincible_check(current_time)
            self.adjust_rect()
        elif (current_time - self.transition_timer) < 915:
            self.image = frames[2]
            self.adjust_rect()
            self.in_transition_state = False
            self.state = c.WALK
            self.big = False
            self.transition_timer = 0
            self.hurt_invisible_timer = 0
            self.become_small()


    def adjust_rect(self):
        """Makes sure new Rect has the same bottom and left
        location as previous Rect"""
        x = self.rect.x
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = bottom


    def become_small(self):
        self.big = False
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames
        bottom = self.rect.bottom
        left = self.rect.x
        image = self.right_frames[0]
        self.rect = image.get_rect()
        self.rect.bottom = bottom
        self.rect.x = left


    def flag_pole_sliding(self, current_time):
        """State where Mario is sliding down the flag pole"""
        self.state = c.FLAGPOLE
        self.in_transition_state = True
        self.x_vel = 0
        self.y_vel = 0

        if self.flag_pole_timer == 0:
            self.flag_pole_timer = current_time
        elif self.rect.bottom < 493:
            if (current_time - self.flag_pole_timer) < 65:
                self.image = self.right_frames[9]
            elif (current_time - self.flag_pole_timer) < 130:
                self.image = self.right_frames[10]
            elif (current_time - self.flag_pole_timer) >= 130:
                self.flag_pole_timer = current_time
            self.rect.right = self.flag_pole_right - 10
            self.y_vel = 5
            self.rect.y += self.y_vel

            if self.rect.bottom >= 488:
                self.flag_pole_timer = current_time

        elif self.rect.bottom >= 493:
            self.image = self.right_frames[10]

    def sitting_at_bottom_of_pole(self, current_time):
        """State when mario is at the bottom of the flag pole"""
        if self.flag_pole_timer == 0:
            self.flag_pole_timer = current_time
            self.image = self.left_frames[10]
        elif (current_time - self.flag_pole_timer) < 210:
            self.image = self.left_frames[10]
        else:
            self.in_transition_state = False
            self.state = c.WALK



    def set_state_to_bottom_of_pole(self):
        """Sets Mario to the BOTTOM_OF_POLE state"""
        self.image = self.left_frames[9]
        right = self.rect.right
        self.rect.bottom = 493
        self.rect.x = right
        self.flag_pole_timer = 0
        self.state = c.BOTTOM_OF_POLE



    def check_for_special_state(self, current_time):
        """Determines if Mario is invincible, Fire Mario or recently hurt"""
        self.check_if_invincible(current_time)
        self.check_if_fire()
        self.check_if_hurt_invincible(current_time)


    def check_if_invincible(self, current_time):
        if self.invincible:
            if ((current_time - self.invincible_start_timer) < 10000):
                self.change_frame_list(current_time, 30)
            elif ((current_time - self.invincible_start_timer) < 12000):
                self.change_frame_list(current_time, 100)
            else:
                self.invincible = False
        else:
            if self.big:
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames
            else:
                self.right_frames = self.invincible_small_frames_list[0][0]
                self.left_frames = self.invincible_small_frames_list[0][1]


    def change_frame_list(self, current_time, frame_switch_speed):
        if (current_time - self.invincible_animation_timer) > frame_switch_speed:
            if self.invincible_index < (len(self.invincible_small_frames_list) - 1):
                self.invincible_index += 1
            else:
                self.invincible_index = 0

            if self.big:
                frames = self.invincible_big_frames_list[self.invincible_index]
            else:
                frames = self.invincible_small_frames_list[self.invincible_index]

            self.right_frames = frames[0]
            self.left_frames = frames[1]

            self.invincible_animation_timer = current_time


    def check_if_fire(self):
        if self.fire and self.invincible == False:
            self.right_frames = self.fire_frames[0]
            self.left_frames = self.fire_frames[1]


    def check_if_hurt_invincible(self, current_time):
        """Check if Mario is still temporarily invincible after getting hurt"""
        if self.hurt_invisible and self.state != c.BIG_TO_SMALL:
            if self.hurt_invisible_timer2 == 0:
                self.hurt_invisible_timer2 = current_time
            elif (current_time - self.hurt_invisible_timer2) < 2000:
                self.hurt_invincible_check(current_time)
            else:
                self.hurt_invisible = False
                self.hurt_invisible_timer = 0
                self.hurt_invisible_timer2 = 0
                for frames in self.all_images:
                    for image in frames:
                        image.set_alpha(255)


    def hurt_invincible_check(self, current_time):
        """Makes Mario invincible on a fixed interval"""
        if self.hurt_invisible_timer == 0:
            self.hurt_invisible_timer = current_time
        elif (current_time - self.hurt_invisible_timer) < 35:
            self.image.set_alpha(0)
        elif (current_time - self.hurt_invisible_timer) < 70:
            self.image.set_alpha(255)
            self.hurt_invisible_timer = current_time


    def animation(self):
        if self.state == c.DEATH_JUMP \
            or self.state == c.SMALL_TO_BIG \
            or self.state == c.BIG_TO_FIRE \
            or self.state == c.BIG_TO_SMALL \
            or self.state == c.FLAGPOLE \
            or self.state == c.BOTTOM_OF_POLE:
            pass
        elif self.facing_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]











