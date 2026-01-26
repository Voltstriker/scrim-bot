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
Utility commands and features for the Discord bot.

This module defines the Utils cog, which provides helpful commands and tools
for server management and bot administration.

Classes
-------
Utils
    A collection of utility commands and features for the Discord bot.

Functions
---------
setup(bot)
    Loads the Utils cog into the bot.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

if TYPE_CHECKING:
    from utils.discord_bot import DiscordBot  # pylint: disable=import-error,no-name-in-module


class DatabaseResetConfirmView(discord.ui.View):
    """
    View for confirming database reset operation.

    Attributes
    ----------
    approved : bool or None
        Whether the reset was approved (True), declined (False), or timed out (None).
    interaction : discord.Interaction or None
        The interaction from the button press.
    """

    def __init__(self) -> None:
        """Initialise the confirmation view with a 60-second timeout."""
        super().__init__(timeout=60.0)
        self.approved: bool | None = None
        self.interaction: discord.Interaction | None = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.danger, emoji="✅")
    async def approve_button(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        """
        Handle approval of database reset.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this button.
        _button : discord.ui.Button
            The button that was pressed (unused).
        """
        self.approved = True
        self.interaction = interaction
        self.stop()

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.secondary, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, _button: discord.ui.Button) -> None:
        """
        Handle decline of database reset.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered this button.
        _button : discord.ui.Button
            The button that was pressed (unused).
        """
        self.approved = False
        self.interaction = interaction
        self.stop()


