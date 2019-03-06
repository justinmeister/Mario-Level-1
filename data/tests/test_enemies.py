import unittest
from ..states import level1
from ..components import powerups
from ..components import enemies
from .. import constants as c
from pprint import pprint


class TestEnemies(unittest.TestCase):

        def test_enemies_init_velocity(self):
                """Test the initial velocity of monster constructors"""
                goomba = enemies.Goomba()
                koopa = enemies.Koopa()

                """Test starting velocity of both monsters constructors"""
                self.assertEquals(goomba.x_vel, -2)
                self.assertEquals(goomba.y_vel, 0)
                self.assertEquals(koopa.x_vel, -2)
                self.assertEquals(koopa.y_vel, 0)

                """Test starting velocity against bad values"""
                self.assertNotEquals(goomba.x_vel, -12)
                self.assertNotEquals(goomba.x_vel, -11)
                self.assertNotEquals(goomba.x_vel, 0)
                self.assertNotEquals(goomba.x_vel, 12)
                self.assertNotEquals(goomba.x_vel, 7)
                self.assertNotEquals(goomba.y_vel, -7)
                self.assertNotEquals(koopa.x_vel, -4)
                self.assertNotEquals(koopa.x_vel, -3)
                self.assertNotEquals(koopa.x_vel, -9)
                self.assertNotEquals(koopa.x_vel, 0)
                self.assertNotEquals(koopa.x_vel, 4)
                self.assertNotEquals(koopa.x_vel, 2)
                self.assertNotEquals(koopa.y_vel, 5)

        def test_enemies_init_direction(self):
                """Test the initial direction of monster constructors"""
                goomba = enemies.Goomba()
                koopa = enemies.Koopa()

                """Test starting direction of both monsters constructors"""
                self.assertEquals(goomba.direction, 'left')
                self.assertEquals(koopa.direction, 'left')

                """Test starting direction against other possible value"""
                self.assertNotEquals(goomba.direction, 'right')
                self.assertNotEquals(koopa.direction, 'right')

        def test_enemies_init_frame_index(self):
                """Test the initial frame_index of monster constructors"""

                goomba = enemies.Goomba()
                koopa = enemies.Koopa()

                """Test initial frame index"""
                self.assertEquals(goomba.frame_index, 0)
                self.assertEquals(koopa.frame_index, 0)

                """Check frame index against bad values"""
                self.assertNotEquals(goomba.frame_index, 2)
                self.assertNotEquals(koopa.frame_index, 2)
                self.assertNotEquals(goomba.frame_index, 1)
                self.assertNotEquals(koopa.frame_index, 1)
                self.assertNotEquals(goomba.frame_index, 3)
                self.assertNotEquals(koopa.frame_index, 3)
                self.assertNotEquals(goomba.frame_index, 100)
                self.assertNotEquals(koopa.frame_index, 100)
                self.assertNotEquals(goomba.frame_index, 'right')
                self.assertNotEquals(koopa.frame_index, 'right')
                self.assertNotEquals(goomba.frame_index, 23)
                self.assertNotEquals(koopa.frame_index, 23)

        def test_enemies_init_gravity(self):
                """Test initial gravity of koopa and goomba constructors"""

                goomba = enemies.Goomba()
                koopa = enemies.Koopa()

                """Test initial gravity value"""
                self.assertEquals(goomba.gravity, 1.5)
                self.assertEquals(koopa.gravity, 1.5)

                """Check gravity against bad values"""
                self.assertNotEquals(goomba.gravity, 2)
                self.assertNotEquals(goomba.gravity, 10)
                self.assertNotEquals(goomba.gravity, -1)
                self.assertNotEquals(goomba.gravity, 'right')
                self.assertNotEquals(goomba.gravity, -8)
                self.assertNotEquals(goomba.gravity, 121)
                self.assertNotEquals(goomba.gravity, 3)
                self.assertNotEquals(koopa.gravity, 3)
                self.assertNotEquals(koopa.gravity, 21)
                self.assertNotEquals(koopa.gravity, 14)
                self.assertNotEquals(koopa.gravity, 'left')
                self.assertNotEquals(koopa.gravity, 21)
                self.assertNotEquals(koopa.gravity, -212)
                self.assertNotEquals(koopa.gravity, 12312)

        def test_enemies_init_state(self):
                """Test initial gravity of koopa and goomba constructors"""

                goomba = enemies.Goomba()
                koopa = enemies.Koopa()

                """Test initial state value"""
                self.assertEquals(goomba.state, 'walk')
                self.assertEquals(koopa.state, 'walk')

                """Check state against bad values"""
                self.assertNotEquals(goomba.state, 2)
                self.assertNotEquals(goomba.state, 'falling')
                self.assertNotEquals(goomba.state, 'left')
                self.assertNotEquals(goomba.state, 'right')
                self.assertNotEquals(goomba.state, 'death jump')
                self.assertNotEquals(goomba.state, 'jumped on')
                self.assertNotEquals(goomba.state, 'resting')
                self.assertNotEquals(goomba.state, 'bumped')
                self.assertNotEquals(goomba.state, 'slide')
                self.assertNotEquals(koopa.state, 2)
                self.assertNotEquals(koopa.state, 'falling')
                self.assertNotEquals(koopa.state, 'left')
                self.assertNotEquals(koopa.state, 'right')
                self.assertNotEquals(koopa.state, 'death jump')
                self.assertNotEquals(koopa.state, 'jumped on')
                self.assertNotEquals(koopa.state, 'resting')
                self.assertNotEquals(koopa.state, 'bumped')
                self.assertNotEquals(koopa.state, 'slide')



        def test_goomba_velocity_change(self):
                """This test is to confirm that the velocity will change when the direction of the goomba changes"""

                goomba1 = enemies.Goomba()
                """Test to insure proper initial value"""
                self.assertEquals(goomba1.x_vel, -2)
                self.assertEquals(goomba1.y_vel, 0)

                """Change direction"""
                goomba1.direction = 'right'
                """Call set velocity function to change the sign of x_vel"""
                goomba1.set_velocity()

                """Test for desired value 2"""
                self.assertEquals(goomba1.x_vel, 2)
                self.assertEquals(goomba1.y_vel, 0)

        def test_koopa_velocity_change(self):
                """This test is to confirm that the velocity will change when the direction of the koopa changes"""
                koopa = enemies.Koopa()

                """Test to insure proper initial value"""
                self.assertEquals(koopa.x_vel, -2)
                self.assertEquals(koopa.y_vel, 0)

                """Change direction"""
                koopa.direction = 'right'
                """Call set velocity function to change the sign of x_vel"""
                koopa.set_velocity()

                """Test for desired value 2"""
                self.assertEquals(koopa.x_vel, 2)
                self.assertEquals(koopa.y_vel, 0)

if __name__ == '__main__':
    unittest.main()
