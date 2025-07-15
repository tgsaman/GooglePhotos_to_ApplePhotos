import unittest
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    from pyexiftool.exiftool import ExifTool
    PYEXIFTOOL_AVAILABLE = True
except Exception:
    PYEXIFTOOL_AVAILABLE = False

class TestPyExifToolCommands(unittest.TestCase):
    def test_pyexiftool_execute(self):
        if not PYEXIFTOOL_AVAILABLE or shutil.which("exiftool") is None:
            self.skipTest("pyexiftool or exiftool not installed")

        sample = Path("tests/Sample Photos/IMG_9993.JPG")
        with TemporaryDirectory() as tmp:
            dst = Path(tmp) / "IMG_9993.JPG"
            shutil.copy(sample, dst)
            with ExifTool(executable="exiftool") as et:
                et.execute(b"-overwrite_original", b"-XPComment=Hello", str(dst).encode())
                output = et.execute(b"-XPComment", str(dst).encode())
            self.assertIn(b"Hello", output)

if __name__ == "__main__":
    unittest.main()
