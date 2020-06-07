"""
Provide class Worker.
"""

from __future__ import annotations

from logging import warning
from time import sleep
from typing import TYPE_CHECKING

from .backup_file import BackupFile
from .util import Util
from .worker_status import WorkerStatus

if TYPE_CHECKING:
    from subprocess import Popen
    from typing import Final, List


class Worker:
    """
    Provide a class to do the heavy lifting of the backup process.
    """

    _QUERY_STRING: Final[str] = ('Data saved. Files are now ready to be '
                                 + 'copied.\n')

    def __init__(self: Worker, proc: 'Popen[str]') -> None:
        self._backup_files: List[BackupFile] = []
        self._proc: 'Popen[str]' = proc
        self.status: WorkerStatus = WorkerStatus.IDLE

    def backup(self: Worker) -> None:
        """
        Make a backup of the current world.

        The approach for this is:

        * Send 'save hold' to server stdin.
        * Send 'save query' to server stdin once every second.
            * Stop when _QUERY_STRING is found from server stdout.
        * Parse file names and lengths from server stdout.
        * Copy files to temporary directory.
        * Truncate files to correct length.
        * Create zip archive in temporary directory with files copied
          previously.
        * Copy zip archive to backups directory.
        """

        if self.status is not WorkerStatus.IDLE:
            warning('Previous save not completed; not starting a new one')
            return

        self._command('save hold')
        self.status = WorkerStatus.QUERY

        while self.status is not WorkerStatus.READY:
            self._command('save query')
            sleep(1)

        Util.archive_files(self._backup_files)

        self._command('save resume')
        self.status = WorkerStatus.IDLE

    def thread_stdout(self: Worker) -> None:
        """
        Forward server stdout and scan for important information.

        Lines are scanned for confirmation that files were saved
        successfully and names/lengths of those files.
        """

        assert self._proc is not None
        assert self._proc.stdout is not None

        line: str
        for line in self._proc.stdout:
            print(line, end='')

            if (self.status is WorkerStatus.QUERY
                    and line == self._QUERY_STRING):
                self.status = WorkerStatus.INFO
            elif self.status is WorkerStatus.INFO:
                self._backup_files = []

                files: List[str] = line.rstrip().split(', ')
                for file in files:
                    (loc, length) = file.split(':')
                    self._backup_files.append(BackupFile(loc, int(length)))

                self.status = WorkerStatus.READY

    def _command(self: Worker, string: str) -> None:
        """
        Echo command to stdout and send it to server stdin.
        """

        assert self._proc is not None
        assert self._proc.stdin is not None

        if not self._proc.poll():
            print(string)
            self._proc.stdin.write(string + '\n')
