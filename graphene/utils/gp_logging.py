from logging import config


class GPLogging:
    """
    Sets up the logging configuration file, only needs to be done once
    """

    LOGGING_FILE_NAME = "logging.conf"

    def __init__(self):
        config.fileConfig(self.LOGGING_FILE_NAME,
                          disable_existing_loggers=False)
