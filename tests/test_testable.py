import unittest

from test.itest import ITest
from test.testable import AStep


class TestAStep(unittest.TestCase):

    def test_astep_assess_state_default_expected_pass(self):
        step = AStep('Default untested', ITest.State.PASS)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.PASS)

    def test_astep_assess_state_default_expected_untested(self):
        step = AStep('Default untested')
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNTESTED)

    def test_astep_assess_state_expected_contains_pass(self):
        step = AStep('Default untested', ITest.State.PASS, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)


if __name__ == '__main__':
    unittest.main()