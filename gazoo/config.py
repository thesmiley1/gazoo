"""
Provides class Config
"""

from __future__ import annotations

from configparser import DEFAULTSECT, ConfigParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


class Config:
    """
    Provides convenient access to configuration

    It wraps ConfigParser from the standard library to provide
    convenience properties that return values of the appropriate type.
    Default values are stored internally and constants for manipulating
    config files are provided for external use.
    """

    _DEFAULT_BACKUP_INTERVAL: Final[int] = 600
    _DEFAULT_DEBUG: Final[bool] = False

    _SECTION_NAME: Final[str] = 'gazoo'

    DEFAULTS_STRING: Final[str] = f'''backup_interval={_DEFAULT_BACKUP_INTERVAL}
debug={str(_DEFAULT_DEBUG).lower()}
'''
    """
    String of default settings for the config file
    """

    PREAMBLE: Final[str] = f'''[{DEFAULTSECT}]
{DEFAULTS_STRING}
[{_SECTION_NAME}]
'''
    """
    String to prepend to the string for a config file

    It sets defaults in the default section and adds an application-
    specific section to satisfy configparser so it doeesn't have to be
    present in every config file.
    """

    def __init__(self: 'Config', config: ConfigParser) -> None:
        self._config: ConfigParser = config

    @property
    def backup_interval(self: 'Config') -> int:
        """
        The time between backups (in seconds)
        """

        return self._config.getint(self._SECTION_NAME, 'backup_interval')

    @property
    def debug(self: 'Config') -> bool:
        """
        Indicates if debug mode is on
        """

        return self._config.getboolean(self._SECTION_NAME, 'debug')
