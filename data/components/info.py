__author__ = 'justinarmstrong'

import pygame as pg
from .. import setup


class Character(pg.sprite.Sprite):
    """Parent class for all characters used for the overhead level info"""
    def __init__(self, character):
        super(Character, self).__init__()
        self.value = character
        self.sprite_sheet = setup.GFX['text_images']
        self.create_numbers_image_dict()
        self.image = self.image_dict[character]
        self.rect = self.image.get_rect()


    def create_numbers_image_dict(self):
        """Creates the initial images for the score"""
        self.image_dict = {}
        image_list = []

        image_list.append(self.get_image(3, 230, 7, 7))
        image_list.append(self.get_image(12, 230, 7, 7))
        image_list.append(self.get_image(19, 230, 7, 7))
        image_list.append(self.get_image(27, 230, 7, 7))
        image_list.append(self.get_image(35, 230, 7, 7))
        image_list.append(self.get_image(43, 230, 7, 7))
        image_list.append(self.get_image(51, 230, 7, 7))
        image_list.append(self.get_image(59, 230, 7, 7))
        image_list.append(self.get_image(67, 230, 7, 7))
        image_list.append(self.get_image(75, 230, 7, 7))

        for image, i in enumerate(image_list):
            self.image_dict[str(i)] = image


    def get_image(self, x, y, width, height):
        """Extracts image from sprite sheet"""
        image = pg.Surface([width, height])
        rect = image.get_rect()

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((92, 148, 252))
        image = pg.transform.scale(image,
                                   (int(rect.width*c.BRICK_SIZE_MULTIPLIER),
                                    int(rect.height*c.BRICK_SIZE_MULTIPLIER)))
        return image



class OverheadInfo(object):
    """Class for level information like score, coin total,
        and time remaining"""
    def __init__(self):
        self.score = 0
        self.score_images = []
        self.coin_total = 0
        self.time = 400
        self.current_time = 0
        self.create_score_group()


    def create_score_group(self):
        self.score_group = pg.sprite.Group()

        for number in range(6):
            self.score_group.add(Character(str(number)))

        for number in self.score_group:
            number.rect.x = 100 + (number.rect.width * number.value)


    def update(self, level_info):
        self.score = level_info['score']
        self.coin_total = level_info['coin_total']
        self.current_time = level_info['current_time']
        self.update_score()


    def update_score(self):
        """Updates what numbers are to be blitted for the score"""



    def update_time(self):
        pass