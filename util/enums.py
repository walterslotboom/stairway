from enum import Enum
from functools import total_ordering
import argparse


class TextualEnum(Enum):
    # Enum string representations include the enum test (e.g. "Color.red". This class simply strips that off.
    def __str__(self):
        return self.name


@total_ordering
class OrderedEnum(TextualEnum):
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class EnumedAttributes:
    # use for coupling regex named groups with class attributes
    class Attributes(TextualEnum):
        pass

    def __init__(self, **kwargs):
        for attribute in self.Attributes:
            setattr(self, attribute.name, kwargs.get(attribute.name, None))


class ArgChoiceEnum(TextualEnum):
    # use for easy definition of argparse argtypes:
    #
    #     class SelectionOptions(ArgChoiceEnum):
    #         recurse = 0
    #         some = 1
    #         none = 2
    #
    #    parser = argparse.ArgumentParser()
    #    parser.add_argument('--select',
    #                        type=SelectionOptions.arg_type,
    #                        choices=SelectionOptions,
    #                        help="what you want?")
    #
    # The value returned in the parsed arguments is not the string, but an instance of the enum
    @classmethod
    def arg_type(cls, s: str) -> 'ArgChoiceEnum':
        '''
        argparse type validation function, that takes a string and if valid, returns the
        matching enum object
        '''
        try:
            return cls[s]
        except KeyError:
            raise argparse.ArgumentError()
