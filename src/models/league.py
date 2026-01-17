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

"""League-related data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..utils.database import Database


@dataclass
class League:  # pylint: disable=too-many-instance-attributes
    """
    Represents a competition league.

    Attributes
    ----------
    id : int
        Unique league identifier.
    name : str
        League name.
    game_id : int
        Foreign key to the game being played.
    match_format : int
        Foreign key to the match format configuration.
    discord_server : str, optional
        Discord server ID where the league is hosted.
    created_date : datetime
        When the league was created.
    created_by : int
        Foreign key to the user who created the league.
    updated_date : datetime, optional
        When the league was last updated.
    updated_by : int, optional
        Foreign key to the user who last updated the league.
    """

    id: int
    name: str
    game_id: int
    match_format: int
    discord_server: Optional[str]
    created_date: datetime
    created_by: int
    updated_date: Optional[datetime] = None
    updated_by: Optional[int] = None

    @classmethod
    def from_row(cls, row) -> "League":
        """
        Create a League instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing league data.

        Returns
        -------
        League
            League model instance.
        """
        return cls(
            id=row["id"],
            name=row["name"],
            game_id=row["game_id"],
            match_format=row["match_format"],
            discord_server=row["discord_server"] if row["discord_server"] else None,
            created_date=row["created_date"],
            created_by=row["created_by"],
            updated_date=row["updated_date"] if row["updated_date"] else None,
            updated_by=row["updated_by"] if row["updated_by"] else None,
        )

    def save(self, db: Database) -> int:
        """
        Save the league to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The league ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new league
            league_id = db.insert(
                "leagues",
                {
                    "name": self.name,
                    "game_id": self.game_id,
                    "match_format": self.match_format,
                    "discord_server": self.discord_server,
                    "created_date": self.created_date,
                    "created_by": self.created_by,
                },
            )
            if league_id:
                object.__setattr__(self, "id", league_id)
                return league_id
            raise ValueError("Failed to insert league")
        # Update existing league
        db.update(
            "leagues",
            {
                "name": self.name,
                "game_id": self.game_id,
                "match_format": self.match_format,
                "discord_server": self.discord_server,
                "updated_date": self.updated_date,
                "updated_by": self.updated_by,
            },
            "id = ?",
            (self.id,),
        )
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the league from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("leagues", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, league_id: int) -> Optional["League"]:
        """
        Retrieve a league by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        league_id : int
            League ID to retrieve.

        Returns
        -------
        League, optional
            League instance if found, None otherwise.
        """
        row = db.select_one("leagues", where="id = ?", parameters=(league_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_server(cls, db: Database, discord_server: str) -> list["League"]:
        """
        Retrieve all leagues in a Discord server.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        discord_server : str
            Discord server ID.

        Returns
        -------
        list[League]
            List of leagues in the server.
        """
        rows = db.select("leagues", where="discord_server = ?", parameters=(discord_server,), order_by="name")
        return [cls.from_row(row) for row in rows]


@dataclass
class LeagueMembership:
    """
    Represents a team's membership in a league.

    Attributes
    ----------
    league_id : int
        Foreign key to the league.
    team_id : int
        Foreign key to the team.
    joined_date : datetime
        When the team joined the league.
    joined_by : int
        Foreign key to the user who added the team.
    """

    league_id: int
    team_id: int
    joined_date: datetime
    joined_by: int

    @classmethod
    def from_row(cls, row) -> "LeagueMembership":
        """
        Create a LeagueMembership instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing league membership data.

        Returns
        -------
        LeagueMembership
            LeagueMembership model instance.
        """
        return cls(league_id=row["league_id"], team_id=row["team_id"], joined_date=row["joined_date"], joined_by=row["joined_by"])

    def save(self, db: Database) -> None:
        """
        Save the league membership to the database (insert only, composite key).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        # Check if already exists
        existing = db.select_one("league_membership", where="league_id = ? AND team_id = ?", parameters=(self.league_id, self.team_id))
        if not existing:
            db.insert(
                "league_membership",
                {"league_id": self.league_id, "team_id": self.team_id, "joined_date": self.joined_date, "joined_by": self.joined_by},
            )

    def delete(self, db: Database) -> int:
        """
        Delete the league membership from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("league_membership", "league_id = ? AND team_id = ?", (self.league_id, self.team_id))

    @classmethod
    def get_by_league(cls, db: Database, league_id: int) -> list["LeagueMembership"]:
        """
        Retrieve all teams in a league.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        league_id : int
            League ID to filter by.

        Returns
        -------
        list[LeagueMembership]
            List of league memberships.
        """
        rows = db.select("league_membership", where="league_id = ?", parameters=(league_id,), order_by="joined_date")
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_team(cls, db: Database, team_id: int) -> list["LeagueMembership"]:
        """
        Retrieve all leagues a team is in.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID to filter by.

        Returns
        -------
        list[LeagueMembership]
            List of league memberships.
        """
        rows = db.select("league_membership", where="team_id = ?", parameters=(team_id,))
        return [cls.from_row(row) for row in rows]
