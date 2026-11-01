import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("seltenheit.py")
SPEC = importlib.util.spec_from_file_location("seltenheit", MODULE_PATH)
seltenheit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(seltenheit)


class SeltenheitTests(unittest.TestCase):
    def setUp(self):
        self.eintraege = [
            {
                "text": "Test",
                "woerter": [
                    {"lemma": ["häufig I", "selten I"]},
                    {"lemma": ["häufig I"]},
                ],
            },
            {"text": "Test", "woerter": [{"lemma": ["häufig I"]}]},
        ]

    def test_lemmas_der_zeile_entfernt_duplikate_und_leere_werte(self):
        self.assertEqual(
            seltenheit.lemmas_der_zeile(self.eintraege[0]),
            {"häufig I", "selten I"},
        )

    def test_lese_zeilen_liest_gzip_jsonl(self):
        with tempfile.TemporaryDirectory() as verzeichnis:
            pfad = Path(verzeichnis) / "daten.jsonl.gz"
            with gzip.open(pfad, "wt", encoding="utf-8") as datei:
                datei.write(json.dumps(self.eintraege[0], ensure_ascii=False) + "\n")
            self.assertEqual(list(seltenheit.lese_zeilen(pfad)), [self.eintraege[0]])

    def test_zaehlung_und_gewicht(self):
        haeufigkeiten, zeilen = seltenheit.berechne_text_lemmahaeufigkeiten(self.eintraege, "Test")
        self.assertEqual(zeilen, 2)
        self.assertEqual(haeufigkeiten, {"häufig I": 2, "selten I": 1})
        self.assertAlmostEqual(seltenheit.seltenheitsgewicht(1, 2), 0.693147, places=5)

    def test_sortierung_nach_seltenheit(self):
        werte = seltenheit.sortiere_lemmas({"häufig I": 2, "selten I": 1}, 2)
        self.assertEqual([wert[0] for wert in werte], ["selten I", "häufig I"])

    def test_svg_und_textausgabe(self):
        with tempfile.TemporaryDirectory() as verzeichnis:
            svg = Path(verzeichnis) / "test.svg"
            seltenheit.schreibe_svg(svg, "Test & Text", {"selten I": 1, "häufig I": 2}, 2)
            inhalt = svg.read_text(encoding="utf-8")
            self.assertIn("Test &amp; Text", inhalt)
            self.assertIn("Relative Seltenheit", inhalt)
            self.assertIn("selten I", inhalt)

    def test_text_abschnitt_und_komplette_ausgabe(self):
        abschnitt = seltenheit.text_abschnitt(
            "Titel", "Test", 2, [("selten I", 1, 0.693147)]
        )
        self.assertIn("Lemma\tZeilen\tRelative Seltenheit", abschnitt)
        eintraege = [
            {"text": text, "woerter": [{"lemma": ["lemma I"]}]}
            for _, text, _ in seltenheit.TEXTS
        ]
        ausgabe = seltenheit.berechne_ausgabe(eintraege)
        self.assertIn("## I.5 Erra and Išum", ausgabe)
        self.assertIn("## II.1 The Babylonian Theodicy", ausgabe)

    def test_main_erzeugt_alle_dateien(self):
        with tempfile.TemporaryDirectory() as verzeichnis:
            ordner = Path(verzeichnis)
            eingabe = ordner / "daten.jsonl.gz"
            ausgabe = ordner / "Seltenheit.txt"
            grafik = ordner / "grafiken"
            eintraege = [
                {"text": text, "woerter": [{"lemma": ["lemma I"]}]}
                for _, text, _ in seltenheit.TEXTS
            ]
            with gzip.open(eingabe, "wt", encoding="utf-8") as datei:
                datei.write("\n".join(json.dumps(eintrag) for eintrag in eintraege))
            seltenheit.main(eingabe, ausgabe, grafik)
            self.assertTrue(ausgabe.exists())
            self.assertTrue((grafik / "erra_isum.svg").exists())
            self.assertTrue((grafik / "theodizee.svg").exists())

    def test_ausgabe_fehlender_text(self):
        with self.assertRaises(ValueError):
            seltenheit.berechne_text_lemmahaeufigkeiten(self.eintraege, "fehlt")


if __name__ == "__main__":
    unittest.main()
