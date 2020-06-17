"""
Provide class BackupFile.
"""

from __future__ import annotations

from errno import ENOENT
from pathlib import Path

from .util import Util


class BackupFile:
    """
    Provide convenience properties for backup files.
    """

    def __init__(self: BackupFile, path_fragment: str, length: int) -> None:
        self._path = Path(path_fragment)

        self.length = length

    @property
    def source_path(self: BackupFile) -> Path:
        """
        Get the actual source path for the backup file.

        The bedrock server gives paths that can can be missing a
        directory (specifically, the `db` subdirectory in the world
        directory), so attempt to figure out the right file.
        """

        found = list(self._world_dir_path.glob(f'**/{self._path.name}'))

        if len(found) == 0:
            raise OSError(ENOENT, 'Matching file not found', self._path)

        if len(found) > 1:
            raise OSError(ENOENT, f'Found {len(found)} matching files',
                          self._path)

        return found[0]

    @property
    def world_dir_name(self: BackupFile) -> str:
        """
        Get the name of the world directory for this backup file.
        """

        return self._path.parts[0]

    @property
    def _world_dir_path(self: BackupFile) -> Path:
        return Util.worlds_dir_path().joinpath(self.world_dir_name)
