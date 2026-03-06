#!/usr/bin/env bash

set -euo pipefail

echo "Running .env if it exists"
[ -f .env ] && source .env

BRANCH="${BRANCH:-$(git symbolic-ref --short HEAD)}"
echo "BRANCH='$BRANCH'"
VENV_NAME="${VENV_NAME:-mut}"
echo "VENV_NAME='$VENV_NAME'"
echo

echo "Pulling branch: $BRANCH"
git pull origin "$BRANCH"
echo

# Skip if we're already in a virtual env.
# Create new venv if it doesn't exist.
# Then, activate it.
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ ! -f "$VENV_NAME/bin/activate" ]; then
        echo "Creating virtual env: $VENV_NAME"
        python3 -m venv "$VENV_NAME"
    fi
    echo "Activating venv"
    source "$VENV_NAME/bin/activate"
    echo
fi

echo "Installing requirements, if any"
[ -f requirements.txt ] && pip install --upgrade -r requirements.txt
echo

set +euo pipefail
