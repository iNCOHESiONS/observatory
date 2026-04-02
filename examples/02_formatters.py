from observatory import FileLogger, combined, date_time, linebreak

logger = FileLogger(
    formatter=combined(
        date_time(),
        linebreak(),
    )
)

logger.info("The quick brown fox jumps over the lazy dog.")
