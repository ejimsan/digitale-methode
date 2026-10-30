import unittest
from unittest.mock import patch

from kwic_search import suche_belege


class KwicSearchTests(unittest.TestCase):
    def test_searches_ebl_manuscripts_and_oracc_with_and_semantics(self):
        corpus = [
            {"text": "T1", "zeile": "1", "woerter": [
                {"wert": "x", "lemma": ["X"]}, {"wert": "y", "lemma": ["Y"]},
                {"wert": "x2", "lemma": ["X"]},
            ]},
            {"text": "T2", "zeile": "2", "woerter": [
                {"wert": "x", "lemma": ["X"]},
            ]},
        ]
        manuscripts = [{
            "periode": "alt", "manuskript": "M", "zeile": "3",
            "woerter": [{"wert": "y", "lemma": ["Y"]},
                        {"wert": "x", "lemma": ["X"]}],
        }]
        oracc = [
            {"text": "O1", "zeile": "4", "woerter": [
                {"wert": "X", "oracc": "x[a]"},
                {"wert": "Y", "oracc": "y[b]"},
            ]},
            {"text": "O2", "zeile": "5", "woerter": [
                {"wert": "X", "oracc": "x[a]"},
            ]},
        ]

        def load(path):
            return iter({
                "ebl_korpus.jsonl.gz": corpus,
                "ebl_korpus_manuskripte.jsonl.gz": manuscripts,
                "oracc.jsonl.gz": oracc,
            }[path.name])

        with patch("kwic_search._lese_jsonl_gz", side_effect=load):
            results = suche_belege([("X", "x[a]"), ("Y", "y[b]")])
        self.assertEqual(results, [
            ("T1, 1", "", "x", "y x2"),
            ("T1, 1", "x y", "x2", ""),
            ("alt, M, 3", "y", "x", ""),
            ("O1, 4", "", "X", "Y"),
        ])

    def test_skips_oracc_when_a_search_term_has_no_mapping(self):
        def load(path):
            if path.name == "oracc.jsonl.gz":
                self.fail("Oracc must not be read without mappings.")
            return iter(())

        with patch("kwic_search._lese_jsonl_gz", side_effect=load):
            self.assertEqual(suche_belege([("X", ()), ("Y", "y[b]")]), [])

    def test_rejects_invalid_search_terms_before_reading_data(self):
        with patch("kwic_search._lese_jsonl_gz") as read_data:
            with self.assertRaises(ValueError):
                suche_belege([])
        read_data.assert_not_called()


if __name__ == "__main__":
    unittest.main()
