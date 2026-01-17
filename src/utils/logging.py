# Copyright 2025 Voltstriker

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Logging configuration for Discord Bots.

This module provides a custom logging formatter and sets up logging
handlers for console and file output.
"""

import logging
import os


class LoggingFormatter(logging.Formatter):
    """
    Custom logging formatter that applies ANSI colour codes to log messages
    based on their severity level.
    """

    def __init__(self, colours: dict[str, str] | None = None) -> None:
        super().__init__()

        # Define logging colours
        self.colours: dict[str, str] = colours or {
            "black": "\x1b[30m",
            "red": "\x1b[31m",
            "green": "\x1b[32m",
            "yellow": "\x1b[33m",
            "blue": "\x1b[34m",
            "grey": "\x1b[38;5;240m",
            "purple": "\x1b[35m",
        }
        self.formats: dict[str, str] = {
            "reset": "\x1b[0m",
            "bold": "\x1b[1m",
            "italic": "\x1b[3m",
            "underline": "\x1b[4m",
            "strikethrough": "\x1b[9m",
        }
        self.log_formats: dict[int, str] = {
            logging.DEBUG: self.colours["grey"],
            logging.INFO: self.colours["blue"],
            logging.WARNING: self.colours["yellow"],
            logging.ERROR: self.colours["red"],
            logging.CRITICAL: self.colours["red"],
        }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record with ANSI colour codes.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            The formatted log message with colour codes.
        """
        # Fetch the colour for the log level
        log_color = self.log_formats.get(record.levelno, self.formats["reset"])

        # Format the log message
        # YYYY-MM-DD HH:MM:SS [LEVEL] logger_name: message
        formatter = logging.Formatter(
            (
                f"{self.colours['grey']}{self.formats['bold']}{{asctime}} {self.formats['reset']}"
                f"{log_color}{self.formats['bold']}{{levelname:<8}}{self.formats['reset']} "
                f"{self.colours['purple']}{{name}}{self.formats['reset']} "
                f"{{message}}{self.formats['reset']}"
            ),
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )
        return formatter.format(record)

    @staticmethod
    def start_logging(log_name: str = "discord_bot", log_level: str = "INFO", log_path: str | None = None) -> logging.Logger:
        """
        Sets up logging with a console handler and a file handler.

        Parameters
        ----------
        log_name : str, optional
            The name of the logger instance. Defaults to 'discord_bot'.
        log_level : str, optional
            The logging level as a string (e.g., 'DEBUG', 'INFO'). If None, it defaults 'INFO' if not set.
        log_path : str, optional
            The directory path where the log file will be stored. Defaults to the current working directory.
        Returns
        -------
        logging.Logger
            The configured logger instance.
        """

        log_level = os.getenv("LOG_LEVEL", log_level).upper()
        logger = logging.getLogger(log_name)
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LoggingFormatter())

        # File handler
        if log_path is None:
            log_path = os.getcwd()
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        log_file = os.path.join(log_path, f"{log_name}.log")
        file_handler = logging.FileHandler(filename=log_file, encoding="utf-8", mode="w")
        file_handler_formatter = logging.Formatter("[{asctime}] [{levelname:^8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
        file_handler.setFormatter(file_handler_formatter)

        # Add the handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
