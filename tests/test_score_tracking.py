import json
import os
import tempfile
import unittest

from main import record_high_score


class HighScoreTrackingTests(unittest.TestCase):
    def test_record_high_score_keeps_top_scores(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "high_scores.json")

            record_high_score(60, 96.4, 60, path, name="Alice")
            record_high_score(72, 98.1, 60, path, name="Bob")
            record_high_score(68, 97.0, 60, path, name="Cara")

            with open(path, "r", encoding="utf-8") as handle:
                scores = json.load(handle)

            self.assertEqual(len(scores), 3)
            self.assertEqual(scores[0]["name"], "Bob")
            self.assertEqual(scores[0]["wpm"], 72)
            self.assertEqual(scores[1]["name"], "Cara")
            self.assertEqual(scores[2]["name"], "Alice")


if __name__ == "__main__":
    unittest.main()
