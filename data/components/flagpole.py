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
        super(Flag, self).__init__()  # Initialize parent class
        self.sprite_sheet = setup.GFX['item_objects']  # Set sprite category
        self.frames = []  # Declare frames attribute
        self.frames.append(
            self.get_image(128, 32, 16, 16))  # Get image and assign location
        self.image = self.frames[0]  # declare Image and load first frame image
        self.rect = self.image.get_rect()  # declare and instantiate rect
        self.rect.right = x  # Set rect x pos
        self.rect.y = y  # Set rect y pos
        self.state = c.TOP_OF_POLE  # Declare state name

    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet

           Return: image object
        """
        image = pg.Surface([width, height])  # Create image surface
        rect = image.get_rect()  # Retrieve initial rect object
        # Bind sprite dimensions to sprite_sheet
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)  # Set color scheme
        # Resize image to fit sprite_sheet
        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image

    def update(self, *args):
        """Updates behavior"""
        self.handle_state()

    def handle_state(self):
        """Determines behavior based on state"""
        if self.state == c.TOP_OF_POLE:  # Check flag position
            self.image = self.frames[0]  # Set image frame
        elif self.state == c.SLIDE_DOWN:  # Check flag position
            self.sliding_down()  # call sliding down animation
        elif self.state == c.BOTTOM_OF_POLE:  # Check flag position
            self.image = self.frames[0]  # Set image frame

    def sliding_down(self):
        """State when Mario reaches flag pole"""
        self.y_vel = 5  # set initial vertical value
        self.rect.y += self.y_vel  # Update vertical value based on velocity
        if self.rect.bottom >= 485:  # Check is flag is at the bottom
            self.state = c.BOTTOM_OF_POLE  # switch to Bottom pole state


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
        super(Pole, self).__init__()  # Initialize parent class
        self.sprite_sheet = setup.GFX['tile_set']  # Set sprite category
        self.frames = []  # Declare frames attribute
        self.frames.append(
            self.get_image(263, 144, 2, 16))  # Get image and assign location
        self.image = self.frames[0]  # declare Image and load first frame image
        self.rect = self.image.get_rect()  # declare Image and load first frame
        self.rect.x = x  # Set rect x pos
        self.rect.y = y  # Set rect y pos

    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet

           Return: image object
        """
        image = pg.Surface([width, height])  # Create image surface
        rect = image.get_rect()  # Retrieve initial rect object
        # Bind sprite dimensions to sprite_sheet
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey(c.BLACK)  # Set color scheme
        # Resize image to fit sprite_sheet
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
        super(Finial, self).__init__()  # initialize parent class
        self.sprite_sheet = setup.GFX['tile_set']  # Set sprite category
        self.frames = []  # Declare frames attribute
        self.frames.append(
            self.get_image(228, 120, 8, 8))  # Get image and assign location
        self.image = self.frames[0]  # declare Image and load first frame image
        self.rect = self.image.get_rect()  # declare Image and load first frame
        self.rect.centerx = x  # Set rect x pos
        self.rect.bottom = y  # Set rect y pos

    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet

           Return: image object
        """
        # Create image surface
        image = pg.Surface([width, height])
        # Retrieve initial rect object
        rect = image.get_rect()
        # Bind sprite dimensions to sprite_sheet
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        # Set color scheme
        image.set_colorkey(c.BLACK)
        # Resize image to fit sprite_sheet
        image = pg.transform.scale(image,
                                   (int(rect.width*c.SIZE_MULTIPLIER),
                                    int(rect.height*c.SIZE_MULTIPLIER)))
        return image

    def update(self, *args):
        pass
