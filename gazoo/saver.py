from pathlib import Path, PurePath
from subprocess import Popen
from time import sleep
from typing import Final, List, Tuple
from logging import debug, info

from gazoo.save_status import SaveStatus
from gazoo.util import Util


class Saver:
    QUERY_STRING: Final[str] = ('Data saved. Files are now ready to be copied.'
                                + '\n')

    def __init__(self: 'Saver', proc: Popen) -> None:
        self.info: List[Tuple[Path, int]] = []
        self.proc: Popen = proc
        self.status: SaveStatus = SaveStatus.IDLE

    def run(self: 'Saver'):
        if self.status is not SaveStatus.IDLE:
            return

        self.status = SaveStatus.HOLD
        self.command('save hold')

        self.status = SaveStatus.QUERY

        while self.status is not SaveStatus.READY:
            self.command('save query')
            sleep(1)

        for loc, length in self.info:
            print(f'{loc}: {length}')

        # Saver(self.save_info).save()
        self.save()

        for i in range(5):
            sleep(1)
            print(i)

        self.command('save resume')
        self.status = SaveStatus.IDLE

    def command(self: 'Saver', string: str) -> None:
        assert self.proc is not None
        assert self.proc.stdin is not None

        if not self.proc.poll():
            print(string)
            self.proc.stdin.write(string + '\n')

    def save(self: 'Saver'):
        Util.ensure_temp_dir()

        base_path: str = ''  # FIXME Path ???
        for loc, length in self.info:
            if base_path == '':
                base_path = loc.parts[0]

            src: PurePath = Util.worlds_dir_path().joinpath(loc)
            debug(f'src: {src}')

            dst: PurePath = Util.temp_dir_path().joinpath(loc)
            debug(f'dst: {dst}')

            # have_all_dirs: bool = False
            # while not have_all_dirs:
            #     # Path.cwd().joinpath('worlds', loc).
            #     print(f'{loc}: {length}')

    def thread_stdout(self: 'Saver') -> None:
        assert self.proc is not None
        assert self.proc.stdout is not None

        line: str
        for line in self.proc.stdout:
            print(line, end='')
            if self.status is SaveStatus.INFO:
                files: List[str] = line.rstrip().split(', ')

                self.info = []

                for file in files:
                    (loc, length) = file.split(':')
                    self.info.append((Path(loc), int(length)))

                self.status = SaveStatus.READY

            if (self.status is SaveStatus.QUERY
                    and line == self.QUERY_STRING):
                self.status = SaveStatus.INFO
