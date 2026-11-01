"""Berechnet Lemma-Häufigkeiten und Seltenheitsgewichte für das Manuskriptkorpus."""

from __future__ import annotations

import argparse
import gzip
import html
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "daten" / "ebl_korpus_manuskripte.jsonl.gz"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "Seltenheit.txt"
DEFAULT_GRAPHICS = Path(__file__).resolve().parent
TEXTS = (
    ("## I.5 Erra and Išum", "L 1.0.5.0 Standard Babylonian I", "erra_isum.svg"),
    ("## II.1 The Babylonian Theodicy", "L 2.1 Standard Babylonian -", "theodizee.svg"),
)


def lese_zeilen(pfad: Path) -> Iterable[dict]:
    """Liest JSONL-Datensätze aus einer gzip-komprimierten Datei."""
    with gzip.open(pfad, "rt", encoding="utf-8") as datei:
        for nummer, text in enumerate(datei, 1):
            if not text.strip():
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError as fehler:
                raise ValueError(f"Ungültiges JSON in {pfad}, Zeile {nummer}") from fehler


def lemmas_der_zeile(eintrag: dict) -> set[str]:
    """Gibt die unterschiedlichen, gültigen Lemmata einer Zeile zurück."""
    return {
        lemma
        for wort in eintrag.get("woerter", [])
        for lemma in wort.get("lemma", [])
        if isinstance(lemma, str) and lemma
    }


def berechne_text_lemmahaeufigkeiten(
    eintraege: Iterable[dict], text: str
) -> tuple[Counter[str], int]:
    """Zählt Lemmata einmal je Zeile und gibt Zählung und Zeilenzahl zurück."""
    haeufigkeiten: Counter[str] = Counter()
    zeilen = 0
    for eintrag in eintraege:
        if eintrag.get("text") != text:
            continue
        lemmas = lemmas_der_zeile(eintrag)
        if lemmas:
            zeilen += 1
            haeufigkeiten.update(lemmas)
    if not haeufigkeiten:
        raise ValueError(f"Der Text {text!r} enthält keine lemmatisierten Zeilen.")
    return haeufigkeiten, zeilen


def seltenheitsgewicht(haeufigkeit: int, zeilen: int) -> float:
    """Berechnet -ln(relative Häufigkeit)."""
    return -math.log(haeufigkeit / zeilen)


def sortiere_lemmas(
    haeufigkeiten: Counter[str], zeilen: int
) -> list[tuple[str, int, float]]:
    """Sortiert Lemmata nach Seltenheit und ergänzt ihr Gewicht."""
    werte = [
        (lemma, haeufigkeit, seltenheitsgewicht(haeufigkeit, zeilen))
        for lemma, haeufigkeit in haeufigkeiten.items()
    ]
    return sorted(werte, key=lambda wert: (-wert[2], wert[0]))


def text_abschnitt(titel: str, text: str, zeilen: int, werte: list[tuple[str, int, float]]) -> list[str]:
    ausgabe = [
        "",
        titel,
        f"Korpusbezeichnung: {text}",
        f"Ausgewertete lemmatisierte Manuskriptzeilen: {zeilen}",
        f"Ausgegebene Lemmata: {len(werte)}",
        "Lemma\tZeilen\tRelative Seltenheit",
        "--------------------------------",
    ]
    ausgabe.extend(f"{lemma}\t{anzahl}\t{gewicht:.6f}" for lemma, anzahl, gewicht in werte)
    return ausgabe


def berechne_ausgabe(eintraege: Iterable[dict]) -> list[str]:
    """Erzeugt die vollständige Textausgabe für beide Texte."""
    eintraege = list(eintraege)
    ausgabe = [
        "Seltenheitsauswertung aller Lemmata",
        "Gezählt wird höchstens einmal pro Lemma und Manuskriptzeile.",
        "Relative Seltenheit: -ln(relative Häufigkeit).",
    ]
    for titel, text, _ in TEXTS:
        haeufigkeiten, zeilen = berechne_text_lemmahaeufigkeiten(eintraege, text)
        ausgabe.extend(text_abschnitt(titel, text, zeilen, sortiere_lemmas(haeufigkeiten, zeilen)))
    return ausgabe + [""]


