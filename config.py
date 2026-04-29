from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    logging_config: str
    logging_level: str
    stop: None

settings = Settings(
    logging_config='''{
        "version": 1,
        "disable_existing_loggers": "False",
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"]
        }
    }''',
    logging_level = 'DEBUG',
    stop = None
)
