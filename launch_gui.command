#!/bin/bash
# Simple launcher for the Tkinter GUI
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=python3
if [ -x "$REPO_ROOT/venv/bin/python" ]; then
    PYTHON="$REPO_ROOT/venv/bin/python"
fi

$PYTHON "$REPO_ROOT/photo_metadata_gui.py"
read -n 1 -s -r -p "Press any key to close this window"

