from configparser import DEFAULTSECT, ConfigParser
from pathlib import Path, PurePath
from shutil import rmtree
from typing import Final, Optional, Type


class Config:
    DEFAULT_DEBUG: Final[bool] = False
    DEFAULT_SAVE_INTERVAL: Final[int] = 600

    DEFAULTS_STRING: Final[str] = f'''debug={str(DEFAULT_DEBUG).lower()}
save_interval={DEFAULT_SAVE_INTERVAL}
'''

    SECTION_NAME: Final[str] = 'gazoo'

    PREAMBLE: Final[str] = f'''[{DEFAULTSECT}]
{DEFAULTS_STRING}
[{SECTION_NAME}]
'''


    def __init__(self: 'Config', config: ConfigParser) -> None:
        self.config: ConfigParser = config

    @property
    def debug(self: 'Config') -> bool:
        return self.config.getboolean(self.SECTION_NAME, 'debug')

    @property
    def save_interval(self: 'Config') -> int:
        return self.config.getint(self.SECTION_NAME, 'save_interval')
