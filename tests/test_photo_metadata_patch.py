import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from unittest.mock import patch

from photo_metadata_patch import (
    index_media_files,
    load_json_metadata,
    get_duplicate_type,
    process_metadata_files,
)


class TestPhotoMetadataPatch(unittest.TestCase):
    def test_index_media_files(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").mkdir()
            (root / "b").mkdir()
            file1 = root / "a" / "IMG.JPG"
            file2 = root / "b" / "img.jpg"
            file1.touch()
            file2.touch()

            index = index_media_files(root, {".jpg"})
            self.assertIn("img.jpg", index)
            self.assertEqual(len(index["img.jpg"]), 2)

    def test_load_json_metadata(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / "good.json"
            bad = root / "bad.json"
            good.write_text(json.dumps({"a": 1}))
            bad.write_text("{ invalid json }")

            self.assertEqual(load_json_metadata(good), {"a": 1})
            self.assertIsNone(load_json_metadata(bad))

    def test_get_duplicate_type(self):
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
            self.assertEqual(
                get_duplicate_type(matches, "A", media_index), "Exact Duplicate"
            )

            meta2.write_text(json.dumps({"url": "B"}))
            self.assertEqual(
                get_duplicate_type(matches, "A", media_index), "Misleading Duplicate"
            )

            # unique when only one match
            self.assertEqual(
                get_duplicate_type([file1], "A", media_index), "Unique"
            )

    def test_commands_include_overwrite_flag(self):
        report = Path("tests/output.csv")
        if report.exists():
            report.unlink()
        with patch("photo_metadata_patch.apply_metadata_batch") as mock_apply:
            mock_apply.return_value = True
            process_metadata_files(
                "tests",
                dry_run=True,
                parallel_workers=1,
                output_path=report,
            )
            mock_apply.assert_called_once()
            cmds = mock_apply.call_args[0][0]
            self.assertTrue(cmds and all(cmd[0] == "-overwrite_original_in_place" for cmd in cmds))
        report.unlink()


if __name__ == "__main__":
    unittest.main()

