import unittest
from unittest import TestCase

from test.itest import ITest
from test.testable import Step, Flight


class TestStep(TestCase):

    def test_step__assess_state__expected_pass__actual_pass(self):
        step = Step(None, ITest.State.PASS)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.PASS)

    def test_step__assess_state__expected_pass__actual_marginal(self):
        step = Step(None, ITest.State.MARGINAL)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.MARGINAL)

    def test_step__assess_state__default_expected_pass__actual_untested(self):
        step = Step(None)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNTESTED)

    def test_step__assess_state__explicit_single_expected_pass__actual_pass(self):
        step = Step(None, ITest.State.PASS, expecteds=[ITest.State.PASS])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.PASS)

    def test_step__assess_state__explicit_single_expected_pass__actual_fail(self):
        step = Step(None, ITest.State.FAIL, expecteds=[ITest.State.PASS])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.FAIL)

    def test_step__assess_state__single_expected_marginal__actual_marginal(self):
        step = Step(None, ITest.State.MARGINAL, expecteds=[ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)

    def test_step__assess_state__single_expected_marginal__actual_fail(self):
        step = Step(None, ITest.State.FAIL, expecteds=[ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNEXPECTED)

    def test_step__assess_state__multi_expected_contains_pass__actual_pass(self):
        step = Step(None, ITest.State.PASS, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)

    def test_step__assess_state__multi_expected_contains_pass__actual_expected_nonpass(self):
        step = Step(None, ITest.State.MARGINAL, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.EXPECTED)

    def test_step__assess_state__multi_expected_contains_pass__actual_unexpected_nonpass(self):
        step = Step(None, ITest.State.FAIL, expecteds=[ITest.State.PASS, ITest.State.MARGINAL])
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.UNEXPECTED)


class TestAFlight(TestCase):

    def test_flight__single_pass(self):
        flight = Flight()
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        self.assertEqual(flight.result.state, ITest.State.PASS)

    def test_flight__pass_fail(self):
        flight = Flight()
        flight.response = ITest.Response.proceed
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.FAIL
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        self.assertEqual(flight.result.state, ITest.State.FAIL)

    def test_flight__nested_marginal(self):
        flight_outer = Flight()
        flight_outer.response = ITest.Response.proceed
        with flight_outer.stepper(None, ITest.State.UNTESTED, None) as stepper:
            stepper.result.state = ITest.State.PASS
        self.assertEqual(flight_outer.result.state, ITest.State.PASS)
        with flight_outer.flyer(None, None, ITest.State.UNTESTED, None) as flight_inner:
            flight_inner.response = ITest.Response.proceed
            with flight_inner.stepper(None, ITest.State.UNTESTED, None) as stepper:
                stepper.result.state = ITest.State.MARGINAL
            self.assertEqual(flight_inner.result.state, ITest.State.MARGINAL)
        self.assertEqual(flight_outer.result.state, ITest.State.MARGINAL)


if __name__ == '__main__':
    unittest.main()
