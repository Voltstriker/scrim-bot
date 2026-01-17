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

| Command   | Parameters              | Scoped User | Description                                                            |
| --------- | ----------------------- | ----------- | ---------------------------------------------------------------------- |
| `/info`   | None                    | Bot Owner   | Display information about the bot including server count and latency   |
| `/ping`   | None                    | Bot Owner   | Test the bot's responsiveness and display latency                      |
| `/sync`   | `scope` (global\|guild) | Bot Owner   | Synchronise slash commands either globally or to the current guild     |
| `/unsync` | `scope` (global\|guild) | Bot Owner   | Unsynchronise slash commands either globally or from the current guild |

> **Note**: All commands currently require bot owner permissions. Additional team management and match commands will be added in future updates.

## Issues or Questions

If you have any issues or questions you can log an [issue](https://github.com/Voltstriker/scrim-bot/issues) on GitHub.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details
