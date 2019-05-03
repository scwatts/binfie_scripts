import pathlib
import unittest


import skeleton.utils


from . import tests_directory


class QuakeInvSqrtTestCase(unittest.TestCase):

    def test_quake_invsqrt_1(self):
        self.assertEqual(skeleton.utils.quake_invsqrt(0.15625), 2.5254863388218056)

    def test_quake_invsqrt_2(self):
        self.assertEqual(skeleton.utils.quake_invsqrt(225), 0.06665154746355062)

    def test_quake_invsqrt_3(self):
        with (tests_directory / 'data/number.txt').open('r') as fh:
            number = float(fh.read().rstrip())
        self.assertEqual(skeleton.utils.quake_invsqrt(number), 0.003899667155571461)
