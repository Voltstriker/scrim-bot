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


import discord
from discord.ext import commands
from discord.ext.commands import Context


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
    say(context, message)
        Sends a message as the bot in the current channel.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialises the General cog.

        Parameters
        ----------
        bot : discord.ext.commands.Bot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    @commands.hybrid_command(name="info", description="Get information about the bot")
    @commands.is_owner()
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
        await context.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """
    Loads the General cog into the bot.

    Parameters
    ----------
    bot : discord.ext.commands.Bot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(General(bot))
