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

"""Match-related data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Match:
    """
    Represents a match between two teams.

    Attributes
    ----------
    id : int
        Unique match identifier.
    league_id : int
        Foreign key to the league.
    challenging_team : int
        Foreign key to the team issuing the challenge.
    defending_team : int
        Foreign key to the team being challenged.
    issued_date : datetime
        When the match was issued.
    issued_by : int
        Foreign key to the user who issued the match.
    match_date : datetime
        Scheduled date/time for the match.
    winning_team : int, optional
        Foreign key to the team that won the match.
    match_accepted : bool
        Whether the match has been accepted by the defending team.
    match_cancelled : bool
        Whether the match was cancelled.
    """

    id: int
    league_id: int
    challenging_team: int
    defending_team: int
    issued_date: datetime
    issued_by: int
    match_date: datetime
    winning_team: Optional[int] = None
    match_accepted: bool = False
    match_cancelled: bool = False

    @classmethod
    def from_row(cls, row) -> "Match":
        """
        Create a Match instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing match data.

        Returns
        -------
        Match
            Match model instance.
        """
        return cls(
            id=row["id"],
            league_id=row["league_id"],
            challenging_team=row["challenging_team"],
            defending_team=row["defending_team"],
            issued_date=row["issued_date"],
            issued_by=row["issued_by"],
            match_date=row["match_date"],
            winning_team=row.get("winning_team"),
            match_accepted=bool(row.get("match_accepted", 0)),
            match_cancelled=bool(row.get("match_cancelled", 0)),
        )


@dataclass
class MatchResult:
    """
    Represents the result of a single round in a match.

    Attributes
    ----------
    match_id : int
        Foreign key to the match.
    round : int
        Round number.
    map_id : int
        Foreign key to the map played.
    challenging_team_score : int
        Score for the challenging team.
    defending_team_score : int
        Score for the defending team.
    winning_team : int
        Foreign key to the team that won this round.
    """

    match_id: int
    round: int
    map_id: int
    challenging_team_score: int
    defending_team_score: int
    winning_team: int

    @classmethod
    def from_row(cls, row) -> "MatchResult":
        """
        Create a MatchResult instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing match result data.

        Returns
        -------
        MatchResult
            MatchResult model instance.
        """
        return cls(
            match_id=row["match_id"],
            round=row["round"],
            map_id=row["map_id"],
            challenging_team_score=row["challenging_team_score"],
            defending_team_score=row["defending_team_score"],
            winning_team=row["winning_team"],
        )
