#!/bin/bash
# Setup venv and open Swift GUI
cd "$(dirname "$0")"
if [ ! -d venv ]; then
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi
source venv/bin/activate
export PYTHON_EXECUTABLE="$(pwd)/venv/bin/python"
open -a Xcode PhotoMetadataGUI.swift
