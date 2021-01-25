from util.enums import OrderedEnum, TextualEnum


class ITest:
    # possible test states in order so that worst result can propagate up test result hierarchy
    class State(OrderedEnum):
        UNTESTED = 55
        INAPPLICABLE = 45
        PASS = 40
        EXPECTED = 35
        UNKNOWN = 30  # was tested but indeterminate result
        ABEND = 20  # usually problem in automation not product
        MARGINAL = 15  # often used for performance or known issues
        UNEXPECTED = 10
        FAIL = 5

    BAD_STATE = []
    for state in State:
        if state <= State.ABEND:
            BAD_STATE.append(state)

    # possible responses upon failing a step
    class Response(TextualEnum):
        preserve = 1  # stop all tests so state can be examined
        conclude = 2  # @todo add support for this
        proceed = 3  # log failure and keep running (for minor issues)

    class Phase(OrderedEnum):
        reserve = 10  # allocate physical resources
        prepare = 20  # establish base state, setup key objects used in test
        test = 30  # what all this is for
        audit = 40  # case independent checks for tangential issues
        restore = 50  # reestablish base state; object cleanup
        report = 60  # output the results to screen / log / database / etc
        release = 70  # return physical resources to pool

    class InvalidStatusException(Exception):
        pass
