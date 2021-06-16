"""
    Wrap Minecraft bedrock server to make proper backups.
"""

from __future__ import annotations

from argparse import ArgumentParser
from logging import DEBUG
from logging import basicConfig as basic_config
from typing import TYPE_CHECKING

from .util import Util
from .wrapper import Wrapper

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Final

_LOGGING_TAG: Final[str] = 'gazoo'


def main() -> None:
    """
    Run the module as an application.
    """

    config = Util.read_config()
    basic_config(
        datefmt='%Y-%m-%d %H:%M:%S',
        format=f'[%(asctime)s %(levelname)s] [{_LOGGING_TAG}] %(message)s',
        level=(DEBUG if config.debug else None),
    )

    parser = ArgumentParser(
        description='Wrap Minecraft bedrock server to make proper backups')
    parser.set_defaults(config=config)
    parser.set_defaults(func=_run)

    subparsers = parser.add_subparsers()

    cleanup_parser = subparsers.add_parser('cleanup')
    cleanup_parser.set_defaults(func=_cleanup)

    restore_parser = subparsers.add_parser('restore')
    restore_parser.set_defaults(func=_restore)
    restore_parser.add_argument(
        'num_or_path',
        default=1,
        help='backup number ' +
        '(starting from 1, going back in time; defaults to 1) ' +
        'or path (absolute or relative) to the backup to restore',
        nargs='?')

    args = parser.parse_args()
    args.func(args)


def _cleanup(_args: Namespace) -> None:
    Util.cleanup_archives()


def _restore(args: Namespace) -> None:
    Util.restore_backup(args.num_or_path)


def _run(args: Namespace) -> None:
    Wrapper(args.config).run()


if __name__ == '__main__':
    main()
