__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup
from .. import constants as c


class Flag(pg.sprite.Sprite):
    """Flag on top of the flag pole at the end of the level
    Following Properties:
        Sprite

    Attributes:
        _Sprite__g: A associative array of all groups the sprite belongs to.
        frames: array of collision frames matching the sprite image dimensions.
        image: The dimensions of the sprite image and orientation
        rect: A rect object that holds relative directions for the sprite
        sprite_sheet: Surface object that holds dimensions for the sprite sheet
        state: A string to be matched against
    """
    def __init__(self, x, y):
        super(Flag, self).__init__()
        self.sprite_sheet = setup.GFX['item_objects']
        self.frames = []
        self.frames.append(
            self.get_image(128, 32, 16, 16))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.right = x
        self.rect.y = y
        self.state = c.TOP_OF_POLE

    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image

    def update(self, *args):
        """Updates behavior"""
        self.handle_state()

    def handle_state(self):
        """Determines behavior based on state"""
        if self.state == c.TOP_OF_POLE:
            self.image = self.frames[0]
        elif self.state == c.SLIDE_DOWN:
            self.sliding_down()
        elif self.state == c.BOTTOM_OF_POLE:
            self.image = self.frames[0]

    def sliding_down(self):
        """State when Mario reaches flag pole"""
        self.y_vel = 5
        self.rect.y += self.y_vel

        if self.rect.bottom >= 485:
            self.state = c.BOTTOM_OF_POLE


class Pole(pg.sprite.Sprite):
    """Pole that the flag is on top of
    Following Properties:
        Sprite

    Attributes:
        _Sprite__g: A associative array of all groups the sprite belongs to.
        frames: array of collision frames matching the sprite image dimensions.
        image: The dimensions of the sprite image and orientation
        rect: A rect object that holds relative directions for the sprite
        sprite_sheet: Surface object that holds dimensions for the sprite sheet
    """
    def __init__(self, x, y):
        super(Pole, self).__init__()
        self.sprite_sheet = setup.GFX['tile_set']
        self.frames = []
        self.frames.append(
            self.get_image(263, 144, 2, 16))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)
        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image

    def update(self, *args):
        """Placeholder for update, since there is nothing to update"""
        pass


class Finial(pg.sprite.Sprite):
    """The top of the flag pole
    Following Properties:
        Sprite

    Attributes:
        _Sprite__g: A associative array of all groups the sprite belongs to.
        frames: array of collision frames matching the sprite image dimensions.
        image: The dimensions of the sprite image and orientation
        rect: A rect object that holds relative directions for the sprite
        sprite_sheet: Surface object that holds dimensions for the sprite sheet
    """
    def __init__(self, x, y):
        super(Finial, self).__init__()
        self.sprite_sheet = setup.GFX['tile_set']
        self.frames = []
        self.frames.append(
            self.get_image(228, 120, 8, 8))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

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

    def update(self, *args):
        pass
