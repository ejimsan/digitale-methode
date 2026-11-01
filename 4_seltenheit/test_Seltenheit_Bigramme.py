import gzip
import json
import tempfile
import unittest
from pathlib import Path

import Seltenheit_Bigramme as bigramme


class SeltenheitBigrammeTests(unittest.TestCase):
    def test_homonyme_werden_erkannt(self):
        self.assertTrue(bigramme.lemma_vorhanden("ina", {"ina I"}))
        self.assertTrue(bigramme.lemma_vorhanden("ša", {"ša I"}))
        self.assertFalse(bigramme.lemma_vorhanden("ina I", {"ina II"}))

    def test_bigramm_zaehlt_gemeinsame_zeilen(self):
        eintraege = [
            {"text": "Test", "woerter": [{"lemma": ["ina I", "ša I"]}]},
            {"text": "Test", "woerter": [{"lemma": ["ina I"]}]},
            {"text": "Andere", "woerter": [{"lemma": ["ina I", "ša I"]}]},
        ]
        with tempfile.TemporaryDirectory() as verzeichnis:
            pfad = Path(verzeichnis) / "daten.jsonl.gz"
            with gzip.open(pfad, "wt", encoding="utf-8") as datei:
                for eintrag in eintraege:
                    datei.write(json.dumps(eintrag) + "\n")
            self.assertEqual(
                bigramme.bigramm_haeufigkeiten(pfad, "Test", "ina", "ša"),
                1,
            )

    def test_formatiert_absolute_und_relative_haeufigkeit(self):
        antwort = bigramme.formatiere_antwort(
            "ina",
            "ša",
            {"Text": 2},
            {"Text": 10},
        )
        self.assertIn("absolut 2 Zeilen, relative Seltenheit 1.609438", antwort)

    def test_schreibt_svg_mit_achsen_und_letztem_bigramm(self):
        with tempfile.TemporaryDirectory() as verzeichnis:
            pfad = Path(verzeichnis) / "Bigramme_output.svg"
            bigramme.schreibe_svg(
                pfad,
                "ina",
                "ša",
                {"Text A": 2, "Text B": 1},
                {"Text A": 10, "Text B": 20},
            )
            inhalt = pfad.read_text(encoding="utf-8")
            self.assertIn("Bigramm: ina + ša", inhalt)
            self.assertIn("relative Seltenheit", inhalt)
            self.assertIn("Eingabetext", inhalt)
            self.assertIn("Absolute Bigramm-Häufigkeit (Zeilen)", inhalt)
            self.assertIn("relative Seltenheit: 2.996", inhalt)


if __name__ == "__main__":
    unittest.main()
