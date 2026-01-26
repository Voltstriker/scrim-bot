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
import sqlite3
from datetime import datetime


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
        Sets up logging with a console handler and file handler.

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


def add_database_handler(logger: logging.Logger, database_path: str) -> None:
    """
    Add a database logging handler to an existing logger.

    This function should be called after the database schema has been initialised
    to avoid errors when trying to write to a non-existent logs table.

    Parameters
    ----------
    logger : logging.Logger
        The logger instance to add the database handler to.
    database_path : str
        Path to the SQLite database file where logs will be stored.
    """
    db_handler = DatabaseHandler(database_path)
    db_formatter = logging.Formatter("{message}", style="{")
    db_handler.setFormatter(db_formatter)
    logger.addHandler(db_handler)


class DatabaseHandler(logging.Handler):
    """
    Custom logging handler that writes log records to a SQLite database.

    This handler stores log messages in a database table for persistent
    logging and analysis.
    """

    def __init__(self, database_path: str) -> None:
        """
        Initialise the database logging handler.

        Parameters
        ----------
        database_path : str
            Path to the SQLite database file where logs will be stored.
        """
        super().__init__()
        self.database_path = database_path
        self.connection: sqlite3.Connection | None = None

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the database.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to write to the database.
        """
        # Skip database-related DEBUG logs to prevent recursion and lock contention
        if record.levelno == logging.DEBUG and ("database" in record.name.lower() or "Executed query" in record.getMessage()):
            return

        try:
            # Connect to database if not already connected
            if self.connection is None:
                # Set a 0.1 second timeout - if database is locked, skip the log entry
                self.connection = sqlite3.connect(self.database_path, timeout=0.1, check_same_thread=False)

            cursor = self.connection.cursor()

            # Insert log record into the logs table
            cursor.execute(
                """
                INSERT INTO logs (timestamp, level, logger_name, message, module, function, line_number)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),
                    record.levelname,
                    record.name,
                    self.format(record),
                    record.module,
                    record.funcName,
                    record.lineno,
                ),
            )

            self.connection.commit()
        except sqlite3.OperationalError:
            # Silently fail if database is locked - logging failures shouldn't break the application
            pass
        except Exception:
            # Silently fail to avoid recursion if logging the error causes another error
            self.handleError(record)

    def close(self) -> None:
        """
        Close the database connection when the handler is closed.
        """
        if self.connection:
            self.connection.close()
            self.connection = None
        super().close()
