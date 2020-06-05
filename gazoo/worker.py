"""
Provide class Worker.
"""

from __future__ import annotations

from datetime import datetime
from logging import error, warning
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING
from zipfile import ZipFile
from os import rename

from .util import Util
from .worker_status import WorkerStatus

if TYPE_CHECKING:
    from subprocess import Popen
    from typing import BinaryIO, Final, List, Tuple


class Worker:
    """
    Provide a class to do the heavy lifting of the backup process.
    """

    _QUERY_STRING: Final[str] = ('Data saved. Files are now ready to be '
                                 + 'copied.\n')

    def __init__(self: Worker, proc: 'Popen[str]') -> None:
        self._info: List[Tuple[Path, int]] = []
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

        self._archive_files()

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
                self._info = []

                files: List[str] = line.rstrip().split(', ')
                for file in files:
                    (loc, length) = file.split(':')
                    self._info.append((Path(loc), int(length)))

                self.status = WorkerStatus.READY

    def _archive_files(self: Worker) -> None:
        """
        Copy saved files to backup archive.
        """

        Util.ensure_temp_dir()

        first_path: Path
        (first_path, _) = self._info[0]

        world_dir_name: str = first_path.parts[0]
        world_dir_path: Path = Util.worlds_dir_path().joinpath(
            world_dir_name)

        datetime_string = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        zip_file_name = f'{world_dir_name} {datetime_string}.zip'

        zip_file_path = Util.temp_dir_path().joinpath(zip_file_name)
        zip_file = ZipFile(zip_file_path, 'w')

        for loc, length in self._info:
            if world_dir_name != loc.parts[0]:
                error(('world_dir_name mismatch: '
                       + '{world_dir_name} {loc.parts[0]}'))

            assert world_dir_path is not None
            found: List[Path] = list(world_dir_path.glob(f'**/{loc.name}'))

            if len(found) == 0:
                error(f'No file found for {loc}')
                continue

            if len(found) > 1:
                error(f'Found {len(found)} files for {loc}')

            source_file_path: Path = found[0]

            source_file: BinaryIO
            with source_file_path.open(mode='rb') as source_file:
                zip_file.writestr(str(source_file_path.relative_to(
                    Util.worlds_dir_path())), source_file.read(length))

        final_dest_path = Util.backups_dir_path().joinpath(zip_file_name)
        rename(zip_file_path, final_dest_path)

        Util.ensure_temp_dir()

    def _command(self: Worker, string: str) -> None:
        """
        Echo command to stdout and send it to server stdin.
        """

        assert self._proc is not None
        assert self._proc.stdin is not None

        if not self._proc.poll():
            print(string)
            self._proc.stdin.write(string + '\n')
