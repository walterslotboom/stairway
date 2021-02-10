import inspect
import unittest

from test.itest import ITest
from test.testable import Step, AStair


class TestStep(unittest.TestCase):

    def test_step__assess_state__expected_pass__actual_pass(self):
        step = Step(inspect.currentframe(), ITest.State.PASS)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.PASS)

    def test_step__assess_state__expected_pass__actual_marginal(self):
        step = Step(inspect.currentframe(), ITest.State.MARGINAL)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.MARGINAL)

    def test_step__assess_state__default_expected_pass__actual_untested(self):
        step = Step('Default untested')
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNTESTED)

    def test_step__assess_state__explicit_single_expected_pass__actual_pass(self):
        step = Step('Default untested', ITest.State.PASS, expecteds=[ITest.State.PASS])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.PASS)

    def test_step__assess_state__explicit_single_expected_pass__actual_fail(self):
        step = Step('Default untested', ITest.State.FAIL, expecteds=[ITest.State.PASS])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.FAIL)

    def test_step__assess_state__single_expected_marginal__actual_marginal(self):
        step = Step('Default untested', ITest.State.MARGINAL, expecteds=[ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)

    def test_step__assess_state__single_expected_marginal__actual_fail(self):
        step = Step('Default untested', ITest.State.FAIL, expecteds=[ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNEXPECTED)

    def test_step__assess_state__multi_expected_contains_pass__actual_pass(self):
        step = Step('Default untested', ITest.State.PASS, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)

    def test_step__assess_state__multi_expected_contains_pass__actual_expected_nonpass(self):
        step = Step('Default untested', ITest.State.MARGINAL, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)

    def test_step__assess_state__multi_expected_contains_pass__actual_unexpected_nonpass(self):
        step = Step('Default untested', ITest.State.FAIL, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNEXPECTED)


# class TestAStair(unittest.TestCase):
#
#     def test_stepper(self):
#         stair = AStair()
#         with stair.stepper('description', ITest.State.UNTESTED, 'message', [ITest.State.PASS]) as stepper:
#             stepper.result.state = ITest.State.PASS
#         self.assertEqual(stair.result.state, ITest.State.PASS)




if __name__ == '__main__':
    unittest.main()