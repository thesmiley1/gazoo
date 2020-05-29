from logging import DEBUG, WARNING, debug
from logging import basicConfig as basic_config
from typing import Final

from gazoo.config import Config
from gazoo.wrapper import Wrapper
from gazoo.util import Util

LOGGING_TAG: Final[str] = 'gazoo'


def main() -> None:
    config: Config = Util.read_config()

    basic_config(
        datefmt='%Y-%m-%d %H:%M:%S',
        format=f'[%(asctime)s %(levelname)s] [{LOGGING_TAG}] %(message)s',
        level=(DEBUG if config.debug else WARNING),
    )

    debug(config.config)

    Wrapper(config).run()


if __name__ == '__main__':
    main()
