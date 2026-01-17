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
        return cls(user_id=row["user_id"], team_id=row["team_id"], joined_date=row["joined_date"], updated_date=row.get("updated_date"))


@dataclass
class TeamPermissionsUser:
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
            updated_date=row.get("updated_date"),
            updated_by=row.get("updated_by"),
        )


@dataclass
class TeamPermissionsRole:
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
            updated_date=row.get("updated_date"),
            updated_by=row.get("updated_by"),
        )
