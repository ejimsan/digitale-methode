import tempfile
import unittest
from pathlib import Path

import Seltenheit_Anfrage as anfrage


AUSGABE = """\
## Text A
Ausgewertete lemmatisierte Manuskriptzeilen: 10
Lemma\tZeilen\tSeltenheitsgewicht
foo I\t2\t1.609438

## Text B
Ausgewertete lemmatisierte Manuskriptzeilen: 20
Lemma\tZeilen\tSeltenheitsgewicht
foo I\t5\t1.386294
"""


class SeltenheitAnfrageTests(unittest.TestCase):
    def test_liest_texte_und_haeufigkeiten(self):
        with tempfile.TemporaryDirectory() as verzeichnis:
            pfad = Path(verzeichnis) / "Seltenheit.txt"
            pfad.write_text(AUSGABE, encoding="utf-8")
            self.assertEqual(
                anfrage.lese_ausgabe(pfad),
                {"Text A": {"foo I": 2}, "Text B": {"foo I": 5}},
            )
            self.assertEqual(
                anfrage.zeilenzahlen_aus_ausgabe(pfad),
                {"Text A": 10, "Text B": 20},
            )

    def test_formatiert_absolute_und_relative_haeufigkeit(self):
        antwort = anfrage.formatiere_antwort(
            "foo I",
            {"Text A": {"foo I": 2}, "Text B": {"foo I": 5}},
            {"Text A": 10, "Text B": 20},
        )
        self.assertIn("absolut 2 Zeilen, relativ 0.200000 (20.00%)", antwort)
        self.assertIn("absolut 5 Zeilen, relativ 0.250000 (25.00%)", antwort)

    def test_basisform_findet_homonymnummer(self):
        haeufigkeiten = {"ina I": 63, "ina II": 2}
        self.assertEqual(anfrage.finde_haeufigkeit("ina", haeufigkeiten), 65)
        self.assertEqual(anfrage.finde_haeufigkeit("ina I", haeufigkeiten), 63)

    def test_unicode_basisform_findet_homonymnummer(self):
        self.assertEqual(anfrage.finde_haeufigkeit("ša", {"ša I": 74}), 74)

    def test_suche_ist_unabhaengig_von_gross_und_kleinschreibung(self):
        self.assertEqual(anfrage.finde_haeufigkeit("erra", {"Erra I": 48}), 48)

    def test_nicht_gefunden(self):
        antwort = anfrage.formatiere_antwort(
            "fehlt", {"Text A": {"foo I": 2}}, {"Text A": 10}
        )
        self.assertIn("Text A: nicht gefunden", antwort)


if __name__ == "__main__":
    unittest.main()
