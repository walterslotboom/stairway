from demo.demo_report_case import *
from test.testable import ASuite


class MultiCaseSuite(ASuite):
    DESCRIPTION = "All demo cases"

    def __init__(self, **kwargs):
        testables = [FailingCase(**kwargs), AbendCase(**kwargs), ExpectedCase(**kwargs),
                     UnknownCase(**kwargs), UntestedCase(**kwargs), UnexpectedCase(**kwargs),
                     InapplicableCase(**kwargs)]
        super().__init__(testables, **kwargs)


class SingleCaseSuite(ASuite):
    DESCRIPTION = "Suite containing single case"

    def __init__(self, **kwargs):
        testables = [MarginalCase(**kwargs)]
        super().__init__(testables, **kwargs)


class MixedSuiteAndCaseSuite(ASuite):
    DESCRIPTION = "One suite & one case"

    def __init__(self, **kwargs):
        testables = [SingleCaseSuite(**kwargs), PassingCase(**kwargs)]
        super().__init__(testables, **kwargs)


class EmptySuite(ASuite):
    DESCRIPTION = "No subsuites or cases"

    def __init__(self, **kwargs):
        testables = []
        super().__init__(testables, **kwargs)


class UnexpectedSuite(ASuite):

    DESCRIPTION = "Unexpected variants"

    def __init__(self, **kwargs):
        testables = [UnexpectedSingleCase(**kwargs), UnexpectedMultipleCase(**kwargs), UnexpectedEmptyCase(**kwargs)]
        super().__init__(testables, **kwargs)


class ExpectedSuite(ASuite):
    DESCRIPTION = "Expected variants"

    def __init__(self, **kwargs):
        testables = [ExpectedPassSingleCase(**kwargs), ExpectedPassMultiCase(**kwargs),
                     ExpectedSingleMarginalCase(**kwargs), ExpectedMarginalMultiCase(**kwargs)]
        super().__init__(testables, **kwargs)


class FlightSuite(ASuite):
    DESCRIPTION = "Expected variants"

    def __init__(self, **kwargs):
        testables = [NamedFlightCase(**kwargs), UnnamedFlightCase(**kwargs), NestedFlightCase(**kwargs)]
        super().__init__(testables, **kwargs)


class AllSuitesSuite(ASuite):

    DESCRIPTION = "Multi-depth suites and cases"

    def __init__(self, **kwargs):
        testables = [SingleCaseSuite(**kwargs), MultiCaseSuite(**kwargs), MixedSuiteAndCaseSuite(**kwargs),
                     EmptySuite(**kwargs), UnexpectedSuite(**kwargs), ExpectedSuite(**kwargs), FlightSuite(**kwargs)]
        super().__init__(testables, **kwargs)


if __name__ == '__main__':
    # arg_parser = AllResultsCase.make_arg_parser()
    # args = AllSuitesSuite.parse_args(arg_parser, sys.argv[1:])
    # AllSuitesSuite(**args).execute()
    arg_parser = FlightSuite.make_arg_parser()
    args = FlightSuite.parse_args(arg_parser, sys.argv[1:])
    FlightSuite(**args).execute()
