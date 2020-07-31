import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "DEBUG": "green",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel("DEBUG")
