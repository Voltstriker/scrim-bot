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
Database utility for Discord Bot.

This module provides a database class for performing CRUD operations
on a local SQLite database.
"""

import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Any


class Database:
    """
    SQLite database manager for performing CRUD operations.

    This class provides a simple interface for interacting with a SQLite
    database, including creating tables, inserting, updating, deleting,
    and querying data.
    """

    def __init__(self, database_path: str | None = None, logger: logging.Logger | None = None) -> None:
        """
        Initialise the database connection.

        Args:
            database_path: Path to the SQLite database file. If None, uses
                          DATABASE_PATH environment variable.
            logger: Logger instance for logging operations. If None, uses
                   default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        db_path = database_path or os.getenv("DATABASE_PATH")

        if not db_path:
            raise ValueError("Database path must be provided either as parameter or in DATABASE_PATH environment variable")

        self.database_path: str = db_path

        # Ensure the directory exists
        db_file = Path(self.database_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

        self.logger.debug("Database initialised at: %s", self.database_path)

    @staticmethod
    def _validate_identifier(identifier: str, identifier_type: str = "identifier") -> str:
        """
        Validate and sanitize SQL identifiers (table names, column names).

        This method prevents SQL injection by ensuring identifiers only contain
        safe characters and are properly quoted.

        Args:
            identifier: The identifier to validate (table name, column name, etc.)
            identifier_type: Type of identifier for error messages (e.g., "table name")

        Returns:
            The validated and quoted identifier.

        Raises:
            ValueError: If the identifier contains invalid characters.
        """
        if not identifier:
            raise ValueError(f"Invalid {identifier_type}: identifier cannot be empty")

        # Allow alphanumeric, underscore, and spaces (will be quoted)
        # Reject anything that could be SQL injection
        if not re.match(r"^[a-zA-Z0-9_][a-zA-Z0-9_ ]*$", identifier):
            raise ValueError(f"Invalid {identifier_type} '{identifier}': must contain only " f"alphanumeric characters, underscores, and spaces")

        # Check for reasonable length (SQLite limit is 1024 bytes for identifiers)
        if len(identifier) > 128:
            raise ValueError(f"Invalid {identifier_type}: identifier too long (max 128 characters)")

        # Quote the identifier to prevent injection and allow spaces
        # Use double quotes as per SQLite standard for identifiers
        return f'"{identifier}"'

    @staticmethod
    def _validate_order_by(order_by: str) -> str:
        """
        Validate ORDER BY clause to prevent SQL injection.

        Args:
            order_by: The ORDER BY clause to validate.

        Returns:
            The validated ORDER BY clause.

        Raises:
            ValueError: If the clause contains suspicious content.
        """
        # Allow only safe characters: alphanumeric, underscore, comma, space, ASC, DESC
        if not re.match(r"^[a-zA-Z0-9_,\s]+$", order_by):
            raise ValueError(f"Invalid ORDER BY clause '{order_by}': must contain only " f"column names, commas, spaces, and ASC/DESC")

        # Check for SQL keywords that shouldn't be in ORDER BY
        dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "CREATE", "ALTER", "EXEC", "--", "/*", ";"]
        order_by_upper = order_by.upper()
        for keyword in dangerous_keywords:
            if keyword in order_by_upper:
                raise ValueError(f"Invalid ORDER BY clause: contains forbidden keyword '{keyword}'")

        return order_by

    def connect(self) -> None:
        """
        Establish connection to the database.

        This method creates a connection to the SQLite database and sets up
        a cursor for executing queries.
        """
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.cursor = self.connection.cursor()
            self.logger.debug("Connected to database: %s", self.database_path)
        except sqlite3.Error as ex:
            self.logger.error("Failed to connect to database: %s", ex)
            raise

    def disconnect(self) -> None:
        """
        Close the database connection.

        This method commits any pending transactions and closes the database
        connection.
        """
        if self.connection:
            try:
                self.connection.commit()
                self.connection.close()
                self.connection = None
                self.cursor = None
                self.logger.debug("Disconnected from database")
            except sqlite3.Error as ex:
                self.logger.error("Error disconnecting from database: %s", ex)
                raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def execute(self, query: str, parameters: tuple | dict | None = None) -> sqlite3.Cursor | None:
        """
        Execute a SQL query.

        Args:
            query: SQL query string to execute.
            parameters: Parameters to substitute in the query. Can be a tuple
                       for positional parameters or dict for named parameters.

        Returns:
            Cursor object with query results, or None if connection not established.
        """
        if not self.cursor:
            self.logger.error("Database cursor not available. Call connect() first.")
            return None

        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            self.logger.debug("Executed query: %s", query)
            return self.cursor
        except sqlite3.Error as ex:
            self.logger.error("Error executing query: %s", ex)
            self.logger.error("Query: %s", query)
            raise

    def commit(self) -> None:
        """
        Commit the current transaction.

        This method saves all changes made since the last commit.
        """
        if self.connection:
            try:
                self.connection.commit()
                self.logger.debug("Transaction committed")
            except sqlite3.Error as ex:
                self.logger.error("Error committing transaction: %s", ex)
                raise

    def rollback(self) -> None:
        """
        Roll back the current transaction.

        This method discards all changes made since the last commit.
        """
        if self.connection:
            try:
                self.connection.rollback()
                self.logger.debug("Transaction rolled back")
            except sqlite3.Error as ex:
                self.logger.error("Error rolling back transaction: %s", ex)
                raise

    def create_table(self, table_name: str, columns: dict[str, str], if_not_exists: bool = True) -> None:
        """
        Create a new table in the database.

        Args:
            table_name: Name of the table to create.
            columns: Dictionary mapping column names to their SQL type definitions.
                    Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL"}
            if_not_exists: If True, only creates table if it doesn't exist.
        """
        # Validate table name
        validated_table = self._validate_identifier(table_name, "table name")

        # Validate column names and build column definitions
        validated_columns = []
        for col, dtype in columns.items():
            validated_col = self._validate_identifier(col, "column name")
            validated_columns.append(f"{validated_col} {dtype}")

        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        column_definitions = ", ".join(validated_columns)
        query = f"CREATE TABLE {if_not_exists_clause}{validated_table} ({column_definitions})"

        self.execute(query)
        self.commit()
        self.logger.info("Table '%s' created successfully", table_name)

    def insert(self, table_name: str, data: dict[str, Any]) -> int | None:
        """
        Insert a new row into the table.

        Args:
            table_name: Name of the table to insert into.
            data: Dictionary mapping column names to values.

        Returns:
            The row ID of the newly inserted row, or None if insert failed.
        """
        # Validate table name and column names
        validated_table = self._validate_identifier(table_name, "table name")
        validated_columns = [self._validate_identifier(col, "column name") for col in data.keys()]

        columns = ", ".join(validated_columns)
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {validated_table} ({columns}) VALUES ({placeholders})"

        self.execute(query, tuple(data.values()))
        self.commit()

        last_row_id = self.cursor.lastrowid if self.cursor else None
        self.logger.debug("Inserted row with ID %s into '%s'", last_row_id, table_name)
        return last_row_id

    def insert_many(self, table_name: str, data_list: list[dict[str, Any]]) -> None:
        """
        Insert multiple rows into the table.

        Args:
            table_name: Name of the table to insert into.
            data_list: List of dictionaries, each mapping column names to values.
        """
        if not data_list:
            self.logger.warning("No data provided for insert_many operation")
            return

        # Validate table name and column names
        validated_table = self._validate_identifier(table_name, "table name")
        validated_columns = [self._validate_identifier(col, "column name") for col in data_list[0].keys()]

        columns = ", ".join(validated_columns)
        placeholders = ", ".join(["?" for _ in data_list[0]])
        query = f"INSERT INTO {validated_table} ({columns}) VALUES ({placeholders})"

        if self.cursor:
            try:
                self.cursor.executemany(query, [tuple(data.values()) for data in data_list])
                self.commit()
                self.logger.debug("Inserted %s rows into '%s'", len(data_list), table_name)
            except sqlite3.Error as ex:
                self.logger.error("Error inserting multiple rows: %s", ex)
                raise

    def select(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        table_name: str,
        columns: list[str] | None = None,
        where: str | None = None,
        parameters: tuple | dict | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[sqlite3.Row]:
        """
        Select rows from the table.

        Args:
            table_name: Name of the table to select from.
            columns: List of column names to select. If None, selects all columns.
            where: WHERE clause (without the WHERE keyword). Example: "age > ?"
            parameters: Parameters to substitute in the WHERE clause.
            order_by: ORDER BY clause (without the ORDER BY keyword). Example: "name ASC"
            limit: Maximum number of rows to return.

        Returns:
            List of Row objects containing the query results.
        """
        # Validate table name
        validated_table = self._validate_identifier(table_name, "table name")

        # Validate column names if provided
        if columns:
            validated_columns = [self._validate_identifier(col, "column name") for col in columns]
            column_str = ", ".join(validated_columns)
        else:
            column_str = "*"

        query = f"SELECT {column_str} FROM {validated_table}"

        if where:
            query += f" WHERE {where}"
        if order_by:
            validated_order = self._validate_order_by(order_by)
            query += f" ORDER BY {validated_order}"
        if limit:
            query += f" LIMIT {limit}"

        cursor = self.execute(query, parameters)
        if cursor:
            results = cursor.fetchall()
            self.logger.debug("Selected %s rows from '%s'", len(results), table_name)
            return results
        return []

    def select_one(
        self,
        table_name: str,
        columns: list[str] | None = None,
        where: str | None = None,
        parameters: tuple | dict | None = None,
    ) -> sqlite3.Row | None:
        """
        Select a single row from the table.

        Args:
            table_name: Name of the table to select from.
            columns: List of column names to select. If None, selects all columns.
            where: WHERE clause (without the WHERE keyword).
            parameters: Parameters to substitute in the WHERE clause.

        Returns:
            Row object containing the query result, or None if no row found.
        """
        results = self.select(table_name, columns, where, parameters, limit=1)
        return results[0] if results else None

    def update(
        self,
        table_name: str,
        data: dict[str, Any],
        where: str,
        parameters: tuple | dict | None = None,
    ) -> int:
        """
        Update rows in the table.

        Args:
            table_name: Name of the table to update.
            data: Dictionary mapping column names to new values.
            where: WHERE clause (without the WHERE keyword) specifying which rows to update.
            parameters: Parameters to substitute in the WHERE clause.

        Returns:
            Number of rows affected by the update.
        """
        # Validate table name and column names
        validated_table = self._validate_identifier(table_name, "table name")
        validated_columns = [self._validate_identifier(col, "column name") for col in data.keys()]

        set_clause = ", ".join([f"{validated_col} = ?" for validated_col in validated_columns])
        query = f"UPDATE {validated_table} SET {set_clause} WHERE {where}"

        # Combine data values and where parameters
        if parameters:
            if isinstance(parameters, dict):
                all_params = {**data, **parameters}
            else:
                all_params = tuple(data.values()) + parameters
        else:
            all_params = tuple(data.values())

        cursor = self.execute(query, all_params)
        self.commit()

        rows_affected = cursor.rowcount if cursor else 0
        self.logger.debug("Updated %s rows in '%s'", rows_affected, table_name)
        return rows_affected

    def delete(
        self,
        table_name: str,
        where: str,
        parameters: tuple | dict | None = None,
    ) -> int:
        """
        Delete rows from the table.

        Args:
            table_name: Name of the table to delete from.
            where: WHERE clause (without the WHERE keyword) specifying which rows to delete.
            parameters: Parameters to substitute in the WHERE clause.

        Returns:
            Number of rows affected by the delete.
        """
        # Validate table name
        validated_table = self._validate_identifier(table_name, "table name")
        query = f"DELETE FROM {validated_table} WHERE {where}"

        cursor = self.execute(query, parameters)
        self.commit()

        rows_affected = cursor.rowcount if cursor else 0
        self.logger.debug("Deleted %s rows from '%s'", rows_affected, table_name)
        return rows_affected

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table to check.

        Returns:
            True if the table exists, False otherwise.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        cursor = self.execute(query, (table_name,))
        if cursor:
            result = cursor.fetchone()
            return result is not None
        return False

    def get_table_info(self, table_name: str) -> list[sqlite3.Row]:
        """
        Get information about a table's structure.

        Args:
            table_name: Name of the table to get information about.

        Returns:
            List of Row objects containing column information (cid, name, type, etc.).
        """
        # Validate table name
        validated_table = self._validate_identifier(table_name, "table name")
        query = f"PRAGMA table_info({validated_table})"
        cursor = self.execute(query)
        if cursor:
            return cursor.fetchall()
        return []

    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        """
        Drop (delete) a table from the database.

        Args:
            table_name: Name of the table to drop.
            if_exists: If True, only drops table if it exists (no error if it doesn't).
        """
        # Validate table name
        validated_table = self._validate_identifier(table_name, "table name")
        if_exists_clause = "IF EXISTS " if if_exists else ""
        query = f"DROP TABLE {if_exists_clause}{validated_table}"

        self.execute(query)
        self.commit()
        self.logger.info("Table '%s' dropped successfully", table_name)

    def drop_all_tables(self) -> int:
        """
        Drop all tables from the database (excluding SQLite system tables and logs table).

        This method retrieves all user-created tables and drops them, except for the
        logs table which is preserved to maintain logging functionality during the reset.
        System tables (those starting with 'sqlite_') are also preserved.

        Foreign key constraints are temporarily disabled during the operation to avoid
        constraint violation errors when dropping tables with dependencies.

        Returns:
            int: Number of tables dropped.
        """
        # Temporarily disable foreign key constraints to avoid issues with table dependencies
        self.execute("PRAGMA foreign_keys = OFF")
        self.commit()

        # Get list of all user tables (excluding logs table)
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'logs'"
        cursor = self.execute(tables_query)
        tables = []

        if cursor:
            tables = [row[0] for row in cursor.fetchall()]

            # Drop all tables
            for table_name in tables:
                self.drop_table(table_name, if_exists=True)

            self.logger.info("Dropped %d table(s)", len(tables))

        # Re-enable foreign key constraints
        self.execute("PRAGMA foreign_keys = ON")
        self.commit()

        return len(tables)

    def initialise_schema(self) -> None:
        """
        Initialise the database schema with all required tables.

        This function creates the necessary tables for the bot to function.
        It should only be called when the database is first created.
        """
        self.logger.info("Initialising database schema...")

        # Create logs table for database logging
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                function TEXT,
                line_number INTEGER
            )
            """
        )

        # Create games table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                series TEXT
            )
            """
        )

        # Create maps table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mode TEXT NOT NULL,
                experience_code TEXT,
                game_id INTEGER NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id)
            )
            """
        )

        # Create match_formats table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS match_formats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_players INTEGER NOT NULL,
                match_count INTEGER NOT NULL
            )
            """
        )

        # Create permitted_maps table (composite primary key)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS permitted_maps (
                match_format_id INTEGER,
                map_id INTEGER,
                PRIMARY KEY (match_format_id, map_id),
                FOREIGN KEY (match_format_id) REFERENCES match_formats(id),
                FOREIGN KEY (map_id) REFERENCES maps(id)
            )
            """
        )

        # Create users table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL,
                display_name TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create teams table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tag TEXT NOT NULL,
                captain_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                discord_server TEXT NOT NULL,
                FOREIGN KEY (captain_id) REFERENCES users(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
            """
        )

        # Create leagues table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS leagues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                game_id INTEGER NOT NULL,
                match_format INTEGER NOT NULL,
                discord_server TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                updated_date TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (game_id) REFERENCES games(id),
                FOREIGN KEY (match_format) REFERENCES match_formats(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id)
            )
            """
        )

        # Create team_membership table (composite primary key)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS team_membership (
                user_id INTEGER,
                team_id INTEGER,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP,
                PRIMARY KEY (user_id, team_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
            """
        )

        # Create team_permissions_users table (composite primary key)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS team_permissions_users (
                team_id INTEGER,
                user_id INTEGER,
                perm_edit_details INTEGER DEFAULT 0,
                perm_edit_members INTEGER DEFAULT 0,
                perm_join_leagues INTEGER DEFAULT 0,
                perm_issue_matches INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                updated_date TIMESTAMP,
                updated_by INTEGER,
                PRIMARY KEY (team_id, user_id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id)
            )
            """
        )

        # Create team_permissions_roles table (composite primary key)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS team_permissions_roles (
                team_id INTEGER,
                role_id TEXT NOT NULL,
                perm_edit_details INTEGER DEFAULT 0,
                perm_edit_members INTEGER DEFAULT 0,
                perm_join_leagues INTEGER DEFAULT 0,
                perm_issue_matches INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL,
                updated_date TIMESTAMP,
                updated_by INTEGER,
                PRIMARY KEY (team_id, role_id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (created_by) REFERENCES users(id),
                FOREIGN KEY (updated_by) REFERENCES users(id)
            )
            """
        )

        # Create league_membership table (composite primary key)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS league_membership (
                league_id INTEGER,
                team_id INTEGER,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                joined_by INTEGER NOT NULL,
                PRIMARY KEY (league_id, team_id),
                FOREIGN KEY (league_id) REFERENCES leagues(id),
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (joined_by) REFERENCES users(id)
            )
            """
        )

        # Create matches table
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_id INTEGER NOT NULL,
                challenging_team INTEGER NOT NULL,
                defending_team INTEGER NOT NULL,
                issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                issued_by INTEGER NOT NULL,
                match_date TIMESTAMP NOT NULL,
                winning_team INTEGER,
                match_accepted INTEGER DEFAULT 0,
                match_cancelled INTEGER DEFAULT 0,
                FOREIGN KEY (league_id) REFERENCES leagues(id),
                FOREIGN KEY (challenging_team) REFERENCES teams(id),
                FOREIGN KEY (defending_team) REFERENCES teams(id),
                FOREIGN KEY (winning_team) REFERENCES teams(id),
                FOREIGN KEY (issued_by) REFERENCES users(id)
            )
            """
        )

        # Create match_results table (composite primary key)
        self.execute(
            """
            CREATE TABLE IF NOT EXISTS match_results (
                match_id INTEGER,
                round INTEGER,
                map_id INTEGER NOT NULL,
                challenging_team_score INTEGER NOT NULL,
                defending_team_score INTEGER NOT NULL,
                winning_team INTEGER NOT NULL,
                PRIMARY KEY (match_id, round),
                FOREIGN KEY (match_id) REFERENCES matches(id),
                FOREIGN KEY (map_id) REFERENCES maps(id),
                FOREIGN KEY (winning_team) REFERENCES teams(id)
            )
            """
        )

        self.commit()
        self.logger.info("Database schema initialised successfully")
