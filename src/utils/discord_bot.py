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

import discord
from discord.ext import commands


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
    bot_prefix : str
        The command prefix for the bot, retrieved from environment variables.
    user_name : str
        The name of the bot, with a default value of "Sons of Valour".
    app_dir : pathlib.Path
        The application directory path.

    Methods
    -------
    __init__(logger, intents)
        Initializes the DiscordBot instance.
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

    Notes
    -----
    - The bot disables the default help command.
    - The invite URL is logged on startup.
    - Cogs are loaded dynamically from the cogs directory.
    """

    def __init__(self, logger: logging.Logger, intents: discord.Intents) -> None:
        """
        Initialize the DiscordBot instance.

        Parameters
        ----------
        logger : logging.Logger
            The logger instance for logging bot events.
        intents : discord.Intents
            The intents to use for the bot.
        """
        super().__init__(
            command_prefix=commands.when_mentioned_or(os.getenv("COMMAND_PREFIX", "!")),
            intents=intents,
            help_command=None,  # Disable the default help command
        )

        self.logger = logger
        self.bot_prefix = os.getenv("COMMAND_PREFIX", "!")
        self.user_name = os.getenv("BOT_NAME", "Scrim Bot")
        self.app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        print(self.app_dir)

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
                    self.logger.error(f"Failed to load extension {extension}\n{exception}")

        self.logger.info(f"Loaded extensions: {', '.join(cogs_loaded)}")

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

    async def on_command_error(self, context, error) -> None:
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            self.logger.warning(f"Command not found: {context.message.content}")
            await context.send("Command not found. Use `!help` to see available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            self.logger.warning(f"Missing argument for command {context.command}: {error.param.name}")
            await context.send(f"Missing required argument: {error.param.name}")
        elif isinstance(error, commands.MissingPermissions):
            self.logger.warning(f"Missing permissions for command {context.command}: {error.missing_permissions}")
            await context.send("You don't have permission to use this command.")
        else:
            self.logger.error(f"Unhandled error: {error}")
            await context.send("An error occurred while processing your command.")
