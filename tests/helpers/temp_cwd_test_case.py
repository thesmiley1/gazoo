"""
Provide cass `TempCwdTestCase`.
"""

from __future__ import annotations

from os import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase


class TempCwdTestCase(TestCase):
    """
    Provide automatic setup/teardoown of a temporary working directory.
    """

    def setUp(self: TempCwdTestCase) -> None:
        self._orig_cwd = Path.cwd()
        self._temp_cwd = TemporaryDirectory()

        chdir(self._temp_cwd.name)

    def tearDown(self: TempCwdTestCase) -> None:
        chdir(self._orig_cwd)
        self._temp_cwd.cleanup()
