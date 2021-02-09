import random
import sys
from src.test.testable import ACase, ACliTestable
from src.test.itest import ITest


class AllResultsCase(ACase):

    DESCRIPTION = "Sampling of all step states"

    def __init__(self, **kwargs):
        self.steps = None
        super().__init__(**kwargs)

    def prepare(self):
        super().prepare()
        self.steps = [
            ('Fail step description', ITest.State.FAIL, 'Fail step message'),
            ('Abend step description', ITest.State.ABEND, 'Abend step message'),
            ('Expected step description', ITest.State.EXPECTED, 'Expected step message'),
            ('Marginal step description', ITest.State.MARGINAL, 'Marginal step message'),
            ('Pass step description', ITest.State.PASS, 'Pass step message'),
            ('Unknown step description', ITest.State.UNKNOWN, 'Unknown step message'),
            ('Untested step description', ITest.State.UNTESTED, 'Untested step message'),
            ('Unexpected step description', ITest.State.UNEXPECTED, 'Unexpected step message'),
            ('Inapplicable step description', ITest.State.INAPPLICABLE, 'Inapplicable step message'),
        ]

    def test(self):
        super().test()
        random.shuffle(self.steps)
        for step in self.steps:
            description, result, message = step
            with self.stepper(description, result, message):
                pass


class DemoCase(ACase):
    pass


class FailingCase(DemoCase):
    DESCRIPTION = "Failure demo"

    def test(self):
        with self.stepper('Fail step description', ITest.State.FAIL, 'Fail step message'):
            pass


class AbendCase(DemoCase):
    DESCRIPTION = "Abend demo"

    def test(self):
        with self.stepper('Abend step description', ITest.State.ABEND, 'Abend step message'):
            pass


class ExpectedCase(DemoCase):
    DESCRIPTION = "Expected demo"

    def test(self):
        with self.stepper('Expected step description', ITest.State.EXPECTED, 'Expected step message'):
            pass


class MarginalCase(DemoCase):
    DESCRIPTION = "Marginal demo"

    def test(self):
        with self.stepper('Marginal step description', ITest.State.MARGINAL, 'Marginal step message'):
            pass


class PassingCase(DemoCase):
    DESCRIPTION = "Passing demo"

    def test(self):
        with self.stepper('Pass step description', ITest.State.PASS, 'Pass step message'):
            pass


class UnknownCase(DemoCase):
    DESCRIPTION = "Unknown demo"

    def test(self):
        with self.stepper('Unknown step description', ITest.State.UNKNOWN, 'Unknown step message'):
            pass


class UntestedCase(DemoCase):
    DESCRIPTION = "Untested demo"

    def test(self):
        with self.stepper('Untested step description', ITest.State.UNTESTED, 'Untested step message'):
            pass


class UnexpectedCase(DemoCase):
    DESCRIPTION = "Unexpected demo"

    def test(self):
        with self.stepper('Unexpected step description', ITest.State.UNEXPECTED, 'Unexpected step message'):
            pass


class UnexpectedSingleCase(DemoCase):
    DESCRIPTION = "Unexpected pass with single expectation"

    def test(self):
        with self.stepper('Unexpected step description', ITest.State.UNTESTED, 'Unexpected step message',
                          [ITest.State.MARGINAL]) as stepper:
            stepper.result.state = ITest.State.PASS


class UnexpectedMultipleCase(DemoCase):
    DESCRIPTION = "Unexpected marginal with multi expectation"

    def test(self):
        with self.stepper('Unexpected step description', ITest.State.UNTESTED, 'Unexpected step message',
                          [ITest.State.FAIL, ITest.State.ABEND]) as stepper:
            stepper.result.state = ITest.State.MARGINAL


class UnexpectedEmptyCase(DemoCase):
    DESCRIPTION = "Unexpected marginal when no expectation"

    def test(self):
        with self.stepper('Unexpected step description', ITest.State.UNTESTED, 'Unexpected step message',
                          []) as stepper:
            stepper.result.state = ITest.State.MARGINAL


class ExpectedPassSingleCase(DemoCase):
    DESCRIPTION = "Expected pass with single expectation"

    def test(self):
        with self.stepper('Pass step description', ITest.State.UNTESTED, 'Pass step message',
                          [ITest.State.PASS]) as stepper:
            stepper.result.state = ITest.State.PASS


class ExpectedPassMultiCase(DemoCase):
    DESCRIPTION = "Expected pass with multiple expectations"

    def test(self):
        with self.stepper('Pass step description', ITest.State.UNTESTED, 'Pass step message',
                          [ITest.State.PASS, ITest.State.MARGINAL]) as stepper:
            stepper.result.state = ITest.State.PASS


class ExpectedSingleMarginalCase(DemoCase):
    DESCRIPTION = "Expected marginal with single expectation"

    def test(self):
        with self.stepper('Marginal step description', ITest.State.UNTESTED, 'Marginal step message',
                          [ITest.State.MARGINAL]) as stepper:
            stepper.result.state = ITest.State.MARGINAL


class ExpectedMarginalMultiCase(DemoCase):
    DESCRIPTION = "Expected marginal with multiple expectations"

    def test(self):
        with self.stepper('Marginal step description', ITest.State.UNTESTED, 'Marginal step message',
                          [ITest.State.MARGINAL, ITest.State.PASS]) as stepper:
            stepper.result.state = ITest.State.MARGINAL


class InapplicableCase(DemoCase):
    DESCRIPTION = "Inapplicable demo"

    def test(self):
        with self.stepper('Inapplicable step description', ITest.State.INAPPLICABLE, 'Inapplicable step message'):
            pass


class NamedFlightCase(DemoCase):
    DESCRIPTION = 'Named flight demo'

    def test(self):
        loops = 3
        with self.flyer('Passes * {}'.format(loops)) as flight:
            for index in range(1, loops):
                with flight.stepper('Flight step #{}'.format(index), ITest.State.PASS):
                    pass


class UnnamedFlightCase(DemoCase):
    DESCRIPTION = 'Unnamed flight demo'

    def test(self):
        loops = 3
        with self.flyer() as flight:
            for index in range(1, loops):
                with flight.stepper('Flight step #{}'.format(index), ITest.State.PASS):
                    pass


class NestedFlightCase(DemoCase):
    DESCRIPTION = 'Unnamed flight demo'

    def test(self):
        loops = 3
        with self.flyer('Outer passes * {}'.format(loops)) as outer_flight:
            for outer in range(0, loops):
                with outer_flight.flyer('Inner passes * {} #{}'.format(loops, outer)) as inner_flight:
                    for inner in range(0, loops):
                        with inner_flight.stepper('Flight step #{}'.format(inner), ITest.State.PASS):
                            pass


if __name__ == '__main__':
    # arg_parser = AllResultsCase.make_arg_parser()
    # args = AllResultsCase.parse_args(arg_parser, sys.argv[1:])
    # ExpectedPassMultiCase(**args).execute()
    # arg_parser = UnnamedFlightCase.make_arg_parser()
    # args = UnnamedFlightCase.parse_args(arg_parser, sys.argv[1:])
    # UnnamedFlightCase(**args).execute()
    arg_parser = FailingCase.make_arg_parser()
    args = FailingCase.parse_args(arg_parser, sys.argv[1:])
    args[ACliTestable.Args.response.name] = ITest.Response.preserve.name
    FailingCase(**args).execute()
