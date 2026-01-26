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

| Command           | Parameters              | Scoped User | Description                                                                     |
| ----------------- | ----------------------- | ----------- | ------------------------------------------------------------------------------- |
| `/info`           | None                    | All Users   | Display information about the bot including server count and latency            |
| `/displayname`    | `name`                  | All Users   | Set your display name in the bot (used for team memberships and other displays) |
| `/ping`           | None                    | Bot Owner   | Test the bot's responsiveness and display latency                               |
| `/sync`           | `scope` (global\|guild) | Bot Owner   | Synchronise slash commands either globally or to the current guild              |
| `/unsync`         | `scope` (global\|guild) | Bot Owner   | Unsynchronise slash commands either globally or from the current guild          |
| `/database reset` | None                    | Bot Owner   | Reset all database tables with confirmation (ephemeral, preserves logs)         |

### Admin Management Commands

| Command         | Parameters            | Scoped User | Description                                                                                    |
| --------------- | --------------------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `/admin add`    | `target` (user\|role) | Bot Owner   | Add a user or role as a bot administrator (users and roles can execute restricted bot actions) |
| `/admin remove` | `target` (user\|role) | Bot Owner   | Remove a user or role from bot administrators                                                  |
| `/admins`       | None                  | Bot Owner   | List all bot administrators (both users and roles)                                             |

### Game Management Commands

| Command         | Parameters                             | Scoped User | Description                             |
| --------------- | -------------------------------------- | ----------- | --------------------------------------- |
| `/games list`   | None                                   | Admin       | List all games in the database          |
| `/games add`    | `name`, `series` (optional)            | Admin       | Add a new game to the database          |
| `/games update` | `game_id`, `name`, `series` (optional) | Admin       | Update an existing game in the database |
| `/games delete` | `game_id`                              | Admin       | Delete a game from the database         |

### Map Management Commands

| Command       | Parameters                                                          | Scoped User | Description                                     |
| ------------- | ------------------------------------------------------------------- | ----------- | ----------------------------------------------- |
| `/maps`       | `game` (optional, autocomplete)                                     | All Users   | List all maps, optionally filtered by game name |
| `/map add`    | `name`, `mode`, `game` (autocomplete), `experience_code` (optional) | Admin       | Add a new map to the database                   |
| `/map edit`   | `map_id`, `name`, `mode`, `experience_code` (all optional)          | Admin       | Update an existing map in the database          |
| `/map remove` | `map_id`                                                            | Admin       | Delete a map from the database                  |

### User Management Commands

| Command         | Parameters | Scoped User | Description                                                |
| --------------- | ---------- | ----------- | ---------------------------------------------------------- |
| `/users list`   | None       | All Users   | List all users in the database with their team memberships |
| `/users search` | `user`     | All Users   | Search for a user by Discord tag                           |

### Team Management Commands

| Command         | Parameters                                   | Scoped User  | Description                                                                                |
| --------------- | -------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------ |
| `/teams`        | `league`, `user`, `search` (all optional)    | All Users    | List teams on the server with optional filters, or list your teams when used in DMs        |
| `/team create`  | `name`, `tag`                                | All Users    | Create a new team with the specified name and tag                                          |
| `/team members` | `team_id`                                    | All Users    | List all members of a team (displays Owner, Captains, and Members sections)                |
| `/team invite`  | `team_id`, `user`                            | Team Captain | Invite a user to join your team by team ID (captain only, sends DM with Accept/Decline)    |
| `/team edit`    | `team_id`, `name`, `tag` (name/tag optional) | Team Captain | Edit your team's name or tag by team ID (captain only, at least one parameter required)    |
| `/team leave`   | `team_id`                                    | All Users    | Leave a team by team ID (captains must transfer captaincy first)                           |
| `/team remove`  | `team_id`, `user`                            | Team Captain | Remove a member from your team by team ID (captain only, cannot remove captain)            |
| `/team owner`   | `team_id`, `user`                            | Team Captain | Transfer captaincy to another team member by team ID (captain only, requires confirmation) |

## Issues or Questions

If you have any issues or questions you can log an [issue](https://github.com/Voltstriker/scrim-bot/issues) on GitHub.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
