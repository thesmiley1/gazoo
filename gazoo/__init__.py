"""
    Wrapper for Minecraft bedrock server to make proper backups.
"""

from __future__ import annotations

from logging import DEBUG
from logging import basicConfig as basic_config
from typing import TYPE_CHECKING

from gazoo.config import Config
from gazoo.util import Util
from gazoo.wrapper import Wrapper

if TYPE_CHECKING:
    from typing import Final

_LOGGING_TAG: Final[str] = 'gazoo'


def main() -> None:
    """
    Function main runs the module as an application.
    """

    config: Config = Util.read_config()

    basic_config(
        datefmt='%Y-%m-%d %H:%M:%S',
        format=f'[%(asctime)s %(levelname)s] [{_LOGGING_TAG}] %(message)s',
        level=(DEBUG if config.debug else None),
    )

    Wrapper(config).run()


if __name__ == '__main__':
    main()
