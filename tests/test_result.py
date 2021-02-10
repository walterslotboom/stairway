import unittest

from test.itest import ITest
from test.result import AResult


class TestAResult(unittest.TestCase):

    def test_state(self):
        result = AResult('description', ITest.State.UNTESTED)
        self.assertIn(result.state, ITest.State)
        self.assertEqual(result.state, ITest.State.UNTESTED)


if __name__ == '__main__':
    unittest.main()
