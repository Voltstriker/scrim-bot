import os
from pathlib import Path

import discord
from dotenv import load_dotenv

from utils import database, discord_bot, logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.LoggingFormatter.start_logging(
    log_name="scrim_bot",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_path=os.getenv("LOG_PATH"),
)

# Check if database exists and initialize if needed
db_path = os.getenv("DATABASE_PATH")
if db_path:
    db_file = Path(db_path)
    db_exists = db_file.exists()

    if not db_exists:
        logger.info(f"Database file not found at {db_path}. Creating and initializing...")
        db = database.Database(database_path=db_path, logger=logger)
        with db:
            db.initialize_schema()
        logger.info("Database created and initialized successfully")
    else:
        logger.info(f"Database file found at {db_path}")
else:
    logger.error("DATABASE_PATH not set in environment variables")
    raise ValueError("Missing DATABASE_PATH in environment variables.")

# Create bot instance
intents = discord.Intents.all()
bot = discord_bot.DiscordBot(logger=logger, intents=intents)

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
