# GooglePhotos_to_ApplePhotos

This utility processes the JSON metadata that accompanies a Google Photos export and applies it to the matching media files. The goal is to restore location data and creation timestamps so that the files behave correctly in Apple Photos.

## Requirements
- **macOS** with Python 3.8+
- [`exiftool`](https://exiftool.org/) must be installed and available on your `PATH`. The easiest way is via [Homebrew](https://brew.sh/):
  ```bash
  brew install exiftool
  ```
- [`pyexiftool`](https://pypi.org/project/pyexiftool/) installed in a Python virtual environment. Run `launch_swift_gui.command` to set up the environment automatically.

## Usage
Run the script and pass the path to your extracted Google Photos export. By default it will modify the files in place. Use `--dry-run` to generate the log and batch file without running `exiftool`.

```bash
python3 photo_metadata_patch.py /path/to/export --dry-run
```

You can control the number of worker threads with `--workers`:

```bash
python3 photo_metadata_patch.py /path/to/export --workers 8
```

By default a `metadata_report.csv` file is written to your Desktop. Use `--output` to specify a different location.

```bash
python3 photo_metadata_patch.py /path/to/export --output /tmp/report.csv
```

## GUI Launcher
### Tkinter
Double‑click the `launch_gui.command` file for the original Tkinter interface. The script locates the Python modules relative to its own path so it works even if the project is moved into subfolders. It lets you choose the export folder and optional CSV destination. Make sure your photos aren’t open in other apps so Finder doesn’t lock them.

### SwiftUI
For a macOS-native interface built with SwiftUI, run `launch_swift_gui.command`. It sets up a virtual environment with `pyexiftool`, exports environment variables for the Python interpreter and script path, and then opens `PhotoMetadataGUI.swift` in Xcode. The Swift version mirrors the Python GUI and invokes `photo_metadata_patch.py` behind the scenes using the venv's Python interpreter.

## Testing
Basic unit tests are located in the `tests` directory and can be run with:

```bash
python3 -m unittest discover -s tests
```
