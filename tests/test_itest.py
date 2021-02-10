import unittest
from unittest import TestCase

from test.itest import ITest


class TestITest(TestCase):

    def test_state(self, state=ITest.State.PASS):
        self.assertIn(state, ITest.State)


if __name__ == '__main__':
    unittest.main()
