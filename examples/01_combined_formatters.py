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

colors = {
    LogLevel.verbose: "bisque",
    LogLevel.debug: "!32m",
    LogLevel.info: "!37m",
    LogLevel.warning: "orange",
    LogLevel.error: "!31m",
    LogLevel.critical: "!31m",
}

modifiers = {
    LogLevel.verbose: "italic",
    LogLevel.debug: "italic",
    LogLevel.info: "none",
    LogLevel.warning: "bold",
    LogLevel.error: "bold",
    LogLevel.critical: "inverse",
}

logger = FileLogger(
    formatter=combined(
        log_level(
            fmt="<{modifier}><{color}>({level}) {msg}</>",
            color_getter=colors.__getitem__,
            modifier_getter=modifiers.__getitem__,
        ),
        line_info(fmt="<!33m>[{file}@L{loc}]</> {msg}"),
        date_time(fmt="<!34m><bold>[%H:%M:%S]</> {}"),
        foreground(),
        linebreak(),
    )
)

msg = "The quick brown fox jumps over the lazy dog."

logger.verbose(msg)
logger.debug(msg)
logger.info(msg)
logger.warning(msg)
logger.error(msg)
logger.critical(msg)
