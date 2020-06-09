"""
Test module gazoo.config.
"""

from __future__ import annotations

from configparser import ConfigParser
from unittest import TestCase, main

from gazoo.config import Config


class TestConfig(TestCase):
    """
    Test class Config.
    """

    def setUp(self: TestConfig) -> None:
        parser: ConfigParser = ConfigParser()
        parser.read_string(Config.PREAMBLE)

        self.config: Config = Config(parser)

    def test_backup_interval(self: TestConfig) -> None:
        """
        Test `Config.backup_interval`.

        Expect int of default value.
        """

        self.assertEqual(self.config.backup_interval, 600)

    def test_debug(self: TestConfig) -> None:
        """
        Test `Config.debug`.

        Expect bool of default value.
        """

        self.assertEqual(self.config.debug, False)


if __name__ == 'main':
    main()