def schreibe_svg(pfad: Path, titel: str, haeufigkeiten: Counter[str], zeilen: int) -> None:
    """Schreibt den nach Seltenheit geordneten Wortschatz als SVG-Diagramm."""
    werte = sortiere_lemmas(haeufigkeiten, zeilen)
    balkenhoehe, rand_oben = 18, 80
    rand_links, rand_rechts, rand_unten = 210, 55, 55
    breite, diagramm_breite = 1000, 735
    hoehe = rand_oben + len(werte) * balkenhoehe + rand_unten
    maximum = max(1.0, max(gewicht for _, _, gewicht in werte))
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{breite}" height="{hoehe}" viewBox="0 0 {breite} {hoehe}">',
        '<style>text { font-family: sans-serif; fill: #222; } .title { font-size: 20px; font-weight: bold; } .label { font-size: 12px; } .value { font-size: 11px; } .axis { stroke: #222; stroke-width: 1; } .bar { fill: #4c78a8; }</style>',
        f'<text x="{rand_links}" y="30" class="title">{html.escape(titel)}</text>',
        f'<text x="{rand_links}" y="52" class="label">Wortschatz nach Seltenheit (seltenste zuerst)</text>',
        f'<text x="{rand_links}" y="68" class="label">Relative Seltenheit: -ln(relative Häufigkeit)</text>',
    ]
    for index, (lemma, _, gewicht) in enumerate(werte):
        y = rand_oben + index * balkenhoehe
        balkenbreite = max(2, round(gewicht / maximum * diagramm_breite))
        svg.extend(
            [
                f'<text x="{rand_links - 8}" y="{y + 13}" text-anchor="end" class="label">{html.escape(lemma)}</text>',
                f'<rect x="{rand_links}" y="{y + 2}" width="{balkenbreite}" height="12" class="bar"/>',
                f'<text x="{rand_links + balkenbreite + 6}" y="{y + 13}" class="value">{gewicht:.3f}</text>',
            ]
        )
    achsen_y = rand_oben + len(werte) * balkenhoehe
    svg.extend(
        [
            f'<line x1="{rand_links}" y1="{rand_oben - 4}" x2="{rand_links}" y2="{achsen_y}" class="axis"/>',
            f'<line x1="{rand_links}" y1="{achsen_y}" x2="{breite - rand_rechts}" y2="{achsen_y}" class="axis"/>',
            f'<text x="{breite / 2}" y="{hoehe - 12}" text-anchor="middle" class="label">Relative Seltenheit -ln(relative Häufigkeit)</text>',
            f'<text x="18" y="{rand_oben + (achsen_y - rand_oben) / 2}" text-anchor="middle" transform="rotate(-90 18 {rand_oben + (achsen_y - rand_oben) / 2})" class="label">Lemma (nach Seltenheit geordnet)</text>',
            "</svg>\n",
        ]
    )
    pfad.write_text("\n".join(svg), encoding="utf-8", newline="\n")


def main(
    eingabe: Path = DEFAULT_INPUT,
    ausgabe: Path = DEFAULT_OUTPUT,
    grafik_verzeichnis: Path = DEFAULT_GRAPHICS,
) -> None:
    """Erzeugt Textausgabe und je eine SVG-Grafik pro Text."""
    eintraege = list(lese_zeilen(eingabe))
    ausgabe.parent.mkdir(parents=True, exist_ok=True)
    ausgabe.write_text("\n".join(berechne_ausgabe(eintraege)) + "\n", encoding="utf-8", newline="\n")
    grafik_verzeichnis.mkdir(parents=True, exist_ok=True)
    for titel, text, dateiname in TEXTS:
        haeufigkeiten, zeilen = berechne_text_lemmahaeufigkeiten(eintraege, text)
        schreibe_svg(grafik_verzeichnis / dateiname, titel, haeufigkeiten, zeilen)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eingabe", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--ausgabe", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--grafik-verzeichnis", type=Path, default=DEFAULT_GRAPHICS)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.eingabe, args.ausgabe, args.grafik_verzeichnis)
