import csv
import tempfile
import unittest
from pathlib import Path

from kwic_export import exportiere_csv


class KwicExportTests(unittest.TestCase):
    def test_exports_utf8_csv_and_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "nested" / "results.csv"
            rows = [("Text, 1", "vor", "šarru", "danach")]
            self.assertEqual(exportiere_csv(rows, path), path)
            with path.open(encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(list(csv.reader(stream)), [
                    ["Beleg", "Wörter vor Keyword", "Keyword", "Wörter nach Keyword"],
                    list(rows[0]),
                ])

    def test_refuses_existing_file_unless_overwrite_is_enabled(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "results.csv"
            path.write_text("old", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                exportiere_csv([], path)
            exportiere_csv([], path, ueberschreiben=True)
            self.assertIn("Beleg", path.read_text(encoding="utf-8-sig"))

    def test_requires_boolean_overwrite_option(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(TypeError):
                exportiere_csv([], Path(temp) / "results.csv", 1)


if __name__ == "__main__":
    unittest.main()
