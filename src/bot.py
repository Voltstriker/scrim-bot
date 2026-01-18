"""
Main entry point for Scrim Bot.

This module initialises the Discord bot, sets up logging, checks for and
initialises the database if needed, and launches the bot with the configured
Discord token.
"""

import os
from pathlib import Path

import discord
from dotenv import load_dotenv

from utils import database, discord_bot, logging  # pylint: disable=no-name-in-module

# Load environment variables from .env file
load_dotenv()

# Set up logging (without database handler initially)
logger = logging.LoggingFormatter.start_logging(
    log_name="scrim_bot",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_path=os.getenv("LOG_PATH"),
)

# Check if database exists and initialise if needed
db_path = os.getenv("DATABASE_PATH")
if db_path:
    db_file = Path(db_path)
    needs_initialisation = False

    if not db_file.exists():
        logger.info("Database file not found at %s. Creating and initialising...", db_path)
        needs_initialisation = True
    else:
        logger.info("Database file found at %s", db_path)
        # Check if the schema has been initialised by verifying logs table exists
        db = database.Database(database_path=db_path, logger=logger)
        with db:
            if not db.table_exists("logs"):
                logger.warning("Database file exists but schema not initialised. Initialising schema...")
                needs_initialisation = True

    # Initialise schema if needed
    if needs_initialisation:
        db = database.Database(database_path=db_path, logger=logger)
        with db:
            db.initialise_schema()

    # Now that database exists with schema, add database logging handler
    logging.add_database_handler(logger, db_path)
    logger.debug("Database logging handler enabled")

    # Create persistent database instance for the bot
    db_instance = database.Database(database_path=db_path, logger=logger)
    db_instance.connect()
    logger.debug("Persistent database connection established")
else:
    logger.error("DATABASE_PATH not set in environment variables")
    raise ValueError("Missing DATABASE_PATH in environment variables.")

# Create bot instance with database
intents = discord.Intents.all()
bot = discord_bot.DiscordBot(logger=logger, database=db_instance, intents=intents)

# Launch the Discord bot
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("Missing Discord secret token in environment variables.")

try:
    bot.run(token)
except discord.PrivilegedIntentsRequired as ex:
    logger.error("Privileged intents are required but not enabled for the bot. Please enable the necessary intents in the Discord Developer Portal.")
    raise ex
except Exception as ex:
    logger.error("An error occurred while running the bot.")
    raise ex
