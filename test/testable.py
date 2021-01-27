"""
Includes core classes for running tests, recording results, and reporting those results.

Testable hierarchy contains base classes for suites, cases, flights (collections of steps), and steps. Results
automatically propagate up through the testable hierarchy as tests run, and are summarized as they complete. Progress
tracking and results is integrated into the running of the testable objects.
"""
from __future__ import annotations
import contextlib
import pdb

from typing import Dict, List

from test.itest import ITest
from test.result import StepResult, CaseResult, SuiteResult, FlightResult, AResult
from util.enums import TextualEnum
from util.service.report_service import IReport, ReportService
from argparse import ArgumentParser


class ATestable:
    """
    Base class underlying all test actions from a single atomic step to to the largest aggregate suites.

    Abstract class to force functionality for larger constructs.
    It's ultimate purpose is the tracking of the test for its final reporting, but it can be accessed any manipulated
    all during its lifetime.

    :ivar _name: short name for summary references
    :ivar description: long description for meaningful reporting
    :ivar _response: How to react when result state is not pass.
    For non-steps, the run-mode of the tests at large (usually passed from CLI), primarily to pass down to subtestables.
    For steps, the specific response for that step. Therefore subclasses have different setters/getters.
    @todo Is more rigorous response OOP needed?
    :ivar _result: current / final result of testable execution
    """

    DESCRIPTION: str or None = None

    def __init__(self) -> None:
        self._name: str or None = None
        self.description: str = self.DESCRIPTION
        self._response: ITest.Response or None = None
        self._result: AResult or None = None  # should be immediately overridden to untested (for starters)

    def record_result(self, result: AResult) -> None:
        """
        Preserve the final state of testable for future reporting.
        Result object is polymorphic based on type of testable
        :param result: final state of testable
        """
        self._result.record_result(result)

    def report(self) -> None:
        """
        Report the testable's recorded result(s) to I/O (stdout by default)
        """
        self._result.report()

    def reset_result(self) -> None:
        """
        Resets the testable's result and message to that dictated by initialization.
        This is useful when looping a testable to try and induce an intermittent failure.
        """
        self._result.reset()

    @contextlib.contextmanager
    def demarcate_phase(self, phase: str) -> None:
        """
        Output wrapper for bookending any discreet phase of a test
        :param phase: textual name or short description
        """
        message = '{} / {} phase'.format(self.name, phase)
        with ReportService.demarcate(message, IReport.Level.none, IReport.Patency.medium):
            yield

    @property
    def name(self) -> str:
        """
        Short testable name. Primarily for overwriting by subclasses.
        :return: Short name for testable
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def result(self) -> AResult:
        """
        Results are a distinct (if dependent) entity from the test itself.
        Can be accessed during runs but most important at completion.

        :return: Result object with description, state, and optional message
        """
        return self._result

    @result.setter
    def result(self, value: AResult) -> None:
        self._result = value

    @property
    def default_description(self) -> str:
        """
        For testables that do not provide a description, this provides a default (that's better than None).

        :return: string containing the default description of an object
        """
        return '{} ({})'.format(self.name, self.description)


class ACliTestable:
    """
    Mixin for adding command-line handling to higher-level testable objects (e.g. case & suite).

    Contains argument parsing and initialization.

    :ivar **log: Logging level above which to report all events.:
    :ivar **response: Action with which to respond to an unexpected result state.:
    """

    class Args(TextualEnum):
        """
        Valid command-line parameters
        """
        log: int or str = 1
        response: int or str = 2

    @property
    def name(self) -> str:
        """
        The default shortname for CLI-callable testables is the class name.
        This is because they are almost always explicitly and uniquely defined.
        :return: Class name for test.
        """
        return type(self).__name__

    def __init__(self, **kwargs: str) -> None:
        super().__init__()
        self._kwargs = kwargs
        # report all events above the specified level (default info)
        level_name = kwargs.get(self.Args.log.name, str(IReport.Level.info))
        ReportService.level_threshold = IReport.Level[level_name]
        # respond to a bad result with the specified action (default preserve)
        response_name = kwargs.get(ACliTestable.Args.response.name, ITest.Response.preserve.name)
        self._response = ITest.Response[response_name]

    # command-line processing
    @staticmethod
    def parse_args(parser: ArgumentParser, argsv: str) -> Dict[str, str]:
        """
        Parse the list of command line strings into a dictionary

        :param parser: The ArgumentParser that defines acceptable CLI input
        :param argsv: Raw list of CLI string parameters
        :return: dictionary of CLI arguments and values
        """
        args = parser.parse_args(argsv)
        return vars(args)

    @staticmethod
    def make_arg_parser() -> ArgumentParser:
        """
        Create the argument parser specific to CLI-callable tests

        :return: argument parse for CLI-callable tests
        """
        parser = ArgumentParser()
        log_choices = tuple(str(level) for level in IReport.Level)
        parser.add_argument('--%s' % ACliTestable.Args.log.name, '-g', required=False, choices=log_choices,
                            default=IReport.Level.info.name)
        response_choices = tuple(str(response) for response in ITest.Response)
        parser.add_argument('--%s' % ACliTestable.Args.response.name, '-s', required=False, choices=response_choices,
                            default=ITest.Response.preserve.name)
        return parser


# Atomic checks within cases. Should only be used within context manager
class AStep(ATestable):
    """
    Single, atomic checks within larger testables.

    Steps are the basic building blocks from which all meaningful tests are formed.
    They perform a singular validation / verification that is recorded and reported.
    Their final state dictates the result of not only the step itself, but encompassing testables.

    :ivar _result: Current result of the step, including description, state, message
    :ivar expecteds: All acceptable final states of the step
    :ivar response: Action with which to respond to unexpected final states

    Should only be used within context manager.
    """

    def __init__(self, description: str or None = None, state: ITest.State = ITest.State.UNTESTED,
                 message: str or None = None, expecteds: List[ITest.State] = None,
                 response=ITest.Response.preserve):
        """
        Initialization of test step

        :param description: Meaningful but short explanation of the step
        :param state: Initial state of the step, which will be updated accordingly
        :param message: Explanation of state
        :param expecteds: All acceptable final states of the step
        :param response: Action with which to respond to failures
        """
        super().__init__()
        self._result = None
        self.result = StepResult(description, state, message)
        if expecteds is None:
            expecteds = [ITest.State.PASS]  # Pass is the default expected final state
        self.expecteds = expecteds
        self.response = response

    def __enter__(self) -> AStep:
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        self.result.report()

    def assess_state(self) -> None:
        """
        Evaluate state against expectations and adjust final result accordingly.

        This is complicated by the possibility of multiple expected states.
        """
        if len(self.expecteds) == 1:  # only a single expected result, the default
            # Pass is the default expectation so no special handling ...
            if ITest.State.PASS not in self.expecteds:
                # ... but if non-Pass expected we need to report it even if it matches
                if self.result.state in self.expecteds:
                    self.result.message = 'actual {} == expected {}: {}'.format(self.result.state, self.expecteds[0],
                                                                                self.result.message)

                    self.result.state = ITest.State.EXPECTED
                else:
                    self.result.message = 'actual {} != expected {}: {}'.format(self.result.state, self.expecteds[0],
                                                                                self.result.message)
                    self.result.state = ITest.State.UNEXPECTED

        else:
            # If multiple expecteds, we report the details regardless
            expecteds = [expected.name for expected in self.expecteds]
            if self.result.state in self.expecteds:
                msg = 'actual {} in expected {}: {}'.format(self.result.state, expecteds, self.result.message)
                self.result.message = msg
                self.result.state = ITest.State.EXPECTED
            else:
                msg = 'actual {} not in expected {}: {}'.format(self.result.state, expecteds, self.result.message)
                self.result.message = msg
                self.result.state = ITest.State.UNEXPECTED

    @property
    def response(self) -> ITest.Response:
        """
        How to respond to an unexpected result state
        :return: Current response action
        """
        return self._response

    @response.setter
    def response(self, response) -> None:
        """
        Validates response action is valid before setting it
        :param response: Desired respond action for unexpected result state
        """
        if response in ITest.Response:
            self._response = response
        else:
            raise ITest.InvalidStatusException('Response {} not in valid responses: {}'.format(response,
                                                                                               ITest.Response))


class AStairs(ATestable):
    """
    Aggregates individual steps into larger, more meaningful sequences (e.g. flights & cases).

    This consists primarily of two constructs:
    * Context managers for individual steps and aggregate flights
    * Result reporting which involves the propagation of step results upward through the hierarchy
    """

    @contextlib.contextmanager
    def stepper(self, description: str or None = None, state: ITest.State = ITest.State.UNTESTED,
                message: str or None = None, expecteds: List[ITest.State] = None,
                response: ITest.Response = ITest.Response.preserve) -> AStep:
        """
        Runs an individual step's actions and verifications

        All steps should be run within this context to ensure proper recording / reporting at the case level
        The real essence of the step, however, is in the AStep object.

        :param description: Meaningful but short explanation of the step
        :param state: Initial state of the step, which will be updated accordingly
        :param message: Explanation of state
        :param expecteds: All acceptable final states of the step
        :param response: Action with which to respond to failures
        """
        if expecteds is None:
            expecteds = [ITest.State.PASS]
        with AStep(description, state, message, expecteds, response) as step:
            try:
                yield step  # results can be updated anytime in context
            finally:
                step.assess_state()
                self.record_step(step.result)  # @todo Change to record_result?
                if step.result.state in ITest.BAD_STATE:
                    if self._response == ITest.Response.preserve and step.response == ITest.Response.preserve:
                        pdb.set_trace()

    # All flights need to be run within this context, currently for reporting but later for state/exception handling
    @contextlib.contextmanager
    def flyer(self, name: str or None = None, description: str or None = None,
              state: ITest.State = ITest.State.UNTESTED, message: str or None = None) -> AFlight:
        """
        Runs a series of individual steps and records/reports result as a single entity.

        This is particularly useful for running large numbers of similar permutations.
        Additional usages include iterating over the same step/series to trigger intermittent/unpredictable issues.
        :param name: Short name for reporting references
        :param description: Meaningful but short explanation of the step
        :param state: Initial state of the step, which will be updated accordingly
        :param message: Explanation of state
        """
        if name is None:
            name = AFlight.NAME
        with ReportService.demarcate("'{}' Flight".format(name), IReport.Level.info, IReport.Patency.minor):
            with AFlight(name, description, state, message) as flight:
                try:
                    yield flight  # results can be updated anytime in context
                finally:
                    # step.assess_state()
                    self.record_result(flight.result)

    def record_step(self, step_result):
        """
        Record result for an step

        @todo What value is this providing if only called for steps

        :param step_result: Steps result
        """
        super().record_result(step_result)


class AFlight(AStairs, AStep):
    NAME = 'Unnamed'

    def __init__(self, name, description, state, message):
        super().__init__(description, state, message)
        if name is None:
            name = self.NAME
        self.name = name
        self._result = FlightResult(self.name, self.default_description)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._result.report(recurse=False)


class ACase(ACliTestable, AStairs):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._result = CaseResult(self.name, self.default_description)

    def reserve(self):
        pass

    def prepare(self):
        pass

    def test(self):
        pass

    def audit(self):
        pass

    def restore(self):
        pass

    def report(self):  # included here for explicitness
        super().report()

    def release(self):
        pass

    # runs all test phases with standardized recording / reporting
    def execute(self):

        with ReportService.demarcate(self.name, IReport.Level.info, IReport.Patency.major, trail=False):
            ReportService.report('Description: {}'.format(self.description), timestamp=False)
            ReportService.report('Parameters: {}'.format(str(self._kwargs)), timestamp=False)
            with self.demarcate_phase(ITest.Phase.reserve.name):
                self.reserve()
            try:
                with self.demarcate_phase(ITest.Phase.prepare.name):
                    self.prepare()
                with self.demarcate_phase(ITest.Phase.test.name):
                    self.test()
                with self.demarcate_phase(ITest.Phase.audit.name):
                    self.audit()
                with self.demarcate_phase(ITest.Phase.restore.name):
                    self.restore()
            except Exception as exception:
                import traceback
                self._result.result = ITest.State.ABEND
                self._result.message = str(exception) + '\n\n' + traceback.format_exc()
            with self.demarcate_phase(ITest.Phase.report.name):
                self.report()
            with self.demarcate_phase(ITest.Phase.release.name):
                self.release()


class ASuite(ACliTestable, ATestable):

    def __init__(self, testables=None, **kwargs):
        super().__init__(**kwargs)
        self.testables = testables  # list of subsuites and cases
        self._result = SuiteResult(self.name, self.default_description)

    # Suites have less phases than cases since they are primarily just organizational
    def execute(self):
        with ReportService.demarcate(self.name, IReport.Level.info, IReport.Patency.major, trail=False):
            ReportService.report('Description: {}'.format(self.description), timestamp=False)
            ReportService.report('Parameters: {}'.format(str(self._kwargs)), timestamp=False)

            with self.demarcate_phase(ITest.Phase.test.name):
                self.test()
            with self.demarcate_phase(ITest.Phase.report.name):
                self.report()

    def test(self):
        for testable in self.testables:
            testable.execute()
            self.record_result(testable.result)
