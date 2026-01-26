# Scrim Bot

<p align="center">
    <a href="https://github.com/Voltstriker/scrim-bot/blob/main/LICENSE.md"><img alt="GitHub License" src="https://img.shields.io/github/license/Voltstriker/scrim-bot?style=for-the-badge"></a>
    <a href="https://github.com/Voltstriker/scrim-bot/releases"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/Voltstriker/scrim-bot?sort=semver&display_name=release&style=for-the-badge"></a>
    <a href="https://github.com/Voltstriker/scrim-bot/actions"><img alt="GitHub branch check runs" src="https://img.shields.io/github/check-runs/Voltstriker/scrim-bot/main?style=for-the-badge"></a>
    <a href="https://github.com/Voltstriker/scrim-bot/commits/main/"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/Voltstriker/scrim-bot/main?style=for-the-badge"></a>
    <a href="https://github.com/Voltstriker/scrim-bot/issues"><img alt="GitHub Issues or Pull Requests" src="https://img.shields.io/github/issues/Voltstriker/scrim-bot?style=for-the-badge"></a>
    <img alt="Repository code style" src="https://img.shields.io/badge/code%20style-black-black?style=for-the-badge">
</p>

**Scrim Bot** is a Discord Bot designed to assist competitive teams with organising and challenging other teams to practice scrims or matches.

## Installation

1. Download the latest release or clone this repository
2. Register a Discord bot on the [developer portal](https://discord.com/developers/applications)
3. Copy `.env.example` to `.env` and update it with your Discord bot token
4. Install the application and its dependencies using the command: `python -m pip install .`
5. Launch the application using the command: `python src/bot.py`

> **Note**: You may need to replace `python` with `py`, `python3`, `python3.11`, etc. depending on what Python versions you have installed on the machine.

### Development Setup

For development with additional tools (Black, Pylint, Pyright):

1. Clone the repository
2. Install with development dependencies: `python -m pip install -e .[dev]`
3. Run the bot: `python src/bot.py`

## Bot Commands

The following commands are available in the bot:

### General Commands

| Command           | Scoped User | Description                                                                     |
| ----------------- | ----------- | ------------------------------------------------------------------------------- |
| `/info`           | All Users   | Display information about the bot including server count and latency            |
| `/displayname`    | All Users   | Set your display name in the bot (used for team memberships and other displays) |
| `/ping`           | Bot Owner   | Test the bot's responsiveness and display latency                               |
| `/sync`           | Bot Owner   | Synchronise slash commands either globally or to the current guild              |
| `/unsync`         | Bot Owner   | Unsynchronise slash commands either globally or from the current guild          |
| `/database reset` | Bot Owner   | Truncate and recreate all database tables (except logs)                         |

### Admin Management Commands

| Command         | Scoped User | Description                                                                                    |
| --------------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `/admin add`    | Bot Owner   | Add a user or role as a bot administrator (users and roles can execute restricted bot actions) |
| `/admin remove` | Bot Owner   | Remove a user or role from bot administrators                                                  |
| `/admins`       | Bot Owner   | List all bot administrators (both users and roles)                                             |

### Game Management Commands

| Command         | Scoped User | Description                             |
| --------------- | ----------- | --------------------------------------- |
| `/games list`   | Admin       | List all games in the database          |
| `/games add`    | Admin       | Add a new game to the database          |
| `/games update` | Admin       | Update an existing game in the database |
| `/games delete` | Admin       | Delete a game from the database         |

### Map Management Commands

| Command       | Scoped User | Description                                     |
| ------------- | ----------- | ----------------------------------------------- |
| `/maps`       | All Users   | List all maps, optionally filtered by game name |
| `/map add`    | Admin       | Add a new map to the database                   |
| `/map edit`   | Admin       | Update an existing map in the database          |
| `/map remove` | Admin       | Delete a map from the database                  |

### User Management Commands

| Command         | Scoped User | Description                                                |
| --------------- | ----------- | ---------------------------------------------------------- |
| `/users list`   | Admin       | List all users in the database with their team memberships |
| `/users search` | All Users   | Search for a user by Discord tag                           |

### Team Management Commands

| Command         | Scoped User  | Description                                                                         |
| --------------- | ------------ | ----------------------------------------------------------------------------------- |
| `/teams`        | All Users    | List teams on the server with optional filters, or list your teams when used in DMs |
| `/team create`  | All Users    | Create a new team with the specified name and tag                                   |
| `/team members` | All Users    | List all members of a team                                                          |
| `/team invite`  | Team Captain | Invite a user to join your team                                                     |
| `/team edit`    | Team Captain | Edit your team's name or tag                                                        |
| `/team leave`   | All Users    | Leave a team the user is a member of                                                |
| `/team remove`  | Team Captain | Remove a member from your team by team ID                                           |
| `/team owner`   | Team Owner   | Transfer ownership to another team member by team ID                                |

## Issues or Questions

If you have any issues or questions you can log an [issue](https://github.com/Voltstriker/scrim-bot/issues) on GitHub.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