class Utils(commands.Cog, name="Utils"):
    """
    A collection of utility commands and features for the Discord bot.

    This cog provides various utility functions that enhance the bot's
    capabilities, including useful commands and tools for server management.

    Attributes
    ----------
    bot : discord.ext.commands.Bot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the Utils cog.
    ping(context)
        Responds with "Pong!" to test the bot's responsiveness.
    sync(context, scope)
        Synchronises the bot's slash commands.
    unsync(context, scope)
        Unsynchronises the bot's slash commands.
    database_reset(context)
        Resets the database tables with confirmation.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the Utils cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Responds with Pong! to test bot responsiveness.")
    @commands.is_owner()
    async def ping(self, context: Context) -> None:
        """
        Responds with "Pong!" to test the bot's responsiveness.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        latency = round(self.bot.latency * 1000)
        await context.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.hybrid_command(name="sync", description="Synchronises the slash commands.")
    @app_commands.describe(scope="The scope of the sync. Can be `global` or `guild`")
    @app_commands.choices(scope=[app_commands.Choice(name="global", value="global"), app_commands.Choice(name="guild", value="guild")])
    @commands.is_owner()
    async def sync(self, context: Context, scope: str | None = None) -> None:
        """
        Synchronises the bot's slash commands.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        scope : str or None, optional
            The scope of the synchronisation. Can be 'global' or 'guild'.

        Sends
        -----
        discord.Embed
            A message indicating the result of the synchronisation operation.
        """
        if scope == "global":
            embed = discord.Embed(description="Syncing commands globally...", color=0xFFFF00)
            message = await context.send(embed=embed)
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                description=f"Slash commands have been globally synchronised. Synced {len(synced)} command(s).",
                color=0xBEBEFE,
            )
            await message.edit(embed=embed)
            return
        if scope == "guild":
            if context.guild is None:
                embed = discord.Embed(description="This command must be used in a guild.", color=0xE02B2B)
                await context.send(embed=embed)
                return
            embed = discord.Embed(description="Syncing commands in this guild...", color=0xFFFF00)
            message = await context.send(embed=embed)
            self.bot.tree.copy_global_to(guild=context.guild)
            synced = await self.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description=f"Slash commands have been synchronised in this guild. Synced {len(synced)} command(s).",
                color=0xBEBEFE,
            )
            await message.edit(embed=embed)
            return
        embed = discord.Embed(description="The scope must be `global` or `guild`.", color=0xE02B2B)
        await context.send(embed=embed)

    @commands.hybrid_command(name="unsync", description="Unsynchronises the slash commands.")
    @app_commands.describe(scope="The scope of the sync. Can be `global`, `current_guild` or `guild`")
    @app_commands.choices(scope=[app_commands.Choice(name="global", value="global"), app_commands.Choice(name="guild", value="guild")])
    @commands.is_owner()
    async def unsync(self, context: Context, scope: str | None = None) -> None:
        """
        Unsynchronises the bot's slash commands.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        scope : str or None, optional
            The scope of the unsynchronisation. Can be 'global' or 'guild'.

        Sends
        -----
        discord.Embed
            A message indicating the result of the unsynchronisation operation.
        """
        if scope == "global":
            embed = discord.Embed(description="Unsyncing commands globally...", color=0xFFFF00)
            message = await context.send(embed=embed)
            self.bot.tree.clear_commands(guild=None)
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                description=f"Slash commands have been globally unsynchronised. {len(synced)} command(s) remaining.",
                color=0xBEBEFE,
            )
            await message.edit(embed=embed)
            return
        if scope == "guild":
            if context.guild is None:
                embed = discord.Embed(description="This command must be used in a guild.", color=0xE02B2B)
                await context.send(embed=embed)
                return
            embed = discord.Embed(description="Unsyncing commands in this guild...", color=0xFFFF00)
            message = await context.send(embed=embed)
            self.bot.tree.clear_commands(guild=context.guild)
            synced = await self.bot.tree.sync(guild=context.guild)
            embed = discord.Embed(
                description=f"Slash commands have been unsynchronised in this guild. {len(synced)} command(s) remaining.",
                color=0xBEBEFE,
            )
            await message.edit(embed=embed)
            return
        embed = discord.Embed(description="The scope must be `global` or `guild`.", color=0xE02B2B)
        await context.send(embed=embed)

    @commands.hybrid_group(name="database", description="Database management commands")
    @commands.is_owner()
    async def database(self, context: Context) -> None:
        """
        Command group for database management.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        if context.invoked_subcommand is None:
            await context.send("Please specify a subcommand: reset")

    @database.command(name="reset", description="Reset all database tables (requires confirmation)")
    @commands.is_owner()
    async def database_reset(self, context: Context) -> None:
        """
        Reset all database tables after confirmation.

        This command will drop all existing tables and recreate them using
        the schema defined in the Database class. All data will be lost.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        await context.defer(ephemeral=True)

        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ Database Reset Confirmation",
            description=(
                "**WARNING:** This action will:\n"
                "• Drop all existing database tables\n"
                "• Delete all data permanently\n"
                "• Recreate empty tables with the current schema\n\n"
                "**This action cannot be undone!**\n\n"
                "Do you want to proceed?"
            ),
            colour=discord.Colour.red(),
        )
        embed.set_footer(text="This confirmation will expire in 60 seconds")

        # Create view with approval buttons
        view = DatabaseResetConfirmView()
        message = await context.send(embed=embed, view=view)

        # Wait for user response
        await view.wait()

        # Disable all buttons after response or timeout
        for item in view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        if view.approved is None:
            # Timeout - no response
            embed = discord.Embed(
                title="⏱️ Confirmation Timeout",
                description="Database reset cancelled due to timeout.",
                colour=discord.Colour.orange(),
            )
            await message.edit(embed=embed, view=view)
            return

        if not view.approved:
            # User declined
            embed = discord.Embed(
                title="❌ Database Reset Cancelled",
                description="Database reset has been cancelled.",
                colour=discord.Colour.green(),
            )
            await view.interaction.response.edit_message(embed=embed, view=view)  # type: ignore[union-attr]
            return

        # User approved - proceed with reset
        if view.interaction:
            await view.interaction.response.edit_message(
                embed=discord.Embed(
                    title="🔄 Resetting Database...",
                    description="Dropping tables and recreating schema...",
                    colour=discord.Colour.yellow(),
                ),
                view=view,
            )

        try:
            # Drop all existing tables
            tables_dropped = self.bot.database.drop_all_tables()

            # Recreate schema
            self.bot.database.initialise_schema()
            self.bot.logger.info("Database schema recreated successfully")  # type: ignore[attr-defined]

            # Update the ephemeral confirmation message
            embed = discord.Embed(
                title="✅ Database Reset Complete",
                description="Database has been successfully reset. See the channel for details.",
                colour=discord.Colour.green(),
            )
            await message.edit(embed=embed, view=view)

            # Send public success message to the channel
            public_embed = discord.Embed(
                title="✅ Database Reset Complete",
                description=(
                    f"Successfully reset the database:\n"
                    f"• Dropped {tables_dropped} table(s)\n"
                    f"• Recreated schema with empty tables\n\n"
                    f"The database is now ready for use."
                ),
                colour=discord.Colour.green(),
            )
            public_embed.set_footer(text=f"Reset by {context.author.name}")
            await context.send(embed=public_embed, ephemeral=True)

        except Exception as e:
            self.bot.logger.error("Error resetting database: %s", e)  # type: ignore[attr-defined]
            embed = discord.Embed(
                title="❌ Database Reset Failed",
                description=f"An error occurred while resetting the database:\n```{e}```",
                colour=discord.Colour.red(),
            )
            await message.edit(embed=embed, view=view)


async def setup(bot: DiscordBot) -> None:
    """
    Loads the Utils cog into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(Utils(bot))
