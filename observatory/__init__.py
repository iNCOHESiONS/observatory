"""
Observatory
-----------

A small and modular logging library with dynamic formatting capabitilies.

:copyright: (c) 2026 by iNCOHESiONS.
:license: MIT, see LICENSE for more details.
"""

import os
from typing import Callable

from .core import Logger, LogLevel
from .formatters import (
    background,
    colored,
    combined,
    date_time,
    foreground,
    line_info,
    linebreak,
    log_level,
    prefix_tag,
)
from .loggers import FileLogger, MultiLogger

if os.name == "nt":
    from colorama import just_fix_windows_console

    just_fix_windows_console()
    del just_fix_windows_console

__all__ = [
    "background",
    "colored",
    "combined",
    "date_time",
    "FileLogger",
    "foreground",
    "line_info",
    "linebreak",
    "log_level",
    "LogLevel",
    "MultiLogger",
    "prefix_tag",
]

_loggers: dict[str, Logger] = {}


def get_logger[T: Logger = FileLogger](
    name: str, /, *, factory: Callable[[], T] = FileLogger
) -> T:
    """
    Returns a `Logger` with the specified name, creating it using `factory` if necessary.\n
    By default, creates a `FileLogger` whose `file` is `stdout`.

    Parameters
    ----------
    name: `str`
        The name of the logger.
    factory: `Callable[[], T]`
        The factory to use to create the logger, if necessary.

    Returns
    -------
    `T`
        The logger with the specified name.
    """

    return _loggers[name] if name in _loggers else factory()  # pyright: ignore[reportReturnType]


getLogger = get_logger  # alias
