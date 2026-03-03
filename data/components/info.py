"""Info component for Super Mario Bros."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pygame as pg

from data import constants as c
from .. import setup
from . import flashing_coin


class Character(pg.sprite.Sprite):
    """Parent class for all characters used for the overhead level info"""

    def __init__(self, image: pg.Surface) -> None:
        super(Character, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()


class OverheadInfo:
    """Class for level information like score, coin total,
    and time remaining"""

    sprite_sheet: pg.Surface
    coin_total: int
    time: int
    current_time: float
    total_lives: int
    top_score: int
    state: str
    special_state: Optional[str]
    game_info: Dict[str, Any]

    image_dict: Dict[str, pg.Surface]
    score_images: List[Character]
    mario_label: List[Character]
    world_label: List[Character]
    time_label: List[Character]
    stage_label: List[Character]
    label_list: List[List[Character]]
    center_labels: List[List[Character]]
    count_down_images: List[Character]
    coin_count_images: List[Character]
    flashing_coin: Optional[flashing_coin.Coin]
    life_times_image: Optional[pg.Surface]
    life_times_rect: Optional[pg.Rect]
    life_total_label: List[Character]
    mario_image: Optional[pg.Surface]
    mario_rect: Optional[pg.Rect]
    game_over_label: List[List[Character]]
    time_out_label: List[List[Character]]
    player_one_label: List[Character]
    player_two_label: List[Character]
    main_menu_labels: List[List[Character]]

    def __init__(self, game_info: Dict[str, Any], state: str) -> None:
        self.sprite_sheet = setup.GFX["text_images"]
        self.coin_total = game_info[c.COIN_TOTAL]
        self.time = 401
        self.current_time: float = 0
        self.total_lives = game_info[c.LIVES]
        self.top_score = game_info[c.TOP_SCORE]
        self.state = state
        self.special_state: Optional[str] = None
        self.game_info = game_info

        self.create_image_dict()
        self.create_score_group()
        self.create_info_labels()
        self.create_load_screen_labels()
        self.create_countdown_clock()
        self.create_coin_counter()
        self.create_flashing_coin()
        self.create_mario_image()
        self.create_game_over_label()
        self.create_time_out_label()
        self.create_main_menu_labels()

    def create_image_dict(self) -> None:
        """Creates the initial images for the score"""
        self.image_dict: Dict[str, pg.Surface] = {}
        image_list: List[pg.Surface] = []

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

        image_list.append(self.get_image(83, 230, 7, 7))
        image_list.append(self.get_image(91, 230, 7, 7))
        image_list.append(self.get_image(99, 230, 7, 7))
        image_list.append(self.get_image(107, 230, 7, 7))
        image_list.append(self.get_image(115, 230, 7, 7))
        image_list.append(self.get_image(123, 230, 7, 7))
        image_list.append(self.get_image(3, 238, 7, 7))
        image_list.append(self.get_image(11, 238, 7, 7))
        image_list.append(self.get_image(20, 238, 7, 7))
        image_list.append(self.get_image(27, 238, 7, 7))
        image_list.append(self.get_image(35, 238, 7, 7))
        image_list.append(self.get_image(44, 238, 7, 7))
        image_list.append(self.get_image(51, 238, 7, 7))
        image_list.append(self.get_image(59, 238, 7, 7))
        image_list.append(self.get_image(67, 238, 7, 7))
        image_list.append(self.get_image(75, 238, 7, 7))
        image_list.append(self.get_image(83, 238, 7, 7))
        image_list.append(self.get_image(91, 238, 7, 7))
        image_list.append(self.get_image(99, 238, 7, 7))
        image_list.append(self.get_image(108, 238, 7, 7))
        image_list.append(self.get_image(115, 238, 7, 7))
        image_list.append(self.get_image(123, 238, 7, 7))
        image_list.append(self.get_image(3, 246, 7, 7))
        image_list.append(self.get_image(11, 246, 7, 7))
        image_list.append(self.get_image(20, 246, 7, 7))
        image_list.append(self.get_image(27, 246, 7, 7))
        image_list.append(self.get_image(48, 248, 7, 7))

        image_list.append(self.get_image(68, 249, 6, 2))
        image_list.append(self.get_image(75, 247, 6, 6))

        character_string = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ -*"

        for character, image in zip(character_string, image_list):
            self.image_dict[character] = image

    def get_image(self, x: int, y: int, width: int, height: int) -> pg.Surface:
        """Extracts image from sprite sheet"""
        image = pg.Surface([width, height])

        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((92, 148, 252))
        image = pg.transform.scale(
            image, (int(width * 2.9), int(height * 2.9))
        )
        return image

    def create_score_group(self) -> None:
        """Creates the initial empty score (000000)"""
        self.score_images: List[Character] = []
        self.create_label(self.score_images, "000000", 75, 55)

    def create_info_labels(self) -> None:
        """Creates the labels that describe each info"""
        self.mario_label: List[Character] = []
        self.world_label: List[Character] = []
        self.time_label: List[Character] = []
        self.stage_label: List[Character] = []

        self.create_label(self.mario_label, "MARIO", 75, 30)
        self.create_label(self.world_label, "WORLD", 450, 30)
        self.create_label(self.time_label, "TIME", 625, 30)
        self.create_label(self.stage_label, "1-1", 472, 55)

        self.label_list: List[List[Character]] = [
            self.mario_label,
            self.world_label,
            self.time_label,
            self.stage_label,
        ]

    def create_load_screen_labels(self) -> None:
        """Creates labels for the center info of a load screen"""
        world_label: List[Character] = []
        number_label: List[Character] = []

        self.create_label(world_label, "WORLD", 280, 200)
        self.create_label(number_label, "1-1", 430, 200)

        self.center_labels: List[List[Character]] = [world_label, number_label]

    def create_countdown_clock(self) -> None:
        """Creates the count down clock for the level"""
        self.count_down_images: List[Character] = []
        self.create_label(self.count_down_images, str(self.time), 645, 55)

    def create_label(
        self, label_list: List[Character], string: str, x: int | float, y: int | float
    ) -> None:
        """Creates a label (WORLD, TIME, MARIO)"""
        for letter in string:
            label_list.append(Character(self.image_dict[letter]))

        self.set_label_rects(label_list, int(x), int(y))

    def set_label_rects(
        self, label_list: List[Character], x: int, y: int
    ) -> None:
        """Set the location of each individual character"""
        for i, letter in enumerate(label_list):
            if letter.rect is not None:
                letter.rect.x = x + ((letter.rect.width + 3) * i)
                letter.rect.y = y
                if letter.image == self.image_dict["-"]:
                    letter.rect.y += 7
                    letter.rect.x += 2

    def create_coin_counter(self) -> None:
        """Creates the info that tracks the number of coins Mario collects"""
        self.coin_count_images: List[Character] = []
        self.create_label(self.coin_count_images, "*00", 300, 55)

    def create_flashing_coin(self) -> None:
        """Creates the flashing coin next to the coin total"""
        self.flashing_coin = flashing_coin.Coin(280, 53)

    def create_mario_image(self) -> None:
        """Get the mario image"""
        self.life_times_image = self.get_image(75, 247, 6, 6)
        self.life_times_rect = self.life_times_image.get_rect(center=(378, 295))
        self.create_label(self.life_total_label, str(self.total_lives), 450, 285)

        self.sprite_sheet = setup.GFX["mario_bros"]
        self.mario_image = self.get_image(178, 32, 12, 16)
        self.mario_rect = self.mario_image.get_rect(center=(320, 290))

    def create_game_over_label(self) -> None:
        """Create the label for the GAME OVER screen"""
        game_label: List[Character] = []
        over_label: List[Character] = []

        self.create_label(game_label, "GAME", 280, 300)
        self.create_label(over_label, "OVER", 400, 300)

        self.game_over_label: List[List[Character]] = [game_label, over_label]

    def create_time_out_label(self) -> None:
        """Create the label for the time out screen"""
        time_out_label: List[Character] = []

        self.create_label(time_out_label, "TIME OUT", 290, 310)
        self.time_out_label: List[List[Character]] = [time_out_label]

    def create_main_menu_labels(self) -> None:
        """Create labels for the MAIN MENU screen"""
        player_one_game: List[Character] = []
        player_two_game: List[Character] = []
        top: List[Character] = []
        top_score: List[Character] = []

        self.create_label(player_one_game, "1 PLAYER GAME", 272, 360)
        self.create_label(player_two_game, "2 PLAYER GAME", 272, 405)
        self.create_label(top, "TOP - ", 290, 465)
        self.create_label(top_score, "000000", 400, 465)

        self.main_menu_labels: List[List[Character]] = [
            player_one_game,
            player_two_game,
            top,
            top_score,
        ]

    def update(
        self, level_info: Dict[str, Any], mario: Optional[Any] = None
    ) -> None:
        """Updates all overhead info"""
        self.mario = mario
        self.handle_level_state(level_info)

    def handle_level_state(self, level_info: Dict[str, Any]) -> None:
        """Updates info based on what state the game is in"""
        if self.state == c.MAIN_MENU:
            self.score = level_info[c.SCORE]
            self.update_score_images(self.score_images, self.score)
            self.update_score_images(self.main_menu_labels[3], self.top_score)
            self.update_coin_total(level_info)
            if self.flashing_coin:
                self.flashing_coin.update(level_info[c.CURRENT_TIME])

        elif self.state == c.LOAD_SCREEN:
            self.score = level_info[c.SCORE]
            self.update_score_images(self.score_images, self.score)
            self.update_coin_total(level_info)

        elif self.state == c.LEVEL:
            self.score = level_info[c.SCORE]
            self.update_score_images(self.score_images, self.score)
            if (
                level_info[c.LEVEL_STATE] != c.FROZEN
                and self.mario is not None
                and self.mario.state != c.WALKING_TO_CASTLE
                and self.mario.state != c.END_OF_LEVEL_FALL
                and not self.mario.dead
            ):
                self.update_count_down_clock(level_info)
            self.update_coin_total(level_info)
            if self.flashing_coin:
                self.flashing_coin.update(level_info[c.CURRENT_TIME])

        elif self.state == c.TIME_OUT:
            self.score = level_info[c.SCORE]
            self.update_score_images(self.score_images, self.score)
            self.update_coin_total(level_info)

        elif self.state == c.GAME_OVER:
            self.score = level_info[c.SCORE]
            self.update_score_images(self.score_images, self.score)
            self.update_coin_total(level_info)

        elif self.state == c.FAST_COUNT_DOWN:
            level_info[c.SCORE] += 50
            self.score = level_info[c.SCORE]
            self.update_count_down_clock(level_info)
            self.update_score_images(self.score_images, self.score)
            self.update_coin_total(level_info)
            if self.flashing_coin:
                self.flashing_coin.update(level_info[c.CURRENT_TIME])
            if self.time == 0:
                self.state = c.END_OF_LEVEL

        elif self.state == c.END_OF_LEVEL:
            if self.flashing_coin:
                self.flashing_coin.update(level_info[c.CURRENT_TIME])

    def update_score_images(
        self, images: List[Character], score: int
    ) -> None:
        """Updates what numbers are to be blitted for the score"""
        index = len(images) - 1

        for digit in reversed(str(score)):
            rect = images[index].rect
            images[index] = Character(self.image_dict[digit])
            images[index].rect = rect
            index -= 1

    def update_count_down_clock(self, level_info: Dict[str, Any]) -> None:
        """Updates current time"""
        if self.state == c.FAST_COUNT_DOWN:
            self.time -= 1

        elif (level_info[c.CURRENT_TIME] - self.current_time) > 400:
            self.current_time = level_info[c.CURRENT_TIME]
            self.time -= 1
        self.count_down_images = []
        self.create_label(self.count_down_images, str(self.time), 645, 55)
        if len(self.count_down_images) < 2:
            for i in range(2):
                self.count_down_images.insert(0, Character(self.image_dict["0"]))
            self.set_label_rects(self.count_down_images, 645, 55)
        elif len(self.count_down_images) < 3:
            self.count_down_images.insert(0, Character(self.image_dict["0"]))
            self.set_label_rects(self.count_down_images, 645, 55)

    def update_coin_total(self, level_info: Dict[str, Any]) -> None:
        """Updates the coin total and adjusts label accordingly"""
        self.coin_total = level_info[c.COIN_TOTAL]

        coin_string = str(self.coin_total)
        if len(coin_string) < 2:
            coin_string = "*0" + coin_string
        elif len(coin_string) > 2:
            coin_string = "*00"
        else:
            coin_string = "*" + coin_string

        first_coin: Optional[Character] = (
            self.coin_count_images[0] if self.coin_count_images else None
        )
        if first_coin and first_coin.rect:
            x = first_coin.rect.x
            y = first_coin.rect.y
        else:
            x, y = 300, 55

        self.coin_count_images = []

        self.create_label(self.coin_count_images, coin_string, x, y)

    def draw(self, surface: pg.Surface) -> None:
        """Draws overhead info based on state"""
        if self.state == c.MAIN_MENU:
            self.draw_main_menu_info(surface)
        elif self.state == c.LOAD_SCREEN:
            self.draw_loading_screen_info(surface)
        elif self.state == c.LEVEL:
            self.draw_level_screen_info(surface)
        elif self.state == c.GAME_OVER:
            self.draw_game_over_screen_info(surface)
        elif self.state == c.FAST_COUNT_DOWN:
            self.draw_level_screen_info(surface)
        elif self.state == c.END_OF_LEVEL:
            self.draw_level_screen_info(surface)
        elif self.state == c.TIME_OUT:
            self.draw_time_out_screen_info(surface)

    def draw_main_menu_info(self, surface: pg.Surface) -> None:
        """Draws info for main menu"""
        for info in self.score_images:
            surface.blit(info.image, info.rect)  # type: ignore[arg-type]

        for label in self.main_menu_labels:
            for letter in label:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        for character in self.coin_count_images:
            surface.blit(character.image, character.rect)  # type: ignore[arg-type]

        for label in self.label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        if self.flashing_coin:
            surface.blit(self.flashing_coin.image, self.flashing_coin.rect)  # type: ignore[arg-type]

    def draw_loading_screen_info(self, surface: pg.Surface) -> None:
        """Draws info for loading screen"""
        for info in self.score_images:
            surface.blit(info.image, info.rect)  # type: ignore[arg-type]

        for word in self.center_labels:
            for letter in word:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        for character in self.life_total_label:
            surface.blit(character.image, character.rect)  # type: ignore[arg-type]

        if self.mario_image and self.mario_rect:
            surface.blit(self.mario_image, self.mario_rect)
        if self.life_times_image and self.life_times_rect:
            surface.blit(self.life_times_image, self.life_times_rect)

        for character in self.coin_count_images:
            surface.blit(character.image, character.rect)  # type: ignore[arg-type]

        for label in self.label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        if self.flashing_coin:
            surface.blit(self.flashing_coin.image, self.flashing_coin.rect)  # type: ignore[arg-type]

    def draw_level_screen_info(self, surface: pg.Surface) -> None:
        """Draws info during regular game play"""
        for info in self.score_images:
            surface.blit(info.image, info.rect)  # type: ignore[arg-type]

        for digit in self.count_down_images:
            surface.blit(digit.image, digit.rect)  # type: ignore[arg-type]

        for character in self.coin_count_images:
            surface.blit(character.image, character.rect)  # type: ignore[arg-type]

        for label in self.label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        if self.flashing_coin:
            surface.blit(self.flashing_coin.image, self.flashing_coin.rect)  # type: ignore[arg-type]

    def draw_game_over_screen_info(self, surface: pg.Surface) -> None:
        """Draws info when game over"""
        for info in self.score_images:
            surface.blit(info.image, info.rect)  # type: ignore[arg-type]

        for word in self.game_over_label:
            for letter in word:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        for character in self.coin_count_images:
            surface.blit(character.image, character.rect)  # type: ignore[arg-type]

        for label in self.label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        if self.flashing_coin:
            surface.blit(self.flashing_coin.image, self.flashing_coin.rect)  # type: ignore[arg-type]

    def draw_time_out_screen_info(self, surface: pg.Surface) -> None:
        """Draws info when on the time out screen"""
        for info in self.score_images:
            surface.blit(info.image, info.rect)  # type: ignore[arg-type]

        for word in self.time_out_label:
            for letter in word:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        for character in self.coin_count_images:
            surface.blit(character.image, character.rect)  # type: ignore[arg-type]

        for label in self.label_list:
            for letter in label:
                surface.blit(letter.image, letter.rect)  # type: ignore[arg-type]

        if self.flashing_coin:
            surface.blit(self.flashing_coin.image, self.flashing_coin.rect)  # type: ignore[arg-type]
