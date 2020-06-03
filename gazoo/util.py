"""
Provide class Util.
"""

from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING

from gazoo.config import Config

if TYPE_CHECKING:
    from typing import Final, Optional, Type


class Util:
    """
    Provide misc functions for fs paths, config, setup, etc.
    """

    _BACKUPS_DIR_NAME: Final[str] = 'backups'
    _BASE_DIR_NAME: Final[str] = 'gazoo'
    _CONFIG_FILE_NAME: Final[str] = 'gazoo.cfg'
    _TEMP_DIR_NAME: Final[str] = '.tmp'
    _WORLDS_DIR_NAME: Final[str] = 'worlds'

    _backups_dir_path: Optional[Path] = None
    _base_dir_path: Optional[Path] = None
    _config_file_path: Optional[Path] = None
    _temp_dir_path: Optional[Path] = None
    _worlds_dir_path: Optional[Path] = None

    @classmethod
    def backups_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the application backups directory.
        """

        if cls._backups_dir_path is None:
            cls._backups_dir_path = cls.base_dir_path().joinpath(
                cls._BACKUPS_DIR_NAME)

        return cls._backups_dir_path

    @classmethod
    def base_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the base directory for application data.
        """

        if cls._base_dir_path is None:
            cls._base_dir_path = Path.cwd().joinpath(cls._BASE_DIR_NAME)

        return cls._base_dir_path

    @classmethod
    def config_file_path(cls: Type[Util]) -> Path:
        """
        Get the path to the application configuration file.
        """

        if cls._config_file_path is None:
            cls._config_file_path = cls.base_dir_path().joinpath(
                cls._CONFIG_FILE_NAME)

        return cls._config_file_path

    @classmethod
    def ensure_backups_dir(cls: Type[Util]) -> None:
        """
        Ensure the application backups directory exists.
        """

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
        and folders contained within are deleted.
        """

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

        if cls._temp_dir_path is None:
            cls._temp_dir_path = cls.base_dir_path().joinpath(
                cls._TEMP_DIR_NAME)

        return cls._temp_dir_path

    @classmethod
    def worlds_dir_path(cls: Type[Util]) -> Path:
        """
        Get the path to the server worlds directory.
        """

        return Path.cwd().joinpath(cls._WORLDS_DIR_NAME)
