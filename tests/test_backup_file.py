"""
Test module `gazoo.backup_file`.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest import main

from gazoo.backup_file import BackupFile
from gazoo.util import Util

from .helpers.temp_cwd_test_case import TempCwdTestCase

if TYPE_CHECKING:
    from typing import Optional


class TestBackupFile(TempCwdTestCase):
    """
    Test class `BackupFile`.
    """

    def test_source_path_multi_matching_files(self: TestBackupFile) -> None:
        """
        Test `BackupFile.source_path` with multiple matching files.

        Expect `FileNotFoundError`.
        """

        Util.worlds_dir_path().mkdir()

        world_dir = Util.worlds_dir_path().joinpath('world')
        world_dir.mkdir()

        dir1: Path = world_dir.joinpath('dir1')
        dir1.mkdir()

        dir2: Path = world_dir.joinpath('dir2')
        dir2.mkdir()

        file1: Path = dir1.joinpath('foo.bar')
        file1.touch()

        file2: Path = dir2.joinpath('foo.bar')
        file2.touch()

        backup_file = BackupFile(str(Path('world').joinpath('foo.bar')), 22)

        file_not_found_error = FileNotFoundError()
        try:
            backup_file.source_path
        except FileNotFoundError as err:
            file_not_found_error = err
        finally:
            self.assertRegex(str(file_not_found_error),
                             'Found 2 matching files')

    def test_source_path_no_matching_files(self: TestBackupFile) -> None:
        """
        Test `BackupFile.source_path` with no matching files.

        Expect `FileNotFoundError`.
        """

        backup_file = BackupFile('foo/bar.baz', 99)

        file_not_found_error: Optional[FileNotFoundError] = None
        try:
            backup_file.source_path
        except FileNotFoundError as err:
            file_not_found_error = err
        finally:
            self.assertRegex(str(file_not_found_error),
                             'Matching file not found')

    def test_source_path_one_matching_file(self: TestBackupFile) -> None:
        """
        Test `BackupFile.source_path` with one matching file.

        Expect path to file.
        """
        Util.worlds_dir_path().mkdir()

        world_dir_path = Util.worlds_dir_path().joinpath('world')
        world_dir_path.mkdir()

        dir_path: Path = world_dir_path.joinpath('dir')
        dir_path.mkdir()

        file_path: Path = dir_path.joinpath('foo.bar')
        file_path.touch()

        backup_file = BackupFile(str(Path('world').joinpath('foo.bar')), 32)

        self.assertEqual(backup_file.source_path, file_path)

    def test_world_dir_name(self: TestBackupFile) -> None:
        """
        Test `BackupFile.world_dir_name`.
        """

        backup_file = BackupFile(str(Path('worldname', 'foo.bar')), 44)
        self.assertEqual(backup_file.world_dir_name, 'worldname')


if __name__ == 'main':
    main()
