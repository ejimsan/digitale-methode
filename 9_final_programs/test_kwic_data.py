import gzip
import json
import tempfile
import unittest
from pathlib import Path

from kwic_data import (
    _belegangabe,
    _ebl_lemma_praesent,
    _kwic_zeilen,
    _lese_jsonl_gz,
    _normalisiere_suchbegriffe,
    _oracc_lemma_liste,
    _oracc_schluessel,
    _oracc_schluessel_im_eintrag,
)


class KwicDataTests(unittest.TestCase):
    def test_reads_jsonl_gzip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "rows.jsonl.gz"
            with gzip.open(path, "wt", encoding="utf-8") as stream:
                stream.write(json.dumps({"id": 1}) + "\n")
                stream.write(json.dumps({"id": 2}) + "\n")
            self.assertEqual(list(_lese_jsonl_gz(path)), [{"id": 1}, {"id": 2}])

    def test_parses_oracc_lemma_and_rejects_malformed(self):
        self.assertEqual(_oracc_schluessel("šarru[king]"), ("šarru", "king"))
        self.assertIsNone(_oracc_schluessel("šarru"))
        self.assertIsNone(_oracc_schluessel("šarru[king"))

    def test_oracc_lemma_list_normalizes_and_validates(self):
        self.assertEqual(_oracc_lemma_liste("x[a]"), ("x[a]",))
        self.assertEqual(_oracc_lemma_liste(["x[a]", "", "x[a]"]), ("x[a]",))
        for value in (None, 4, ["x[a]", 2]):
            with self.subTest(value=value), self.assertRaises(TypeError):
                _oracc_lemma_liste(value)

    def test_normalizes_search_inputs(self):
        self.assertEqual(_normalisiere_suchbegriffe((" x ", "a[a]")),
                         [("x", ("a[a]",))])
        self.assertEqual(
            _normalisiere_suchbegriffe([("x", ["a[a]", "b[b]"])]),
            [("x", ("a[a]", "b[b]"))],
        )
        for value, error in (([], ValueError), ("x", TypeError), ([("", "a")], TypeError)):
            with self.subTest(value=value), self.assertRaises(error):
                _normalisiere_suchbegriffe(value)

    def test_ebl_and_oracc_entry_matching(self):
        entry = {"woerter": [{"lemma": ["x"]}, {"oracc": "x[a]"}]}
        self.assertTrue(_ebl_lemma_praesent(entry, "x"))
        self.assertFalse(_ebl_lemma_praesent(entry, "y"))
        self.assertEqual(_oracc_schluessel_im_eintrag(entry), {("x", "a")})

    def test_citation_and_kwic_rows(self):
        entry = {
            "text": "Text 1", "zeile": "3", "periode": "alt",
            "manuskript": "M1", "manuskript_zeile": "4",
            "woerter": [{"wert": "a"}, {"wert": "b"}, {"wert": "c"}],
        }
        self.assertEqual(_belegangabe("ebl_korpus", entry), "Text 1, 3")
        self.assertEqual(_belegangabe("ebl_korpus_manuskripte", entry), "alt, M1, 4")
        self.assertEqual(_belegangabe("oracc", {"zeile": None}), "")
        self.assertEqual(
            _kwic_zeilen("ebl_korpus", entry, [1]),
            [("Text 1, 3", "a", "b", "c")],
        )
        self.assertEqual(_kwic_zeilen("oracc", entry, []), [])


if __name__ == "__main__":
    unittest.main()
