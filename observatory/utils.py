import re
from functools import reduce

import observatory.css_colors as colors
import observatory.modifiers as modifiers

__all__ = [
    "colorize",
    "hex_to_ansi",
    "noop_tags",
]


_RESET = "\033[0m"

_COLORS = {name.casefold(): value for name, value in vars(colors).items()}
_MODIFIERS = {name.casefold(): value for name, value in vars(modifiers).items()}

_CLOSING_MODFS = {
    "reset": _RESET,
    "none": _RESET,  # alias
    "bold": "\033[22m",
    "dim": "\033[22m",
    "faint": "\033[22m",  # alias
    "italic": "\033[23m",
    "underline": "\033[24m",
    "blinking": "\033[25m",
    "inverse": "\033[27m",
    "reverse": "\033[27m",  # alias
    "hidden": "\033[28m",
    "invisible": "\033[28m",  # alias
    "strikethrough": "\033[29m",
}


_TAG_PATTERN = re.compile(r"<(.*?)>")
_LITERAL_OPENING_TAG_PATTERN = re.compile(r"<([A-Za-z_]+)>")
_LITERAL_CLOSING_TAG_PATTERN = re.compile(r"</([A-Za-z_]+)?>")
_HEX_TAG_PATTERN = re.compile(r"<#([0-9A-Fa-f]{6})>")
_SIMPLIFIED_ANSI_CODE_TAG_PATTERN = re.compile(r"<!(.*?)>")
_RAW_ANSI_CODE_TAG_PATTERN = re.compile(r"<@(.*?)>")


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


def colorize(
    msg: str,
    /,
    *,
    colors: dict[str, str] | None = None,
    background: bool = False,
) -> str:
    """
    Parses a message, turning all tags (case insensitive) into ANSI color and modifier codes.

    Supports:
    - Hex colors: tags with a leading #, e.g., `<#FF0000>`, a pure red.\n
    - Simplified ANSI codes: tags with a leading !, where the ! gets replaced with `ESC[{N}{content}m`,
      where `N` is replaced by `4` if `background` is `True`, and `3` otherwise. Tag content must be within [1, 9].
      By default, since `background` is `False`, `<!1>` gets turned into ESC[31m, a red foreground, for example.\n
    - Raw ANSI codes: tags with a leading @, where the @ gets replaced with `ESC[`, allowing for any other ANSI codes to be used.
    - ANSI modifiers: tags that don't contain any of the previous leads, e.g., `<bold>`.\n
    - Color literals: tags that don't contain any of the previous leads, and aren't modifiers. Controlled by the `colors` argument.
      Uses CSS colors by default, e.g., `<rebecca_purple>`.\n
    - Closing tags, general and specific for modifiers: `</>` for resetting all colors and modifiers,
      and </{modifier}> for resetting specific modifiers, e.g., `</bold>`.

    See https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797 for more information on ANSI escape codes.

    Parameters
    ----------
    msg: `str`
        The message to colorize.
    colors: `dict[str, str]`, optional
        A mapping of color literals to hex colors or raw or simplified codes, to be further translated into escape codes ready for the terminal.
        `observatory.css_colors`'s contents by default. Alternatively, use `observatory.ansi_colors` for more widely compatible colors.
    background: `bool`, optional
        Whether hex colors and simplified ANSI codes should be interpreted as background colors, instead of foreground (i.e., text) colors. `False` by default.

    Returns
    -------
    `str`
        The reformatted message.

    Raises
    ------
    `ValueError`
        When a tag's opening contents aren't recognized.
    """

    colors = colors or _COLORS

    def __handle_case(match: re.Match[str]) -> str:
        return f"<{match.group(1).casefold()}>"

    def __handle_hex(match: re.Match[str]) -> str:
        return hex_to_ansi(match.group(1), background=background)

    def __handle_simplified_ansi(match: re.Match[str]) -> str:
        n = int(match.group(1))

        if not (1 <= n <= 9):
            raise ValueError(
                f"The contents of a simplified ANSI tag are out of range. Expected a number within [1, 9], found {n}."
            )

        return f"\033[{4 if background else 3}{n}m"

    def __handle_raw_ansi(match: re.Match[str]) -> str:
        return f"\033[{match.group(1)}"

    def __handle_opening(match: re.Match[str]) -> str:
        name = match.group(1)
        try:
            return _MODIFIERS[name] if name in _MODIFIERS else f"<{colors[name]}>"
        except IndexError:
            raise ValueError(f'Unknown color or modifier: "{name}".')

    def __handle_closing(match: re.Match[str]) -> str:
        return _CLOSING_MODFS[tag] if (tag := match.group(1)) else _RESET

    steps = {
        _TAG_PATTERN: __handle_case,
        _LITERAL_OPENING_TAG_PATTERN: __handle_opening,
        _LITERAL_CLOSING_TAG_PATTERN: __handle_closing,
        _HEX_TAG_PATTERN: __handle_hex,
        _SIMPLIFIED_ANSI_CODE_TAG_PATTERN: __handle_simplified_ansi,
        _RAW_ANSI_CODE_TAG_PATTERN: __handle_raw_ansi,
    }

    applied = reduce(
        lambda acc, item: item[0].sub(item[1], acc), steps.items(), str(msg)
    )

    return applied + _RESET


def noop_tags(msg: str, /) -> str:
    """
    Simply removes all tags from a message, preventing any colors or modifiers from being applied.

    Parameters
    ----------
    msg: `str`
        The message to remove tags from.
    """

    return _TAG_PATTERN.sub("", msg)
