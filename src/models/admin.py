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

"""Bot configuration data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from utils.database import Database  # pylint: disable=import-error,no-name-in-module


# pylint: disable=too-many-instance-attributes
@dataclass
class BotAdminConfig:
    """
    Represents a bot configuration entry in the database.

    This model stores bot administrator configurations, which can be scoped
    to either a specific Discord user or a Discord role within a server.

    Attributes
    ----------
    id : int
        Unique configuration identifier.
    discord_user_id : str, optional
        Discord user snowflake ID (for user-scoped configurations).
    discord_server_id : str, optional
        Discord server/guild snowflake ID (for role-scoped configurations).
    discord_role_id : str, optional
        Discord role snowflake ID (for role-scoped configurations).
    scope : str
        Configuration scope, either 'user' or 'role'.
    admin : bool
        Whether this configuration grants admin privileges.
    created_date : datetime
        When the admin configuration was created.
    created_by : int
        User ID who created this admin configuration.
    updated_date : datetime, optional
        When the admin configuration was last updated.
    updated_by : int, optional
        User ID who last updated this admin configuration.
    """

    id: int
    discord_user_id: Optional[str]
    discord_server_id: Optional[str]
    discord_role_id: Optional[str]
    scope: str
    admin: bool
    created_date: datetime
    created_by: int
    updated_date: Optional[datetime]
    updated_by: Optional[int]

    @classmethod
    def from_row(cls, row) -> "BotAdminConfig":
        """
        Create a BotAdminConfig instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing bot configuration data.

        Returns
        -------
        BotAdminConfig
            BotAdminConfig model instance.
        """
        return cls(
            id=row["id"],
            discord_user_id=row["discord_user_id"] if row["discord_user_id"] else None,
            discord_server_id=row["discord_server_id"] if row["discord_server_id"] else None,
            discord_role_id=row["discord_role_id"] if row["discord_role_id"] else None,
            scope=row["scope"],
            admin=bool(row["admin"]),
            created_date=row["created_date"],
            created_by=row["created_by"],
            updated_date=row["updated_date"] if row["updated_date"] else None,
            updated_by=row["updated_by"] if row["updated_by"] else None,
        )

    def save(self, db: Database) -> int:
        """
        Save the bot configuration to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The configuration ID.

        Raises
        ------
        ValueError
            If insert operation fails or if scope is invalid.
        """
        if self.scope not in ("user", "role"):
            raise ValueError(f"Invalid scope: {self.scope}. Must be 'user' or 'role'")

        if self.id == 0:
            # Insert new configuration
            config_id = db.insert(
                "admins",
                {
                    "discord_user_id": self.discord_user_id,
                    "discord_server_id": self.discord_server_id,
                    "discord_role_id": self.discord_role_id,
                    "scope": self.scope,
                    "admin": 1 if self.admin else 0,
                    "created_date": self.created_date,
                    "created_by": self.created_by,
                    "updated_date": self.updated_date,
                    "updated_by": self.updated_by,
                },
            )
            if config_id:
                object.__setattr__(self, "id", config_id)
                return config_id
            raise ValueError("Failed to insert bot configuration")
        # Update existing configuration
        db.update(
            "admins",
            {
                "discord_user_id": self.discord_user_id,
                "discord_server_id": self.discord_server_id,
                "discord_role_id": self.discord_role_id,
                "scope": self.scope,
                "admin": 1 if self.admin else 0,
                "updated_date": self.updated_date,
                "updated_by": self.updated_by,
            },
            "id = ?",
            (self.id,),
        )
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the bot configuration from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("admins", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, config_id: int) -> Optional["BotAdminConfig"]:
        """
        Retrieve a bot configuration by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        config_id : int
            Configuration ID to retrieve.

        Returns
        -------
        BotAdminConfig, optional
            BotAdminConfig instance if found, None otherwise.
        """
        row = db.select_one("admins", where="id = ?", parameters=(config_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_user_id(cls, db: Database, discord_user_id: str) -> Optional["BotAdminConfig"]:
        """
        Retrieve a bot configuration by Discord user ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        discord_user_id : str
            Discord user snowflake ID.

        Returns
        -------
        BotAdminConfig, optional
            BotAdminConfig instance if found, None otherwise.
        """
        row = db.select_one("admins", where="discord_user_id = ? AND scope = 'user'", parameters=(discord_user_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_server_and_role(cls, db: Database, discord_server_id: str, discord_role_id: str) -> Optional["BotAdminConfig"]:
        """
        Retrieve a bot configuration by server ID and role ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        discord_server_id : str
            Discord server/guild snowflake ID.
        discord_role_id : str
            Discord role snowflake ID.

        Returns
        -------
        BotAdminConfig, optional
            BotAdminConfig instance if found, None otherwise.
        """
        row = db.select_one(
            "admins",
            where="discord_server_id = ? AND discord_role_id = ? AND scope = 'role'",
            parameters=(discord_server_id, discord_role_id),
        )
        return cls.from_row(row) if row else None

    @classmethod
    def get_all(cls, db: Database) -> list["BotAdminConfig"]:
        """
        Retrieve all bot configurations.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        list[BotAdminConfig]
            List of all bot configurations, sorted by ID.
        """
        rows = db.select("admins", order_by="id")
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_all_admins(cls, db: Database) -> list["BotAdminConfig"]:
        """
        Retrieve all admin bot configurations.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        list[BotAdminConfig]
            List of all admin configurations, sorted by ID.
        """
        rows = db.select("admins", where="admin = 1", order_by="id")
        return [cls.from_row(row) for row in rows]
