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
Game management commands for the Discord bot.

This module defines the GameManagement cog, which provides commands for
bot owners to manage games in the database.

Classes
-------
GameManagement
    A collection of game management commands for the Discord bot.

Functions
---------
setup(bot)
    Loads the GameManagement cog into the bot.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands import Context

from models import Game  # pylint: disable=import-error

if TYPE_CHECKING:
    from utils.discord_bot import DiscordBot  # pylint: disable=import-error,no-name-in-module


class GameManagement(commands.Cog, name="Game Management"):
    """
    A collection of game management commands for the Discord bot.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the GameManagement cog.
    games_add(context, name, series)
        Adds a new game to the database.
    games_list(context)
        Lists all games in the database.
    games_update(context, game_id, name, series)
        Updates an existing game in the database.
    games_delete(context, game_id)
        Deletes a game from the database.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the GameManagement cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    ################################################
    # Game Management Commands
    ################################################
    @commands.hybrid_group(name="games", description="Manage games in the database")
    async def games(self, context: Context) -> None:
        """
        Command group for managing games.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        if context.invoked_subcommand is None:
            await context.send("Please specify a subcommand: add, list, update, or delete.")

    @games.command(name="add", description="Add a new game to the database")
    @commands.is_owner()
    async def games_add(self, context: Context, name: str, series: Optional[str] = None) -> None:
        """
        Add a new game to the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        name : str
            The name of the game.
        series : str, optional
            The game series/franchise name.
        """
        await context.defer()
        try:
            # Check if game already exists
            existing_games = Game.get_all(self.bot.database)
            for existing_game in existing_games:
                if existing_game.name.lower() == name.lower():
                    await context.send(f"❌ A game with the name '{name}' already exists.")
                    return

            # Create and save the new game
            game = Game(id=0, name=name, series=series)
            game_id = game.save(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Game Added",
                description="Successfully added game to the database.",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="ID", value=str(game_id), inline=True)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Series", value=series if series else "None", inline=True)
            embed.set_footer(text=f"Added by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error adding game: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while adding the game: {e}")

    @games.command(name="list", description="List all games in the database")
    async def games_list(self, context: Context) -> None:
        """
        List all games in the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        await context.defer()
        try:
            games = Game.get_all(self.bot.database)

            if not games:
                await context.send("No games found in the database.")
                return

            # Create embed with game list
            embed = discord.Embed(
                title="🎮 Games Database",
                description=f"Found {len(games)} game(s) in the database.",
                colour=discord.Colour.blue(),
            )

            # Add games as fields (max 25 fields per embed)
            for game in games[:25]:
                series_text = f" ({game.series})" if game.series else ""
                embed.add_field(
                    name=f"{game.name}{series_text}",
                    value=f"ID: {game.id}",
                    inline=True,
                )

            if len(games) > 25:
                embed.set_footer(text=f"Showing first 25 of {len(games)} games")
            else:
                embed.set_footer(text=f"Requested by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error listing games: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while listing games: {e}")

    @games.command(name="update", description="Update an existing game in the database")
    @commands.is_owner()
    async def games_update(self, context: Context, game_id: int, name: Optional[str] = None, series: Optional[str] = None) -> None:
        """
        Update an existing game in the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        game_id : int
            The ID of the game to update.
        name : str, optional
            The new name for the game.
        series : str, optional
            The new series/franchise name.
        """
        await context.defer()
        try:
            # Check if game exists
            game = Game.get_by_id(self.bot.database, game_id)
            if not game:
                await context.send(f"❌ No game found with ID {game_id}.")
                return

            # Update fields if provided
            if name is not None:
                # Check if new name already exists (excluding current game)
                existing_games = Game.get_all(self.bot.database)
                for existing_game in existing_games:
                    if existing_game.id != game_id and existing_game.name.lower() == name.lower():
                        await context.send(f"❌ A game with the name '{name}' already exists.")
                        return
                object.__setattr__(game, "name", name)

            if series is not None:
                object.__setattr__(game, "series", series)

            # Save the updated game
            game.save(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Game Updated",
                description="Successfully updated game in the database.",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="ID", value=str(game.id), inline=True)
            embed.add_field(name="Name", value=game.name, inline=True)
            embed.add_field(name="Series", value=game.series if game.series else "None", inline=True)
            embed.set_footer(text=f"Updated by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error updating game: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while updating the game: {e}")

    @games.command(name="delete", description="Delete a game from the database")
    @commands.is_owner()
    async def games_delete(self, context: Context, game_id: int) -> None:
        """
        Delete a game from the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        game_id : int
            The ID of the game to delete.
        """
        await context.defer()
        try:
            # Check if game exists
            game = Game.get_by_id(self.bot.database, game_id)
            if not game:
                await context.send(f"❌ No game found with ID {game_id}.")
                return

            # Store game details for confirmation message
            game_name = game.name
            game_series = game.series

            # Delete the game
            rows_deleted = game.delete(self.bot.database)

            if rows_deleted > 0:
                # Create success embed
                embed = discord.Embed(
                    title="✅ Game Deleted",
                    description="Successfully deleted game from the database.",
                    colour=discord.Colour.red(),
                )
                embed.add_field(name="ID", value=str(game_id), inline=True)
                embed.add_field(name="Name", value=game_name, inline=True)
                embed.add_field(name="Series", value=game_series if game_series else "None", inline=True)
                embed.set_footer(text=f"Deleted by {context.author.name}")

                await context.send(embed=embed)
            else:
                await context.send(f"❌ Failed to delete game with ID {game_id}.")

        except Exception as e:
            self.bot.logger.error("Error deleting game: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while deleting the game: {e}")


async def setup(bot: DiscordBot) -> None:
    """
    Loads the GameManagement cog into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(GameManagement(bot))
