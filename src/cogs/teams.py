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
Team management commands for the Discord bot.

This module defines the Teams cog, which provides commands for
managing competitive teams, their members, and membership applications.

Classes
-------
Teams
    A collection of team management commands for the Discord bot.

Functions
---------
setup(bot)
    Loads the Teams cog into the bot.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands import Context

from models import BotAdminConfig, Team, User, TeamMembership, League, LeagueMembership  # pylint: disable=import-error

if TYPE_CHECKING:
    from utils.discord_bot import DiscordBot  # pylint: disable=import-error,no-name-in-module


async def is_owner_or_admin_or_captain(bot: DiscordBot, context: Context, team: Team, requester_user_id: int) -> bool:
    """
    Check if user is bot owner, admin, or team captain.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance.
    context : Context
        The command context.
    team : Team
        The team to check captaincy for.
    requester_user_id : int
        Database ID of the requesting user.

    Returns
    -------
    bool
        True if user is owner, admin, or captain.
    """
    # Check if user is team owner
    if team.owner_id == requester_user_id:
        return True

    # Check if user is bot owner
    if await context.bot.is_owner(context.author):
        return True

    # Check if user is in admins table
    admin_config = BotAdminConfig.get_by_user_id(bot.database, str(context.author.id))
    if admin_config and admin_config.admin:
        return True

    # Check if user has any admin roles (if in a guild)
    if context.guild and hasattr(context.author, "roles"):
        for role in context.author.roles:  # type: ignore[attr-defined]
            role_config = BotAdminConfig.get_by_server_and_role(bot.database, str(context.guild.id), str(role.id))
            if role_config and role_config.admin:
                return True

    return False


class TeamInviteView(discord.ui.View):
    """
    A view for accepting or declining team invitations.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance.
    team_id : int
        The ID of the team being invited to.
    invited_user_id : int
        The database ID of the invited user.
    channel_id : int
        The ID of the channel where the invitation was sent.
    """

    def __init__(self, bot: DiscordBot, team_id: int, invited_user_id: int, channel_id: int) -> None:
        """
        Initialise the team invite view.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance.
        team_id : int
            The ID of the team.
        invited_user_id : int
            The database ID of the invited user.
        channel_id : int
            The ID of the channel where the invitation was sent.
        """
        super().__init__(timeout=172800)  # 48 hour timeout - invitation expires after this period
        self.bot = bot
        self.team_id = team_id
        self.invited_user_id = invited_user_id
        self.channel_id = channel_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # pylint: disable=unused-argument
        """
        Handle the Accept button press.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this callback.
        button : discord.ui.Button
            The button that was pressed.
        """
        try:
            # Verify the user pressing the button is the invited user
            db_user = User.get_by_discord_id(self.bot.database, str(interaction.user.id))
            if not db_user or db_user.id != self.invited_user_id:
                await interaction.response.send_message("❌ This invitation is not for you.", ephemeral=True)
                return

            # Get team details
            team = Team.get_by_id(self.bot.database, self.team_id)
            if not team:
                await interaction.response.send_message("❌ Team no longer exists.", ephemeral=True)
                self.stop()
                return

            # Check if user is already a member
            existing_memberships = TeamMembership.get_by_team(self.bot.database, team.id)
            for membership in existing_memberships:
                if membership.user_id == self.invited_user_id:
                    await interaction.response.send_message(f"❌ You are already a member of **{team.name}**.", ephemeral=True)
                    self.stop()
                    return

            # Add user to team
            membership = TeamMembership(user_id=self.invited_user_id, team_id=team.id, captain=False, joined_date=datetime.now(), updated_date=None)
            membership.save(self.bot.database)

            # Update the original message
            embed = discord.Embed(
                title="✅ Invitation Accepted",
                description=f"You have joined **{team.name}** [{team.tag}]!",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="Team ID", value=str(team.id), inline=True)

            await interaction.response.edit_message(embed=embed, view=None)

            # Send notification to the original channel
            try:
                channel = self.bot.get_channel(self.channel_id)
                if channel and isinstance(channel, discord.abc.Messageable):
                    notification_embed = discord.Embed(
                        title="✅ Invitation Accepted",
                        description=f"{interaction.user.mention} has accepted the invitation and joined **{team.name}** [{team.tag}]!",
                        colour=discord.Colour.green(),
                    )
                    await channel.send(embed=notification_embed)
            except Exception as channel_error:
                self.bot.logger.error("Error sending channel notification: %s", channel_error)

            self.stop()

        except Exception as e:
            self.bot.logger.error("Error accepting team invite: %s", e)
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # pylint: disable=unused-argument
        """
        Handle the Decline button press.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this callback.
        button : discord.ui.Button
            The button that was pressed.
        """
        try:
            # Verify the user pressing the button is the invited user
            db_user = User.get_by_discord_id(self.bot.database, str(interaction.user.id))
            if not db_user or db_user.id != self.invited_user_id:
                await interaction.response.send_message("❌ This invitation is not for you.", ephemeral=True)
                return

            # Get team details
            team = Team.get_by_id(self.bot.database, self.team_id)
            if not team:
                await interaction.response.send_message("❌ Team no longer exists.", ephemeral=True)
                self.stop()
                return

            # Update the original message
            embed = discord.Embed(
                title="❌ Invitation Declined",
                description=f"You have declined the invitation to join **{team.name}** [{team.tag}].",
                colour=discord.Colour.red(),
            )

            await interaction.response.edit_message(embed=embed, view=None)

            # Send notification to the original channel
            try:
                channel = self.bot.get_channel(self.channel_id)
                if channel and isinstance(channel, discord.abc.Messageable):
                    notification_embed = discord.Embed(
                        title="❌ Invitation Declined",
                        description=f"{interaction.user.mention} has declined the invitation to join **{team.name}** [{team.tag}].",
                        colour=discord.Colour.red(),
                    )
                    await channel.send(embed=notification_embed)
            except Exception as channel_error:
                self.bot.logger.error("Error sending channel notification: %s", channel_error)

            self.stop()

        except Exception as e:
            self.bot.logger.error("Error declining team invite: %s", e)
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)


