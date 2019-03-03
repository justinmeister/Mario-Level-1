import unittest
from ..states import level1
from ..components import powerups


class TestLevel1(unittest.TestCase):

    def setUp(self):
        self.l1 = level1.Level1()
        self.l1.startup
        self.l1.setup_bricks()


    def test_bounce_fireball(self):
        fb1 = powerups.FireBall(1,1,True)
        fb2 = powerups.FireBall(1,1,False)
        self.l1.bounce_fireball(fb1)
        self.assertEquals(fb1.y_vel, -8)
        self.assertEquals(fb1.x_vel, 15)
        self.l1.bounce_fireball(fb2)
        self.assertEquals(fb2.y_vel, -8)
        self.assertEquals(fb2.x_vel, -15)



if __name__ == '__main__':
    unittest.main()
