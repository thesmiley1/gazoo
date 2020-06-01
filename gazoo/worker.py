from logging import debug, error, info
from pathlib import Path
from shutil import copyfile
from subprocess import Popen # pylint: disable=unused-import
from time import sleep
from typing import Final, List, Optional, Tuple
from zipfile import ZipFile
from datetime import datetime

from gazoo.worker_status import WorkerStatus
from gazoo.util import Util


class Worker:
    QUERY_STRING: Final[str] = ('Data saved. Files are now ready to be copied.'
                                + '\n')

    def __init__(self: 'Worker', proc: 'Popen[str]') -> None:
        self.info: List[Tuple[Path, int]] = []
        self.proc: 'Popen[str]' = proc
        self.status: WorkerStatus = WorkerStatus.IDLE

    def backup(self: 'Worker') -> None:
        if self.status is not WorkerStatus.IDLE:
            return

        self.command('save hold')
        self.status = WorkerStatus.QUERY

        while self.status is not WorkerStatus.READY:
            self.command('save query')
            sleep(1)

        for loc, length in self.info:
            debug(f'{loc}: {length}')

        self.copy_files()

        self.command('save resume')
        self.status = WorkerStatus.IDLE

    def command(self: 'Worker', string: str) -> None:
        assert self.proc is not None
        assert self.proc.stdin is not None

        if not self.proc.poll():
            print(string)
            self.proc.stdin.write(string + '\n')

    def copy_files(self: 'Worker') -> None:
        Util.ensure_temp_dir()

        world_dir_name: str = ''
        world_dir_path: Optional[Path] = None
        for loc, length in self.info:
            if world_dir_name == '':
                world_dir_name = loc.parts[0]
                world_dir_path = Util.worlds_dir_path().joinpath(world_dir_name)
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

            # src: Path = Util.worlds_dir_path().joinpath(loc)
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

        # zip tmp/world
        zip_file_path = Util.temp_dir_path().joinpath(zip_file_name)
        zip_file = ZipFile(zip_file_path, 'w')

        temp_world_dir_path = Util.temp_dir_path().joinpath(world_dir_name)

        assert world_dir_path is not None
        for file_path in temp_world_dir_path.glob('**/*'):
            zip_file.write(file_path, file_path.relative_to(
                Util.temp_dir_path()))

        # world_saves_dir_path = Util.saves_dir_path().joinpath(world_dir_name)
        # world_saves_dir_path.mkdir(exist_ok=True)

        # copy zip file to saves dir
        final_dst = Util.saves_dir_path().joinpath(zip_file_name)
        copyfile(zip_file_path, final_dst)

    def thread_stdout(self: 'Worker') -> None:
        assert self.proc is not None
        assert self.proc.stdout is not None

        line: str
        for line in self.proc.stdout:
            print(line, end='')
            if self.status is WorkerStatus.INFO:
                files: List[str] = line.rstrip().split(', ')

                self.info = []

                for file in files:
                    (loc, length) = file.split(':')
                    self.info.append((Path(loc), int(length)))

                self.status = WorkerStatus.READY

            if (self.status is WorkerStatus.QUERY
                    and line == self.QUERY_STRING):
                self.status = WorkerStatus.INFO
