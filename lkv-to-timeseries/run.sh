#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/lkv"

# Install python3-venv if the venv module is not available
if ! python3 -c "import venv" 2>/dev/null; then
    echo "Installing python3-venv..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y python3-venv
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y python3-venv
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3-venv
    else
        echo "ERROR: Cannot install python3-venv automatically on this system." >&2
        echo "Please install the Python venv module manually and re-run this script." >&2
        exit 1
    fi
fi

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
