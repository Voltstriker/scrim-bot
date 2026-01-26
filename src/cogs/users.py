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

"""
User management commands for the Discord bot.

This module defines the UserManagement cog, which provides commands for
viewing and searching users in the database.

Classes
-------
UserManagement
    A collection of user management commands for the Discord bot.

Functions
---------
setup(bot)
    Loads the UserManagement cog into the bot.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands import Context

from models import User, Team, TeamMembership  # pylint: disable=import-error

if TYPE_CHECKING:
    from utils.discord_bot import DiscordBot  # pylint: disable=import-error,no-name-in-module


class UserManagement(commands.Cog, name="User Management"):
    """
    A collection of user management commands for the Discord bot.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the UserManagement cog.
    users_list(context)
        Lists all users in the database.
    users_search(context, user)
        Searches for a user by Discord tag.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the UserManagement cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    ################################################
    # User Management Commands
    ################################################
    @commands.hybrid_group(name="users", description="Manage users in the database")
    async def users(self, context: Context) -> None:
        """
        Command group for managing users.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        if context.invoked_subcommand is None:
            await context.send("Please specify a subcommand: list or search.")

    @users.command(name="list", description="List all users in the database")
    async def users_list(self, context: Context) -> None:
        """
        List all users in the database with their team memberships.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        await context.defer()
        try:
            users = User.get_all(self.bot.database)

            if not users:
                await context.send("No users found in the database.")
                return

            # Create embed with user list
            embed = discord.Embed(
                title="👥 Users Database",
                description=f"Found {len(users)} user(s) in the database.",
                colour=discord.Colour.blue(),
            )

            # Add users as fields (max 25 fields per embed)
            for user in users[:25]:
                # Get teams for this user
                memberships = TeamMembership.get_by_user(self.bot.database, user.id)
                team_names = []
                for membership in memberships:
                    team = Team.get_by_id(self.bot.database, membership.team_id)
                    if team:
                        team_names.append(team.name)

                teams_text = ", ".join(team_names) if team_names else "No teams"
                display_text = user.display_name if user.display_name else "No display name"

                embed.add_field(
                    name=f"{display_text}",
                    value=f"ID: {user.id} | Discord ID: {user.discord_id}\nTeams: {teams_text}",
                    inline=False,
                )

            if len(users) > 25:
                embed.set_footer(text=f"Showing first 25 of {len(users)} users")
            else:
                embed.set_footer(text=f"Requested by {context.author.name}")

            await context.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.bot.logger.error("Error listing users: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while listing users: {e}")

    @users.command(name="search", description="Search for a user by Discord tag")
    async def users_search(self, context: Context, user: discord.User) -> None:
        """
        Search for a user in the database by Discord user tag.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        user : discord.User
            The Discord user to search for.
        """
        await context.defer()
        try:
            # Search for user by Discord ID
            db_user = User.get_by_discord_id(self.bot.database, str(user.id))

            if not db_user:
                await context.send(f"❌ User {user.mention} not found in the database.")
                return

            # Get teams for this user
            memberships = TeamMembership.get_by_user(self.bot.database, db_user.id)
            team_names = []
            for membership in memberships:
                team = Team.get_by_id(self.bot.database, membership.team_id)
                if team:
                    team_names.append(team.name)

            teams_text = ", ".join(team_names) if team_names else "No teams"

            # Create success embed
            embed = discord.Embed(
                title="🔍 User Found",
                description="Found user in the database.",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="Database ID", value=str(db_user.id), inline=True)
            embed.add_field(name="Discord ID", value=db_user.discord_id, inline=True)
            embed.add_field(name="Display Name", value=db_user.display_name if db_user.display_name else "None", inline=True)
            embed.add_field(name="Teams", value=teams_text, inline=False)
            embed.add_field(name="Created Date", value=db_user.created_date.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
            embed.set_footer(text=f"Searched by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error searching for user: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while searching for the user: {e}")


async def setup(bot: DiscordBot) -> None:
    """
    Loads the UserManagement cog into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(UserManagement(bot))
