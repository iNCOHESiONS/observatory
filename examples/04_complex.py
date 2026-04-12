from observatory import (
    FileLogger,
    LogLevel,
    combined,
    date_time,
    foreground,
    line_info,
    linebreak,
    log_level,
)

colors = ("bisque", "!2", "!7", "orange", "!1", "!1")
modifiers = ("italic", "italic", "none", "bold", "bold", "inverse")

logger = FileLogger(
    formatter=combined(
        log_level(
            fmt="<{modifier}><{color}>({level}) {msg}</>",
            color_getter=dict(zip(LogLevel, colors)).__getitem__,
            modifier_getter=dict(zip(LogLevel, modifiers)).__getitem__,
        ),
        line_info(fmt="<!3>[{file}@L{loc}]</> {msg}"),
        date_time(fmt="<!4><bold>[%H:%M:%S]</> {}"),
        foreground(),
        linebreak(),
    )
)

msg = "The quick brown fox jumps over the lazy dog."

for level in LogLevel:
    logger.log(msg, level)
