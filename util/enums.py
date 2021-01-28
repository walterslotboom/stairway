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
    """

    def __lt__(self, other: OrderedEnum) -> bool:
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __le__(self, other: OrderedEnum) -> bool:
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __eq__(self, other: OrderedEnum) -> bool:
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

    def __ne__(self, other: OrderedEnum) -> bool:
        if self.__class__ is other.__class__:
            return self.value != other.value
        return NotImplemented

    def __ge__(self, other: OrderedEnum) -> bool:
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other: OrderedEnum) -> bool:
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
