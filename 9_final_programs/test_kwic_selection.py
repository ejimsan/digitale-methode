import unittest
from unittest.mock import patch

from kwic_selection import _passende_eintraege, bestimme_lemma


class KwicSelectionTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {
                "_id": "šarru", "lemma": ["šarru"],
                "forms": [{"lemma": ["šarru"]}],
                "meaning": "König",
                "oraccWords": [
                    {"lemma": "šarru", "guideWord": "king"},
                    {"lemma": "šarru", "guideWord": "king"},
                    {"lemma": "lugal", "guideWord": "king"},
                ],
            },
            {"_id": "šarru II", "lemma": ["šarru"]},
            {"_id": "awīlu", "lemma": ["awīlu"], "oraccWords": []},
        ]

    def test_matches_lemma_and_inflected_forms_case_insensitively(self):
        self.assertEqual(
            [item["_id"] for item in _passende_eintraege(self.entries, "šarru")],
            ["šarru", "šarru II"],
        )
        self.assertEqual(_passende_eintraege(self.entries, "missing"), [])

    @patch("kwic_selection._lese_jsonl_gz")
    @patch("builtins.input", side_effect=[
        "", "missing", "ŠARRU", "info", "0", "nope", "1", "hmm", "j",
        "awīlu", "1", "n",
    ])
    def test_selects_multiple_entries_and_handles_invalid_responses(
        self, _input, read_data
    ):
        read_data.return_value = iter(self.entries)
        with patch("builtins.print") as output:
            selected = bestimme_lemma()
        self.assertEqual(
            selected,
            [
                ("šarru", ("šarru[king]", "lugal[king]")),
                ("awīlu", ()),
            ],
        )
        printed = " ".join(str(call) for call in output.call_args_list)
        self.assertIn("keine Bedeutung", printed)
        self.assertIn("Keine passenden Lemmata", printed)

    @patch("kwic_selection._lese_jsonl_gz")
    @patch("builtins.input", side_effect=["šarru", "1", "nein"])
    def test_single_choice_returns_a_tuple(self, _input, read_data):
        read_data.return_value = iter(self.entries)
        self.assertEqual(
            bestimme_lemma(), ("šarru", ("šarru[king]", "lugal[king]"))
        )


if __name__ == "__main__":
    unittest.main()
