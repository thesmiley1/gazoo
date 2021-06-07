"""
Provide class CleanupWorker.
"""

from __future__ import annotations

from logging import warning

from .util import Util
from .worker_status import WorkerStatus

class CleanupWorker:
    """
    Provide a class to do the heavy lifting of the cleanup process.
    """

    def __init__(self: CleanupWorker) -> None:
        self.status: WorkerStatus = WorkerStatus.IDLE

    def cleanup(self: CleanupWorker) -> None:
        """
        Clean up the backup directory.
        """

        if self.status is not WorkerStatus.IDLE:
            warning('previous cleanup not completed; not starting a new one')
            return

        self.status = WorkerStatus.WORKING

        Util.cleanup_archives()

        self.status = WorkerStatus.IDLE
