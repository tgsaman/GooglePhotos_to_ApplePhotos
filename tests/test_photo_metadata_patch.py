import json
from pathlib import Path
from tempfile import TemporaryDirectory
from photo_metadata_patch import index_media_files, load_json_metadata, get_duplicate_type


def test_index_media_files():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a").mkdir()
        (root / "b").mkdir()
        file1 = root / "a" / "IMG.JPG"
        file2 = root / "b" / "img.jpg"
        file1.touch()
        file2.touch()

        index = index_media_files(root, {".jpg"})
        assert "img.jpg" in index
        assert len(index["img.jpg"]) == 2


def test_load_json_metadata():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        good = root / "good.json"
        bad = root / "bad.json"
        good.write_text(json.dumps({"a": 1}))
        bad.write_text("{ invalid json }")
        assert load_json_metadata(good) == {"a": 1}
        assert load_json_metadata(bad) is None


def test_get_duplicate_type():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a").mkdir()
        (root / "b").mkdir()
        file1 = root / "a" / "IMG.JPG"
        file2 = root / "b" / "IMG.JPG"
        file1.touch()
        file2.touch()
        meta1 = file1.with_name(file1.name + ".supplemental-metadata.json")
        meta2 = file2.with_name(file2.name + ".supplemental-metadata.json")
        meta1.write_text(json.dumps({"url": "A"}))
        meta2.write_text(json.dumps({"url": "A"}))

        media_index = index_media_files(root, {".jpg"})
        matches = media_index["img.jpg"]
        assert get_duplicate_type(matches, "A", media_index) == "Misleading Duplicate"

        meta2.write_text(json.dumps({"url": "B"}))
        assert get_duplicate_type(matches, "A", media_index) == "Exact Duplicate"

        # unique when only one match
        assert get_duplicate_type([file1], "A", media_index) == "Unique"

