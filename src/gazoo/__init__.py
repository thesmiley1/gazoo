"""
    Wrap Minecraft bedrock server to make proper backups.
"""

from __future__ import annotations

from logging import DEBUG, error
from logging import basicConfig as basic_config
from sys import argv
from typing import TYPE_CHECKING

from .config import Config
from .util import Util
from .wrapper import Wrapper

if TYPE_CHECKING:
    from typing import Final

_LOGGING_TAG: Final[str] = 'gazoo'


def main() -> None:
    """
    Run the module as an application.
    """

    config: Config = Util.read_config()

    basic_config(
        datefmt='%Y-%m-%d %H:%M:%S',
        format=f'[%(asctime)s %(levelname)s] [{_LOGGING_TAG}] %(message)s',
        level=(DEBUG if config.debug else None),
    )

    if len(argv) > 1:
        if argv[1] == 'restore':
            Util.restore_backup()
        else:
            error(f'Unrecognized command "{argv[1]}"')
    else:
        Wrapper(config).run()


if __name__ == '__main__':
    main()
