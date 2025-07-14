#!/bin/bash
# Simple launcher for the Tkinter GUI
cd "$(dirname "$0")"
python3 photo_metadata_gui.py
read -n 1 -s -r -p "Press any key to close this window"

