import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/python/auth_log_triage.py"
spec = importlib.util.spec_from_file_location("auth_log_triage", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class AuthTests(unittest.TestCase):
    def test_sample_alerts(self):
        sample = Path(__file__).resolve().parents[1] / "samples/auth_events.csv"
        result = module.analyze(module.load_events(sample))
        self.assertEqual(result["events_analyzed"], 7)
        self.assertEqual([a["type"] for a in result["alerts"]],
                         ["repeated_failures", "success_after_failures"])

    def test_reject_bad_ip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.csv"
            path.write_text("timestamp,username,source_ip,event,outcome\n2026-09-01T12:00:00Z,u,invalid,login,failure\n")
            with self.assertRaisesRegex(ValueError, "Invalid CSV row 2"):
                module.load_events(path)

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):
            module.analyze([], threshold=0)

    def test_event_ordering(self):
        sample = Path(__file__).resolve().parents[1] / "samples/auth_events.csv"
        events = module.load_events(sample)
        self.assertEqual(events, sorted(events, key=lambda x: x["timestamp"]))

if __name__ == "__main__":
    unittest.main()
