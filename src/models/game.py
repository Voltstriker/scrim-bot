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

from ..utils.database import Database


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
        return cls(id=row["id"], name=row["name"], series=row["series"] if row["series"] else None)

    def save(self, db: Database) -> int:
        """
        Save the game to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The game ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new game
            game_id = db.insert("games", {"name": self.name, "series": self.series})
            if game_id:
                object.__setattr__(self, "id", game_id)
                return game_id
            raise ValueError("Failed to insert game")
        # Update existing game
        db.update("games", {"name": self.name, "series": self.series}, "id = ?", (self.id,))
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the game from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("games", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, game_id: int) -> Optional["Game"]:
        """
        Retrieve a game by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        game_id : int
            Game ID to retrieve.

        Returns
        -------
        Game, optional
            Game instance if found, None otherwise.
        """
        row = db.select_one("games", where="id = ?", parameters=(game_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_all(cls, db: Database) -> list["Game"]:
        """
        Retrieve all games.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        list[Game]
            List of all games.
        """
        rows = db.select("games", order_by="name")
        return [cls.from_row(row) for row in rows]


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

    def save(self, db: Database) -> int:
        """
        Save the map to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The map ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new map
            map_id = db.insert("maps", {"name": self.name, "mode": self.mode, "game_id": self.game_id})
            if map_id:
                object.__setattr__(self, "id", map_id)
                return map_id
            raise ValueError("Failed to insert map")
        # Update existing map
        db.update("maps", {"name": self.name, "mode": self.mode, "game_id": self.game_id}, "id = ?", (self.id,))
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the map from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("maps", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, map_id: int) -> Optional["Map"]:
        """
        Retrieve a map by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        map_id : int
            Map ID to retrieve.

        Returns
        -------
        Map, optional
            Map instance if found, None otherwise.
        """
        row = db.select_one("maps", where="id = ?", parameters=(map_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_game(cls, db: Database, game_id: int) -> list["Map"]:
        """
        Retrieve all maps for a game.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        game_id : int
            Game ID to filter by.

        Returns
        -------
        list[Map]
            List of maps for the game.
        """
        rows = db.select("maps", where="game_id = ?", parameters=(game_id,), order_by="name")
        return [cls.from_row(row) for row in rows]


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
    """

    id: int
    max_players: int
    match_count: int

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
        return cls(id=row["id"], max_players=row["max_players"], match_count=row["match_count"])

    def save(self, db: Database) -> int:
        """
        Save the match format to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            The match format ID.

        Raises
        ------
        ValueError
            If insert operation fails.
        """
        if self.id == 0:
            # Insert new match format
            format_id = db.insert("match_formats", {"max_players": self.max_players, "match_count": self.match_count})
            if format_id:
                object.__setattr__(self, "id", format_id)
                return format_id
            raise ValueError("Failed to insert match format")
        # Update existing match format
        db.update("match_formats", {"max_players": self.max_players, "match_count": self.match_count}, "id = ?", (self.id,))
        return self.id

    def delete(self, db: Database) -> int:
        """
        Delete the match format from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("match_formats", "id = ?", (self.id,))

    @classmethod
    def get_by_id(cls, db: Database, format_id: int) -> Optional["MatchFormat"]:
        """
        Retrieve a match format by ID.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        format_id : int
            Match format ID to retrieve.

        Returns
        -------
        MatchFormat, optional
            MatchFormat instance if found, None otherwise.
        """
        row = db.select_one("match_formats", where="id = ?", parameters=(format_id,))
        return cls.from_row(row) if row else None


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

    def save(self, db: Database) -> None:
        """
        Save the permitted map to the database (insert only, composite key).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        # Check if already exists
        existing = db.select_one(
            "permitted_maps",
            where="match_format_id = ? AND map_id = ?",
            parameters=(self.match_format_id, self.map_id),
        )
        if not existing:
            db.insert("permitted_maps", {"match_format_id": self.match_format_id, "map_id": self.map_id})

    def delete(self, db: Database) -> int:
        """
        Delete the permitted map from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("permitted_maps", "match_format_id = ? AND map_id = ?", (self.match_format_id, self.map_id))

    @classmethod
    def get_by_format(cls, db: Database, match_format_id: int) -> list["PermittedMap"]:
        """
        Retrieve all permitted maps for a match format.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        match_format_id : int
            Match format ID to filter by.

        Returns
        -------
        list[PermittedMap]
            List of permitted maps for the format.
        """
        rows = db.select("permitted_maps", where="match_format_id = ?", parameters=(match_format_id,))
        return [cls.from_row(row) for row in rows]
