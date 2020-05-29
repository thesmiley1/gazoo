from logging import debug, error, info
from pathlib import Path, PurePath
from shutil import copyfile
from subprocess import Popen
from time import sleep
from typing import Final, List, Optional, Tuple

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
            debug(f'{loc}: {length}')

        self.save()

        for i in range(5):
            sleep(1)
            info(i)

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

        base_path: str = ''
        full_base_path: Optional[Path] = None
        for loc, length in self.info:
            if base_path == '':
                base_path = loc.parts[0]
                full_base_path = Util.worlds_dir_path().joinpath(base_path)
            elif base_path != loc.parts[0]:
                error(f'base_path mismatch: {base_path} {loc.parts[0]}')

            assert full_base_path is not None
            found: List[Path] = list(full_base_path.glob(f'**/{loc.name}'))

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
