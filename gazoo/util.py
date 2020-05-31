from configparser import ConfigParser
from pathlib import Path
from shutil import rmtree
from typing import Final, Optional, Type # pylint: disable=unused-import

from gazoo.config import Config


class Util:
    _BASE_DIR_NAME: Final[str] = 'gazoo'
    _CONFIG_FILE_NAME: Final[str] = 'gazoo.cfg'
    _SAVES_DIR_NAME: Final[str] = 'saves'
    _TEMP_DIR_NAME: Final[str] = '.tmp'
    _WORLDS_DIR_NAME: Final[str] = 'worlds'

    _base_dir_path: Optional[Path] = None
    _config_file_path: Optional[Path] = None
    _saves_dir_path: Optional[Path] = None
    _temp_dir_path: Optional[Path] = None
    _worlds_dir_path: Optional[Path] = None

    @classmethod
    def base_dir_path(cls: 'Type[Util]') -> Path:
        if cls._base_dir_path is None:
            cls._base_dir_path = Path.cwd().joinpath(cls._BASE_DIR_NAME)

        return cls._base_dir_path

    @classmethod
    def config_file_path(cls: 'Type[Util]') -> Path:
        if cls._config_file_path is None:
            cls._config_file_path = cls.base_dir_path().joinpath(
                cls._CONFIG_FILE_NAME)

        return cls._config_file_path

    @classmethod
    def ensure_base_dir(cls: 'Type[Util]') -> None:
        cls.base_dir_path().mkdir(exist_ok=True)

    @classmethod
    def ensure_config_file(cls: 'Type[Util]') -> None:
        if cls.config_file_path().is_file():
            return

        cls.ensure_base_dir()

        with cls.config_file_path().open(mode='w') as config_file:
            config_file.write(Config.DEFAULTS_STRING)

    @classmethod
    def ensure_saves_dir(cls: 'Type[Util]') -> None:
        cls.saves_dir_path().mkdir(exist_ok=True)

    @classmethod
    def ensure_setup(cls: 'Type[Util]') -> None:
        cls.ensure_base_dir()
        cls.ensure_config_file()
        cls.ensure_saves_dir()
        cls.ensure_temp_dir()

    @classmethod
    def ensure_temp_dir(cls: 'Type[Util]') -> None:
        cls.temp_dir_path().mkdir(exist_ok=True)

        found: Path
        for found in cls.temp_dir_path().glob('*'):
            if found.is_dir() and not found.is_symlink():
                rmtree(found)
            else:
                found.unlink()

    @classmethod
    def read_config(cls: 'Type[Util]') -> Config:
        config_string: str = ''

        if cls.config_file_path().is_file():
            with cls.config_file_path().open() as config_file:
                config_string = config_file.read()

        config_string = f'{Config.PREAMBLE}{config_string}'

        config = ConfigParser(empty_lines_in_values=False)
        config.read_string(config_string)

        return Config(config)

    @classmethod
    def saves_dir_path(cls: 'Type[Util]') -> Path:
        if cls._saves_dir_path is None:
            cls._saves_dir_path = cls.base_dir_path().joinpath(
                cls._SAVES_DIR_NAME)

        return cls._saves_dir_path

    @classmethod
    def temp_dir_path(cls: 'Type[Util]') -> Path:
        if cls._temp_dir_path is None:
            cls._temp_dir_path = cls.base_dir_path().joinpath(
                cls._TEMP_DIR_NAME)

        return cls._temp_dir_path

    @classmethod
    def worlds_dir_path(cls: 'Type[Util]') -> Path:
        return Path.cwd().joinpath(cls._WORLDS_DIR_NAME)
