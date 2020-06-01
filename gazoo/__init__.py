"""
    Gazoo wraps Minecraft bedrock server for making proper backups.
"""

from logging import DEBUG
from logging import basicConfig as basic_config
from typing import Final

from gazoo.config import Config
from gazoo.wrapper import Wrapper
from gazoo.util import Util

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
