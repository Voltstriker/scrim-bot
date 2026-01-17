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
├── models/                # Data models (dataclasses)
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── game.py            # Game, Map, MatchFormat models
│   ├── team.py            # Team and team-related models
│   ├── league.py          # League models
│   └── match.py           # Match and match result models
└── utils/                 # Utility modules
    ├── __init__.py
    ├── database.py        # Database operations
    ├── discord_bot.py     # Bot class and configuration
    └── logging.py         # Logging configuration
```

### Data Models

- **Location**: `src/models/` directory
- **Pattern**: Use Python dataclasses for all database entities
- **Type Hints**: All fields must have type annotations (use `Optional` for nullable fields)
- **Conversion Method**: Each model must have a `from_row()` classmethod for database row conversion
- **Docstrings**: NumPy-style documentation for all models and methods
- **Boolean Handling**: Convert SQLite INTEGER (0/1) to Python bool using `bool(row['field'])`
- **Imports**: Models are exported through `models/__init__.py` for clean imports

Example model structure:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Team:
    id: int
    name: str
    captain_id: int

    @classmethod
    def from_row(cls, row) -> 'Team':
        return cls(id=row['id'], name=row['name'], captain_id=row['captain_id'])
```

### Database

- **Type**: SQLite
- **Location**: Configured via `DATABASE_PATH` environment variable
- **Initialisation**: Automatic schema creation on first run if database doesn't exist
- **Access**: Use the `Database` class from `utils.database`
- **Schema**: Fully implemented in `initialise_schema()` method
- **Models**: Use dataclasses from `models/` for type-safe data access

### Database Schema

The database includes the following tables:

- **logs**: Database logging (timestamp, level, logger_name, message)
- **games**: Video games (name, series)
- **maps**: Game maps (name, mode, game_id)
- **match_formats**: Match configurations (max_players, match_count, map_list_id)
- **permitted_maps**: Maps allowed per match format (composite key: match_format_id, map_id)
- **users**: Discord users (discord_id, display_name, created_date)
- **teams**: Competitive teams (name, captain_id, discord_server, created_at)
- **leagues**: Competition leagues (name, game_id, match_format, discord_server)
- **team_membership**: User-team relationships (composite key: user_id, team_id)
- **team_permissions_users**: User-specific team permissions
- **team_permissions_roles**: Role-based team permissions
- **league_membership**: Team-league relationships (composite key: league_id, team_id)
- **matches**: Match challenges (league_id, challenging_team, defending_team, match_date)
- **match_results**: Round results (composite key: match_id, round)

### Logging

- Use the custom `LoggingFormatter` from `utils.logging`
- Log level configured via `LOG_LEVEL` environment variable
- Log path configured via `LOG_PATH` environment variable
- Logger instance passed to all major components
- **Database Logging**: Logs are written to the database `logs` table (added after schema initialisation)

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

The database schema is fully implemented. When working with database entities:

### Using Models

- Import models from `models` package: `from models import Team, User, Match`
- Use `Model.from_row(row)` to convert database rows to typed objects
- Models provide type safety, autocomplete, and clear structure
- All models use dataclasses with full type annotations

### Discord IDs

- Store Discord IDs (user IDs, server IDs, role IDs) as TEXT type
- Discord snowflake IDs can be large (18-19 digits), TEXT handles them safely
- Examples: `"178397727892176897"`, `"1407935391876648981"`

### Boolean Fields

- SQLite stores booleans as INTEGER (0/1)
- Convert to Python bool in models: `bool(row['field_name'])`
- Used in: team permissions, match_cancelled

### Timestamps

- Use SQLite TIMESTAMP type for all date/time fields
- Convert to Python datetime objects in models
- Common timestamp fields: created_date, updated_date, joined_date

### Foreign Keys

- All relationships use foreign key constraints
- Enforces referential integrity at database level
- Common patterns: user_id → users(id), team_id → teams(id)

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

### Working with Models and Database

```python
from utils import database
from models import Team, User

# Fetch and convert to model
with database.Database(database_path=db_path, logger=logger) as db:
    row = db.select_one("teams", where="id = ?", parameters=(team_id,))
    if row:
        team = Team.from_row(row)
        # Now you have a typed object with autocomplete
        print(f"Team: {team.name}, Captain: {team.captain_id}")

# Fetch multiple rows
with database.Database(database_path=db_path, logger=logger) as db:
    rows = db.select("teams", where="discord_server = ?", parameters=(server_id,))
    teams = [Team.from_row(row) for row in rows]
```

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
- **Update the README.md commands table** whenever a new bot command is added to any file in the `src/cogs/` directory
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
- Adding or modifying data models in the `models/` directory

## Additional Notes

- The bot is licensed under Apache License 2.0
- Maintainer: Voltstriker
- Repository: https://github.com/Voltstriker/scrim-bot