class TeamOwnerTransferView(discord.ui.View):
    """
    A view for confirming team captaincy transfer.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance.
    team_id : int
        The ID of the team.
    current_owner_id : int
        The database ID of the current owner.
    new_owner_id : int
        The database ID of the new owner.
    context : Context
        The command context for sending responses.
    """

    def __init__(self, bot: DiscordBot, team_id: int, current_owner_id: int, new_owner_id: int, context: Context) -> None:
        """
        Initialise the team owner transfer view.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance.
        team_id : int
            The ID of the team.
        current_owner_id : int
            The database ID of the current owner.
        new_owner_id : int
            The database ID of the new owner.
        context : Context
            The command context.
        """
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.team_id = team_id
        self.current_owner_id = current_owner_id
        self.new_owner_id = new_owner_id
        self.context = context

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, emoji="✅")
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # pylint: disable=unused-argument
        """
        Handle the Approve button press.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this callback.
        button : discord.ui.Button
            The button that was pressed.
        """
        try:
            # Verify the user pressing the button is the current captain
            db_user = User.get_by_discord_id(self.bot.database, str(interaction.user.id))
            if not db_user or db_user.id != self.current_owner_id:
                await interaction.response.send_message("❌ Only the current captain can approve this transfer.", ephemeral=True)
                return

            # Get team details
            team = Team.get_by_id(self.bot.database, self.team_id)
            if not team:
                await interaction.response.send_message("❌ Team no longer exists.", ephemeral=True)
                self.stop()
                return

            # Verify new captain is still a member
            memberships = TeamMembership.get_by_team(self.bot.database, team.id)
            is_member = any(m.user_id == self.new_owner_id for m in memberships)
            if not is_member:
                await interaction.response.send_message("❌ The new captain is no longer a member of the team.", ephemeral=True)
                self.stop()
                return

            # Transfer captaincy
            object.__setattr__(team, "owner_id", self.new_owner_id)
            team.save(self.bot.database)

            # Get new captain details
            new_captain = User.get_by_id(self.bot.database, self.new_owner_id)
            new_captain_name = new_captain.display_name if new_captain and new_captain.display_name else "Unknown"

            # Update the original message
            embed = discord.Embed(
                title="✅ Captaincy Transferred",
                description=f"**{new_captain_name}** is now the captain of **{team.name}** [{team.tag}]!",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="Team ID", value=str(team.id), inline=True)
            embed.add_field(name="New Captain", value=new_captain_name, inline=True)
            embed.add_field(name="Previous Captain", value=interaction.user.display_name, inline=True)
            embed.set_footer(text=f"Transferred by {interaction.user.name}")

            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()

        except Exception as e:
            self.bot.logger.error("Error approving captaincy transfer: %s", e)
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:  # pylint: disable=unused-argument
        """
        Handle the Decline button press.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this callback.
        button : discord.ui.Button
            The button that was pressed.
        """
        try:
            # Verify the user pressing the button is the current captain
            db_user = User.get_by_discord_id(self.bot.database, str(interaction.user.id))
            if not db_user or db_user.id != self.current_owner_id:
                await interaction.response.send_message("❌ Only the current captain can decline this transfer.", ephemeral=True)
                return

            # Get team details
            team = Team.get_by_id(self.bot.database, self.team_id)
            if not team:
                await interaction.response.send_message("❌ Team no longer exists.", ephemeral=True)
                self.stop()
                return

            # Update the original message
            embed = discord.Embed(
                title="❌ Transfer Cancelled",
                description=f"The captaincy transfer for **{team.name}** [{team.tag}] has been cancelled.",
                colour=discord.Colour.red(),
            )

            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()

        except Exception as e:
            self.bot.logger.error("Error declining captaincy transfer: %s", e)
            await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)


