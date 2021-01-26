import contextlib
import pdb
from test.itest import ITest
from test.result import StepResult, CaseResult, SuiteResult, FlightResult, AResult
from util.enums import TextualEnum
from util.service.report_service import IReport, ReportService
from argparse import ArgumentParser


# base class of all tests from atomic steps to aggregate suites
class ATestable:
    DESCRIPTION = None

    def __init__(self) -> None:
        self._name: str or None = None
        self.description: str = self.DESCRIPTION
        # For non-steps, the run-mode of the tests at large (usually passed from CLI).
        # For steps, the specific response for that step. Thereforez` subclasses have different setters/getters
        self._response: ITest.Response or None = None
        self._result: AResult or None = None  # should be immediately overridden to untested (for starters)

    # Primarily for overwriting by base classes.
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def default_description(self) -> str:
        return '{} ({})'.format(self.name, self.description)

    # Results are a distinct (if dependent) entity from the test itself
    # Can be accessed during runs but most important at completion
    @property
    def result(self) -> AResult:
        return self._result

    @result.setter
    def result(self, value: AResult) -> None:
        self._result = value

    def record_result(self, result: AResult) -> None:
        self._result.record_result(result)

    def report(self) -> None:
        self._result.report()

    # useful when looping to try and induce intermittent failures
    def reset_result(self) -> None:
        self._result.reset()

    # output wrapper for bookending any discreet phase of a test
    @contextlib.contextmanager
    def demarcate_phase(self, phase: str) -> None:
        message = '{} / {} phase'.format(self.name, phase)
        with ReportService.demarcate(message, IReport.Level.none, IReport.Patency.medium):
            yield


class ACliTestable:

    # for extracting kwargs
    class Args(TextualEnum):
        log = 1
        response = 2

    @property
    def name(self):
        return type(self).__name__

    def __init__(self, **kwargs):
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
    def parse_args(parser, argsv):
        args = parser.parse_args(argsv)
        return vars(args)

    @staticmethod
    def make_arg_parser():
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

    def __init__(self, description=None, state=ITest.State.UNTESTED, message=None, expecteds=None,
                 response=ITest.Response.preserve):
        super().__init__()
        self._result = None
        self.result = StepResult(description, state, message)
        if expecteds is None:
            expecteds = [ITest.State.PASS]  # Pass is the default expected final state
        self.expecteds = expecteds
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.result.report()

    # Evaluate state against expectations and adjust final result accordingly.
    # This is complicated by the possibility of multiple expected states.
    def assess_state(self):
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
    def response(self):
        return self._response

    @response.setter
    def response(self, response):
        if response in ITest.Response:
            self._response = response
        else:
            raise ITest.InvalidStatusException('Response {} not in valid responses: {}'.format(response,
                                                                                               ITest.Response))


class AStairs(ATestable):
    # Aggregates steps

    # All steps should be run within this context to ensure proper recording / reporting at the case level
    # The real essence of the step, however, is in the AStep object however.
    @contextlib.contextmanager
    def stepper(self, description=None, state=ITest.State.UNTESTED, message=None, expecteds=None,
                response=ITest.Response.preserve):
        if expecteds is None:
            expecteds = [ITest.State.PASS]
        with AStep(description, state, message, expecteds, response) as step:
            try:
                yield step  # results can be updated anytime in context
            finally:
                step.assess_state()
                self.record_step(step.result)
                if step.result.state in ITest.BAD_STATE:
                    if self._response == ITest.Response.preserve and step.response == ITest.Response.preserve:
                        pdb.set_trace()

    # All flights need to be run within this context, currently for reporting but later for state/exception handling
    @contextlib.contextmanager
    def flyer(self, name=None, description=None, state=ITest.State.UNTESTED, message=None):
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
        self.result.report(recurse=False)


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
