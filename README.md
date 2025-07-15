# GooglePhotos_to_ApplePhotos

This utility processes the JSON metadata that accompanies a Google Photos export and applies it to the matching media files. The goal is to restore location data and creation timestamps so that the files behave correctly in Apple Photos.

## Requirements
- **macOS** with Python 3.8+
- [`exiftool`](https://exiftool.org/) must be installed and available on your `PATH`. The easiest way is via [Homebrew](https://brew.sh/):
  ```bash
  brew install exiftool
  ```
- Optional: `pyexiftool` is needed for fast metadata updates. The Swift GUI launcher will install it in a local virtual environment if missing.


## Usage
Run the script and pass the path to your extracted Google Photos export. By default it will modify the files in place while preserving each file's original modification date using ExifTool's `-P` option. Use `--dry-run` to generate the log and batch file without running `exiftool`.

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
### SwiftUI
Run `./launch_swift_gui.command` to build and launch the Swift interface. The script creates a local Python virtual environment and installs `pyexiftool` if needed.

### Legacy Tkinter
The older Tkinter GUI is archived under `legacy_gui/`. Run `legacy_gui/launch_gui.command` if you prefer that interface.

## Testing
Basic unit tests are located in the `tests` directory and can be run with:

```bash
python3 -m unittest discover -s tests
```
