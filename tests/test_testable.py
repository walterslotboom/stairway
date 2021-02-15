"""
unitests for testables
"""
import unittest
from unittest import TestCase

from test.itest import ITest
from test.testable import Step, Flight, ACase, ASuite


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

    def test_step__reset(self):
        step = Step(None, ITest.State.PASS)
        step.assess_state()
        self.assertEqual(step.result.state, ITest.State.PASS)
        step.reset_result()
        self.assertEqual(step.result.state, ITest.State.RESET)


class TestAFlight(TestCase):

    def test_flight__single_stepper_pass(self):
        flight = Flight()
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        self.assertEqual(flight.result.state, ITest.State.PASS)

    def test_flight__multi_stepper_fail(self):
        flight = Flight()
        flight.response = ITest.Response.proceed
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.FAIL
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        self.assertEqual(flight.result.state, ITest.State.FAIL)

    def test_flight__nested_flights_marginal(self):
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

    def test_flight__reset(self):
        flight = Flight()
        self.assertListEqual(flight.result.subresults, [])
        with flight.stepper(None, ITest.State.UNTESTED) as stepper:
            stepper.result.state = ITest.State.PASS
        flight.reset_result()
        self.assertEqual(flight.result.state, ITest.State.RESET)
        self.assertListEqual(flight.result.subresults, [])


class TestACase(TestCase):

    def test_acase__stepper_abend(self):
        case = ACase()
        case.response = ITest.Response.proceed
        with case.stepper(None, ITest.State.UNTESTED, None, response=ITest.Response.proceed) as stepper:
            stepper.result.state = ITest.State.ABEND
        self.assertEqual(case.result.state, ITest.State.ABEND)

    def test_acase__flight_inapplicable(self):
        case = ACase()
        case.response = ITest.Response.proceed
        with case.flyer(None, None, ITest.State.UNTESTED, None) as flight:
            flight.response = ITest.Response.proceed
            with flight.stepper(None, ITest.State.UNTESTED, None) as stepper:
                stepper.result.state = ITest.State.INAPPLICABLE
            self.assertEqual(flight.result.state, ITest.State.INAPPLICABLE)
        self.assertEqual(case.result.state, ITest.State.INAPPLICABLE)

    # def test_acase__execute(self):
    #     case = ACase()
    #     case.execute()


class TestASuite(TestCase):

    def test_asuite__case_flight_step_unknown(self):
        case = ACase()
        case.response = ITest.Response.proceed
        suite = ASuite([case])
        suite.response = ITest.Response.proceed
        with case.flyer(None, None, ITest.State.UNTESTED, None) as flight:
            flight.response = ITest.Response.proceed
            with flight.stepper(None, ITest.State.UNTESTED, None) as stepper:
                stepper.result.state = ITest.State.UNKNOWN
            self.assertEqual(flight.result.state, ITest.State.UNKNOWN)
        self.assertEqual(case.result.state, ITest.State.UNKNOWN)
        suite.record_result(case.result)
        self.assertEqual(suite.result.state, ITest.State.UNKNOWN)

    # def test_asuite__execute(self):
    #     case = ACase()
    #     suite = ASuite([case])
    #     suite.execute()


if __name__ == '__main__':
    unittest.main()
