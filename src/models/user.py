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
