# Scrim Bot - GitHub Copilot Instructions

## Project Overview

Scrim Bot is a Discord bot built with discord.py designed to help competitive gaming teams organise scrims (practice matches) and official match challenges against other teams.

### Core Concepts

- **Guilds**: Discord servers where the bot is installed (internally referred to as guilds, not "servers")
- **Teams**: Competitive teams registered on the bot with details including:
  - Team name (full name)
  - Shorthand name/tag
  - Competing game
  - Team members (linked to Discord users)
  - One or more team captains
- **Matches/Scrims**: Organised practice games between teams
- **Challenges**: Requests from one team to another for a match at a specific timeslot
  - Can be accepted, declined, or result in an alternative time suggestion
- **Leagues**: Groups of teams, where challenges can only be issued to teams within the same league
- **Direct Messages**: Users can interact with the bot via DMs for personal management

## Language and Spelling Convention

**IMPORTANT**: This project uses **Australian English** spelling throughout all code, documentation, and comments.

### Examples

- ✅ `initialise` not ~~initialize~~
- ✅ `colour` not ~~color~~
- ✅ `organise` not ~~organize~~
- ✅ `centre` not ~~center~~
- ✅ `behaviour` not ~~behavior~~
- ✅ `recognise` not ~~recognize~~

## Technical Stack

### Core Dependencies

- **Python**: 3.11+
- **discord.py**: 2.6.4+ (Discord API wrapper)
- **python-dotenv**: Environment variable management
- **SQLite**: Database for persistent storage

### Development Tools

- **Black**: Code formatter (line length: 150)
- **Pylint**: Linter with docstring requirements
- **Pyright**: Type checker

## Code Style and Standards

### Formatting

- **Line Length**: Maximum 150 characters
- **Code Formatter**: Black with Python 3.11 target
- **Type Hints**: Use type annotations throughout
- **Docstrings**: Required for all public functions, classes, and methods
  - Style: NumPy docstring format
  - Must include parameter documentation
  - Must include return value documentation
  - Must include raised exceptions documentation

### File Structure

```
src/
├── __init__.py
├── bot.py                 # Main bot entry point
├── cogs/                  # Discord.py cogs (command modules)
│   ├── general.py
│   └── utils.py
└── utils/                 # Utility modules
    ├── __init__.py
    ├── database.py        # Database operations
    ├── discord_bot.py     # Bot class and configuration
    └── logging.py         # Logging configuration
```

### Database

- **Type**: SQLite
- **Location**: Configured via `DATABASE_PATH` environment variable
- **Initialisation**: Automatic schema creation on first run if database doesn't exist
- **Access**: Use the `Database` class from `utils.database`
- **Schema**: Placeholder method `initialise_schema()` for table creation

### Logging

- Use the custom `LoggingFormatter` from `utils.logging`
- Log level configured via `LOG_LEVEL` environment variable
- Log path configured via `LOG_PATH` environment variable
- Logger instance passed to all major components

### Environment Variables

Required variables in `.env`:

- `DISCORD_TOKEN`: Bot authentication token
- `DATABASE_PATH`: Path to SQLite database file
- `LOG_LEVEL`: Logging level (e.g., INFO, DEBUG)
- `LOG_PATH`: Directory for log files

## Discord.py Patterns

### Bot Structure

- Use cogs for organising commands and features
- Main bot instance created in `bot.py`
- Custom bot class: `DiscordBot` in `utils.discord_bot`
- Intents: `discord.Intents.all()` (requires privileged intents enabled)

### Command Organisation

Commands should be organised into cogs based on functionality:

- General bot commands (help, info, etc.)
- Team management commands
- Match/scrim commands
- League management commands
- Administrative commands

### Error Handling

- Handle `discord.PrivilegedIntentsRequired` specifically
- Log all errors using the provided logger
- Provide user-friendly error messages in Discord responses

## Database Patterns

### Connection Management

Use context managers for database operations:

```python
with database.Database(database_path=db_path, logger=logger) as db:
    db.execute(query)
```

