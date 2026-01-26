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
Admin management commands for the Discord bot.

This module defines the AdminManagement cog, which provides commands for
managing bot administrators. Only the bot owner can use these commands.

Classes
-------
AdminManagement
    A collection of admin management commands for the Discord bot.

Functions
---------
setup(bot)
    Loads the AdminManagement cog into the bot.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Union

import discord
from discord.ext import commands
from discord.ext.commands import Context

from models import BotAdminConfig, User  # pylint: disable=import-error

if TYPE_CHECKING:
    from utils.discord_bot import DiscordBot  # pylint: disable=import-error,no-name-in-module


class AdminManagement(commands.Cog, name="Admin Management"):
    """
    A collection of admin management commands for the Discord bot.

    Attributes
    ----------
    bot : DiscordBot
        The bot instance to which this cog is attached.

    Methods
    -------
    __init__(bot)
        Initialises the AdminManagement cog.
    admin(context)
        Command group for managing admins.
    admin_add(context, target)
        Adds a user or role as a bot administrator.
    admin_remove(context, target)
        Removes a user or role from bot administrators.
    admins_list(context)
        Lists all bot administrators.
    """

    def __init__(self, bot: DiscordBot) -> None:
        """
        Initialises the AdminManagement cog.

        Parameters
        ----------
        bot : DiscordBot
            The bot instance to which this cog is attached.
        """
        self.bot = bot

    ################################################
    # Admin Management Commands
    ################################################
    @commands.hybrid_group(name="admin", description="Manage bot administrators")
    @commands.is_owner()
    async def admin(self, context: Context) -> None:
        """
        Command group for managing bot administrators.

        Only the bot owner can use these commands.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        if context.invoked_subcommand is None:
            await context.send("Please specify a subcommand: add or remove.")

    @admin.command(name="add", description="Add a user or role as a bot administrator")
    @commands.is_owner()
    async def admin_add(self, context: Context, target: Union[discord.Member, discord.User, discord.Role]) -> None:
        """
        Add a user or role as a bot administrator.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        target : Union[discord.Member, discord.User, discord.Role]
            The user or role to add as an administrator.
        """
        await context.defer()

        try:
            if isinstance(target, (discord.User, discord.Member)):
                # Adding a user as admin
                existing = BotAdminConfig.get_by_user_id(self.bot.database, str(target.id))
                if existing:
                    await context.send(f"❌ {target.mention} is already a bot administrator.")
                    return

                # Ensure user exists in users table
                user = User.get_by_discord_id(self.bot.database, str(target.id))
                if not user:
                    user = User(
                        id=0,
                        discord_id=str(target.id),
                        display_name=target.display_name,
                        created_date=datetime.now(),
                    )
                    user.save(self.bot.database)

                # Ensure the command author exists in users table
                author_user = User.get_by_discord_id(self.bot.database, str(context.author.id))
                if not author_user:
                    author_user = User(
                        id=0,
                        discord_id=str(context.author.id),
                        display_name=context.author.display_name,
                        created_date=datetime.now(),
                    )
                    author_user.save(self.bot.database)

                # Create user admin configuration
                admin_config = BotAdminConfig(
                    id=0,
                    discord_user_id=str(target.id),
                    discord_server_id=None,
                    discord_role_id=None,
                    scope="user",
                    admin=True,
                    created_date=datetime.now(),
                    created_by=author_user.id,
                    updated_date=None,
                    updated_by=None,
                )
                admin_config.save(self.bot.database)

                embed = discord.Embed(
                    title="✅ Administrator Added",
                    description=f"User {target.mention} has been added as a bot administrator.",
                    colour=discord.Colour.green(),
                )
                embed.add_field(name="User ID", value=str(target.id), inline=True)
                embed.add_field(name="Scope", value="User", inline=True)
                embed.set_footer(text=f"Added by {context.author.name}")

            elif isinstance(target, discord.Role):
                # Adding a role as admin
                if not context.guild:
                    await context.send("❌ Role administrators can only be added in a server.")
                    return

                existing = BotAdminConfig.get_by_server_and_role(self.bot.database, str(context.guild.id), str(target.id))
                if existing:
                    await context.send(f"❌ Role {target.mention} is already a bot administrator.")
                    return

                # Ensure the command author exists in users table
                author_user = User.get_by_discord_id(self.bot.database, str(context.author.id))
                if not author_user:
                    author_user = User(
                        id=0,
                        discord_id=str(context.author.id),
                        display_name=context.author.display_name,
                        created_date=datetime.now(),
                    )
                    author_user.save(self.bot.database)

                # Create role admin configuration
                admin_config = BotAdminConfig(
                    id=0,
                    discord_user_id=None,
                    discord_server_id=str(context.guild.id),
                    discord_role_id=str(target.id),
                    scope="role",
                    admin=True,
                    created_date=datetime.now(),
                    created_by=author_user.id,
                    updated_date=None,
                    updated_by=None,
                )
                admin_config.save(self.bot.database)

                embed = discord.Embed(
                    title="✅ Administrator Added",
                    description=f"Role {target.mention} has been added as a bot administrator.",
                    colour=discord.Colour.green(),
                )
                embed.add_field(name="Server ID", value=str(context.guild.id), inline=True)
                embed.add_field(name="Role ID", value=str(target.id), inline=True)
                embed.add_field(name="Scope", value="Role", inline=True)
                embed.set_footer(text=f"Added by {context.author.name}")

            else:
                await context.send("❌ Target must be a user or role.")
                return

            await context.send(embed=embed)

        except ValueError as ve:
            self.bot.logger.error("Error adding admin: %s", ve)  # type: ignore[attr-defined]
            await context.send(f"❌ Failed to add administrator: {ve}")
        except Exception as e:
            self.bot.logger.error("Error adding admin: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while adding administrator: {e}")

    @admin.command(name="remove", description="Remove a user or role from bot administrators")
    @commands.is_owner()
    async def admin_remove(self, context: Context, target: Union[discord.Member, discord.User, discord.Role]) -> None:
        """
        Remove a user or role from bot administrators.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        target : Union[discord.Member, discord.User, discord.Role]
            The user or role to remove from administrators.
        """
        await context.defer()

        try:
            if isinstance(target, (discord.User, discord.Member)):
                # Prevent removal of bot owner
                app_info = await self.bot.application_info()
                if app_info.owner and target.id == app_info.owner.id:
                    await context.send("❌ Cannot remove the bot owner from administrators.")
                    return

                # Removing a user admin
                admin_config = BotAdminConfig.get_by_user_id(self.bot.database, str(target.id))
                if not admin_config:
                    await context.send(f"❌ {target.mention} is not a bot administrator.")
                    return

                admin_config.delete(self.bot.database)

                embed = discord.Embed(
                    title="✅ Administrator Removed",
                    description=f"User {target.mention} has been removed from bot administrators.",
                    colour=discord.Colour.orange(),
                )
                embed.add_field(name="User ID", value=str(target.id), inline=True)
                embed.set_footer(text=f"Removed by {context.author.name}")

            elif isinstance(target, discord.Role):
                # Removing a role admin
                if not context.guild:
                    await context.send("❌ Role administrators can only be removed in a server.")
                    return

                admin_config = BotAdminConfig.get_by_server_and_role(self.bot.database, str(context.guild.id), str(target.id))
                if not admin_config:
                    await context.send(f"❌ Role {target.mention} is not a bot administrator.")
                    return

                admin_config.delete(self.bot.database)

                embed = discord.Embed(
                    title="✅ Administrator Removed",
                    description=f"Role {target.mention} has been removed from bot administrators.",
                    colour=discord.Colour.orange(),
                )
                embed.add_field(name="Server ID", value=str(context.guild.id), inline=True)
                embed.add_field(name="Role ID", value=str(target.id), inline=True)
                embed.set_footer(text=f"Removed by {context.author.name}")

            else:
                await context.send("❌ Target must be a user or role.")
                return

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error removing admin: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while removing administrator: {e}")

    @commands.hybrid_command(name="admins", description="List all bot administrators")
    @commands.is_owner()
    async def admins_list(self, context: Context) -> None:
        """
        List all bot administrators.

        Parameters
        ----------
        context : discord.ext.commands.Context
            The context in which the command was invoked.
        """
        await context.defer()

        try:
            admins = BotAdminConfig.get_all(self.bot.database)

            if not admins:
                await context.send("No administrators found in the database.")
                return

            # Create embed with admin list
            embed = discord.Embed(
                title="👑 Bot Administrators",
                description=f"Found {len(admins)} administrator(s).",
                colour=discord.Colour.gold(),
            )

            user_admins = []
            role_admins = []

            for admin in admins:
                if admin.scope == "user" and admin.discord_user_id:
                    user_admins.append(self._format_user_admin(admin))
                elif admin.scope == "role" and admin.discord_role_id and admin.discord_server_id:
                    role_admins.append(await self._format_role_admin(admin))

            if user_admins:
                embed.add_field(name="👤 User Administrators", value="\n".join(user_admins), inline=False)

            if role_admins:
                embed.add_field(name="🎭 Role Administrators", value="\n".join(role_admins), inline=False)

            embed.set_footer(text=f"Requested by {context.author.name}")

            await context.send(embed=embed)

        except Exception as e:
            self.bot.logger.error("Error listing admins: %s", e)  # type: ignore[attr-defined]
            await context.send(f"❌ An error occurred while listing administrators: {e}")

    def _format_user_admin(self, admin: BotAdminConfig) -> str:
        """
        Format a user admin entry for display.

        Parameters
        ----------
        admin : BotAdminConfig
            The admin configuration to format.

        Returns
        -------
        str
            Formatted user admin string.
        """
        return f"• <@{admin.discord_user_id}> (ID: {admin.discord_user_id})"

    async def _format_role_admin(self, admin: BotAdminConfig) -> str:
        """
        Format a role admin entry for display.

        Parameters
        ----------
        admin : BotAdminConfig
            The admin configuration to format.

        Returns
        -------
        str
            Formatted role admin string.
        """
        guild = self.bot.get_guild(int(admin.discord_server_id))  # type: ignore[arg-type]
        if not guild:
            return f"• Role ID: {admin.discord_role_id} in Server ID: {admin.discord_server_id} *(Server not found)*"

        role = guild.get_role(int(admin.discord_role_id))  # type: ignore[arg-type]
        if not role:
            return f"• Role ID: {admin.discord_role_id} in {guild.name} *(Role not found)*"

        return f"• {role.mention} in {guild.name} (Role ID: {admin.discord_role_id})"


async def setup(bot: DiscordBot) -> None:
    """
    Loads the AdminManagement cog into the bot.

    Parameters
    ----------
    bot : DiscordBot
        The bot instance to load the cog into.
    """
    await bot.add_cog(AdminManagement(bot))
