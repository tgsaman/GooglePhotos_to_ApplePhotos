#!/bin/bash
# Setup venv and open Swift GUI
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -d venv ]; then
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi
source venv/bin/activate
export PYTHON_EXECUTABLE="$REPO_ROOT/venv/bin/python"
export PY_SCRIPT_PATH="$REPO_ROOT/photo_metadata_patch.py"
open -a Xcode "$REPO_ROOT/PhotoMetadataGUI.swift"
