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

from utils.database import Database  # pylint: disable=import-error,no-name-in-module


@dataclass
class Match:  # pylint: disable=too-many-instance-attributes
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
            winning_team=row["winning_team"] if row["winning_team"] else None,
            match_accepted=bool(row.get("match_accepted", 0)),
            match_cancelled=bool(row.get("match_cancelled", 0)),
        )

    def save(self, db: Database) -> int:
        """
        Save the match to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The match ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new match
            match_id = db.insert(
                "matches",
                {
                    "league_id": self.league_id,
                    "challenging_team": self.challenging_team,
                    "defending_team": self.defending_team,
                    "issued_date": self.issued_date,
                    "issued_by": self.issued_by,
                    "match_date": self.match_date,
                    "match_accepted": int(self.match_accepted),
                    "match_cancelled": int(self.match_cancelled),
                },
            )
            if match_id:
                object.__setattr__(self, "id", match_id)
                return match_id
            raise ValueError("Failed to insert match")
        # Update existing match
        db.update(
            "matches",
            {
                "league_id": self.league_id,
                "challenging_team": self.challenging_team,
                "defending_team": self.defending_team,
                "match_date": self.match_date,
                "winning_team": self.winning_team,
                "match_accepted": int(self.match_accepted),
                "match_cancelled": int(self.match_cancelled),
            },
            "id = ?",
            (self.id,),
        )
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the match from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("matches", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, match_id: int) -> Optional["Match"]:
        """
        Retrieve a match by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        match_id : int
            Match ID to retrieve.

        Returns
        -------
        Match, optional
            Match instance if found, None otherwise.
        """
        row = db.select_one("matches", where="id = ?", parameters=(match_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_league(cls, db: Database, league_id: int) -> list["Match"]:
        """
        Retrieve all matches in a league.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        league_id : int
            League ID to filter by.

        Returns
        -------
        list[Match]
            List of matches in the league.
        """
        rows = db.select("matches", where="league_id = ?", parameters=(league_id,), order_by="match_date DESC")
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_team(cls, db: Database, team_id: int) -> list["Match"]:
        """
        Retrieve all matches for a team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID to filter by.

        Returns
        -------
        list[Match]
            List of matches for the team.
        """
        rows = db.select(
            "matches",
            where="challenging_team = ? OR defending_team = ?",
            parameters=(team_id, team_id),
            order_by="match_date DESC",
        )
        return [cls.from_row(row) for row in rows]


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

    def save(self, db: Database) -> None:
        """
        Save the match result to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        # Check if already exists
        existing = db.select_one("match_results", where="match_id = ? AND round = ?", parameters=(self.match_id, self.round))
        if not existing:
            db.insert(
                "match_results",
                {
                    "match_id": self.match_id,
                    "round": self.round,
                    "map_id": self.map_id,
                    "challenging_team_score": self.challenging_team_score,
                    "defending_team_score": self.defending_team_score,
                    "winning_team": self.winning_team,
                },
            )
        else:
            db.update(
                "match_results",
                {
                    "map_id": self.map_id,
                    "challenging_team_score": self.challenging_team_score,
                    "defending_team_score": self.defending_team_score,
                    "winning_team": self.winning_team,
                },
                "match_id = ? AND round = ?",
                (self.match_id, self.round),
            )

    def delete(self, db: Database) -> int:
        """
        Delete the match result from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("match_results", "match_id = ? AND round = ?", (self.match_id, self.round))

    @classmethod
    def get_by_match(cls, db: Database, match_id: int) -> list["MatchResult"]:
        """
        Retrieve all results for a match.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        match_id : int
            Match ID to filter by.

        Returns
        -------
        list[MatchResult]
            List of match results ordered by round.
        """
        rows = db.select("match_results", where="match_id = ?", parameters=(match_id,), order_by="round")
        return [cls.from_row(row) for row in rows]
