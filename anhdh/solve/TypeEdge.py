from enum import Enum
class TypeEdge(Enum):
    HUMP = 1
    REVERSE_HUMP = 2
    BORDER  = 3

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3