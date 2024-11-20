# Type helpers
from typing import TypeVar, Union

# IgnoreMe is a helper to ignore a type in a Union
T = TypeVar('T')
class IgnoreMe:
    pass
Ignored = Union[T, IgnoreMe]

class DateTimeStringClass:
    pass
DateTimeString = Union[str, DateTimeStringClass]
