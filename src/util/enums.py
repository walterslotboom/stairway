"""
Custom enumeration classes

Used primarily for fromalizing CLI interactions and reporting, and comparison of restricted values.
"""
from __future__ import annotations
from enum import Enum
from functools import total_ordering


class TextualEnum(Enum):
    """
    Strips the class name from Enum string representations (e.g. "Color.red" becomes "red").
    """
    def __str__(self) -> str:
        return self.name


@total_ordering
class OrderedEnum(TextualEnum):
    """
    Enumeration of textualizable values that can be ordered for comparison operations.

    The total_ordering decorator deduces comparison operations
    """

    def __le__(self, other: OrderedEnum) -> bool:
        return isinstance(other, OrderedEnum) and (self.value <= other.value)

    def __eq__(self, other: OrderedEnum) -> bool:
        return isinstance(other, OrderedEnum) and (self.value == other.value)

    # @todo Why didn't the default __contains__ work?
    def __contains__(self, item):
        return item in self.__iter__()
