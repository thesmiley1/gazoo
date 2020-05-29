from enum import Enum, auto


class SaveStatus(Enum):
    IDLE = auto()
    HOLD = auto()
    QUERY = auto()
    INFO = auto()
    READY = auto()
    WORKING = auto()
