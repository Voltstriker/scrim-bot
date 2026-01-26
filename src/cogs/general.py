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
General commands and features for the Discord bot.

This module defines the General cog, which provides basic commands for bot owners,
including the ability to send messages as the bot.

Classes
-------
General
    A collection of general commands for the Discord bot.

Functions
---------
setup(bot)
    Loads the General cog into the bot.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Context

from models import User  # pylint: disable=import-error

if TYPE_CHECKING:
    from utils.discord_bot import DiscordBot  # pylint: disable=import-error,no-name-in-module


class General(commands.Cog, name="General"):
    """
    A collection of general commands for the Discord bot.

    Attributes
    ----------
    bot : discord.ext.commands.Bot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the General cog.
    info(context)
        Display information about the bot.
    displayname(context, name)
        Set the user's display name in the bot.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the General cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    @commands.hybrid_command(name="info", description="Get information about the bot")
    async def info(self, context: Context) -> None:
        """Display information about the bot

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        embed = discord.Embed(
            title="Scrim Bot",
            description="**Scrim Bot** is a Discord Bot designed to assist competitive teams with organising and challenging other teams to practice scrims or matches.",  # pylint: disable=line-too-long
            color=discord.Color.blue(),
        )
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.set_footer(text=f"Requested by {context.author.name}")
        await context.send(embed=embed, ephemeral=True)

    @commands.hybrid_command(name="displayname", description="Set your display name in the bot")
    async def displayname(self, context: Context, *, name: str) -> None:
        """
        Set your display name in the bot.

        If you are not registered in the users table, you will be added automatically.
        This display name is used when the bot shows team memberships and other information.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        name : str
            The display name to set.
        """
        await context.defer()

        discord_id = str(context.author.id)

        # Check if user exists in the database
        user = User.get_by_discord_id(self.bot.database, discord_id)

        if user:
            # Update existing user's display name
            object.__setattr__(user, "display_name", name)
            user.save(self.bot.database)
            embed = discord.Embed(
                title="Display Name Updated",
                description=f"Your display name has been updated to **{name}**.",
                color=discord.Color.green(),
            )
        else:
            # Create new user with display name
            user = User(id=0, discord_id=discord_id, display_name=name, created_date=datetime.now())
            user.save(self.bot.database)
            embed = discord.Embed(
                title="Display Name Set",
                description=f"You have been registered in the bot with display name **{name}**.",
                color=discord.Color.green(),
            )

        embed.set_footer(text=f"Requested by {context.author.name}")
        await context.send(embed=embed, ephemeral=True)


async def setup(bot: DiscordBot) -> None:
    """
    Loads the General cog into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(General(bot))
