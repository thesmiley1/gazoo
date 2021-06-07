"""
Provide class Wrapper.
"""

from __future__ import annotations

from logging import exception, info
from pathlib import Path, PurePath
from signal import SIGINT, signal
from subprocess import PIPE, Popen
from sys import stderr, stdin
from threading import Thread, Timer
from typing import TYPE_CHECKING

from .config import Config
from .backup_worker import BackupWorker
from .cleanup_worker import CleanupWorker
from .util import Util
from .worker_status import WorkerStatus

if TYPE_CHECKING:
    from types import FrameType
    from typing import Dict, Final, Optional, Type


class Wrapper:
    """
    Wrap bedrock server instance.

    Threads are created for stdin, stdout, and stderr, in addition to a
    Timer thread for performing the backup.
    """

    _SERVER_BIN: Final[str] = 'bedrock_server'

    _server_bin_path: Optional[Path] = None

    @classmethod
    def server_bin_path(cls: Type[Wrapper]) -> PurePath:
        """
        Get the full path to the bedrock server binary.
        """

        if cls._server_bin_path is None:
            _server_bin_path = Path.cwd().joinpath(cls._SERVER_BIN)

        return _server_bin_path

    def __init__(self: Wrapper, config: Config) -> None:
        self._config = config
        self._proc: 'Optional[Popen[str]]' = None
        self._threads: Dict[str, Thread] = {}
        self._timers: Dict[str, Timer] = {}
        self._backup_worker: Optional[BackupWorker] = None
        self._cleanup_worker: Optional[CleanupWorker] = None

        signal(SIGINT, self._signal_sigint)

    def run(self: Wrapper) -> None:
        """
        Start the bedrock server, run the wrapper.
        """

        self._proc = Popen([self.server_bin_path()],
                           bufsize=1,
                           stderr=PIPE,
                           stdin=PIPE,
                           stdout=PIPE,
                           text=True)

        self._backup_worker = BackupWorker(self._proc)
        self._cleanup_worker = CleanupWorker()

        self._timers['next_backup'] = Timer(self._config.backup_interval,
                                            self._thread_backup_timer)
        self._timers['next_backup'].name = 'next_backup'

        self._timers['next_cleanup'] = Timer(self._config.cleanup_interval,
                                             self._thread_cleanup_timer)
        self._timers['next_cleanup'].name = 'next_cleanup'

        self._threads['setup'] = Thread(name='setup', target=Util.ensure_setup)

        self._threads['stderr'] = Thread(name='stderr',
                                         target=self._thread_stderr)

        self._threads['stdin'] = Thread(daemon=True,
                                        name='stdin',
                                        target=self._thread_stdin)

        self._threads['stdout'] = Thread(name='stdout',
                                         target=self._backup_worker.thread_stdout)

        for timer in self._timers.values():
            timer.start()

        for thread in self._threads.values():
            thread.start()

        for key in ['setup', 'stderr', 'stdout']:
            self._threads[key].join()

        self._timers['next_backup'].cancel()
        self._timers['next_cleanup'].cancel()

        if self._timers.get('cur_backup') is not None:
            self._timers['cur_backup'].join()

        if self._timers.get('cur_cleanup') is not None:
            self._timers['cur_cleanup'].join()

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

        assert self._backup_worker is not None

        this_backup = self._timers['next_backup']
        this_backup.name = 'this_backup'

        self._timers['next_backup'] = Timer(self._config.backup_interval,
                                            self._thread_backup_timer)
        self._timers['next_backup'].name = 'next_backup'
        self._timers['next_backup'].start()

        if self._backup_worker.status is not WorkerStatus.IDLE:
            info('previous backup not completed; not attempting new backup')
            return

        self._timers['cur_backup'] = this_backup
        self._timers['cur_backup'].name = 'cur_backup'

        try:
            self._backup_worker.backup()
        except RuntimeError as error:
            exception('backup failed', exc_info=error)

    def _thread_cleanup_timer(self: Wrapper) -> None:
        """
        Set the next timer, start a new cleanup if one is not running
        """

        assert self._cleanup_worker is not None

        this_cleanup = self._timers['next_cleanup']
        this_cleanup.name = 'this_cleanup'

        self._timers['next_cleanup'] = Timer(self._config.cleanup_interval,
                                             self._thread_cleanup_timer)
        self._timers['next_cleanup'].name = 'next_cleanup'
        self._timers['next_cleanup'].start()

        if self._cleanup_worker.status is not WorkerStatus.IDLE:
            info('previous cleanup not completed; not attempting new cleanup')
            return

        self._timers['cur_cleanup'] = this_cleanup
        self._timers['cur_cleanup'].name = 'cur_cleanup'

        try:
            self._cleanup_worker.cleanup()
        except RuntimeError as error:
            exception('cleanup failed', exc_info=error)


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
