# Sentry Mattermost
A plugin for Sentry to enable notifications to Mattermost Open Source Chat.

# Usage
Install with pip and enable the plugin in a Project:

    pip install sentry_mattermost


# Contributing
We use Docker to setup a development stack. Make sure you have the Docker Toolbox
installed first.

## First time setup
Setups Python, Docker containers and Sentry admin:

    make bootstrap

## Development
Each time you update the code, restart the containers:

    make restart
