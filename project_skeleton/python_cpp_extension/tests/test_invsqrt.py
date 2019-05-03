import pathlib
import unittest


import _skeleton


from . import tests_directory


class QuakeInvSqrtTestCase(unittest.TestCase):

    def test_quake_invsqrt_1(self):
        self.assertEqual(_skeleton.quake_invsqrt(0.15625), 2.5254862308502197)

    def test_quake_invsqrt_2(self):
        self.assertEqual(_skeleton.quake_invsqrt(225), 0.06665154546499252)

    def test_quake_invsqrt_3(self):
        with (tests_directory / 'data/number.txt').open('r') as fh:
            number = float(fh.read().rstrip())
        self.assertEqual(_skeleton.quake_invsqrt(number), 0.003899667179211974)