### Identifier Validation

All SQL identifiers (table names, column names) are automatically validated and quoted by the `Database` class to prevent SQL injection.

### CRUD Operations

The `Database` class provides methods for:

- `create_table()`: Create new tables with column definitions
- `insert()`: Insert records with automatic parameterisation
- `select()`: Query with WHERE clauses and ORDER BY
- `update()`: Update records with WHERE conditions
- `delete()`: Delete records with WHERE conditions
- `drop_table()`: Drop tables

## Data Model Considerations

When implementing the schema in `initialise_schema()`, consider:

### Teams Table

- Primary key (team ID)
- Team name (full)
- Team tag/shorthand
- Game being played
- League affiliation
- Creation timestamp

### Team Members Table

- Link between teams and Discord users
- Discord user ID
- Team ID (foreign key)
- Role (captain vs. regular member)
- Join date

### Matches/Scrims Table

- Match ID
- Challenging team (foreign key)
- Challenged team (foreign key)
- Proposed time
- Status (pending, accepted, declined, completed)
- Alternative time suggestions
- League ID

### Leagues Table

- League ID
- League name
- Game
- Settings/rules

## Security Considerations

- Never commit the `.env` file
- All database queries use parameterised statements
- SQL identifiers are validated before use
- Privileged intents must be enabled in Discord Developer Portal

## Testing Commands

When implementing new commands:

1. Test in both guild (server) and DM contexts
2. Verify permission checks for captain-only actions
3. Test error handling for invalid inputs
4. Ensure Australian English in all user-facing messages

## Common Patterns

### Checking Team Captain Status

When implementing commands that require captain permissions, check if the user is a team captain before allowing actions.

### League Validation

When creating challenges, verify both teams are in the same league.

### User Feedback

Always provide clear feedback to users:

- Success messages for completed actions
- Detailed error messages for failures
- Confirmation prompts for destructive actions

## Development Workflow

1. Install with dev dependencies: `python -m pip install -e .[dev]`
2. Make changes following style guidelines
3. Format code: Use the "Run Black Formatting" task
4. Check formatting: Use the "Check Black Formatting" task
5. Check types: Use the "Check Pyright Types" task
6. Check linting: Use the "Check Pylint Issues" task
7. Test the bot with a test Discord server

### Validation After Changes

**IMPORTANT**: After making any code changes, always run the following validation checks:

1. **Format the code** with Black:

   ```bash
   python -m black --verbose .
   ```

   Or use the VS Code task: "Run Black Formatting"

2. **Check formatting compliance**:

   ```bash
   python -m black --check --verbose .
   ```

   Or use the VS Code task: "Check Black Formatting"

3. **Check type annotations** with Pyright:

   ```bash
   python -m pyright
   ```

   Or use the VS Code task: "Check Pyright Types"

4. **Check code quality** with Pylint:
   ```bash
   python -m pylint **/*.py
   ```
   Or use the VS Code task: "Check Pylint Issues"

These checks ensure code quality, consistency, and adherence to project standards. Fix any issues reported before considering the changes complete.

## Maintaining These Instructions

When making significant changes to the project that would benefit from additional context in these instructions, please:

- **Review this file** and suggest updates to keep it current
- **Update the README.md** with any useful context or information that would help users understand new features
- **Add new sections** for major features, architectural patterns, or conventions
- **Update examples** when implementation patterns change
- **Document new tables/models** when extending the database schema
- **Add new cog categories** when introducing additional command groups
- **Update dependencies** when adding new libraries or tools

Examples of changes that should prompt an update:

- Adding new database tables or modifying the schema structure
- Introducing new Discord bot commands or cog categories
- Adding new utility modules or changing project structure
- Implementing new design patterns or architectural changes
- Adding new environment variables or configuration options
- Changing code style conventions or tooling configurations
- New features or functionality that users should know about

## Additional Notes

- The bot is licensed under Apache License 2.0
- Maintainer: Voltstriker
- Repository: https://github.com/Voltstriker/scrim-bot
