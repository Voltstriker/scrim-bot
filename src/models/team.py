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

"""Team-related data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from utils.database import Database  # pylint: disable=import-error,no-name-in-module


@dataclass
class Team:
    """
    Represents a competitive team.

    Attributes
    ----------
    id : int
        Unique team identifier.
    name : str
        Team name.
    tag : str
        Team tag/shorthand name.
    owner_id : int
        Foreign key to the user who is team owner.
    created_at : datetime
        When the team was created.
    created_by : int
        Foreign key to the user who created the team.
    discord_server : str
        Discord server ID where the team is registered.
    """

    id: int
    name: str
    tag: str
    owner_id: int
    created_at: datetime
    created_by: int
    discord_server: str

    @classmethod
    def from_row(cls, row) -> "Team":
        """
        Create a Team instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing team data.

        Returns
        -------
        Team
            Team model instance.
        """
        return cls(
            id=row["id"],
            name=row["name"],
            tag=row["tag"],
            owner_id=row["owner_id"],
            created_at=row["created_at"],
            created_by=row["created_by"],
            discord_server=row["discord_server"],
        )

    def save(self, db: Database) -> int:
        """
        Save the team to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The team ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new team
            team_id = db.insert(
                "teams",
                {
                    "name": self.name,
                    "tag": self.tag,
                    "owner_id": self.owner_id,
                    "created_at": self.created_at,
                    "created_by": self.created_by,
                    "discord_server": self.discord_server,
                },
            )
            if team_id:
                object.__setattr__(self, "id", team_id)
                return team_id
            raise ValueError("Failed to insert team")
        # Update existing team
        db.update(
            "teams",
            {"name": self.name, "tag": self.tag, "owner_id": self.owner_id, "discord_server": self.discord_server},
            "id = ?",
            (self.id,),
        )
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the team from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("teams", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, team_id: int) -> Optional["Team"]:
        """
        Retrieve a team by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID to retrieve.

        Returns
        -------
        Team, optional
            Team instance if found, None otherwise.
        """
        row = db.select_one("teams", where="id = ?", parameters=(team_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_server(cls, db: Database, discord_server: str) -> list["Team"]:
        """
        Retrieve all teams in a Discord server.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        discord_server : str
            Discord server ID.

        Returns
        -------
        list[Team]
            List of teams in the server.
        """
        rows = db.select("teams", where="discord_server = ?", parameters=(discord_server,), order_by="name")
        return [cls.from_row(row) for row in rows]


@dataclass
class TeamMembership:
    """
    Represents a user's membership in a team.

    Attributes
    ----------
    user_id : int
        Foreign key to the user.
    team_id : int
        Foreign key to the team.
    captain : bool
        Whether the user is a team captain.
    joined_date : datetime
        When the user joined the team.
    updated_date : datetime, optional
        When the membership was last updated.
    """

    user_id: int
    team_id: int
    captain: bool
    joined_date: datetime
    updated_date: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> "TeamMembership":
        """
        Create a TeamMembership instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing team membership data.

        Returns
        -------
        TeamMembership
            TeamMembership model instance.
        """
        return cls(
            user_id=row["user_id"],
            team_id=row["team_id"],
            captain=bool(row["captain"]),
            joined_date=row["joined_date"],
            updated_date=row["updated_date"] if row["updated_date"] else None,
        )

    def save(self, db: Database) -> None:
        """
        Save the team membership to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        # Check if already exists
        existing = db.select_one("team_membership", where="user_id = ? AND team_id = ?", parameters=(self.user_id, self.team_id))
        if not existing:
            db.insert(
                "team_membership",
                {
                    "user_id": self.user_id,
                    "team_id": self.team_id,
                    "captain": int(self.captain),
                    "joined_date": self.joined_date,
                },
            )
        else:
            db.update(
                "team_membership",
                {"captain": int(self.captain), "updated_date": self.updated_date},
                "user_id = ? AND team_id = ?",
                (self.user_id, self.team_id),
            )

    def delete(self, db: Database) -> int:
        """
        Delete the team membership from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("team_membership", "user_id = ? AND team_id = ?", (self.user_id, self.team_id))

    @classmethod
    def get_by_team(cls, db: Database, team_id: int) -> list["TeamMembership"]:
        """
        Retrieve all memberships for a team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID to filter by.

        Returns
        -------
        list[TeamMembership]
            List of team memberships.
        """
        rows = db.select("team_membership", where="team_id = ?", parameters=(team_id,))
        memberships = [cls.from_row(row) for row in rows]
        memberships.sort(key=lambda m: m.joined_date)
        return memberships

    @classmethod
    def get_by_user(cls, db: Database, user_id: int) -> list["TeamMembership"]:
        """
        Retrieve all team memberships for a user.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        user_id : int
            User ID to filter by.

        Returns
        -------
        list[TeamMembership]
            List of team memberships.
        """
        rows = db.select("team_membership", where="user_id = ?", parameters=(user_id,))
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_user_and_team(cls, db: Database, user_id: int, team_id: int) -> Optional["TeamMembership"]:
        """
        Retrieve a specific team membership for a user and team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        user_id : int
            User ID to filter by.
        team_id : int
            Team ID to filter by.

        Returns
        -------
        TeamMembership, optional
            Team membership if found, None otherwise.
        """
        row = db.select_one("team_membership", where="user_id = ? AND team_id = ?", parameters=(user_id, team_id))
        return cls.from_row(row) if row else None
