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
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from models import Game, Map  # pylint: disable=import-error

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


class MapManagement(commands.Cog, name="Map Management"):
    """
    A collection of map management commands for the Discord bot.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the MapManagement cog.
    maps_list(context, game_id)
        Lists all maps in the database, optionally filtered by game.
    maps_add(context, name, mode, game_id, experience_code)
        Adds a new map to the database.
    maps_edit(context, map_id, name, mode, experience_code)
        Updates an existing map in the database.
    maps_remove(context, map_id)
        Deletes a map from the database.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the MapManagement cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    ################################################
    # Map Management Commands
    ################################################
    async def game_autocomplete(
        self, interaction: discord.Interaction, current: str  # pylint: disable=unused-argument
    ) -> list[app_commands.Choice[str]]:
        """
        Autocomplete callback for game selection.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the autocomplete.
        current : str
            The current text the user has typed.

        Returns
        -------
        list[app_commands.Choice[str]]
            List of game name choices matching the current input.
        """
        games = Game.get_all(self.bot.database)
        # Filter games by current input (case-insensitive)
        filtered_games = [game for game in games if current.lower() in game.name.lower()][:25]  # Discord limits autocomplete to 25 choices

        return [app_commands.Choice(name=game.name, value=game.name) for game in filtered_games]

    async def map_autocomplete(
        self, interaction: discord.Interaction, current: str  # pylint: disable=unused-argument
    ) -> list[app_commands.Choice[str]]:
        """
        Autocomplete callback for map selection.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the autocomplete.
        current : str
            The current text the user has typed.

        Returns
        -------
        list[app_commands.Choice[str]]
            List of map choices matching the current input, formatted with game and mode info.
        """
        maps = Map.get_all(self.bot.database)

        # Build formatted choices with game information
        choices = []
        for map_obj in maps:
            game = Game.get_by_id(self.bot.database, map_obj.game_id)
            game_name = game.name if game else "Unknown"

            # Format: "{Map Name} - {Game Mode} ({Experience Code}) ({Game Name})"
            if map_obj.experience_code:
                display_name = f"{map_obj.name} - {map_obj.mode} ({map_obj.experience_code}) ({game_name})"
            else:
                display_name = f"{map_obj.name} - {map_obj.mode} ({game_name})"

            # Filter by current input (search in display name)
            if current.lower() in display_name.lower():
                choices.append(app_commands.Choice(name=display_name[:100], value=str(map_obj.id)))

            if len(choices) >= 25:  # Discord limits autocomplete to 25 choices
                break

        return choices

    @commands.hybrid_command(name="maps", description="List all maps in the database")
    @app_commands.autocomplete(game=game_autocomplete)
    async def maps(self, context: Context, game: Optional[str] = None) -> None:
        """
        List all maps in the database, optionally filtered by game.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        game : str, optional
            Filter maps by game name (with autocomplete).
        """
        await context.defer()
        try:
            if game:
                # Find game by name
                games = Game.get_all(self.bot.database)
                game_obj = next((g for g in games if g.name.lower() == game.lower()), None)

                if not game_obj:
                    await context.send(f"❌ No game found with name '{game}'.")
                    return

                maps = Map.get_by_game(self.bot.database, game_obj.id)
                title = f"🗺️ Maps for {game_obj.name}"
            else:
                # Get all maps
                maps = Map.get_all(self.bot.database)
                title = "🗺️ All Maps"

            if not maps:
                await context.send("No maps found in the database.")
                return

            # Group maps by game, then by map name
            game_map_groups = defaultdict(lambda: defaultdict(list))

            for map_obj in maps:
                game_for_map = Game.get_by_id(self.bot.database, map_obj.game_id)
                game_name = game_for_map.name if game_for_map else "Unknown"
                game_map_groups[game_name][map_obj.name].append(map_obj)

            # Create embed with grouped map list
            embed = discord.Embed(
                title=title,
                description=f"Found {len(maps)} map(s).",
                colour=discord.Colour.blue(),
            )

            # Add grouped maps as fields (max 25 fields per embed)
            field_count = 0
            for game_name in sorted(game_map_groups.keys()):
                for map_name in sorted(game_map_groups[game_name].keys()):
                    if field_count >= 25:
                        break

                    map_variants = game_map_groups[game_name][map_name]

                    # Build value string with all modes for this map
                    value_parts = []
                    for map_obj in map_variants:
                        if map_obj.experience_code:
                            mode_info = f"• Mode: **{map_obj.mode}** (`{map_obj.experience_code}`)"
                        else:
                            mode_info = f"• Mode: **{map_obj.mode}**"
                        value_parts.append(mode_info)

                    field_name = f"{map_name}" if game else f"{map_name} - {game_name}"
                    field_value = "\n".join(value_parts)

                    embed.add_field(
                        name=field_name,
                        value=field_value,
                        inline=False,
                    )
                    field_count += 1

                if field_count >= 25:
                    break

            if field_count >= 25:
                embed.set_footer(text=f"Showing first 25 map groups of {len(maps)} total maps")
            else:
                embed.set_footer(text=f"Requested by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error listing maps: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while listing maps: {e}")

    @commands.hybrid_group(name="map", description="Manage maps in the database")
    async def map(self, context: Context) -> None:
        """
        Command group for managing maps.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        if context.invoked_subcommand is None:
            await context.send("Please specify a subcommand: add, edit, or remove.")

    @map.command(name="add", description="Add a new map to the database")
    @commands.is_owner()
    @app_commands.autocomplete(game=game_autocomplete)
    async def map_add(self, context: Context, name: str, mode: str, game: str, experience_code: Optional[str] = None) -> None:
        """
        Add a new map to the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        name : str
            The name of the map.
        mode : str
            The game mode for this map.
        game : str
            The name of the game this map belongs to (with autocomplete).
        experience_code : str, optional
            Unique code from the video game that identifies the map.
        """
        await context.defer()
        try:
            # Find game by name
            games = Game.get_all(self.bot.database)
            game_obj = next((g for g in games if g.name.lower() == game.lower()), None)

            if not game_obj:
                await context.send(f"❌ No game found with name '{game}'.")
                return

            # Check if map already exists for this game
            existing_maps = Map.get_by_game(self.bot.database, game_obj.id)
            for existing_map in existing_maps:
                if existing_map.name.lower() == name.lower() and existing_map.mode.lower() == mode.lower():
                    await context.send(f"❌ A map with the name '{name}' and mode '{mode}' already exists for {game_obj.name}.")
                    return

            # Create and save the new map
            new_map = Map(id=0, name=name, mode=mode, game_id=game_obj.id, experience_code=experience_code)
            map_id = new_map.save(self.bot.database)

            # Create success embed
            embed = discord.Embed(
                title="✅ Map Added",
                description="Successfully added map to the database.",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="ID", value=str(map_id), inline=True)
            embed.add_field(name="Name", value=name, inline=True)
            embed.add_field(name="Mode", value=mode, inline=True)
            embed.add_field(name="Game", value=game_obj.name, inline=True)
            embed.add_field(name="Experience Code", value=experience_code if experience_code else "None", inline=True)
            embed.set_footer(text=f"Added by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error adding map: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while adding the map: {e}")

    @map.command(name="edit", description="Update an existing map in the database")
    @commands.is_owner()
    @app_commands.autocomplete(selected_map=map_autocomplete)
    async def map_edit(
        self,
        context: Context,
        selected_map: str,
        name: Optional[str] = None,
        mode: Optional[str] = None,
        experience_code: Optional[str] = None,
    ) -> None:
        """
        Update an existing map in the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        selected_map : str
            The ID of the map to update (with autocomplete).
        name : str, optional
            The new name for the map.
        mode : str, optional
            The new game mode for the map.
        experience_code : str, optional
            The new experience code for the map.
        """
        await context.defer()
        try:
            # Parse map_id from autocomplete value
            try:
                map_id_int = int(selected_map)
            except ValueError:
                await context.send(f"❌ Invalid map ID: {selected_map}.")
                return

            # Check if map exists
            map_obj = Map.get_by_id(self.bot.database, map_id_int)
            if not map_obj:
                await context.send(f"❌ No map found with ID {map_id_int}.")
                return

            # Update fields if provided
            if name is not None:
                object.__setattr__(map_obj, "name", name)

            if mode is not None:
                object.__setattr__(map_obj, "mode", mode)

            if experience_code is not None:
                object.__setattr__(map_obj, "experience_code", experience_code)

            # Save the updated map
            map_obj.save(self.bot.database)

            # Get game name for display
            game = Game.get_by_id(self.bot.database, map_obj.game_id)
            game_name = game.name if game else "Unknown"

            # Create success embed
            embed = discord.Embed(
                title="✅ Map Updated",
                description="Successfully updated map in the database.",
                colour=discord.Colour.green(),
            )
            embed.add_field(name="ID", value=str(map_obj.id), inline=True)
            embed.add_field(name="Name", value=map_obj.name, inline=True)
            embed.add_field(name="Mode", value=map_obj.mode, inline=True)
            embed.add_field(name="Game", value=game_name, inline=True)
            embed.add_field(name="Experience Code", value=map_obj.experience_code if map_obj.experience_code else "None", inline=True)
            embed.set_footer(text=f"Updated by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error updating map: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while updating the map: {e}")

    @map.command(name="remove", description="Delete a map from the database")
    @commands.is_owner()
    @app_commands.autocomplete(selected_map=map_autocomplete)
    async def map_remove(self, context: Context, selected_map: str) -> None:
        """
        Delete a map from the database.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        selected_map : str
            The ID of the map to delete (with autocomplete).
        """
        await context.defer()
        try:
            # Parse map_id from autocomplete value
            try:
                map_id_int = int(selected_map)
            except ValueError:
                await context.send(f"❌ Invalid map ID: {selected_map}.")
                return

            # Check if map exists
            map_obj = Map.get_by_id(self.bot.database, map_id_int)
            if not map_obj:
                await context.send(f"❌ No map found with ID {map_id_int}.")
                return

            # Store map details for confirmation message
            map_name = map_obj.name
            map_mode = map_obj.mode
            game = Game.get_by_id(self.bot.database, map_obj.game_id)
            game_name = game.name if game else "Unknown"

            # Delete the map
            rows_deleted = map_obj.delete(self.bot.database)

            if rows_deleted > 0:
                # Create success embed
                embed = discord.Embed(
                    title="✅ Map Deleted",
                    description="Successfully deleted map from the database.",
                    colour=discord.Colour.red(),
                )
                embed.add_field(name="ID", value=str(map_id_int), inline=True)
                embed.add_field(name="Name", value=map_name, inline=True)
                embed.add_field(name="Mode", value=map_mode, inline=True)
                embed.add_field(name="Game", value=game_name, inline=True)
                embed.set_footer(text=f"Deleted by {context.author.name}")

                await context.send(embed=embed)
            else:
                await context.send(f"❌ Failed to delete map with ID {map_id_int}.")

        except Exception as e:
            self.bot.logger.error("Error deleting map: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while deleting the map: {e}")


async def setup(bot: DiscordBot) -> None:
    """
    Loads the GameManagement and MapManagement cogs into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.
    """
    await bot.add_cog(GameManagement(bot))
    await bot.add_cog(MapManagement(bot))
