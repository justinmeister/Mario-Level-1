import unittest
from ..states import level1
from ..components import powerups
from .. import constants as c
from pprint import pprint


class TestLevel1(unittest.TestCase):

    def setUp(self):
        self.persist = {c.COIN_TOTAL: 0,
                        c.SCORE: 0,
                        c.LIVES: 3,
                        c.TOP_SCORE: 0,
                        c.CURRENT_TIME: 0.0,
                        c.LEVEL_STATE: None,
                        c.CAMERA_START_X: 0,
                        c.MARIO_DEAD: False}

    def test_bounce_fireball(self):
        # Setup
        l1 = level1.Level1()
        l1.startup(0.0, self.persist)
        fb1 = powerups.FireBall(1, 1, True)
        l1.bounce_fireball(fb1)
        fb2 = powerups.FireBall(1, 1, False)
        l1.powerup_group.add(fb2)
        l1.bounce_fireball(fb2)

        # Assertions
        self.assertEquals(fb1.y_vel, -8)
        self.assertEquals(fb1.x_vel, 15)
        self.assertEqual(fb1.state, 'flying')
        self.assertEquals(fb2.y_vel, -8)
        self.assertEquals(fb2.x_vel, -15)
        self.assertEqual(fb2.state, 'bouncing')

    def test_adjust_fireball_position(self):
        # Setup
        l1 = level1.Level1()
        l1.startup(0.0, self.persist)

        # Bouncing FireBall
        fb1 = powerups.FireBall(1, 1, True)
        fb1.state = c.BOUNCING
        l1.adjust_fireball_position(fb1)

        # Flying FireBall
        fb2 = powerups.FireBall(1, 1, False)
        l1.adjust_fireball_position(fb2)

        # Off Screen FireBall
        fb3 = powerups.FireBall(1, 1, True)
        fb3.rect.x = -99999
        l1.enemy_group.add(fb3)
        l1.ground_group.add(fb3)
        l1.adjust_fireball_position(fb3)

        # Assertions
        self.assertEquals(fb1.rect.x, -7)
        self.assertEquals(fb1.rect.y, 11)
        self.assertEquals(fb1.y_vel,  10.9)
        self.assertEquals(fb2.rect.x, -31)
        self.assertEquals(fb2.rect.y, 11)
        self.assertEquals(fb2.y_vel,  10)
        self.assertNotIn(fb3, l1.enemy_group)
        self.assertNotIn(fb3, l1.ground_group)


if __name__ == '__main__':
    unittest.main()
