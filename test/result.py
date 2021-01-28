from test.itest import ITest
from util.service.report_service import ReportService, IReport


# Results are a distinct (if dependent) entity from the test itself
class AResult:

    def __init__(self, description=None, state=ITest.State.UNTESTED, message=None):

        self.description = description
        self._state = None
        self.state = state
        self.message = message

    # State can be accessed during runs but most important at completion
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state in ITest.State:
            self._state = state
        else:
            raise ITest.InvalidStateException('State {} not in valid statuses: {}'.format(state, ITest.State))

    def report(self):
        raise NotImplementedError


class StepResult(AResult):

    def report(self, recurse=True, indent=0):
        message = 'STEP: {} | {} | {}'.format(self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)


class ATestResult(AResult):

    def __init__(self, test, description, state=ITest.State.UNTESTED, message=None):
        super().__init__(description, state, message)
        self.test = test
        self.subresults = []

    def record_result(self, subresult):
        self.subresults.append(subresult)
        # if new subresult is worse than current superresult then make it superresult
        # state is the first instance of the worst result
        if subresult.state < self.state:
            self.description = subresult.description
            self.state = subresult.state
            self.message = subresult.message

    def report(self, recurse=True, indent=0):
        for result in self.subresults:
            result.report(recurse, indent + 1)

    def reset(self):
        # used for stress cases that need to dispose of transient subresults
        self.subresults = []
        self.description = 'Reset'
        self.state = ITest.State.UNKNOWN
        self.message = 'Reset'

    # Not needed if we maintain overall subresult as subresults are added.
    def __assess_results(self):

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
            self.message = '<No subresults>'


# @todo Make reporting level a variable
class FlightResult(ATestResult):

    def report(self, recurse=True, indent=0):
        message = 'FLIGHT {}: {} | {} | {}'.format(self.test, self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)
        if recurse:
            super().report(recurse, indent)


class CaseResult(ATestResult):

    def report(self, recurse=True, indent=0):
        message = 'CASE {}: {} | {} | {}'.format(self.test, self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)
        if recurse:
            super().report(recurse, indent)


class SuiteResult(ATestResult):

    # Only report to case level. Steps will be previously recorded.
    def report(self, recurse=False, indent=0):
        message = 'SUITE {}: {} | {} | {}'.format(self.test, self.description, self.state, self.message)
        message = ReportService.indent(message, indent)
        ReportService.report(message, IReport.Level.info, IReport.Patency.minor)
        super().report(recurse, indent)
