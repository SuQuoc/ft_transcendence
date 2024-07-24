"""
Why? Slot ????

The short answer is slots are more efficient in terms of memory space and speed of access
a bit safer than the default Python method of data access.

https://wiki.python.org/moin/UsingSlots

"""


class SlotXy:

    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y
