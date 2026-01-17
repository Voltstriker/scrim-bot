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


@dataclass
class League:
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
    discord_server : str
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
    discord_server: str
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
            discord_server=row["discord_server"],
            created_date=row["created_date"],
            created_by=row["created_by"],
            updated_date=row.get("updated_date"),
            updated_by=row.get("updated_by"),
        )


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
