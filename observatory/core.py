from abc import ABC, abstractmethod
from enum import IntEnum, auto
from types import TracebackType
from typing import Any, Callable, Self, final

from typing_extensions import NoReturn

__all__ = [
    "Formatter",
    "Logger",
    "LogLevel",
]


@final
class LogLevel(IntEnum):
    """
    Log levels.

    Aliases:
        `trace` -> `verbose`\n
        `warn` -> `warning`\n
        `fatal` -> `critical`
    """

    verbose = auto()
    debug = auto()
    info = auto()
    warning = auto()
    error = auto()
    critical = auto()

    trace = verbose  # alias
    warn = warning  # alias
    fatal = critical  # alias


class Logger(ABC):
    """Base class for loggers."""

    @final
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        _type: type[BaseException] | None,
        _value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.cleanup()

    @abstractmethod
    def log(self, msg: Any, /, level: LogLevel) -> None:
        """
        Logs a message with log level `level`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        level: `LogLevel`
            The log level.
        """

        raise NotImplementedError()

    @final
    def verbose(self, msg: Any, /) -> None:
        """
        Logs a message with log level `LogLevel.verbose`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        """

        self.log(msg, LogLevel.verbose)

    @final
    def debug(self, msg: Any, /) -> None:
        """
        Logs a message with log level `LogLevel.debug`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        """

        self.log(msg, LogLevel.debug)

    @final
    def info(self, msg: Any, /) -> None:
        """
        Logs a message with log level `LogLevel.info`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        """

        self.log(msg, LogLevel.info)

    @final
    def warning(self, msg: Any, /) -> None:
        """
        Logs a message with log level `LogLevel.warning`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        """

        self.log(msg, LogLevel.warning)

    @final
    def error(self, msg: Any, /) -> None:
        """
        Logs a message with log level `LogLevel.error`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        """

        self.log(msg, LogLevel.error)

    @final
    def critical(self, msg: Any, /) -> None:
        """
        Logs a message with log level `LogLevel.critical`.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        """

        self.log(msg, LogLevel.critical)

    trace = verbose  # alias
    warn = warning  # alias
    fatal = critical  # alias

    @final
    def panic(self, msg: Any, /, *, code: int = -1) -> NoReturn:
        """
        Logs a message with log level `LogLevel.critical` and exits the program with code `code`, `-1` by default.

        Parameters
        ----------
        msg: `Any`
            The message to be logged. Will be converted to a string using `str`.
        code: `int`
            The code to exit the program with. `-1` by default.
        """

        self.critical(msg)
        exit(code)

    def cleanup(self) -> None:
        """Used for cleanup; called on `__exit__`, so the user must use the `with` statement, or call this themselves."""


type Formatter = Callable[[str, LogLevel], str]
"""`Formatter`s are functions that return a formatted version of the message based on its original form and its `LogLevel`"""
