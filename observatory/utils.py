import re
from functools import reduce

import observatory.colors

__all__ = [
    "colorize",
    "hex_to_ansi",
]

_RESET = "\033[0m"

_COLORS = {name.casefold(): value for name, value in vars(observatory.colors).items()}

_MODIFIERS = {  # opening -> closing
    "reset": (_RESET, _RESET),
    "none": (_RESET, _RESET),  # alias
    "bold": ("\033[1m", "\033[22m"),
    "dim": ("\033[2m", "\033[22m"),
    "faint": ("\033[2m", "\033[22m"),  # alias
    "italic": ("\033[3m", "\033[23m"),
    "underline": ("\033[4m", "\033[24m"),
    "blinking": ("\033[5m", "\033[25m"),
    "inverse": ("\033[7m", "\033[27m"),
    "reverse": ("\033[7m", "\033[27m"),  # alias
    "hidden": ("\033[8m", "\033[28m"),
    "invisible": ("\033[8m", "\033[28m"),  # alias
    "strikethrough": ("\033[9m", "\033[29m"),
}

_TAG_PATTERN = re.compile(r"<(.*?)>")
_LITERAL_OPENING_TAG_PATTERN = re.compile(r"<([A-Za-z_]+)>")
_LITERAL_CLOSING_TAG_PATTERN = re.compile(r"</([A-Za-z_]+)?>")
_HEX_TAG_PATTERN = re.compile(r"<#([0-9A-Fa-f]{6})>")
_ANSI_CODE_TAG_PATTERN = re.compile(r"<!(.*?)>")


def hex_to_ansi(hex: str, /, *, background: bool = False) -> str:
    """
    Converts a hex color to an ANSI color code.

    Examples
    --------
    >>> hex_to_ansi("#FFFFFF")
    '\033[38;2;255;255;255m'
    >>> hex_to_ansi("#DDDDDD", background=True)
    '\033[48;2;221;221;221'

    Parameters
    ----------
    hex: `str`
        The hex code to convert to ANSI. Trims any leading #.
    background: `bool`
        Whether this is a background color, instead of a foreground (i.e., text) color. `False` by default.

    Returns
    -------
    `str`
        The ANSI code.

    Raises
    ------
    `ValueError`
        If the length of `hex` is not exactly 6 (after trimming).
    """

    hex = hex.replace("#", "")

    if len(hex) != 6:
        raise ValueError(f"Argument {hex} is not of length 6.")

    code = "48" if background else "38"
    r = int(hex[:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:], 16)

    return f"\033[{code};2;{r};{g};{b}m"


def colorize(msg: str, /, *, background: bool = False) -> str:
    """
    Parses a message, turning all tags into ANSI color codes.

    Supports:
    - Hex colors: tags with a leading #, e.g., <#FF0000>, so a pure red.\n
    - ANSI codes: tags with a leading !, where the ! gets replaced with \033[, e.g., <!31m>, a red foreground.\n
    - ANSI modifiers: tags that don't contain any of the previous leads, e.g., <bold>.\n
    - All CSS colors: tags that don't contain any of the previous leads, and aren't modifiers, e.g., <black>.\n
    - Closing tags, general and specific for modifiers: </> for resetting all colors and modifiers, and </{modifier}> for resetting specific modifiers, e.g., </bold>.

    Tagging is case insensitive.

    Parameters
    ----------
    msg: `str`
        The message to colorize.
    background: `bool`
        Whether hex colors should be interpreted as background colors, instead of foreground (i.e., text) colors. `False` by default.

    Returns
    -------
    `str`
        The reformatted message.
    """

    def __handle_case(match: re.Match[str]) -> str:
        return f"<{match.group(1).casefold()}>"

    def __handle_hex(match: re.Match[str]) -> str:
        return hex_to_ansi(match.group(1), background=background)

    def __handle_ansi(match: re.Match[str]) -> str:
        return f"\033[{match.group(1)}"

    def __handle_opening(match: re.Match[str]) -> str:
        return (
            _MODIFIERS[name][0]
            if (name := match.group(1)) in _MODIFIERS
            else hex_to_ansi(_COLORS[name])
        )

    def __handle_closing(match: re.Match[str]) -> str:
        return _MODIFIERS[tag][1] if (tag := match.group(1)) else _RESET

    steps = {
        _TAG_PATTERN: __handle_case,
        _HEX_TAG_PATTERN: __handle_hex,
        _ANSI_CODE_TAG_PATTERN: __handle_ansi,
        _LITERAL_OPENING_TAG_PATTERN: __handle_opening,
        _LITERAL_CLOSING_TAG_PATTERN: __handle_closing,
    }

    applied = reduce(
        lambda acc, item: item[0].sub(item[1], acc), steps.items(), str(msg)
    )

    return applied + _RESET
