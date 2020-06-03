"""
Provide class Worker.
"""

from __future__ import annotations

from datetime import datetime
from logging import debug, error, info
from pathlib import Path
from shutil import copyfile
from time import sleep
from typing import TYPE_CHECKING
from zipfile import ZipFile

from gazoo.util import Util
from gazoo.worker_status import WorkerStatus

if TYPE_CHECKING:
    from subprocess import Popen
    from typing import Final, List, Optional, Tuple


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

        TODO:

        * Read file into memory, truncate in memory, write to zip from
          memory?
        * _MOVE_ zip archive to backups directory.
        * Cleanup at end (ensure_temp_dir).
        """
        # FIXME ^^^ TODO ^^^

        if self.status is not WorkerStatus.IDLE:
            return

        self._command('save hold')
        self.status = WorkerStatus.QUERY

        while self.status is not WorkerStatus.READY:
            self._command('save query')
            sleep(1)

        for loc, length in self._info:
            debug(f'{loc}: {length}')

        self._copy_files()

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
            if self.status is WorkerStatus.INFO:
                files: List[str] = line.rstrip().split(', ')

                self._info = []

                for file in files:
                    (loc, length) = file.split(':')
                    self._info.append((Path(loc), int(length)))

                self.status = WorkerStatus.READY

            if (self.status is WorkerStatus.QUERY
                    and line == self._QUERY_STRING):
                self.status = WorkerStatus.INFO

    def _command(self: Worker, string: str) -> None:
        """
        Echo command to stdout and send it to server stdin.
        """

        assert self._proc is not None
        assert self._proc.stdin is not None

        if not self._proc.poll():
            print(string)
            self._proc.stdin.write(string + '\n')

    # FIXME:  This function is too long.
    def _copy_files(self: Worker) -> None:
        """
        Copy saved files to temp dir, truncate them, and add to zip.
        """

        Util.ensure_temp_dir()

        world_dir_name: str = ''
        world_dir_path: Optional[Path] = None
        for loc, length in self._info:
            if world_dir_name == '':
                world_dir_name = loc.parts[0]
                world_dir_path = Util.worlds_dir_path().joinpath(
                    world_dir_name)
            elif world_dir_name != loc.parts[0]:
                error(('world_dir_name mismatch: '
                       + '{world_dir_name} {loc.parts[0]}'))

            assert world_dir_path is not None
            found: List[Path] = list(world_dir_path.glob(f'**/{loc.name}'))

            if len(found) == 0:
                error(f'No file found for {loc}')

                continue
            elif len(found) > 1:
                error(f'Found {len(found)} files for {loc}')

            src: Path = found[0]
            debug(f'src: {src}')

            dst: Path = Util.temp_dir_path().joinpath(
                src.relative_to(Util.worlds_dir_path()))
            debug(f'dst: {dst}')

            info('Copying {src} to {dst}')
            dst.parent.mkdir(exist_ok=True, parents=True)
            copyfile(src, dst)

            with dst.open('w') as dst_file:
                dst_file.truncate(length)

        datetime_string = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        zip_file_name = f'{world_dir_name} {datetime_string}.zip'

        zip_file_path = Util.temp_dir_path().joinpath(zip_file_name)
        zip_file = ZipFile(zip_file_path, 'w')

        temp_world_dir_path = Util.temp_dir_path().joinpath(world_dir_name)

        assert world_dir_path is not None
        for file_path in temp_world_dir_path.glob('**/*'):
            zip_file.write(file_path, file_path.relative_to(
                Util.temp_dir_path()))

        final_dst = Util.backups_dir_path().joinpath(zip_file_name)
        copyfile(zip_file_path, final_dst)
