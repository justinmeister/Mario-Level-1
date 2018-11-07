__author__ = 'justinarmstrong'

import pygame as pg
from . import setup
from . import constants as c

class Sound(object):
    """Handles all sound for the game"""
    def __init__(self, overhead_info):
        """Initialize the class"""
        self.sfx_dict = setup.SFX
        self.music_dict = setup.MUSIC
        self.overhead_info = overhead_info
        self.game_info = overhead_info.game_info
        self.set_music_mixer()



    def set_music_mixer(self):
        """Sets music for level"""
        if self.overhead_info.state == c.LEVEL:
            if c.MODE == c.DEJAVUMODE:
                pg.mixer.music.load(self.music_dict['dejavu']) #main_theme
            elif c.MODE == c.ENEMYMODE:
                pg.mixer.music.load(self.music_dict['bowser_main_theme_woahnumberone'])
            else:
                pg.mixer.music.load(self.music_dict['main_theme'])
            pg.mixer.music.play()
            self.state = c.NORMAL
        elif self.overhead_info.state == c.GAME_OVER:
            pg.mixer.music.load(self.music_dict['game_over'])
            pg.mixer.music.play()
            self.state = c.GAME_OVER


    def update(self, game_info, mario):
        """Updates sound object with game info"""
        self.game_info = game_info
        self.mario = mario
        self.handle_state()

    def  handle_state(self):
        """Handles the state of the soundn object"""
        if self.state == c.NORMAL:
            if self.mario.dead:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('death_son_of_bitch', c.MARIO_DEAD)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('death_bowser_noooo', c.MARIO_DEAD)
                else:
                    self.play_music('death', c.MARIO_DEAD)
            elif self.mario.invincible \
                    and self.mario.losing_invincibility == False:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('running_in_the_90', c.MARIO_INVINCIBLE)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('bowser_spedup_theme', c.MARIO_INVINCIBLE)
                else:
                    self.play_music('invincible', c.MARIO_INVINCIBLE)
            elif self.mario.state == c.FLAGPOLE:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('victory_theme_cena', c.FLAGPOLE)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('victory_bowser_yeahboy', c.FLAGPOLE)
                else:
                    self.play_music('flagpole', c.FLAGPOLE)
            elif self.overhead_info.time == 100:
                self.play_music('out_of_time', c.TIME_WARNING)


        elif self.state == c.FLAGPOLE:
            if self.mario.state == c.WALKING_TO_CASTLE:
                self.play_music('stage_clear', c.STAGE_CLEAR)

        elif self.state == c.STAGE_CLEAR:
            if self.mario.in_castle:
                self.sfx_dict['count_down'].play()
                self.state = c.FAST_COUNT_DOWN

        elif self.state == c.FAST_COUNT_DOWN:
            if self.overhead_info.time == 0:
                self.sfx_dict['count_down'].stop()
                self.state = c.WORLD_CLEAR

        elif self.state == c. TIME_WARNING:
            if pg.mixer.music.get_busy() == 0:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('gasgasgas', c.SPED_UP_NORMAL) #main_theme_sped_up
                else:
                    self.play_music('main_theme_sped_up', c.SPED_UP_NORMAL)
            elif self.mario.dead:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('death_son_of_bitch', c.MARIO_DEAD)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('death_bowser_noooo', c.MARIO_DEAD)
                else:
                    self.play_music('death', c.MARIO_DEAD)

        elif self.state == c.SPED_UP_NORMAL:
            if self.mario.dead:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('death_son_of_bitch', c.MARIO_DEAD)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('death_bowser_noooo', c.MARIO_DEAD)
                else:
                    self.play_music('death', c.MARIO_DEAD)
            elif self.mario.state == c.FLAGPOLE:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('victory_theme_cena', c.FLAGPOLE)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('victory_bowser_yeahboy', c.FLAGPOLE)
                else:
                    self.play_music('flagpole', c.FLAGPOLE)

        elif self.state == c.MARIO_INVINCIBLE:
            if (self.mario.current_time - self.mario.invincible_start_timer) > 11000:
                #self.play_music('main_theme', c.NORMAL)
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('dejavu', c.NORMAL)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('bowser_main_theme_woahnumberone', c.NORMAL)
                else:
                    self.play_music('main_theme', c.NORMAL)
            elif self.mario.dead:
                if c.MODE == c.DEJAVUMODE:
                    self.play_music('death_son_of_bitch', c.MARIO_DEAD)
                elif c.MODE == c.ENEMYMODE:
                    self.play_music('death_bowser_noooo', c.MARIO_DEAD)
                else:
                    self.play_music('death', c.MARIO_DEAD)


        elif self.state == c.WORLD_CLEAR:
            pass
        elif self.state == c.MARIO_DEAD:
            pass
        elif self.state == c.GAME_OVER:
            pass

    def play_music(self, key, state):
        """Plays new music"""
        pg.mixer.music.load(self.music_dict[key])
        pg.mixer.music.play()
        self.state = state

    def stop_music(self):
        """Stops playback"""
        pg.mixer.music.stop()



