import traceback
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import Callable

from .core import Formatter, LogLevel
from .utils import colorize, noop_tags

__all__ = [
    "background",
    "colored",
    "combined",
    "date_time",
    "foreground",
    "line_info",
    "linebreak",
    "log_level",
    "prefix_tag",
]


def foreground() -> Formatter:
    """
    Creates a `Formatter` that applies `colorize`, consuming all tags in the message, interpreting any hex colors as foreground colors.

    Returns
    -------
    `Formatter`
        The created `Formatter`.
    """

    return lambda msg, _: colorize(msg)


colored = foreground  # alias


def background() -> Formatter:
    """
    Creates a `Formatter` that applies `colorize`, consuming all tags in the message, interpreting any hex colors as background colors.

    Returns
    -------
    `Formatter`
        The created `Formatter`.
    """

    return lambda msg, _: colorize(msg, background=True)


def no_color() -> Formatter:
    """
    Creates a `Formatter` that applies `noop_tags`, removing all tags from the message and preventing any colors or modifiers from being applied.

    Returns
    -------
    `Formatter`
        The created `Formatter`.
    """

    return lambda msg, _: noop_tags(msg)


def prefix_tag(*, contents: str) -> Formatter:
    """
    Creates a `Formatter` that prefixes the message with a tag.
    Useful for changing the color of the message.

    Parameters
    ----------
    contents: `str`
        The contents of the tag, i.e., what goes inside the angle brackets.

    Returns
    -------
    `Formatter`
        The resulting formatter.
    """

    return lambda msg, _: f"<{contents}>{msg}"


def line_info(*, fmt: str = "[{file}@L{loc}] {msg}") -> Formatter:
    """
    Creates a `Formatter` that adds line information (file, LOC) about where this `log` call is from.

    Parameters
    ----------
    fmt: `str`
        The format to use. `"[{file}@L{loc}] {msg}"` by default.\n
        Example: `[example@L43] The quick brown fox jumps over the lazy dog.`

    Returns
    -------
    `Formatter`
        The resulting formatter.
    """

    return lambda msg, _: fmt.format(
        file=Path((frame := traceback.extract_stack()[0]).filename).stem,
        loc=frame.lineno or 0,
        msg=msg,
    )


def log_level(
    *,
    fmt: str = "<{modifier}><{color}>({level})</> {msg}",
    color_getter: Callable[[LogLevel], str] = lambda _: "reset",
    modifier_getter: Callable[[LogLevel], str] = lambda _: "reset",
    name_getter: Callable[[LogLevel], str] = lambda level: level.name.upper(),
) -> Formatter:
    """
    Creates a `Formatter` that prefixes the message with its log level.\n
    Requires a formatter like `background`, `foreground` or `no_color` being applied afterwards to consume the tags in `fmt`.

    Parameters
    ----------
    fmt: `str`
        The format to use. `"<{modifier}><{color}>({level})</> {msg}"` by default.
        Example: (INFO) The quick brown fox jumps over the lazy dog.
    color_getter: `Callable[[LogLevel], str]`
        A function that returns a color to be used in the `fmt`. Simply returns `reset` by default.
    modifier_getter: `Callable[[LogLevel], str]`
        A function that returns a Modifier to be used in the `fmt`. Simply returns `reset` by default.
    name_getter: `Callable[[LogLevel], str]`
        A function that formats the LogLevel. Simply returns its name, uppercased, by default.

    Returns
    -------
    `Formatter`
        The resulting formatter.
    """

    return lambda msg, level: fmt.format(
        msg=msg,
        level=name_getter(level),
        color=color_getter(level),
        modifier=modifier_getter(level),
    )


def date_time(*, fmt: str = "[%H:%M:%S] {}") -> Formatter:
    """
    Creates a `Formatter` that Prefixes the message with formatted date and time information.
    See https://docs.python.org/3.6/library/datetime.html#strftime-and-strptime-behavior for formatting options.

    Parameters
    ----------
    fmt: `str`
        The format to use. `"[%H:%M:%S] {}"` by default.
        Example: `[00:00:00] The quick brown fox jumps over the lazy dog.`

    Returns
    -------
    `Formatter`
        The resulting formatter.
    """

    return lambda msg, _: datetime.now().strftime(fmt).format(msg)


def linebreak(*, end: str = "\n") -> Formatter:
    """
    Creates a `Formatter` that appends `end` to the message, a linebreak by default.

    Parameters
    ----------
    end: `str`
        The ending to append. `\\n` by default.

    Returns
    -------
    `Formatter`
        The resulting formatter.
    """

    return lambda msg, _: msg + end


def combined(*formatters: Formatter) -> Formatter:
    """
    Creates a `Formatter` that applies multiple other formatters in order, effectively combining them.

    Parameters
    ----------
    *formatters: `Formatter`
        The formatters to combine.

    Returns
    -------
    `Formatter`
        A `Formatter` that applies all the specified formatters in order.
    """

    return lambda msg, _: reduce(lambda acc, f: f(acc, _), formatters, msg)
