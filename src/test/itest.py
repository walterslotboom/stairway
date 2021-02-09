"""
Basic testing globals
"""
from src.util.enums import OrderedEnum, TextualEnum


class ITest:
    """
    Interface style class providing basic testing 'globals'
    """

    class State(OrderedEnum):
        """
        Possible test states

        Ordered so that comparison during result assessment is possible.
        """
        UNTESTED = 55  # before and at start of test
        RESET = 50  # used for looping against intermittent failures
        INAPPLICABLE = 45
        PASS = 40
        EXPECTED = 35
        UNKNOWN = 30  # was tested but indeterminate result
        ABEND = 20  # usually problem in automation not product
        MARGINAL = 15  # often used for performance or known issues
        UNEXPECTED = 10
        FAIL = 5

    # Inherently bad states
    BAD_STATE = []
    for state in State:
        if state <= State.ABEND:
            BAD_STATE.append(state)

    class Response(TextualEnum):
        """
        Possible responses to take upon failing a step (or possibly higher constructs)
        """
        preserve = 1  # stop all tests so state can be examined
        conclude = 2  # @todo add support for this
        proceed = 3  # log failure and keep running (for minor issues)

    class Phase(OrderedEnum):
        """
        Standard phases of a test case
        """
        reserve = 10  # allocate physical resources
        prepare = 20  # establish base state, setup key objects used in test
        test = 30  # what all this is for
        audit = 40  # case independent checks for tangential issues
        restore = 50  # reestablish base state; object cleanup
        report = 60  # output the results to screen / log / database / etc
        release = 70  # return physical resources to pool

    class InvalidStateException(Exception):
        """
        Invalid result state for testable
        """
        pass
