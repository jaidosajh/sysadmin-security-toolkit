import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/python/file_integrity.py"
spec = importlib.util.spec_from_file_location("file_integrity", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class IntegrityTests(unittest.TestCase):
    def test_baseline_and_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "a.txt").write_text("hello")
            baseline = module.snapshot(root)
            self.assertEqual(module.compare(baseline, module.snapshot(root)),
                             {"added": [], "removed": [], "changed": []})
            (root / "a.txt").write_text("changed")
            (root / "b.txt").write_text("added")
            changes = module.compare(baseline, module.snapshot(root))
            self.assertEqual(changes["changed"], ["a.txt"])
            self.assertEqual(changes["added"], ["b.txt"])

    def test_no_symlink_follow(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "real.txt").write_text("ok")
            try:
                (root / "alias.txt").symlink_to(root / "real.txt")
            except (OSError, NotImplementedError):
                self.skipTest("symlinks not enabled")
            self.assertEqual(list(module.snapshot(root)), ["real.txt"])

if __name__ == "__main__":
    unittest.main()
