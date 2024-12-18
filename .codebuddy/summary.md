# Project Summary

## Overview
This project is a chess bot designed to interact with the Lichess platform. It utilizes various programming languages and libraries to implement functionalities such as game handling, matchmaking, and engine evaluations. The project is structured to support both local execution and deployment via Docker.

### Languages, Frameworks, and Main Libraries Used
- **Languages**: Python
- **Frameworks**: None specified, but utilizes Python's standard libraries and third-party packages.
- **Main Libraries**:
  - `requests`: For making HTTP requests.
  - `PyYAML`: For handling YAML files.
  - `chess`: A library for chess-related functionalities.
  - `rich`: For enhanced console output.
  - `backoff`: For retrying operations that may fail.
  
## Purpose of the Project
The purpose of this project is to create a chess bot that can play games on the Lichess platform. It features capabilities for evaluating positions, making moves, and handling game states. The bot can be customized and extended with additional game handlers, and it supports logging and configuration through YAML files.

## Build and Configuration Files
Here is a list of relevant files for building and configuring the project:

1. `/Dockerfile`
2. `/docker/Dockerfile`
3. `/docker/Dockerfile.dockerignore`
4. `/requirements.txt`
5. `/config.yml`
6. `/config.yml.default`
7. `/venv/pyvenv.cfg`

## Source Files Locations
The source files for the project can be found in the following directories:

- `/engines/bot/`: Contains the main bot engine files such as `main.py`, `evaluation.py`, and others.
- `/lib/`: Contains various utility modules like `lichess.py`, `matchmaking.py`, and others.
- `/test_bot/`: Contains test files and buggy engine implementations for testing purposes.

## Documentation Files Location
The documentation files are located in the following directories:

- `/docs/`: Contains general documentation files such as `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `SECURITY.md`.
- `/wiki/`: Contains detailed guides and instructions related to the bot's setup and usage, including:
  - `Configure-lichess-bot.md`
  - `Create-a-homemade-engine.md`
  - `Extra-customizations.md`
  - `How-to-create-a-Lichess-OAuth-token.md`
  - `How-to-Install.md`
  - `How-to-Run-lichess-bot.md`
  - `How-to-use-the-Docker-image.md`
  - `Setup-the-engine.md`
  - `Upgrade-to-a-BOT-account.md`