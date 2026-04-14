from dataclasses import dataclass, field
from sys import stdout
from typing import Any, TextIO, override

from .core import Formatter, Logger, LogLevel
from .formatters import linebreak

__all__ = [
    "FileLogger",
    "MultiLogger",
]


@dataclass(slots=True, kw_only=True)
class FileLogger(Logger):
    """
    Logs to a file, and formats whatever message is being logged using `Formatter`s. Empty messages are not logged.\n
    By default, simply adds a line-break at the end of each message. See `observatory.formatters` for more.
    """

    file: TextIO = stdout
    """The file to log to. `stdout` by default."""

    formatter: Formatter = field(default_factory=linebreak)
    """The formatter to run the message through. Empty results are ignored. `linebreak` by default."""

    @override
    def log(self, msg: Any, /, level: LogLevel) -> None:
        if content := self.formatter(str(msg), level):
            self.file.write(content)

    @override
    def __eq__(self, other: Any, /) -> bool:
        return self.file == other.file if isinstance(other, self.__class__) else False

    @override
    def cleanup(self) -> None:
        if not self.file.closed:
            self.file.close()


class MultiLogger(Logger):
    """
    Logs a message to multiple loggers at the same time.
    Useful for having colored, formatted loggers for `stdout` and unformatted colors for saving to a file.
    """

    def __init__(self, *loggers: Logger) -> None:
        self.loggers = loggers

    @override
    def log(self, msg: Any, /, level: LogLevel) -> None:
        for logger in self.loggers:
            logger.log(msg, level)

    @override
    def cleanup(self) -> None:
        for logger in self.loggers:
            logger.cleanup()
