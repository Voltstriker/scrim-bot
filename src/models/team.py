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
    captain_id : int
        Foreign key to the user who is team captain.
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
    captain_id: int
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
            captain_id=row["captain_id"],
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
                    "captain_id": self.captain_id,
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
            {"name": self.name, "tag": self.tag, "captain_id": self.captain_id, "discord_server": self.discord_server},
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
    joined_date : datetime
        When the user joined the team.
    updated_date : datetime, optional
        When the membership was last updated.
    """

    user_id: int
    team_id: int
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
            db.insert("team_membership", {"user_id": self.user_id, "team_id": self.team_id, "joined_date": self.joined_date})
        else:
            db.update("team_membership", {"updated_date": self.updated_date}, "user_id = ? AND team_id = ?", (self.user_id, self.team_id))

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
        rows = db.select("team_membership", where="team_id = ?", parameters=(team_id,), order_by="joined_date")
        return [cls.from_row(row) for row in rows]

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


@dataclass
class TeamPermissionsUser:  # pylint: disable=too-many-instance-attributes
    """
    Represents user-specific permissions for a team.

    Attributes
    ----------
    team_id : int
        Foreign key to the team.
    user_id : int
        Foreign key to the user.
    perm_edit_details : bool
        Permission to edit team details.
    perm_edit_members : bool
        Permission to manage team members.
    perm_join_leagues : bool
        Permission to join leagues.
    perm_issue_matches : bool
        Permission to issue match challenges.
    created_date : datetime
        When the permissions were created.
    created_by : int
        Foreign key to the user who created the permissions.
    updated_date : datetime, optional
        When the permissions were last updated.
    updated_by : int, optional
        Foreign key to the user who last updated the permissions.
    """

    team_id: int
    user_id: int
    perm_edit_details: bool
    perm_edit_members: bool
    perm_join_leagues: bool
    perm_issue_matches: bool
    created_date: datetime
    created_by: int
    updated_date: Optional[datetime] = None
    updated_by: Optional[int] = None

    @classmethod
    def from_row(cls, row) -> "TeamPermissionsUser":
        """
        Create a TeamPermissionsUser instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing team permissions data.

        Returns
        -------
        TeamPermissionsUser
            TeamPermissionsUser model instance.
        """
        return cls(
            team_id=row["team_id"],
            user_id=row["user_id"],
            perm_edit_details=bool(row["perm_edit_details"]),
            perm_edit_members=bool(row["perm_edit_members"]),
            perm_join_leagues=bool(row["perm_join_leagues"]),
            perm_issue_matches=bool(row["perm_issue_matches"]),
            created_date=row["created_date"],
            created_by=row["created_by"],
            updated_date=row["updated_date"] if row["updated_date"] else None,
            updated_by=row["updated_by"] if row["updated_by"] else None,
        )

    def save(self, db: Database) -> None:
        """
        Save the team permissions to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        # Check if already exists
        existing = db.select_one("team_permissions_users", where="team_id = ? AND user_id = ?", parameters=(self.team_id, self.user_id))
        if not existing:
            db.insert(
                "team_permissions_users",
                {
                    "team_id": self.team_id,
                    "user_id": self.user_id,
                    "perm_edit_details": int(self.perm_edit_details),
                    "perm_edit_members": int(self.perm_edit_members),
                    "perm_join_leagues": int(self.perm_join_leagues),
                    "perm_issue_matches": int(self.perm_issue_matches),
                    "created_date": self.created_date,
                    "created_by": self.created_by,
                },
            )
        else:
            db.update(
                "team_permissions_users",
                {
                    "perm_edit_details": int(self.perm_edit_details),
                    "perm_edit_members": int(self.perm_edit_members),
                    "perm_join_leagues": int(self.perm_join_leagues),
                    "perm_issue_matches": int(self.perm_issue_matches),
                    "updated_date": self.updated_date,
                    "updated_by": self.updated_by,
                },
                "team_id = ? AND user_id = ?",
                (self.team_id, self.user_id),
            )

    def delete(self, db: Database) -> int:
        """
        Delete the team permissions from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("team_permissions_users", "team_id = ? AND user_id = ?", (self.team_id, self.user_id))

    @classmethod
    def get_by_team(cls, db: Database, team_id: int) -> list["TeamPermissionsUser"]:
        """
        Retrieve all user permissions for a team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID to filter by.

        Returns
        -------
        list[TeamPermissionsUser]
            List of team permissions.
        """
        rows = db.select("team_permissions_users", where="team_id = ?", parameters=(team_id,))
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_user(cls, db: Database, team_id: int, user_id: int) -> Optional["TeamPermissionsUser"]:
        """
        Retrieve permissions for a specific user on a team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID.
        user_id : int
            User ID.

        Returns
        -------
        TeamPermissionsUser, optional
            Team permissions if found, None otherwise.
        """
        row = db.select_one("team_permissions_users", where="team_id = ? AND user_id = ?", parameters=(team_id, user_id))
        return cls.from_row(row) if row else None


@dataclass
class TeamPermissionsRole:  # pylint: disable=too-many-instance-attributes
    """
    Represents role-based permissions for a team.

    Attributes
    ----------
    team_id : int
        Foreign key to the team.
    role_id : str
        Discord role ID.
    perm_edit_details : bool
        Permission to edit team details.
    perm_edit_members : bool
        Permission to manage team members.
    perm_join_leagues : bool
        Permission to join leagues.
    perm_issue_matches : bool
        Permission to issue match challenges.
    created_date : datetime
        When the permissions were created.
    created_by : int
        Foreign key to the user who created the permissions.
    updated_date : datetime, optional
        When the permissions were last updated.
    updated_by : int, optional
        Foreign key to the user who last updated the permissions.
    """

    team_id: int
    role_id: str
    perm_edit_details: bool
    perm_edit_members: bool
    perm_join_leagues: bool
    perm_issue_matches: bool
    created_date: datetime
    created_by: int
    updated_date: Optional[datetime] = None
    updated_by: Optional[int] = None

    @classmethod
    def from_row(cls, row) -> "TeamPermissionsRole":
        """
        Create a TeamPermissionsRole instance from a database row.

        Parameters
        ----------
        row : sqlite3.Row
            Database row containing role permissions data.

        Returns
        -------
        TeamPermissionsRole
            TeamPermissionsRole model instance.
        """
        return cls(
            team_id=row["team_id"],
            role_id=row["role_id"],
            perm_edit_details=bool(row["perm_edit_details"]),
            perm_edit_members=bool(row["perm_edit_members"]),
            perm_join_leagues=bool(row["perm_join_leagues"]),
            perm_issue_matches=bool(row["perm_issue_matches"]),
            created_date=row["created_date"],
            created_by=row["created_by"],
            updated_date=row["updated_date"] if row["updated_date"] else None,
            updated_by=row["updated_by"] if row["updated_by"] else None,
        )

    def save(self, db: Database) -> None:
        """
        Save the role permissions to the database (insert or update).

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        """
        # Check if already exists
        existing = db.select_one("team_permissions_roles", where="team_id = ? AND role_id = ?", parameters=(self.team_id, self.role_id))
        if not existing:
            db.insert(
                "team_permissions_roles",
                {
                    "team_id": self.team_id,
                    "role_id": self.role_id,
                    "perm_edit_details": int(self.perm_edit_details),
                    "perm_edit_members": int(self.perm_edit_members),
                    "perm_join_leagues": int(self.perm_join_leagues),
                    "perm_issue_matches": int(self.perm_issue_matches),
                    "created_date": self.created_date,
                    "created_by": self.created_by,
                },
            )
        else:
            db.update(
                "team_permissions_roles",
                {
                    "perm_edit_details": int(self.perm_edit_details),
                    "perm_edit_members": int(self.perm_edit_members),
                    "perm_join_leagues": int(self.perm_join_leagues),
                    "perm_issue_matches": int(self.perm_issue_matches),
                    "updated_date": self.updated_date,
                    "updated_by": self.updated_by,
                },
                "team_id = ? AND role_id = ?",
                (self.team_id, self.role_id),
            )

    def delete(self, db: Database) -> int:
        """
        Delete the role permissions from the database.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.

        Returns
        -------
        int
            Number of rows deleted.
        """
        return db.delete("team_permissions_roles", "team_id = ? AND role_id = ?", (self.team_id, self.role_id))

    @classmethod
    def get_by_team(cls, db: Database, team_id: int) -> list["TeamPermissionsRole"]:
        """
        Retrieve all role permissions for a team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID to filter by.

        Returns
        -------
        list[TeamPermissionsRole]
            List of role permissions.
        """
        rows = db.select("team_permissions_roles", where="team_id = ?", parameters=(team_id,))
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_role(cls, db: Database, team_id: int, role_id: str) -> Optional["TeamPermissionsRole"]:
        """
        Retrieve permissions for a specific role on a team.

        Parameters
        ----------
        db : Database
            Database instance to use for the operation.
        team_id : int
            Team ID.
        role_id : str
            Discord role ID.

        Returns
        -------
        TeamPermissionsRole, optional
            Role permissions if found, None otherwise.
        """
        row = db.select_one("team_permissions_roles", where="team_id = ? AND role_id = ?", parameters=(team_id, role_id))
        return cls.from_row(row) if row else None
