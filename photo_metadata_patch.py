import os
import json
import csv
import shutil
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import sys
import argparse
import shlex
try:
    from exiftool import ExifTool
except ImportError:  # graceful fallback for environments without pyexiftool
    ExifTool = None

def flatten_json(y, parent_key='', sep=':'):
    items = {}
    for k, v in y.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_json(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def check_directory_writable(path):
    """Return True if we can create and delete a temp file in path."""
    test_file = Path(path) / ".write_test"
    try:
        with open(test_file, "w") as f:
            f.write("test")
        test_file.unlink()
        return True
    except Exception:
        return False

def print_progress_bar(iteration, total, prefix='', length=40):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% ({iteration}/{total})', end='\r')
    if iteration == total:
        print()

def index_media_files(root_dir, media_exts):
    """Return a mapping of filename to paths for all media files under root_dir."""
    media_index = {}
    for root, _, files in os.walk(root_dir):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in media_exts:
                key = file.lower()
                full_path = Path(root) / file
                media_index.setdefault(key, []).append(full_path)
    return media_index

def load_json_metadata(json_path):
    """Load a JSON file and return the parsed data or None on failure."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def get_duplicate_type(matches, metadata_url, media_index):
    """Determine if a set of files are duplicates based on metadata URLs."""
    urls_seen = []
    for match in matches:
        match_json_path = match.parent / (match.name + ".supplemental-metadata.json")
        if match_json_path.exists():
            match_data = load_json_metadata(match_json_path)
            urls_seen.append(match_data.get("url", "") if match_data else "")
        else:
            urls_seen.append(metadata_url)
    if urls_seen.count(metadata_url) == len(matches):
        return "Exact Duplicate" if len(matches) > 1 else "Unique"
    return "Misleading Duplicate"

def apply_metadata_batch(batch_commands, dry_run):
    """Execute a batch of exiftool commands or preview them when dry_run."""
    if not batch_commands:
        return True

    print(f"Prepared {len(batch_commands)} exiftool commands")
    if dry_run:
        print("\n--- Batch Commands Preview ---")
        for cmd in batch_commands:
            print(" ".join(shlex.quote(c) for c in cmd))
        return True

    if not shutil.which("exiftool"):
        print(
            "Error: 'exiftool' not found. Please install exiftool and ensure it is in your PATH.",
            file=sys.stderr,
        )
        return False

    if ExifTool is None:
        print("Error: pyexiftool not installed", file=sys.stderr)
        return False

    try:
        print(f"Executing exiftool with {len(batch_commands)} commands")
        with ExifTool() as et:
            for cmd in batch_commands:
                et.execute(*[c.encode() for c in cmd])
        return True
    except Exception as e:
        print(f"Exiftool batch error: {e}", file=sys.stderr)
        return False

def process_metadata_files(project_root, dry_run=True, parallel_workers=4, output_path=None):
    """Process all JSON metadata files under project_root."""
    root_path = Path(project_root).expanduser()
    if not root_path.exists():
        print(f"Error: Project root '{root_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not check_directory_writable(root_path):
        print(
            f"Error: Unable to write to '{root_path}'. Close other apps that might lock the files.",
            file=sys.stderr,
        )
        sys.exit(1)

    homeless_json_dir = root_path / "Unmatched_Metadata"
    homeless_json_dir.mkdir(parents=True, exist_ok=True)

    media_extensions = {'.jpg', '.jpeg', '.png', '.mp4', '.mov', '.heic'}
    media_index = index_media_files(root_path, media_extensions)

    log_rows = []
    csv_headers = ["JSON Filename", "Matched Media", "Title", "URL", "Match Type",
                   "Modified?", "File Size in bytes", "Notes", "Missing Fields"]

    batch_commands = []

    def process_json(json_path):
        nonlocal batch_commands
        file = json_path.name
        data = load_json_metadata(json_path)
        if not data:
            row = {
                "JSON Filename": file,
                "Matched Media": "",
                "Title": "",
                "URL": "",
                "Match Type": "",
                "Modified?": "No",
                "File Size in bytes": "",
                "Notes": "Invalid JSON",
                "Missing Fields": "ALL",
            }
            return [row]

        title = data.get("title", "").lower()
        url = data.get("url", "")
        desc = data.get("description", "")
        image_views = data.get("imageViews", "")
        device_type = data.get("googlePhotosOrigin", {}).get("mobileUpload", {}).get("deviceType", "")
        timestamp = data.get("photoTakenTime", {}).get("timestamp") or data.get("creationTime", {}).get("timestamp")
        geo = data.get("geoDataExif", {}) or data.get("geoData", {})

        missing_fields = []
        if not timestamp:
            missing_fields.append("timestamp")
        if not title:
            missing_fields.append("title")
        inject_geo = "latitude" in geo and "longitude" in geo
        if not inject_geo:
            geo = {}
            missing_fields.append("geo")

        matched_files = media_index.get(title, [])
        match_type = "No Match"
        modified = "No"
        note = ""

        if not matched_files:
            try:
                shutil.move(str(json_path), homeless_json_dir / file)
                note = "No matching media file found; moved JSON"
            except Exception as e:
                note = f"Failed to move JSON: {e}"

            flat_json = flatten_json(data)
            row = {
                "JSON Filename": file,
                "Matched Media": "",
                "Title": title,
                "URL": url,
                "Match Type": match_type,
                "Modified?": modified,
                "File Size in bytes": "",
                "Notes": note,
                "Missing Fields": ", ".join(missing_fields),
                **flat_json,
            }
            return [row]

        match_type = get_duplicate_type(matched_files, url, media_index)

        if match_type != "Unique":
            rows = []
            flat_json = flatten_json(data)
            for match in matched_files:
                size = match.stat().st_size
                rows.append({
                    "JSON Filename": file,
                    "Matched Media": match.name,
                    "Title": title,
                    "URL": url,
                    "Match Type": match_type,
                    "Modified?": modified,
                    "File Size in bytes": size,
                    "Notes": f"Skipped overwrite due to {match_type.lower()}",
                    "Missing Fields": ", ".join(missing_fields),
                    **flat_json,
                })
            return rows

        match = matched_files[0]
        size = match.stat().st_size
        if timestamp:
            dt = datetime.utcfromtimestamp(int(timestamp)).strftime("%Y:%m:%d %H:%M:%S")
            comment = f"{url} {desc} Device:{device_type} Views:{image_views}".strip()
            ext = match.suffix.lower()
            cmd = ['-overwrite_original_in_place']

            if ext in {'.mp4', '.mov'}:
                cmd += [
                    f'-QuickTime:CreateDate={dt}',
                    f'-Keys:CreationDate={dt}',
                    f'-UserData:Comment={comment}'
                ]
            elif ext in {'.heic', '.jpg', '.jpeg', '.png'}:
                cmd += [
                    f'-AllDates={dt}',
                    f'-XPComment={comment}'
                ]

            if inject_geo:
                try:
                    lat = geo.get("latitude")
                    lon = geo.get("longitude")
                    alt = geo.get("altitude", 0.0)
                    cmd += [
                        f'-GPSLatitude={lat}',
                        f'-GPSLongitude={lon}',
                        f'-GPSAltitude={alt}'
                    ]
                except Exception as e:
                    inject_geo = False
                    note = f"Metadata queued but skipped GPS (error: {e})"
            else:
                note = "Metadata queued without GPS" if not note else note

            cmd.append(str(match))
      # Ensure we have at least one metadata field *before* the file path
            if any(arg.startswith('-') for arg in cmd[:-1]):
                batch_commands.append(cmd)
            else:
                note = "Metadata skipped: no valid operations"
            modified = "Yes" if not dry_run else "No"
            note = "Metadata queued" if not dry_run and not note else note
            if dry_run:
                note = "Dry run only"

        flat_json = flatten_json(data)
        for key in ["title", "url"]:
            flat_json.pop(key, None)
        row = {
            "JSON Filename": file,
            "Matched Media": match.name,
            "Title": title,
            "URL": url,
            "Match Type": match_type,
            "Modified?": modified,
            "File Size in bytes": size,
            "Notes": note,
            "Missing Fields": ", ".join(missing_fields),
            **flat_json  # injects all flattened JSON keys except duplicates
        }
        return [row]


    json_paths = []
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(".supplemental-metadata.json"):
                json_paths.append(Path(root) / file)

    with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
        total = len(json_paths)
        for i, result in enumerate(executor.map(process_json, json_paths), 1):
            print_progress_bar(i, total, prefix="Processing")
            log_rows.extend(result)

    success = apply_metadata_batch(batch_commands, dry_run)
    all_keys = set()
    for row in log_rows:
        if isinstance(row, dict):
            all_keys.update(row.keys())

    fieldnames = sorted(all_keys)

    log_csv_path = Path(output_path).expanduser() if output_path else Path.home() / "Desktop" / "metadata_report.csv"
    log_csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not check_directory_writable(log_csv_path.parent):
        print(
            f"Error: Cannot write to '{log_csv_path.parent}'. Close other apps that might lock the files.",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        with open(log_csv_path, "w", newline="", encoding="utf-8") as log_file:
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(log_rows)

    except Exception as e:
        print(f"Failed to write CSV log: {e}", file=sys.stderr)
        sys.exit(1)

    if not success:
        print("Exiftool batch failed. Exiting with error.", file=sys.stderr)
        sys.exit(1)

    return log_csv_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply Google Photos metadata to media files")
    parser.add_argument("root", help="Path to the Google Photos export root directory")
    parser.add_argument("--dry-run", action="store_true", help="Show operations without running exiftool")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel worker threads")
    parser.add_argument("--output", help="Path to output CSV (default: ~/Desktop/metadata_report.csv)")
    args = parser.parse_args()

    process_metadata_files(args.root, dry_run=args.dry_run, parallel_workers=args.workers, output_path=args.output)

# Example usage:
# process_metadata_files("sample/filepath/here", dry_run=True, parallel_workers=8)

# Created by Thomas Samandi on 7/12/25 using ChatGPT4o
