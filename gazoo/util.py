"""
Provide class Util.
"""

from __future__ import annotations

from configparser import ConfigParser
from datetime import datetime
from logging import error
from os import rename
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING
from zipfile import ZipFile

from .config import Config

if TYPE_CHECKING:
    from typing import BinaryIO, Final, List, Type

    from .backup_file import BackupFile


class Util:
    """
    Provide stateless utility functions for paths, config, setup, etc.
    """

    _BACKUPS_DIR_NAME: Final[str] = 'backups'
    _BASE_DIR_NAME: Final[str] = 'gazoo'
    _CONFIG_FILE_NAME: Final[str] = 'gazoo.cfg'
    _TEMP_DIR_NAME: Final[str] = '.tmp'
    _WORLDS_DIR_NAME: Final[str] = 'worlds'

    @classmethod
    def archive_files(cls: Type[Util], backup_files: List[BackupFile]) -> None:
        """
        Copy saved files to backup archive.
        """

        Util.ensure_temp_dir()

        world_dir_name = backup_files[0].world_dir_name

        datetime_string = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        zip_file_name = f'{world_dir_name} {datetime_string}.zip'

        zip_file_path = Util.temp_dir_path().joinpath(zip_file_name)
        zip_file = ZipFile(zip_file_path, 'w')

        for backup_file in backup_files:
            if world_dir_name != backup_file.world_dir_name:
                error(('world_dir_name mismatch: '
                       + '{world_dir_name} {loc.parts[0]}'))

            try:
                source_file: BinaryIO
                with backup_file.source_path.open(mode='rb') as source_file:
                    zip_file.writestr(
                        str(backup_file.source_path.relative_to(
                            Util.worlds_dir_path(),
                        )),
                        source_file.read(backup_file.length),
                    )
            except FileNotFoundError as err:
                error(err)

        final_dest_path = Util.backups_dir_path().joinpath(zip_file_name)
        rename(zip_file_path, final_dest_path)

        Util.ensure_temp_dir()

    @classmethod
    def backups_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the application backups directory.
        """

        return cls.base_dir_path().joinpath(cls._BACKUPS_DIR_NAME)

    @classmethod
    def base_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the base directory for application data.
        """

        return Path.cwd().joinpath(cls._BASE_DIR_NAME)

    @classmethod
    def config_file_path(cls: Type[Util]) -> Path:
        """
        Get the path to the application configuration file.
        """

        return cls.base_dir_path().joinpath(cls._CONFIG_FILE_NAME)

    @classmethod
    def ensure_backups_dir(cls: Type[Util]) -> None:
        """
        Ensure the application backups directory exists.

        Also ensure the application base directory exists (needed
        because the application backups directory is a subdirectory of
        the application base directory).
        """

        cls.ensure_base_dir()

        cls.backups_dir_path().mkdir(exist_ok=True)

    @classmethod
    def ensure_base_dir(cls: Type[Util]) -> None:
        """
        Ensure the base directory for application data exists.
        """

        cls.base_dir_path().mkdir(exist_ok=True)

    @classmethod
    def ensure_config_file(cls: Type[Util]) -> None:
        """
        Ensure the application configuration file exists.

        If it does not, write a file with default values.

        Also ensure the application base directory exists (needed
        because the application configuration file lives in the
        application base directory).
        """

        if cls.config_file_path().is_file():
            return

        cls.ensure_base_dir()

        with cls.config_file_path().open(mode='w') as config_file:
            config_file.write(Config.DEFAULTS_STRING)

    @classmethod
    def ensure_setup(cls: Type[Util]) -> None:
        """
        Ensure the filesystem is set up how it is expected to be.

        * base_dir
            * Subdirectory of current working directory that houses all
              persistent application data
        * backups_dir
            * Subdirectory of base_dir that houses all of the backed up
              world saves
        * config_file
            * File in base_dir to store persistent application
              configuration data
        * temp_dir
            * Subdirectory of base_dir that is used as ephemeral storage
              for making temporary copies of files
        """

        cls.ensure_base_dir()

        cls.ensure_backups_dir()
        cls.ensure_config_file()
        cls.ensure_temp_dir()

    @classmethod
    def ensure_temp_dir(cls: Type[Util]) -> None:
        """
        Ensure the application temporary directory exists and is empty.

        In order to ensure the temprary directory is empty, all files
        and folders contained within it are deleted.

        Also ensure the application base directory exists (needed
        because the application temporary directory is a subdirectory of
        the application base directory).
        """

        cls.ensure_base_dir()

        cls.temp_dir_path().mkdir(exist_ok=True)

        found: Path
        for found in cls.temp_dir_path().glob('*'):
            if found.is_dir() and not found.is_symlink():
                rmtree(found)
            else:
                found.unlink()

    @classmethod
    def read_config(cls: Type[Util]) -> Config:
        """
        Read the config file, prepend the preamble, then parse it.

        The preamble that is prepended contains a defaults section with
        default values and an application-specific section that gets the
        values read in from the file.
        """

        config_string: str = ''

        if cls.config_file_path().is_file():
            with cls.config_file_path().open() as config_file:
                config_string = config_file.read()

        config_string = f'{Config.PREAMBLE}{config_string}'

        config = ConfigParser(empty_lines_in_values=False)
        config.read_string(config_string)

        return Config(config)

    @classmethod
    def temp_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the application temporary directory.
        """

        return cls.base_dir_path().joinpath(cls._TEMP_DIR_NAME)

    @classmethod
    def worlds_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the server worlds directory.
        """

        return Path.cwd().joinpath(cls._WORLDS_DIR_NAME)
