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

    _DEFAULT_DEBUG: Final[bool] = False
    _DEFAULT_SAVE_INTERVAL: Final[int] = 600

    _SECTION_NAME: Final[str] = 'gazoo'

    DEFAULTS_STRING: Final[str] = f'''debug={str(_DEFAULT_DEBUG).lower()}
save_interval={_DEFAULT_SAVE_INTERVAL}
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
    def debug(self: 'Config') -> bool:
        """
        Indicates if debug mode is on
        """

        return self._config.getboolean(self._SECTION_NAME, 'debug')

    @property
    def save_interval(self: 'Config') -> int:
        """
        The time between saves (in seconds)
        """

        return self._config.getint(self._SECTION_NAME, 'save_interval')
