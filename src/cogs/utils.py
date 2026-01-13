# Copyright 2025 Sons of Valour

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

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


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
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialises the Utils cog.

        Parameters
        ----------
        bot : discord.ext.commands.Bot
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
        elif scope == "guild":
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


async def setup(bot: commands.Bot) -> None:
    """
    Loads the Utils cog into the bot.

    Parameters
    ----------
    bot : discord.ext.commands.Bot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(Utils(bot))
