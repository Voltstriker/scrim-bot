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
This module contains the implementation of the DiscordBot class.

The DiscordBot class extends the functionality of the discord.ext.commands.Bot
class to provide additional features such as periodic status updates, logging,
and message handling.

Classes
-------
DiscordBot
    A custom bot implementation for managing Discord interactions.
"""

import os
import platform
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands import Context

if TYPE_CHECKING:
    from utils.database import Database  # pylint: disable=cyclic-import


class DiscordBot(commands.Bot):
    """
    A custom implementation of a Discord bot.

    This class extends the `discord.ext.commands.Bot` class to provide
    additional functionality, including periodic status updates, logging,
    and handling incoming messages.

    Attributes
    ----------
    logger : logging.Logger
        The logger instance for logging bot events.
    database : Database
        The database instance for database operations.
    bot_prefix : str
        The command prefix for the bot, retrieved from environment variables.
    user_name : str
        The name of the bot, with a default value of "Scrim Bot".
    app_dir : pathlib.Path
        The application directory path.

    Methods
    -------
    __init__(logger, database, intents)
        Initialises the DiscordBot instance.
    status_task()
        Periodically updates the bot's status.
    before_status_task()
        Ensures the bot is ready before starting the status task.
    setup_hook()
        Performs setup actions when the bot starts for the first time.
    load_cogs()
        Loads all cogs/extensions from the cogs directory.
    on_message(message)
        Handles incoming messages sent in channels the bot has access to.
    on_ready()
        Event handler called when the bot is ready.
    is_owner_or_admin()
        Returns a check decorator that verifies if user is bot owner or admin.
    is_team_owner(team_owner_id, requester_user_id)
        Static method that checks if user is the team owner.
    is_captain(team_id, requester_user_id)
        Checks if user is a captain of the team (via team_membership table).
    is_owner_or_admin_or_captain(context, team, requester_user_id)
        Checks if user is bot owner, admin, or team captain.

    Notes
    -----
    - The bot disables the default help command.
    - The invite URL is logged on startup.
    - Cogs are loaded dynamically from the cogs directory.
    """

    def __init__(self, logger: logging.Logger, database: "Database", intents: discord.Intents) -> None:
        """
        Initialise the DiscordBot instance.

        Parameters
        ----------
        logger : logging.Logger
            The logger instance for logging bot events.
        database : Database
            The database instance for database operations.
        intents : discord.Intents
            The intents to use for the bot.
        """
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("COMMAND_PREFIX", "!")),
            intents=intents,
            help_command=None,  # Disable the default help command
        )

        self.logger = logger
        self.database = database
        self.bot_prefix = os.getenv("COMMAND_PREFIX", "!")
        self.user_name = os.getenv("BOT_NAME", "Scrim Bot")
        self.app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent

    async def setup_hook(self) -> None:
        """
        Performs setup actions when the bot starts for the first time.

        Logs bot authentication details, API versions, and invite URL.
        Loads all cogs/extensions.
        """
        self.logger.info("Python version: %s", platform.python_version())
        self.logger.info("Running on: %s %s (%s)", platform.system(), platform.release(), os.name)
        self.logger.info("Application directory: '%s'", self.app_dir)
        self.logger.info("discord.py API version: %s", discord.__version__)
        self.logger.info(
            "Connecting to Discord API as bot '%s' (%s)", self.user.name if self.user else "Unknown", self.user.id if self.user else "Unknown"
        )

        await self.load_cogs()

    async def load_cogs(self) -> None:
        """
        Loads all cogs/extensions from the cogs directory.

        Iterates through all Python files in the cogs directory, attempts to load each
        as a Discord extension, and logs the result. Successfully loaded extensions
        are tracked and reported.

        Logs
        ----
        - Info: List of successfully loaded extensions.
        - Error: Any exceptions encountered while loading an extension.
        """
        # Load each cog/extension from the cogs directory
        cogs_dir = os.path.join(self.app_dir, "cogs")
        cogs_loaded = []
        for file in os.listdir(cogs_dir):
            if file.endswith(".py"):
                extension = file[:-3]  # Actual file name without .py

                # Load the extension and log the result
                try:
                    cog_path = f"cogs.{extension}"
                    await self.load_extension(cog_path)
                    cogs_loaded.append(extension)
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error("Failed to load extension %s\n%s", extension, exception)

        self.logger.info("Loaded extensions: %s", ", ".join(cogs_loaded))

    async def on_message(self, message: discord.Message) -> None:  # pylint: disable=arguments-differ
        """
        Handles incoming messages sent in channels the bot has access to.

        Processes commands for valid messages - ignores messages from the bot itself or other bots.

        Parameters
        ----------
        message : discord.Message
            The message object that was sent.
        """
        # Ignore messages from the bot itself or other bots
        if message.author == self.user or message.author.bot:
            return

        await self.process_commands(message)

    async def on_ready(self) -> None:
        """
        Event handler called when the bot is ready.

        Logs a message indicating that the bot is online and prints the invite URL.
        Sets the bot's status and activity.
        Ensures the bot owner is added to the database.
        """
        self.logger.info("Bot is online and ready to receive commands.")

        # Set bot status and activity
        activity = discord.Game(name="Organising Scrims")
        await self.change_presence(status=discord.Status.online, activity=activity)

        # Create an invite URL and log to console
        app_info = await self.application_info()
        client_id = str(app_info.id)
        self.logger.info(
            "Invite URL: https://discord.com/oauth2/authorize?client_id=%s&permissions=7336485162839121&scope=bot%%20applications.commands",  # pylint: disable=line-too-long
            client_id,
        )

        # Ensure bot owner is in the database
        await self._ensure_bot_owner_in_database(app_info)

    async def _ensure_bot_owner_in_database(self, app_info: discord.AppInfo) -> None:
        """
        Ensure the bot owner is added to both users and admins tables.

        Parameters
        ----------
        app_info : discord.AppInfo
            The application info containing owner details.
        """
        from datetime import datetime  # pylint: disable=import-outside-toplevel

        from models import BotAdminConfig, User  # pylint: disable=import-outside-toplevel,import-error

        try:
            owner = app_info.owner
            if not owner:
                self.logger.warning("Bot owner information not available")
                return

            # Check if owner exists in users table
            owner_user = User.get_by_discord_id(self.database, str(owner.id))
            if not owner_user:
                owner_user = User(
                    id=0,
                    discord_id=str(owner.id),
                    display_name=owner.display_name,
                    created_date=datetime.now(),
                )
                owner_user.save(self.database)
                self.logger.debug("Bot owner added to users table: %s (ID: %s)", owner.display_name, owner.id)

            # Check if owner exists in admins table
            owner_admin = BotAdminConfig.get_by_user_id(self.database, str(owner.id))
            if not owner_admin:
                owner_admin = BotAdminConfig(
                    id=0,
                    discord_user_id=str(owner.id),
                    discord_server_id=None,
                    discord_role_id=None,
                    scope="user",
                    admin=True,
                    created_date=datetime.now(),
                    created_by=owner_user.id,
                    updated_date=None,
                    updated_by=None,
                )
                owner_admin.save(self.database)
                self.logger.debug("Bot owner added to admins table: %s (ID: %s)", owner.display_name, owner.id)

        except Exception as ex:
            self.logger.error("Failed to add bot owner to database: %s", ex)

    def is_owner_or_admin(self):
        """
        Check if user is bot owner or an admin.

        This method returns a check decorator that can be applied to commands to restrict
        access to bot owners and users/roles that have been granted admin privileges
        through the admins table.

        Returns
        -------
        commands.check
            A check decorator that verifies if the user is the bot owner or has admin privileges.

        Examples
        --------
        >>> @commands.hybrid_command()
        >>> @commands.check(bot.is_owner_or_admin())
        >>> async def my_command(self, context: Context) -> None:
        >>>     await context.send("You have admin privileges!")
        """

        async def predicate(context: Context) -> bool:
            """
            Predicate function that checks if user has owner or admin privileges.

            Parameters
            ----------
            context : Context
                The command context.

            Returns
            -------
            bool
                True if user is owner or admin, False otherwise.
            """
            from models import BotAdminConfig  # pylint: disable=import-outside-toplevel,import-error

            # Check if user is bot owner
            if await context.bot.is_owner(context.author):
                return True

            # Check if user is in admins table
            admin_config = BotAdminConfig.get_by_user_id(self.database, str(context.author.id))
            if admin_config and admin_config.admin:
                return True

            # Check if user has any admin roles (if in a guild)
            if context.guild and hasattr(context.author, "roles"):
                for role in context.author.roles:  # type: ignore[attr-defined]
                    role_config = BotAdminConfig.get_by_server_and_role(self.database, str(context.guild.id), str(role.id))
                    if role_config and role_config.admin:
                        return True

            return False

        return predicate

    @staticmethod
    def is_team_owner(team_owner_id: int, requester_user_id: int) -> bool:
        """
        Check if a user is the owner of a team.

        This is a simple helper function that compares the team's owner ID
        with the requester's user ID to determine if the user is the team owner.

        Parameters
        ----------
        team_owner_id : int
            The database ID of the team's owner.
        requester_user_id : int
            The database ID of the user making the request.

        Returns
        -------
        bool
            True if the requester is the team owner, False otherwise.

        Examples
        --------
        >>> if DiscordBot.is_team_owner(team.owner_id, requester.id):
        >>>     # User is the team owner
        >>>     await process_owner_action()
        """
        return team_owner_id == requester_user_id

    def is_captain(self, team_id: int, requester_user_id: int) -> bool:
        """
        Check if a user is a captain of the team.

        This method checks the team_membership table to determine if the user
        has captain privileges for the specified team.

        Parameters
        ----------
        team_id : int
            The database ID of the team.
        requester_user_id : int
            The database ID of the user making the request.

        Returns
        -------
        bool
            True if the requester is a captain of the team, False otherwise.

        Examples
        --------
        >>> if self.bot.is_captain(team.id, requester.id):
        >>>     # User is a team captain
        >>>     await process_captain_action()
        """
        from models import TeamMembership  # pylint: disable=import-outside-toplevel,import-error

        membership = TeamMembership.get_by_user_and_team(self.database, requester_user_id, team_id)
        return membership is not None and membership.captain

    async def is_owner_or_admin_or_captain(self, context: Context, team, requester_user_id: int) -> bool:
        """
        Check if user is bot owner, admin, or team captain.

        This method uses check_any pattern - evaluates multiple predicates and
        returns True if any pass:
        - Team owner check: bot.is_team_owner() static method
        - Captain check: bot.is_captain() method
        - Owner/Admin check: bot.is_owner_or_admin() predicate

        Parameters
        ----------
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

        # Create team owner check predicate
        async def is_team_owner_check(ctx: Context) -> bool:  # pylint: disable=unused-argument
            """
            Check if user is team owner.

            Parameters
            ----------
            ctx : Context
                The command context (unused, required for predicate signature).

            Returns
            -------
            bool
                True if user is team owner.
            """
            return self.is_team_owner(team.owner_id, requester_user_id)

        # Create captain check predicate
        async def is_captain_check(ctx: Context) -> bool:  # pylint: disable=unused-argument
            """
            Check if user is team captain.

            Parameters
            ----------
            ctx : Context
                The command context (unused, required for predicate signature).

            Returns
            -------
            bool
                True if user is captain.
            """
            return self.is_captain(team.id, requester_user_id)

        # Get owner/admin check predicate
        is_owner_admin_check = self.is_owner_or_admin()

        # Evaluate predicates using check_any pattern - return True if any pass
        checks = [is_team_owner_check, is_captain_check, is_owner_admin_check]
        for check in checks:
            try:
                if await check(context):
                    return True
            except commands.CheckFailure:
                continue

        return False

    async def on_command_error(self, context: commands.Context, error: commands.CommandError) -> None:  # pylint: disable=arguments-differ
        """
        Global error handler for commands.

        Parameters
        ----------
        context : commands.Context
            The invocation context where the error occurred.
        error : commands.CommandError
            The error that was raised during command execution.
        """
        if isinstance(error, commands.CommandNotFound):
            self.logger.warning("Command not found: %s", context.message.content)
            await context.send("Command not found. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            self.logger.warning("Missing argument for command %s: %s", context.command, error.param.name)
            await context.send(f"Missing required argument: {error.param.name}")
        elif isinstance(error, commands.MissingPermissions):
            self.logger.warning("Missing permissions for command %s: %s", context.command, error.missing_permissions)
            await context.send("You don't have permission to use this command.")
        else:
            self.logger.error("Unhandled error: %s", error)
            await context.send("An error occurred while processing your command.")
