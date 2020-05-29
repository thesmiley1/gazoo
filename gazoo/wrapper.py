from logging import info
from pathlib import Path, PurePath
from signal import SIGINT, signal
from subprocess import PIPE, Popen
from sys import stderr, stdin
from threading import Thread, Timer
from time import sleep
from types import FrameType
from typing import Dict, Final, List, Optional, Tuple, Type

from gazoo.config import Config
from gazoo.save_status import SaveStatus
from gazoo.saver import Saver
from gazoo.util import Util


class Wrapper:
    SERVER_BIN: Final[str] = 'bedrock_server'

    @classmethod
    def server_bin_path(cls: 'Type[Wrapper]') -> PurePath:
        return Path.cwd().joinpath(cls.SERVER_BIN)

    def __init__(self: 'Wrapper', config: Config) -> None:
        self.config = config
        self.proc: Optional[Popen] = None
        self.saver: Optional[Saver] = None
        self.threads: Dict[str, Thread] = {}
        self.timers: Dict[str, Timer] = {}

        signal(SIGINT, self.signal_sigint)

    def run(self: 'Wrapper') -> None:
        self.proc = Popen([self.server_bin_path()], bufsize=1,
                          stderr=PIPE, stdin=PIPE, stdout=PIPE, text=True)

        self.saver = Saver(self.proc)

        self.timers['next_save'] = Timer(self.config.save_interval,
                                         self.thread_save_timer)
        self.timers['next_save'].name = 'next_save'

        self.threads['setup'] = Thread(name='setup', target=Util.ensure_setup)

        self.threads['stderr'] = Thread(name='stderr',
                                        target=self.thread_stderr)

        self.threads['stdin'] = Thread(daemon=True, name='stdin',
                                       target=self.thread_stdin)

        self.threads['stdout'] = Thread(name='stdout',
                                        target=self.saver.thread_stdout)

        for timer in self.timers.values():
            timer.start()

        for thread in self.threads.values():
            thread.start()

        for key in ['setup', 'stderr', 'stdout']:
            self.threads[key].join()

        self.timers['next_save'].cancel()

        if self.timers.get('cur_save') is not None:
            self.timers['cur_save'].join()

    def signal_sigint(self: 'Wrapper', signum: int, frame: FrameType) -> None:
        assert self.proc is not None

        self.proc.terminate()
        print()

    def thread_save_timer(self: 'Wrapper') -> None:
        assert self.saver is not None

        this_save = self.timers['next_save']
        this_save.name = 'this_save'

        self.timers['next_save'] = Timer(self.config.save_interval,
                                         self.thread_save_timer)
        self.timers['next_save'].name = 'next_save'
        self.timers['next_save'].start()

        if self.saver.status is not SaveStatus.IDLE:
            info('previous save not completed; not attempting new save')
            return

        self.timers['cur_save'] = this_save
        self.timers['cur_save'].name = 'cur_save'

        self.saver.run()

    def thread_stderr(self: 'Wrapper') -> None:
        assert self.proc is not None
        assert self.proc.stderr is not None

        line: str
        for line in self.proc.stderr:
            print(line, end='', file=stderr)

    def thread_stdin(self: 'Wrapper') -> None:
        assert self.proc is not None
        assert self.proc.stdin is not None

        line: str
        for line in stdin:
            self.proc.stdin.write(line)
