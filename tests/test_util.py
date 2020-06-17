"""
Test module `gazoo.util`.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import main

from gazoo.util import Util

from .helpers.temp_cwd_test_case import TempCwdTestCase


class TestUtil(TempCwdTestCase):
    """
    Test class `Util`.
    """

    def test_backups_dir_path(self: TestUtil) -> None:
        """
        Test `Util.backups_dir_path`.

        Expect `$PWD/gazoo/backups`.
        """

        self.assertEqual(Util.backups_dir_path(),
                         Path.cwd().joinpath('gazoo', 'backups'))

    def test_base_dir_path(self: TestUtil) -> None:
        """
        Test `Util.base_dir_path`.

        Expect `$PWD/gazoo`.
        """

        self.assertEqual(Util.base_dir_path(), Path.cwd().joinpath('gazoo'))

    def test_config_file_path(self: TestUtil) -> None:
        """
        Test `Util.config_file_path`.

        Expect `$PWD/gazoo/gazoo.cfg`.
        """

        self.assertEqual(Util.config_file_path(),
                         Path.cwd().joinpath('gazoo', 'gazoo.cfg'))

    def test_ensure_backups_dir(self: TestUtil) -> None:
        """
        Test `Util.ensure_backups_dir`.

        Expect `$PWD/gazoo/backups` to be a directory that exists.
        """

        Util.ensure_backups_dir()
        self.assertTrue(Path.cwd().joinpath('gazoo', 'backups').is_dir())

    def test_ensure_base_dir(self: TestUtil) -> None:
        """
        Test `Util.ensure_base_dir`.

        Expect `$PWD/gazoo` to be a directory that exists.
        """

        Util.ensure_base_dir()
        self.assertTrue(Path.cwd().joinpath('gazoo').is_dir())

    def test_ensure_config_file(self: TestUtil) -> None:
        """
        Test `Util.ensure_config_file`.

        Expect `$PWD/gazoo/gazoo.cfg` to be a file that exists.
        """

        Util.ensure_config_file()
        self.assertTrue(Path.cwd().joinpath('gazoo', 'gazoo.cfg').is_file())

    def test_ensure_setup(self: TestUtil) -> None:
        """
        Test `Util.ensure_setup`.

        * Expect `$PWD/gazoo` to be a directory that exists.
        * Expect `$PWD/gazoo/backups` to be a directory that exists.
        * Expect `$PWD/gazoo/gazoo.cfg` to be a file that exists.
        * Expect `$PWD/gazoo/.tmp` to be a directory that exists.
        """

        Util.ensure_setup()
        self.assertTrue(Path.cwd().joinpath('gazoo').is_dir())
        self.assertTrue(Path.cwd().joinpath('gazoo', 'backups').is_dir())
        self.assertTrue(Path.cwd().joinpath('gazoo', 'gazoo.cfg').is_file())
        self.assertTrue(Path.cwd().joinpath('gazoo', '.tmp').is_dir())

    def test_ensure_temp_dir(self: TestUtil) -> None:
        """
        Test `Util.ensure_temp_dir`.

        Expect `$PWD/.tmp` to be an empty directory that exists.
        """

        Util.ensure_temp_dir()
        self.assertTrue(Util.temp_dir_path().is_dir())

        temp_file = NamedTemporaryFile(delete=False, dir=Util.temp_dir_path())
        temp_file.close()

        temp_file_path = Path(temp_file.name)
        self.assertTrue(temp_file_path.exists())  # sanity check

        Util.ensure_temp_dir()
        self.assertFalse(temp_file_path.exists())

    def test_read_config(self: TestUtil) -> None:
        """
        Test `Util.read_config`.

        Expect defaults if no configuration file is present, parsed
        values otherwise.
        """

        Util.read_config()  # smoke test

        Util.ensure_base_dir()
        with Path.cwd().joinpath('gazoo',
                                 'gazoo.cfg').open('w') as config_file:
            config_file.write('backup_interval=17\ndebug=true\n')

        config = Util.read_config()

        self.assertEqual(config.backup_interval, 17)
        self.assertTrue(config.debug)

    def test_temp_dir_path(self: TestUtil) -> None:
        """
        Test `Util.temp_dir_path`.

        Expect `$PWD/gazoo/.tmp`.
        """

        self.assertEqual(Util.temp_dir_path(),
                         Path.cwd().joinpath('gazoo', '.tmp'))

    def test_worlds_dir_path(self: TestUtil) -> None:
        """
        Test `Util.worlds_dir_path`.

        Expect `$PWD/worlds`.
        """

        self.assertEqual(Util.worlds_dir_path(), Path.cwd().joinpath('worlds'))


if __name__ == 'main':
    main()
