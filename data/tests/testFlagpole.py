import unittest
from ..components import flagpole
from .. import constants as c
from pprint import pprint

# TODO reset run_all_tests when done


class TestFlagpole(unittest.TestCase):

    def setUp(self):
        self.flag = flagpole.Pole(1, 1)
        self.pole = flagpole.Pole(1, 1)
        self.final = flagpole.Pole(1, 1)
        self.hi = "Hi there"

    def test_flag(self):
        pprint(vars(self.flag))


if __name__ == '__main__':
    unittest.main()
