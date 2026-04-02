from observatory import FileLogger, colored, combined, linebreak, prefix_tag

logger = FileLogger(
    formatter=combined(
        prefix_tag(contents="blue"),
        colored(),
        linebreak(),
    )
)

logger.info("The quick brown fox jumps over the lazy dog.")
