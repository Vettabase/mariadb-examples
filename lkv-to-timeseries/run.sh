#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/lkv"

# Create the venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the venv if no venv is currently active
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "Activating virtual environment..."
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
fi

# Install/update dependencies
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Run the Python script
python3 "$SCRIPT_DIR/iot-lkv.py"
