"""
Module to implement the capability of logging information in an OOP manner.
"""


import logging


class LoggableEntity:
    """
    A class to implement logging capabilities
    """


    def __init__(self, log_level : int = logging.INFO) -> None:
        """
        Constructor method for the  `LoggableEntity` class.

        Args:
            log_level (int): the level to be used for logging information.
        """
        self.logger = self.setup_logging_functionality(log_level)


    def setup_logging_functionality(
            self,
            log_level : int
        ) -> logging.Logger:
        """
        Method to setup the logging functionality.

        Args:
            log_level (int): the level to be used for logging information.
        """

        # Step 1: Creating the logger instance
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(log_level)

        # Step 2: Adding a console handler to show logs on CMD
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Step 3: Formatting the logs
        formatter = logging.Formatter(f'[{self.__class__.__name__}] [%(levelname)s] %(asctime)s: %(message)s')
        console_handler.setFormatter(formatter)

        # Step 4: Configuring the logger to use the console handler
        logger.addHandler(console_handler)

        return logger
