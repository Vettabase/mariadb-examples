#!/usr/bin/env bash
# Source this script to set up the Python virtual environment and install
# dependencies:
#
#   . ./run.sh
#
# Do NOT run it as a regular script (bash run.sh / ./run.sh) because
# activating the virtual environment must happen in the current shell.
#
# set -euo pipefail is intentionally omitted: sourcing a script that calls
# "exit" on error would terminate the calling shell (e.g. an SSH session).
# Errors are handled explicitly below.

echo "Running .env if it exists"
[ -f .env ] && source .env

BRANCH="${BRANCH:-$(git symbolic-ref --short HEAD)}"
echo "BRANCH='$BRANCH'"
VENV_NAME="${VENV_NAME:-lkv}"
echo "VENV_NAME='$VENV_NAME'"
echo

echo "Pulling branch: $BRANCH"
git pull origin "$BRANCH" || echo "Warning: git pull failed (check network/credentials); continuing with local copy."
echo

# Skip if we're already in a virtual env.
# Create new venv if it doesn't exist.
# Then, activate it.
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ ! -f "$VENV_NAME/bin/activate" ]; then
        echo "Creating virtual env: $VENV_NAME"
        if ! python3 -m venv "$VENV_NAME"; then
            echo "Error: failed to create virtual environment '$VENV_NAME'." >&2
            echo "Ensure python3-venv is installed (e.g. sudo apt install python3-venv)." >&2
            return 1 2>/dev/null || exit 1
        fi
    fi
    echo "Activating virtual environment: $VENV_NAME"
    # shellcheck source=/dev/null
    if ! source "$VENV_NAME/bin/activate"; then
        echo "Error: failed to activate virtual environment '$VENV_NAME'." >&2
        return 1 2>/dev/null || exit 1
    fi
    echo
fi

echo "Installing requirements, if any"
if [ -f requirements.txt ]; then
    if grep -q '^mariadb' requirements.txt && ! command -v mariadb_config >/dev/null 2>&1; then
        echo "Error: 'mariadb_config' not found." >&2
        echo "The 'mariadb' Python package requires the MariaDB Connector/C development libraries." >&2
        echo "Install them with: sudo apt install libmariadb-dev" >&2
        return 1 2>/dev/null || exit 1
    fi
    pip install --upgrade -r requirements.txt || echo "Warning: pip install failed; some packages may be missing." >&2
fi
echo
