__author__ = 'justinarmstrong'

import pygame as pg
from .. import constants as c
from .. import setup


class Powerup(pg.sprite.Sprite):
    """Base class for all powerup_group"""
    def __init__(self, x, y):
        super(Powerup, self).__init__()


    def setup_powerup(self, x, y, name, setup_frames):
        """This separate setup function allows me to pass a different
        setup_frames method depending on what the powerup is"""
        self.sprite_sheet = setup.GFX['item_objects']
        self.frames = []
        self.frame_index = 0
        setup_frames()
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.state = c.REVEAL
        self.y_vel = -1
        self.x_vel = 0
        self.direction = c.RIGHT
        self.box_height = y
        self.gravity = 1
        self.max_y_vel = 8
        self.animate_timer = 0
        self.name = name


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


    def update(self, current_time):
        self.handle_state(current_time)


    def handle_state(self, current_time):
        pass


    def revealing(self, *args):
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.y_vel = 0
            self.state = c.SLIDE


    def sliding(self):
        if self.direction == c.RIGHT:
            self.x_vel = 3
        else:
            self.x_vel = -3


    def falling(self):
        if self.y_vel < self.max_y_vel:
            self.y_vel += self.gravity


class Mushroom(Powerup):
    """Powerup that makes Mario become bigger"""
    def __init__(self, x, y, name='mushroom'):
        super(Mushroom, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)


    def setup_frames(self):
        self.frames.append(self.get_image(0, 0, 16, 16))


    def handle_state(self, *args):
        if self.state == c.REVEAL:
            self.revealing()
        elif self.state == c.SLIDE:
            self.sliding()
        elif self.state == c.FALL:
            self.falling()


class FireFlower(Powerup):
    """Powerup that allows Mario to throw fire balls"""
    def __init__(self, x, y, name=c.FIREFLOWER):
        super(FireFlower, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)


    def setup_frames(self):
        self.frames.append(
            self.get_image(0, 32, 16, 16))
        self.frames.append(
            self.get_image(16, 32, 16, 16))
        self.frames.append(
            self.get_image(32, 32, 16, 16))
        self.frames.append(
            self.get_image(48, 32, 16, 16))


    def handle_state(self, current_time):
        if self.state == c.REVEAL:
            self.revealing(current_time)
        elif self.state == c.RESTING:
            self.resting(current_time)


    def revealing(self,current_time):
        """Animation of flower coming out of box"""
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.state = c.RESTING

        self.animation(current_time)


    def resting(self, current_time):
        """Fire Flower staying still on opened box"""
        self.animation(current_time)


    def animation(self, current_time):
        """Method to make the Fire Flower blink"""
        if (current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0

            self.image = self.frames[self.frame_index]
            self.animate_timer = current_time


class Star(Powerup):
    """A powerup that gives mario invincibility"""
    def __init__(self, x, y, name='star'):
        super(Star, self).__init__(x, y)
        self.setup_powerup(x, y, name, self.setup_frames)
        self.animate_timer = 0
        self.rect.y += 1  #looks more centered offset one pixel
        self.gravity = .4


    def setup_frames(self):
        """Creating the self.frames list where the images for the animation
        are stored"""
        self.frames.append(self.get_image(1, 48, 15, 16))
        self.frames.append(self.get_image(17, 48, 15, 16))
        self.frames.append(self.get_image(33, 48, 15, 16))
        self.frames.append(self.get_image(49, 48, 15, 16))


    def handle_state(self, current_time):
        if self.state == c.REVEAL:
            self.revealing(current_time)
        elif self.state == c.BOUNCE:
            self.bouncing(current_time)


    def revealing(self, current_time):
        self.rect.y += self.y_vel

        if self.rect.bottom <= self.box_height:
            self.rect.bottom = self.box_height
            self.start_bounce(-2)
            self.state = c.BOUNCE

        self.animation(current_time)


    def animation(self, current_time):
        if (current_time - self.animate_timer) > 30:
            if self.frame_index < 3:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.animate_timer = current_time
            self.image = self.frames[self.frame_index]


    def start_bounce(self, vel):
        self.y_vel = vel


    def bouncing(self, current_time):
        self.animation(current_time)

        if self.direction == c.LEFT:
            self.x_vel = -5
        else:
            self.x_vel = 5



class FireBall(pg.sprite.Sprite):
    def __init__(self, x, y, facing_right, name=c.FIREBALL):
        super(FireBall, self).__init__()
        self.sprite_sheet = setup.GFX['item_objects']
        self.setup_frames()
        if facing_right:
            self.direction = c.RIGHT
            self.x_vel = 12
        else:
            self.direction = c.LEFT
            self.x_vel = -12
        self.y_vel = 10
        self.gravity = .9
        self.frame_index = 0
        self.animation_timer = 0
        self.state = c.FLYING
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.right = x
        self.rect.y = y
        self.name = name


    def setup_frames(self):
        self.frames = []

        self.frames.append(
            self.get_image(96, 144, 8, 8)) #Frame 1 of flying
        self.frames.append(
            self.get_image(104, 144, 8, 8))  #Frame 2 of Flying
        self.frames.append(
            self.get_image(96, 152, 8, 8))   #Frame 3 of Flying
        self.frames.append(
            self.get_image(104, 152, 8, 8))  #Frame 4 of flying
        self.frames.append(
            self.get_image(112, 144, 16, 16))   #frame 1 of exploding
        self.frames.append(
            self.get_image(112, 160, 16, 16))  #frame 2 of exploding
        self.frames.append(
            self.get_image(112, 176, 16, 16))  #frame 3 of exploding


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


    def update(self, current_time):
        self.handle_state(current_time)
        self.check_if_off_screen()


    def handle_state(self, current_time):

        if self.state == c.FLYING:
            self.animation(current_time)
        elif self.state == c.BOUNCING:
            self.animation(current_time)
        elif self.state == c.EXPLODING:
            self.animation(current_time)


    def animation(self, current_time):
        if self.state == c.FLYING or self.state == c.BOUNCING:
            if (current_time - self.animation_timer) > 200:
                if self.frame_index < 3:
                    self.frame_index += 1
                else:
                    self.frame_index = 0
                self.animation_timer = current_time
                self.image = self.frames[self.frame_index]


        elif self.state == c.EXPLODING:
            if (current_time - self.animation_timer) > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                    self.image = self.frames[self.frame_index]
                    self.animation_timer = current_time
                else:
                    self.kill()


    def explode_transition(self):
        self.frame_index = 4
        centerx = self.rect.centerx
        self.image = self.frames[self.frame_index]
        self.rect.centerx = centerx
        self.state = c.EXPLODING


    def check_if_off_screen(self):
        if (self.rect.x > c.SCREEN_WIDTH) or (self.rect.y > c.SCREEN_HEIGHT) \
            or (self.rect.right < 0):
            self.kill()










