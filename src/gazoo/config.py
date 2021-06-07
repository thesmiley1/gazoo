"""
Provide class Config.
"""

from __future__ import annotations

from configparser import DEFAULTSECT, ConfigParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final


class Config:
    """
    Provide convenient access to configuration.

    ConfigParser from the standard library is wrapped to provide
    convenience properties that return values of the appropriate type.
    Default values are stored internally and constants for manipulating
    configuration files are provided for external use.
    """

    _DEFAULT_BACKUP_INTERVAL: Final[int] = 10 * 60 # 10 minutes
    _DEFAULT_CLEANUP_INTERVAL: Final[int] = 24 * 60 * 60 # 24 hours
    _DEFAULT_DEBUG: Final[bool] = False

    _SECTION_NAME: Final[str] = 'gazoo'

    DEFAULTS_STRING: Final[str] = (
        f'''backup_interval={_DEFAULT_BACKUP_INTERVAL}
cleanup_interval={_DEFAULT_CLEANUP_INTERVAL}
debug={str(_DEFAULT_DEBUG).lower()}
''')
    """
    String of default settings for the config file
    """

    PREAMBLE: Final[str] = f'''[{DEFAULTSECT}]
{DEFAULTS_STRING}
[{_SECTION_NAME}]
'''
    """
    String to prepend to the string for a config file

    Default values are set in the default section and an application-
    specific section is added to satisfy configparser so it doesn't have
    to be present in every configuration fie.
    """

    def __init__(self: 'Config', config: ConfigParser) -> None:
        self._config: ConfigParser = config

    @property
    def backup_interval(self: 'Config') -> int:
        """
        Time between backups (in seconds)
        """

        return self._config.getint(self._SECTION_NAME, 'backup_interval')

    @property
    def cleanup_interval(self: 'Config') -> int:
        """
        Time between cleanups (in seconds)
        """

        return self._config.getint(self._SECTION_NAME, 'cleanup_interval')

    @property
    def debug(self: 'Config') -> bool:
        """
        Indicates if debug mode is on
        """

        return self._config.getboolean(self._SECTION_NAME, 'debug')
