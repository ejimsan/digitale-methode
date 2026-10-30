import unittest
from unittest.mock import patch

from kwic_display import _kontextbreite_eingabe, keyword_in_context_ausgabe


class KwicDisplayTests(unittest.TestCase):
    def test_prompts_until_context_width_is_valid_or_empty(self):
        with patch("builtins.input", side_effect=["abc", "-1", "0", ""]):
            self.assertEqual(_kontextbreite_eingabe(), 0)
        with patch("builtins.input", return_value=""):
            self.assertIsNone(_kontextbreite_eingabe())

    def test_formats_full_context_and_truncates_each_side(self):
        results = [("T, 1", "a b c", "KEY", "d e f")]
        self.assertEqual(
            keyword_in_context_ausgabe(results, 2),
            [("T, 1", "b c", "KEY", "d e")],
        )
        self.assertEqual(
            keyword_in_context_ausgabe(results, 3),
            results,
        )
        self.assertEqual(
            keyword_in_context_ausgabe(results, 0),
            [("T, 1", "", "KEY", "")],
        )

    def test_prints_empty_results(self):
        with patch("builtins.print") as output:
            self.assertEqual(keyword_in_context_ausgabe([], 1), [])
        output.assert_any_call("Keine Belege gefunden.")

    def test_rejects_invalid_context_widths(self):
        for value, error in (("2", TypeError), (True, TypeError), (-1, ValueError)):
            with self.subTest(value=value), self.assertRaises(error):
                keyword_in_context_ausgabe([], value)


if __name__ == "__main__":
    unittest.main()
