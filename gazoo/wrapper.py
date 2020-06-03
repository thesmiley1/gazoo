"""
Provide class Wrapper.
"""

from __future__ import annotations

from logging import info
from pathlib import Path, PurePath
from signal import SIGINT, signal
from subprocess import PIPE, Popen
from sys import stderr, stdin
from threading import Thread, Timer
from typing import TYPE_CHECKING

from gazoo.config import Config
from gazoo.worker import Worker
from gazoo.util import Util
from gazoo.worker_status import WorkerStatus

if TYPE_CHECKING:
    from types import FrameType
    from typing import Dict, Final, Optional, Type


class Wrapper:
    """
    Wrap bedrock server instance.
    """

    _SERVER_BIN: Final[str] = 'bedrock_server'

    @classmethod
    def server_bin_path(cls: Type[Wrapper]) -> PurePath:
        """
        Get the full path to the bedrock server binary.
        """

        return Path.cwd().joinpath(cls._SERVER_BIN)

    def __init__(self: Wrapper, config: Config) -> None:
        self._config = config
        self._proc: 'Optional[Popen[str]]' = None
        self._worker: Optional[Worker] = None
        self._threads: Dict[str, Thread] = {}
        self._timers: Dict[str, Timer] = {}

        signal(SIGINT, self._signal_sigint)

    def run(self: Wrapper) -> None:
        """
        Start the bedrock server, run the wrapper.
        """

        self._proc = Popen([self.server_bin_path()], bufsize=1,
                           stderr=PIPE, stdin=PIPE, stdout=PIPE, text=True)

        self._worker = Worker(self._proc)

        self._timers['next_backup'] = Timer(self._config.save_interval,
                                            self._thread_backup_timer)
        self._timers['next_backup'].name = 'next_backup'

        self._threads['setup'] = Thread(name='setup', target=Util.ensure_setup)

        self._threads['stderr'] = Thread(name='stderr',
                                         target=self._thread_stderr)

        self._threads['stdin'] = Thread(daemon=True, name='stdin',
                                        target=self._thread_stdin)

        self._threads['stdout'] = Thread(name='stdout',
                                         target=self._worker.thread_stdout)

        for timer in self._timers.values():
            timer.start()

        for thread in self._threads.values():
            thread.start()

        for key in ['setup', 'stderr', 'stdout']:
            self._threads[key].join()

        self._timers['next_save'].cancel()

        if self._timers.get('cur_save') is not None:
            self._timers['cur_save'].join()

    def _signal_sigint(self: Wrapper, _signum: int, _frame: FrameType) -> None:
        """
        Handle sigint by terminating the server and printing a line.
        """

        assert self._proc is not None

        self._proc.terminate()
        print()

    def _thread_backup_timer(self: Wrapper) -> None:
        """
        Set the next timer, start a new backup if one is not running.
        """

        assert self._worker is not None

        this_backup = self._timers['next_backup']
        this_backup.name = 'this_backup'

        self._timers['next_backup'] = Timer(self._config.save_interval,
                                            self._thread_backup_timer)
        self._timers['next_backup'].name = 'next_backup'
        self._timers['next_backup'].start()

        if self._worker.status is not WorkerStatus.IDLE:
            info('previous save not completed; not attempting new save')
            return

        self._timers['cur_backup'] = this_backup
        self._timers['cur_backup'].name = 'cur_backup'

        self._worker.backup()

    def _thread_stderr(self: Wrapper) -> None:
        """
        Forward server stderr to system stderr.
        """

        assert self._proc is not None
        assert self._proc.stderr is not None

        line: str
        for line in self._proc.stderr:
            print(line, end='', file=stderr)

    def _thread_stdin(self: Wrapper) -> None:
        """
        Forward system stdin to server stdin.
        """

        assert self._proc is not None
        assert self._proc.stdin is not None

        line: str
        for line in stdin:
            self._proc.stdin.write(line)
