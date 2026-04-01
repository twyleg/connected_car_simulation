import logging
import logging.config
from pathlib import Path


LOG_FILE_PATH = Path("connected_car_simulation.log")


def configure_logging(log_level: str = "INFO") -> None:
    resolved_log_level = log_level.upper()
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "[%(asctime)s.%(msecs)03d][%(levelname)s][%(name)s]: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": resolved_log_level,
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "level": resolved_log_level,
                    "formatter": "simple",
                    "filename": str(LOG_FILE_PATH),
                },
            },
            "root": {
                "level": resolved_log_level,
                "handlers": ["file", "console"],
            },
        }
    )
