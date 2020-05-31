"""
Module save_status provides class SaveStatus.
"""

# FIXME should we be calling this backup instead of save ???

from enum import Enum, auto


class SaveStatus(Enum):
    """
    Class SaveStatus provides constants to track the status of saving.

    These roughly correspond to the server commands used for saving and
    the time in between them.  For reference, the three saving commands
    are `save hold`, `save query`, and `save resume` (in that order).

    - IDLE
        - Before `save hold` and/or after `save resume`
        - In this state nothing is happening with saving; just waiting
        for the next save.
    - QUERY
        - After `save hold` / During `save query`
        - In this state, `save query` is being sent to the server and a
        successful response is being waited for.
    - INFO
        - During `save query`
        - In this state, the previous line of output from the server was
        a successful response to a `save query` command.  The next line
        expected is the payload of metadata about the save files.
    - READY
        - After `save query`
        - In this state, the metadata payload from the server has been
        received and parsed and a save is ready to be made.
    - WORKING
        - Before `save resume`
        - In this state, the saving is in progress.
    """

    IDLE = auto()
    QUERY = auto()
    INFO = auto()
    READY = auto()
    WORKING = auto()
