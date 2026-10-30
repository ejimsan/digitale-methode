import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import kwic_app


class KwicAppTests(unittest.TestCase):
    def setUp(self):
        self.rows = [("T, 1", "", "x", "y")]

    @patch("kwic_app.bestimme_lemma", return_value=("X", ("x[a]",)))
    @patch("kwic_app.suche_belege")
    @patch("kwic_app.keyword_in_context_ausgabe")
    def test_searches_displays_and_exports_with_default_filename(
        self, display, search, _select
    ):
        search.return_value = ["raw"]
        display.return_value = self.rows
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(kwic_app, "CSV_ORDNER", Path(temp)):
                with patch("builtins.input", side_effect=["ja", ""]):
                    result = kwic_app.suche_und_zeige_kwic()
            self.assertTrue((Path(temp) / "konkordanz.csv").exists())
        self.assertEqual(result, self.rows)
        search.assert_called_once_with(("X", ("x[a]",)))
        display.assert_called_once_with(["raw"])

    @patch("kwic_app.bestimme_lemma", return_value=("X", "x[a]"))
    @patch("kwic_app.suche_belege", return_value=[])
    @patch("kwic_app.keyword_in_context_ausgabe", return_value=[])
    def test_rejects_paths_and_skips_export_when_overwrite_is_declined(
        self, _display, _search, _select
    ):
        with patch("builtins.input", side_effect=["j", "..\\outside.csv"]):
            with self.assertRaises(ValueError):
                kwic_app.suche_und_zeige_kwic()
        with tempfile.TemporaryDirectory() as temp:
            existing = Path(temp) / "exists.csv"
            existing.touch()
            with patch.object(kwic_app, "CSV_ORDNER", Path(temp)):
                with patch("builtins.input", side_effect=["j", "exists.csv", "n"]):
                    result = kwic_app.suche_und_zeige_kwic()
            self.assertTrue(existing.exists())
            self.assertEqual(result, [])

    @patch("kwic_app.bestimme_lemma", return_value=("X", "x[a]"))
    @patch("kwic_app.suche_belege", return_value=[])
    @patch("kwic_app.keyword_in_context_ausgabe", return_value=[])
    def test_other_export_response_leaves_results_unchanged(
        self, _display, _search, _select
    ):
        with patch("builtins.input", return_value="maybe"):
            self.assertEqual(kwic_app.suche_und_zeige_kwic(), [])


if __name__ == "__main__":
    unittest.main()
