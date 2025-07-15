#!/bin/bash
# Build and run the SwiftUI GUI, creating a Python venv with PyExifTool if needed.
cd "$(dirname "$0")"

VENV=".venv"
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi
source "$VENV/bin/activate"
if ! python -m pip show pyexiftool >/dev/null 2>&1; then
    echo "Installing PyExifTool..."
    python -m pip install pyexiftool >/dev/null
fi

APP="PhotoMetadataGUIApp"
sdk=$(xcrun --sdk macosx --show-sdk-path 2>/dev/null)
if [ -z "$sdk" ]; then
    echo "Xcode command line tools not found" >&2
    exit 1
fi
swiftc -sdk "$sdk" PhotoMetadataGUI.swift -o "$APP" -framework SwiftUI
./"$APP"
read -n 1 -s -r -p "Press any key to close this window"
