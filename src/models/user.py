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

"""User data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..utils.database import Database


@dataclass
class User:
    """
    Represents a Discord user in the database.

    Attributes
    ----------
    id : int
        Unique user identifier.
    discord_id : str
        Discord snowflake ID.
    display_name : str, optional
        User's display name.
    created_date : datetime
        When the user was added to the database.
    """

    id: int
    discord_id: str
    display_name: Optional[str]
    created_date: datetime

    @classmethod
    def from_row(cls, row) -> "User":
        """
        Create a User instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing user data.

        Returns
        -------
        User
            User model instance.
        """
        return cls(id=row["id"], discord_id=row["discord_id"], display_name=row.get("display_name"), created_date=row["created_date"])

    def save(self, db: Database) -> int:
        """
        Save the user to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The user ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new user
            user_id = db.insert(
                "users",
                {"discord_id": self.discord_id, "display_name": self.display_name, "created_date": self.created_date},
            )
            if user_id:
                object.__setattr__(self, "id", user_id)
                return user_id
            raise ValueError("Failed to insert user")
        # Update existing user
        db.update(
            "users",
            {"discord_id": self.discord_id, "display_name": self.display_name},
            "id = ?",
            (self.id,),
        )
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the user from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("users", "id = ?", (self.id,))

    def refresh(self, db: Database) -> None:
        """
        Reload the user data from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        row = db.select_one("users", where="id = ?", parameters=(self.id,))
        if row:
            object.__setattr__(self, "discord_id", row["discord_id"])
            object.__setattr__(self, "display_name", row["display_name"] if row["display_name"] else None)
            object.__setattr__(self, "created_date", row["created_date"])

    @classmethod
    def get_by_id(cls, db: Database, user_id: int) -> Optional["User"]:
        """
        Retrieve a user by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        user_id : int
            User ID to retrieve.

        Returns
        -------
        User, optional
            User instance if found, None otherwise.
        """
        row = db.select_one("users", where="id = ?", parameters=(user_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_discord_id(cls, db: Database, discord_id: str) -> Optional["User"]:
        """
        Retrieve a user by Discord ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        discord_id : str
            Discord snowflake ID.

        Returns
        -------
        User, optional
            User instance if found, None otherwise.
        """
        row = db.select_one("users", where="discord_id = ?", parameters=(discord_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_all(cls, db: Database) -> list["User"]:
        """
        Retrieve all users.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        list[User]
            List of all users.
        """
        rows = db.select("users", order_by="created_date DESC")
        return [cls.from_row(row) for row in rows]