class Teams(commands.Cog, name="Teams"):
    """
    A collection of team management commands for the Discord bot.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the Teams cog.
    teams(context, league, user, search)
        Lists all teams on the server with optional filters.
    team_create(context, name, tag)
        Creates a new team.
    team_members(context, team_identifier)
        Lists all members of a team.
    team_invite(context, team_id, user)
        Invites a user to join a team by team ID.
    team_edit(context, team_id, name, tag)
        Edits a team's name or tag by team ID (captain only).
    team_search(context, name, tag)
        Searches for a team by name or tag.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the Teams cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    @commands.hybrid_command(name="teams", description="List teams on this server with optional filters")
    async def teams(self, context: Context, league: Optional[str] = None, user: Optional[discord.User] = None, search: Optional[str] = None) -> None:
        """
        List all teams on the server, with optional filtering.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        league : str, optional
            Filter teams by league name.
        user : discord.User, optional
            Filter teams by user membership.
        search : str, optional
            Search teams by name or tag (partial match).
        """
        await context.defer()
        try:
            server_id = str(context.guild.id) if context.guild else None

            # In DM context, default to showing the user's teams
            if not server_id:
                # Get the user from database
                db_user = User.get_by_discord_id(self.bot.database, str(context.author.id))
                if not db_user:
                    await context.send("❌ You are not registered in the database. Join a team first.")
                    return

                # Get teams this user belongs to
                user_memberships = TeamMembership.get_by_user(self.bot.database, db_user.id)
                if not user_memberships:
                    await context.send("❌ You are not a member of any teams.")
                    return

                # Get all teams the user belongs to
                all_teams = []
                for membership in user_memberships:
                    team = Team.get_by_id(self.bot.database, membership.team_id)
                    if team:
                        all_teams.append(team)

                if not all_teams:
                    await context.send("❌ No teams found.")
                    return

                filtered_teams = all_teams

                # Apply search filter if provided
                if search:
                    search_lower = search.lower()
                    filtered_teams = [t for t in filtered_teams if search_lower in t.name.lower() or search_lower in t.tag.lower()]

                if not filtered_teams:
                    await context.send(f"❌ No teams found matching search term '{search}'.")
                    return

                # Create embed with team list
                title_parts = ["📋 Your Teams"]
                if search:
                    title_parts.append(f"matching '{search}'")

                embed = discord.Embed(
                    title=" ".join(title_parts),
                    description=f"Found {len(filtered_teams)} team(s).",
                    colour=discord.Colour.blue(),
                )

                # Add teams (max 25 fields)
                for team in filtered_teams[:25]:
                    captain = User.get_by_id(self.bot.database, team.owner_id)
                    captain_name = captain.display_name if captain and captain.display_name else "Unknown"

                    memberships = TeamMembership.get_by_team(self.bot.database, team.id)
                    member_count = len(memberships)

                    # Get leagues for this team
                    team_leagues = LeagueMembership.get_by_team(self.bot.database, team.id)
                    league_names = []
                    for lm in team_leagues[:3]:  # Show max 3 leagues
                        lg = League.get_by_id(self.bot.database, lm.league_id)
                        if lg:
                            league_names.append(lg.name)

                    league_info = f"Leagues: {', '.join(league_names)}" if league_names else "No leagues"

                    # Get server name
                    server_name = "Unknown Server"
                    try:
                        guild = self.bot.get_guild(int(team.discord_server))
                        if guild:
                            server_name = guild.name
                    except (ValueError, AttributeError):
                        pass

                    embed.add_field(
                        name=f"{team.name} [{team.tag}]",
                        value=f"Server: {server_name}\nCaptain: {captain_name}\nMembers: {member_count}\n{league_info}\nID: {team.id}",
                        inline=False,
                    )

                if len(filtered_teams) > 25:
                    embed.set_footer(text=f"Showing first 25 of {len(filtered_teams)} teams")
                else:
                    embed.set_footer(text=f"Requested by {context.author.name}")

                await context.send(embed=embed)
                return

            # Start with all teams in the server
            all_teams = Team.get_by_server(self.bot.database, server_id)

            if not all_teams:
                await context.send("❌ No teams found in this server.")
                return

            filtered_teams = all_teams

            # Apply league filter
            if league:
                league_obj = None
                leagues = League.get_by_server(self.bot.database, server_id)
                for lg in leagues:
                    if lg.name.lower() == league.lower():
                        league_obj = lg
                        break

                if not league_obj:
                    await context.send(f"❌ No league found with name '{league}' in this server.")
                    return

                # Get teams in this league
                league_memberships = LeagueMembership.get_by_league(self.bot.database, league_obj.id)
                league_team_ids = {lm.team_id for lm in league_memberships}
                filtered_teams = [t for t in filtered_teams if t.id in league_team_ids]

            # Apply user filter
            if user:
                db_user = User.get_by_discord_id(self.bot.database, str(user.id))
                if not db_user:
                    await context.send(f"❌ User {user.mention} is not registered in the database.")
                    return

                # Get teams this user belongs to
                user_memberships = TeamMembership.get_by_user(self.bot.database, db_user.id)
                user_team_ids = {um.team_id for um in user_memberships}
                filtered_teams = [t for t in filtered_teams if t.id in user_team_ids]

            # Apply search filter
            if search:
                search_lower = search.lower()
                filtered_teams = [t for t in filtered_teams if search_lower in t.name.lower() or search_lower in t.tag.lower()]

            if not filtered_teams:
                filter_desc = []
                if league:
                    filter_desc.append(f"league '{league}'")
                if user:
                    filter_desc.append(f"user {user.mention}")
                if search:
                    filter_desc.append(f"search term '{search}'")
                await context.send(f"❌ No teams found matching: {', '.join(filter_desc)}.")
                return

            # Create embed with team list
            title_parts = ["📋 Teams"]
            if league:
                title_parts.append(f"in {league}")
            if user:
                title_parts.append(f"with {user.display_name}")
            if search:
                title_parts.append(f"matching '{search}'")

            embed = discord.Embed(
                title=" ".join(title_parts),
                description=f"Found {len(filtered_teams)} team(s).",
                colour=discord.Colour.blue(),
            )

            # Add teams (max 25 fields)
            for team in filtered_teams[:25]:
                captain = User.get_by_id(self.bot.database, team.owner_id)
                captain_name = captain.display_name if captain and captain.display_name else "Unknown"

                memberships = TeamMembership.get_by_team(self.bot.database, team.id)
                member_count = len(memberships)

                # Get leagues for this team
                team_leagues = LeagueMembership.get_by_team(self.bot.database, team.id)
                league_names = []
                for lm in team_leagues[:3]:  # Show max 3 leagues
                    lg = League.get_by_id(self.bot.database, lm.league_id)
                    if lg:
                        league_names.append(lg.name)

                league_info = f"Leagues: {', '.join(league_names)}" if league_names else "No leagues"

                embed.add_field(
                    name=f"{team.name} [{team.tag}]",
                    value=f"Captain: {captain_name}\nMembers: {member_count}\n{league_info}\nID: {team.id}",
                    inline=False,
                )

            if len(filtered_teams) > 25:
                embed.set_footer(text=f"Showing first 25 of {len(filtered_teams)} teams")
            else:
                embed.set_footer(text=f"Requested by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error listing teams: %s", e)
            await context.send(f"❌ An error occurred while listing teams: {e}")

    @commands.hybrid_group(name="team", description="Manage teams")
    async def team(self, context: Context) -> None:
        """
        Command group for managing teams.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        if context.invoked_subcommand is None:
            await context.send("Please specify a subcommand: create, members, invite, edit, or search.\n\nTip: Use `/teams` to list all teams.")

    @team.command(name="create", description="Create a new team")
    async def team_create(self, context: Context, name: str, tag: str) -> None:
        """
        Create a new team in the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        name : str
            The full name of the team.
        tag : str
            The team tag/shorthand name.
        """
        await context.defer()
        try:
            # Get or create user in database
            discord_user = context.author
            db_user = User.get_by_discord_id(self.bot.database, str(discord_user.id))

            if not db_user:
                # Create new user
                db_user = User(id=0, discord_id=str(discord_user.id), display_name=discord_user.display_name, created_date=datetime.now())
                db_user.save(self.bot.database)

            server_id = str(context.guild.id) if context.guild else None
            if not server_id:
                await context.send("❌ This command can only be used in a server.")
                return

            # Create the team
            team = Team(
                id=0,
                name=name,
                tag=tag,
                owner_id=db_user.id,
                created_at=datetime.now(),
                created_by=db_user.id,
                discord_server=server_id,
            )
            team_id = team.save(self.bot.database)

            # Add creator as team member (and captain)
            membership = TeamMembership(user_id=db_user.id, team_id=team_id, captain=True, joined_date=datetime.now(), updated_date=None)
            membership.save(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Team Created",
                description=f"Successfully created team **{name}** [{tag}].",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="Team ID", value=str(team_id), inline=True)
            embed.add_field(name="Captain", value=discord_user.mention, inline=True)
            embed.add_field(name="Server", value=context.guild.name if context.guild else "Unknown", inline=True)
            embed.set_footer(text=f"Created by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error creating team: %s", e)
            await context.send(f"❌ An error occurred while creating the team: {e}")

    @team.command(name="members", description="List all members of a team by team ID")
    async def team_members(self, context: Context, team_id: int) -> None:
        """
        List all members of a team.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        team_id : int
            The ID of the team.
        """
        await context.defer()
        try:
            server_id = str(context.guild.id) if context.guild else None
            if not server_id:
                await context.send("❌ This command can only be used in a server.")
                return

            # Get team by ID
            team = Team.get_by_id(self.bot.database, team_id)
            if not team:
                await context.send(f"❌ No team found with ID {team_id}.")
                return

            # Verify team is in this server
            if team.discord_server != server_id:
                await context.send(f"❌ Team with ID {team_id} does not exist in this server.")
                return

            # Get team members
            memberships = TeamMembership.get_by_team(self.bot.database, team.id)

            if not memberships:
                await context.send(f"Team **{team.name}** [{team.tag}] has no members.")
                return

            # Create embed with member list
            embed = discord.Embed(
                title=f"👥 {team.name} [{team.tag}] - Members",
                description=f"Found {len(memberships)} member(s).",
                colour=discord.Colour.blue(),
            )

            # Get captain info
            captain = User.get_by_id(self.bot.database, team.owner_id)
            captain_name = captain.display_name if captain and captain.display_name else "Unknown"

            embed.add_field(name="Captain", value=captain_name, inline=False)

            # Add members - collect and sort alphabetically
            member_data = []
            for membership in memberships:
                user = User.get_by_id(self.bot.database, membership.user_id)
                if user:
                    display = user.display_name if user.display_name else f"User {user.id}"
                    is_captain = " 👑" if user.id == team.owner_id else ""
                    member_data.append((display.lower(), f"• {display}{is_captain}"))

            # Sort by display name (case-insensitive) and take first 24
            member_data.sort(key=lambda x: x[0])
            member_list = [member[1] for member in member_data[:24]]

            if member_list:
                embed.add_field(name="Members", value="\n".join(member_list), inline=False)

            if len(memberships) > 24:
                embed.set_footer(text=f"Showing first 24 of {len(memberships)} members")
            else:
                embed.set_footer(text=f"Requested by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error listing team members: %s", e)
            await context.send(f"❌ An error occurred while listing team members: {e}")

    @team.command(name="invite", description="Invite a user to join your team by team ID")
    async def team_invite(self, context: Context, team_id: int, user: discord.User) -> None:
        """
        Invite a user to join a team by team ID.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        team_id : int
            The ID of the team.
        user : discord.User
            The Discord user to invite.
        """
        await context.defer()
        try:
            server_id = str(context.guild.id) if context.guild else None
            if not server_id:
                await context.send("❌ This command can only be used in a server.")
                return

            # Get the requesting user
            requester = User.get_by_discord_id(self.bot.database, str(context.author.id))
            if not requester:
                await context.send("❌ You are not registered in the database. Create a team first.")
                return

            # Get team by ID
            team = Team.get_by_id(self.bot.database, team_id)

            if not team:
                await context.send(f"❌ No team found with ID {team_id}.")
                return

            # Verify team is in this server
            if team.discord_server != server_id:
                await context.send(f"❌ Team with ID {team_id} does not exist in this server.")
                return

            # Check if requester is the team captain, owner, or admin
            if not await is_owner_or_admin_or_captain(self.bot, context, team, requester.id):
                await context.send("❌ Only the team captain (or bot owner/admin) can invite members.")
                return

            # Get or create the invited user
            invited_user = User.get_by_discord_id(self.bot.database, str(user.id))
            if not invited_user:
                invited_user = User(id=0, discord_id=str(user.id), display_name=user.display_name, created_date=datetime.now())
                invited_user.save(self.bot.database)

            # Check if user is already a member
            existing_memberships = TeamMembership.get_by_team(self.bot.database, team.id)
            for membership in existing_memberships:
                if membership.user_id == invited_user.id:
                    await context.send(f"❌ {user.mention} is already a member of **{team.name}**.")
                    return

            # Send invitation via DM
            try:
                # Create invitation embed
                invite_embed = discord.Embed(
                    title="📨 Team Invitation",
                    description=f"You have been invited to join **{team.name}** [{team.tag}]!",
                    colour=discord.Colour.blue(),
                )
                invite_embed.add_field(name="Team", value=f"{team.name} [{team.tag}]", inline=True)
                invite_embed.add_field(name="Team ID", value=str(team.id), inline=True)
                invite_embed.add_field(name="Invited by", value=context.author.display_name, inline=True)

                # Get server name
                server_name = context.guild.name if context.guild else "Unknown Server"
                invite_embed.add_field(name="Server", value=server_name, inline=False)
                invite_embed.set_footer(text="This invitation will expire in 48 hours")

                # Create the view with Accept/Decline buttons
                view = TeamInviteView(self.bot, team.id, invited_user.id, context.channel.id)

                # Send DM to the user
                await user.send(embed=invite_embed, view=view)

                # Confirm invitation sent
                embed = discord.Embed(
                    title="✅ Invitation Sent",
                    description=f"Sent a team invitation to {user.mention} via direct message.",
                    colour=discord.Colour.green(),
                )
                embed.add_field(name="Team", value=f"{team.name} [{team.tag}]", inline=True)
                embed.set_footer(text=f"Invited by {context.author.name}")

                await context.send(embed=embed)

            except discord.Forbidden:
                await context.send(f"❌ Could not send a DM to {user.mention}. They may have DMs disabled.")
            except discord.HTTPException as e:
                await context.send(f"❌ Failed to send invitation: {e}")

        except Exception as e:
            self.bot.logger.error("Error inviting team member: %s", e)
            await context.send(f"❌ An error occurred while inviting the team member: {e}")

    @team.command(name="edit", description="Edit your team's name or tag by team ID")
    async def team_edit(self, context: Context, team_id: int, name: Optional[str] = None, tag: Optional[str] = None) -> None:
        """
        Edit a team's name or tag by team ID.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        team_id : int
            The ID of the team to edit.
        name : str, optional
            The new team name.
        tag : str, optional
            The new team tag.
        """
        await context.defer()
        try:
            server_id = str(context.guild.id) if context.guild else None
            if not server_id:
                await context.send("❌ This command can only be used in a server.")
                return

            # Get the requesting user
            requester = User.get_by_discord_id(self.bot.database, str(context.author.id))
            if not requester:
                await context.send("❌ You are not registered in the database. Create a team first.")
                return

            # Get team by ID
            team = Team.get_by_id(self.bot.database, team_id)

            if not team:
                await context.send(f"❌ No team found with ID {team_id}.")
                return

            # Verify team is in this server
            if team.discord_server != server_id:
                await context.send(f"❌ Team with ID {team_id} does not exist in this server.")
                return

            # Check if requester is the team captain, owner, or admin
            if not await is_owner_or_admin_or_captain(self.bot, context, team, requester.id):
                await context.send("❌ Only the team captain (or bot owner/admin) can edit team details.")
                return

            # Check if at least one parameter is provided
            if not name and not tag:
                await context.send("❌ Please provide at least one field to update: `name` or `tag`.")
                return

            # Update team details
            old_name = team.name
            old_tag = team.tag

            if name:
                object.__setattr__(team, "name", name)
            if tag:
                object.__setattr__(team, "tag", tag)

            team.save(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Team Updated",
                description=f"Successfully updated team **{team.name}** [{team.tag}].",
                colour=discord.Colour.green(),
            )

            changes = []
            if name and name != old_name:
                changes.append(f"Name: {old_name} → {name}")
            if tag and tag != old_tag:
                changes.append(f"Tag: {old_tag} → {tag}")

            if changes:
                embed.add_field(name="Changes", value="\n".join(changes), inline=False)

            embed.add_field(name="Team ID", value=str(team.id), inline=True)
            embed.add_field(name="Captain", value=context.author.mention, inline=True)
            embed.set_footer(text=f"Updated by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error editing team: %s", e)
            await context.send(f"❌ An error occurred while editing the team: {e}")

    @team.command(name="leave", description="Leave a team by team ID")
    async def team_leave(self, context: Context, team_id: int) -> None:
        """
        Leave a team by removing yourself from its membership.

        Parameters
        ----------
        context : Context
            The command context.
        team_id : int
            The ID of the team to leave.

        Notes
        -----
        - Captains cannot leave their own team - they must transfer captaincy first
        - Users can only leave teams they are currently a member of
        - This action cannot be undone
        """
        await context.defer()

        try:
            # Get the user from the database
            db_user = User.get_by_discord_id(self.bot.database, str(context.author.id))
            if not db_user:
                await context.send("❌ You are not registered. Please create or join a team first.")
                return

            # Get the team
            team = Team.get_by_id(self.bot.database, team_id)
            if not team:
                await context.send(f"❌ Team with ID {team_id} does not exist.")
                return

            # Check if user is a member of the team
            memberships = TeamMembership.get_by_team(self.bot.database, team.id)
            membership = next((m for m in memberships if m.user_id == db_user.id), None)
            if not membership:
                await context.send(f"❌ You are not a member of **{team.name}** [{team.tag}].")
                return

            # Check if user is the captain
            if team.owner_id == db_user.id:
                await context.send(
                    f"❌ You cannot leave **{team.name}** [{team.tag}] as you are the captain. "
                    "Please transfer captaincy to another member first or disband the team."
                )
                return

            # Remove the membership
            membership.delete(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Left Team",
                description=f"You have successfully left **{team.name}** [{team.tag}].",
                colour=discord.Colour.green(),
            )

            embed.add_field(name="Team ID", value=str(team.id), inline=True)
            embed.add_field(name="Former Member", value=context.author.mention, inline=True)
            embed.set_footer(text=f"Left by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error leaving team: %s", e)
            await context.send(f"❌ An error occurred while leaving the team: {e}")

    @team.command(name="remove", description="Remove a member from your team by team ID")
    async def team_remove(self, context: Context, team_id: int, user: discord.User) -> None:
        """
        Remove a member from a team (captain only).

        Parameters
        ----------
        context : Context
            The command context.
        team_id : int
            The ID of the team.
        user : discord.User
            The Discord user to remove from the team.

        Notes
        -----
        - Only team captains can remove members
        - Captains cannot remove themselves - use transfer captaincy first
        - The removed member will need to be re-invited to rejoin
        """
        await context.defer()

        try:
            server_id = str(context.guild.id) if context.guild else None
            if not server_id:
                await context.send("❌ This command can only be used in a server.")
                return

            # Get the requesting user
            requester = User.get_by_discord_id(self.bot.database, str(context.author.id))
            if not requester:
                await context.send("❌ You are not registered in the database. Create a team first.")
                return

            # Get team by ID
            team = Team.get_by_id(self.bot.database, team_id)
            if not team:
                await context.send(f"❌ No team found with ID {team_id}.")
                return

            # Verify team is in this server
            if team.discord_server != server_id:
                await context.send(f"❌ Team with ID {team_id} does not exist in this server.")
                return

            # Check if requester is the team captain, owner, or admin
            if not await is_owner_or_admin_or_captain(self.bot, context, team, requester.id):
                await context.send("❌ Only the team captain (or bot owner/admin) can remove members.")
                return

            # Get the user to remove from database
            target_user = User.get_by_discord_id(self.bot.database, str(user.id))
            if not target_user:
                await context.send(f"❌ {user.mention} is not registered in the database.")
                return

            # Check if user is a member of the team
            memberships = TeamMembership.get_by_team(self.bot.database, team.id)
            membership = next((m for m in memberships if m.user_id == target_user.id), None)
            if not membership:
                await context.send(f"❌ {user.mention} is not a member of **{team.name}** [{team.tag}].")
                return

            # Prevent captain from removing themselves
            if target_user.id == team.owner_id:
                await context.send(
                    f"❌ You cannot remove the team captain from **{team.name}** [{team.tag}]. " "Please transfer captaincy to another member first."
                )
                return

            # Remove the membership
            membership.delete(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Member Removed",
                description=f"{user.mention} has been removed from **{team.name}** [{team.tag}].",
                colour=discord.Colour.green(),
            )

            embed.add_field(name="Team ID", value=str(team.id), inline=True)
            embed.add_field(name="Removed By", value=context.author.mention, inline=True)
            embed.set_footer(text=f"Removed by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error removing team member: %s", e)
            await context.send(f"❌ An error occurred while removing the team member: {e}")

    @team.command(name="owner", description="Transfer team captaincy to another member by team ID")
    async def team_owner(self, context: Context, team_id: int, user: discord.User) -> None:
        """
        Transfer team captaincy to another member (captain only).

        Parameters
        ----------
        context : Context
            The command context.
        team_id : int
            The ID of the team.
        user : discord.User
            The Discord user to make the new captain.

        Notes
        -----
        - Only the current team captain can transfer captaincy
        - The new captain must be an existing member of the team
        - A confirmation prompt with 5-minute timeout is shown before transfer
        """
        await context.defer()

        try:
            server_id = str(context.guild.id) if context.guild else None
            if not server_id:
                await context.send("❌ This command can only be used in a server.")
                return

            # Get the requesting user
            requester = User.get_by_discord_id(self.bot.database, str(context.author.id))
            if not requester:
                await context.send("❌ You are not registered in the database. Create a team first.")
                return

            # Get team by ID
            team = Team.get_by_id(self.bot.database, team_id)
            if not team:
                await context.send(f"❌ No team found with ID {team_id}.")
                return

            # Verify team is in this server
            if team.discord_server != server_id:
                await context.send(f"❌ Team with ID {team_id} does not exist in this server.")
                return

            # Check if requester is the team captain, owner, or admin
            if not await is_owner_or_admin_or_captain(self.bot, context, team, requester.id):
                await context.send("❌ Only the team captain (or bot owner/admin) can transfer captaincy.")
                return

            # Get the new captain from database
            new_captain = User.get_by_discord_id(self.bot.database, str(user.id))
            if not new_captain:
                await context.send(f"❌ {user.mention} is not registered in the database.")
                return

            # Check if new captain is trying to transfer to themselves
            if new_captain.id == requester.id:
                await context.send("❌ You are already the captain of this team.")
                return

            # Check if new captain is a member of the team
            memberships = TeamMembership.get_by_team(self.bot.database, team.id)
            is_member = any(m.user_id == new_captain.id for m in memberships)
            if not is_member:
                await context.send(f"❌ {user.mention} is not a member of **{team.name}** [{team.tag}].")
                return

            # Create confirmation embed
            embed = discord.Embed(
                title="⚠️ Confirm Captaincy Transfer",
                description=f"Are you sure you want to transfer captaincy of **{team.name}** [{team.tag}] to {user.mention}?",
                colour=discord.Colour.orange(),
            )
            embed.add_field(name="Team", value=f"{team.name} [{team.tag}]", inline=True)
            embed.add_field(name="Team ID", value=str(team.id), inline=True)
            embed.add_field(name="Current Captain", value=context.author.mention, inline=True)
            embed.add_field(name="New Captain", value=user.mention, inline=True)
            embed.set_footer(text="This confirmation will expire in 5 minutes")

            # Create the view with Approve/Decline buttons
            view = TeamOwnerTransferView(self.bot, team.id, requester.id, new_captain.id, context)

            await context.send(embed=embed, view=view)

        except Exception as e:
            self.bot.logger.error("Error initiating captaincy transfer: %s", e)
            await context.send(f"❌ An error occurred while initiating the captaincy transfer: {e}")


async def setup(bot: DiscordBot) -> None:
    """
    Loads the Teams cog into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(Teams(bot))
