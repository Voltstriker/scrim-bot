"""
Data models for database entities.

This module provides dataclass models that represent database tables,
offering type safety and convenient data access throughout the bot.
"""

from .game import Game, Map, MatchFormat, PermittedMap
from .league import League, LeagueMembership
from .match import Match, MatchResult
from .team import Team, TeamMembership
from .user import User

__all__ = [
    "Game",
    "Map",
    "MatchFormat",
    "PermittedMap",
    "League",
    "LeagueMembership",
    "Match",
    "MatchResult",
    "Team",
    "TeamMembership",
    "User",
]
