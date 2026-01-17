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

"""Game-related data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Game:
    """
    Represents a video game.

    Attributes
    ----------
    id : int
        Unique game identifier.
    name : str
        Game title.
    series : str, optional
        Game series/franchise name.
    """

    id: int
    name: str
    series: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Game":
        """
        Create a Game instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing game data.

        Returns
        -------
        Game
            Game model instance.
        """
        return cls(id=row["id"], name=row["name"], series=row.get("series"))


@dataclass
class Map:
    """
    Represents a game map.

    Attributes
    ----------
    id : int
        Unique map identifier.
    name : str
        Map name.
    mode : str
        Game mode for this map.
    game_id : int
        Foreign key to the game this map belongs to.
    """

    id: int
    name: str
    mode: str
    game_id: int

    @classmethod
    def from_row(cls, row) -> "Map":
        """
        Create a Map instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing map data.

        Returns
        -------
        Map
            Map model instance.
        """
        return cls(id=row["id"], name=row["name"], mode=row["mode"], game_id=row["game_id"])


@dataclass
class MatchFormat:
    """
    Represents a match format configuration.

    Attributes
    ----------
    id : int
        Unique match format identifier.
    max_players : int
        Maximum number of players per team.
    match_count : int
        Number of rounds/games in the match.
    map_list_id : int
        Reference to the map list configuration.
    """

    id: int
    max_players: int
    match_count: int
    map_list_id: int

    @classmethod
    def from_row(cls, row) -> "MatchFormat":
        """
        Create a MatchFormat instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing match format data.

        Returns
        -------
        MatchFormat
            MatchFormat model instance.
        """
        return cls(id=row["id"], max_players=row["max_players"], match_count=row["match_count"], map_list_id=row["map_list_id"])


@dataclass
class PermittedMap:
    """
    Represents a permitted map for a match format.

    Attributes
    ----------
    match_format_id : int
        Foreign key to the match format.
    map_id : int
        Foreign key to the map.
    """

    match_format_id: int
    map_id: int

    @classmethod
    def from_row(cls, row) -> "PermittedMap":
        """
        Create a PermittedMap instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing permitted map data.

        Returns
        -------
        PermittedMap
            PermittedMap model instance.
        """
        return cls(match_format_id=row["match_format_id"], map_id=row["map_id"])
