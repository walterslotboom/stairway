"""
Core results class for testables.

Results automatically propagate up through the results hierarchy as tests run.
Reporting outputs these results in a hierarchical structure mirroring the testables.
"""
from src.test.itest import ITest
from src.util.service.report_service import ReportService, IReport


# Results are a distinct (if dependent) entity from the test itself
class AResult:
    """
    Abstract class underlying all results from individual steps to massive suites

    Contains a description of testable action, current / final state, and associated state message.
    Description is usually static throughout object life, but state and message change as needed.
    Primarily a recording / reporting construct.

    :ivar: description: What the testable was testing:
    :ivar: state: Current / final state of the running testable
    :ivar: message: Optional elaboration regarding the state
    """

    def __init__(self, description: str or None = None, state: ITest.State = ITest.State.UNTESTED,
                 message: str or None = None):
        self.description = description
        self._state = None
        self.state = state
        self.message = message

    @property
    def state(self) -> ITest.State:
        """
        State can be accessed during runs but most important at completion
        :return: Current / final state of the test
        """
        return self._state

    @state.setter
    def state(self, state):
        # @todo Why didn't 'in' work?
        if ITest.State.__contains__(ITest.State, state):
            self._state = state
        else:
            raise ITest.InvalidStateException('State {} not in valid statuses: {}'.format(state, ITest.State))

    def report(self) -> None:
        """
        Output the final result(s) to persistent I/O

        stdout by default but can be extended to log transcripts, database, etc.
        """
        raise NotImplementedError


class StepResult(AResult):
    """
    Result of a step testable's execution
    """

    def report(self, recurse: bool = True, indent: int = 0) -> None:
        """
        Output the final result(s) to persistent I/O

        :param recurse: n/a but exists for polymorphism of the encompassing testable
        :param indent: amount to indent textual output to mirror the testable hierarchy
        """
        message = 'STEP: {} | {} | {}'.format(self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)


class ATestResult(AResult):
    """
    Result of a non-step testable's execution

    Aggregate results are a propagation of the sub-testable's worst step result.

    :ivar: test: Short name of test
    :ivar: subresults: List of results for all testables of the aggregating construct (e.g. flight, case, suite)
    """

    def __init__(self, test: str, description: str, state: ITest.State = ITest.State.UNTESTED,
                 message: str or None = None) -> None:
        super().__init__(description, state, message)
        self.test = test
        self.subresults = []

    def record_result(self, subresult: AResult) -> None:
        """
        Add the result of a sub-testable to the list of results.

        The current result of the super-testable is updated accordingly.
        :param subresult: Result of a subtestable
        """
        self.subresults.append(subresult)
        # If new sub-result is worse than current super-result, then make it super-result.
        # Super-result is the first instance of the worst sub-result.
        if subresult.state < self.state:
            self.description = subresult.description
            self.state = subresult.state
            self.message = subresult.message

    def report(self, recurse: bool = True, indent: int = 0) -> None:
        """
        Iterate through sub-results and report them.

        Increment the indent to mirror testable's.
        """
        for result in self.subresults:
            result.report(recurse, indent + 1)

    def reset(self) -> None:
        """
        Sets result values to RESET state.

        Useful when looping a testable to try and induce an intermittent failure.
        """
        self.subresults = []
        self.description = 'Reset'
        self.state = ITest.State.RESET
        self.message = 'Reset'

    def __assess_results(self) -> None:
        """
        Sets the super-result to the first of its worst sub-results

        Not needed if we maintain overall subresult as subresults are added.
        """
        if len(self.subresults) > 0:

            for status in reversed(ITest.BAD_STATE):  # valid statuses from worst to best

                status_matches = [subresult for subresult in self.subresults if subresult.subresult == status]
                if len(status_matches) > 0:
                    first_worst_result = status_matches[0]
                    if self.description is None:
                        self.description = first_worst_result.description
                    self.subresult = first_worst_result.subresult
                    self.message = first_worst_result.message  # the first worst subresult
                    return
        else:
            self.subresult = ITest.State.UNKNOWN
            self.message = 'No subresults'


# @todo Make reporting level a variable
class FlightResult(ATestResult):
    """
    Result of a flight testable.
    """
    def report(self, recurse: bool = True, indent: int = 0) -> None:
        """
        Report flight result.

        Recurse into sub-flights by default to show hierarchy.
        """
        message = 'FLIGHT {}: {} | {} | {}'.format(self.test, self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)
        if recurse:
            super().report(recurse, indent)


class CaseResult(ATestResult):
    """
    Result of a case testable.

    Recurse into flights by default to show hierarchy.
    """
    def report(self, recurse: bool = True, indent: int = 0) -> None:
        """
        Report case result.

        Recurse into flights by default to show hierarchy.
        """
        message = 'CASE {}: {} | {} | {}'.format(self.test, self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)
        if recurse:
            super().report(recurse, indent)


class SuiteResult(ATestResult):
    """
    Result of a suite testable.
    """
    def report(self, recurse: bool = False, indent: int = 0) -> None:
        """
        Report suite result.

        Only report to case level by default, since steps will be previously recorded.
        """
        message = 'SUITE {}: {} | {} | {}'.format(self.test, self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)
        super().report(recurse, indent)
