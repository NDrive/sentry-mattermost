# Sentry Mattermost
A plugin for Sentry to enable notifications to Mattermost Open Source Chat.

# Usage
Install with pip:

    pip install sentry-mattermost

Enable the integration inside a Project.

# Contributing
Use virtualenv and Python 2.7:

    virtualenv -p python2.7 .env
    source .env/bin/activate

Install development requirements:

    pip install -r dev-requirements.txt

You can use Docker to test the plugin directly in a Sentry instance:

    docker-compose up


# Test

    py.test -v
