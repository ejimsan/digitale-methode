"""Interaktive Abfrage gemeinsamer Lemma-Vorkommen in Textzeilen."""

from __future__ import annotations

import gzip
import html
import json
from pathlib import Path

from Seltenheit_Anfrage import (
    DEFAULT_INPUT as DEFAULT_OUTPUT,
    finde_haeufigkeit,
    lese_ausgabe,
    relative_seltenheit,
    zeilenzahlen_aus_ausgabe,
)


DEFAULT_CORPUS = Path(__file__).resolve().parents[1] / "daten" / "ebl_korpus_manuskripte.jsonl.gz"
DEFAULT_GRAPHIC = Path(__file__).resolve().parent / "Bigramme_output.svg"
TEXTS = {
    "I.5 Erra and Išum": "L 1.0.5.0 Standard Babylonian I",
    "II.1 The Babylonian Theodicy": "L 2.1 Standard Babylonian -",
}


def lemma_vorhanden(gesucht: str, lemmata: set[str]) -> bool:
    """Prüft ein Lemma einschließlich seiner Homonymnummern."""
    return finde_haeufigkeit(gesucht, {lemma: 1 for lemma in lemmata}) is not None


def bigramm_haeufigkeiten(
    pfad: Path, text: str, lemma_1: str, lemma_2: str
) -> int:
    """Zählt Zeilen, die beide gesuchten Lemmata enthalten."""
    treffer = 0
    with gzip.open(pfad, "rt", encoding="utf-8") as datei:
        for rohzeile in datei:
            eintrag = json.loads(rohzeile)
            if eintrag.get("text") != text:
                continue
            lemmata = {
                lemma
                for wort in eintrag.get("woerter", [])
                for lemma in wort.get("lemma", [])
                if isinstance(lemma, str) and lemma
            }
            if lemmata and lemma_vorhanden(lemma_1, lemmata) and lemma_vorhanden(
                lemma_2, lemmata
            ):
                treffer += 1
    return treffer


def formatiere_antwort(
    lemma_1: str,
    lemma_2: str,
    ausgabe: dict[str, int],
    zeilenzahlen: dict[str, int],
) -> str:
    """Formatiert absolute Bigrammhäufigkeit und relative Seltenheit."""
    antwort = [f'\nErgebnisse für Bigramm "{lemma_1} + {lemma_2}":']
    for text, haeufigkeit in ausgabe.items():
        seltenheit = (
            relative_seltenheit(haeufigkeit, zeilenzahlen[text])
            if haeufigkeit
            else None
        )
        if seltenheit is None:
            antwort.append(
                f"- {text}: absolut 0 Zeilen, "
                "relative Seltenheit nicht definiert (0 Treffer)"
            )
            continue
        antwort.append(
            f"- {text}: absolut {haeufigkeit} Zeilen, "
            f"relative Seltenheit {seltenheit:.6f} "
            f"(-ln({haeufigkeit}/{zeilenzahlen[text]}))"
        )
    return "\n".join(antwort)


def schreibe_svg(
    pfad: Path,
    lemma_1: str,
    lemma_2: str,
    haeufigkeiten: dict[str, int],
    zeilenzahlen: dict[str, int],
) -> None:
    """Schreibt die Bigrammhäufigkeiten der beiden Texte als Balkendiagramm."""
    breite, hoehe = 800, 480
    rand_links, rand_rechts, rand_oben, rand_unten = 90, 40, 90, 85
    diagramm_breite = breite - rand_links - rand_rechts
    diagramm_hoehe = hoehe - rand_oben - rand_unten
    maximum = max(1, max(haeufigkeiten.values(), default=0))
    balkenbreite = diagramm_breite / max(1, len(haeufigkeiten) * 2 + 1)
    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{breite}" height="{hoehe}" viewBox="0 0 {breite} {hoehe}">',
        '<style>text { font-family: sans-serif; fill: #222; } .title { font-size: 20px; font-weight: bold; } .label { font-size: 13px; } .value { font-size: 12px; } .axis { stroke: #222; stroke-width: 1; } .bar { fill: #4c78a8; }</style>',
        f'<title>Bigramm-Häufigkeit für {html.escape(lemma_1)} und {html.escape(lemma_2)}</title>',
        '<desc>Die Balken zeigen absolute Häufigkeit in Zeilen; die relative Seltenheit ist der negative Logarithmus der relativen Häufigkeit.</desc>',
        f'<text x="{rand_links}" y="30" class="title">Bigramm: {html.escape(lemma_1)} + {html.escape(lemma_2)}</text>',
        f'<text x="{rand_links}" y="55" class="label">Gemeinsame Nennung in einer Manuskriptzeile</text>',
        f'<text x="{rand_links}" y="73" class="label">Wert: absolute Häufigkeit (relative Seltenheit)</text>',
        f'<line x1="{rand_links}" y1="{rand_oben}" x2="{rand_links}" y2="{rand_oben + diagramm_hoehe}" class="axis"/>',
        f'<line x1="{rand_links}" y1="{rand_oben + diagramm_hoehe}" x2="{breite - rand_rechts}" y2="{rand_oben + diagramm_hoehe}" class="axis"/>',
        f'<text x="{breite / 2}" y="{hoehe - 18}" text-anchor="middle" class="label">Eingabetext</text>',
        f'<text x="20" y="{rand_oben + diagramm_hoehe / 2}" text-anchor="middle" transform="rotate(-90 20 {rand_oben + diagramm_hoehe / 2})" class="label">Absolute Bigramm-Häufigkeit (Zeilen)</text>',
    ]
    for index, (text, haeufigkeit) in enumerate(haeufigkeiten.items()):
        x = rand_links + (2 * index + 1) * balkenbreite
        balkenhoehe = round(haeufigkeit / maximum * diagramm_hoehe)
        y = rand_oben + diagramm_hoehe - balkenhoehe
        seltenheit = (
            relative_seltenheit(haeufigkeit, zeilenzahlen[text])
            if haeufigkeit
            else None
        )
        wert = (
            f"{haeufigkeit} (relative Seltenheit: {seltenheit:.3f})"
            if seltenheit is not None
            else f"{haeufigkeit} (relative Seltenheit: nicht definiert)"
        )
        svg.extend(
            [
                f'<rect x="{x:.1f}" y="{y}" width="{balkenbreite:.1f}" height="{balkenhoehe}" class="bar"/>',
                f'<text x="{x + balkenbreite / 2:.1f}" y="{y - 8}" text-anchor="middle" class="value">{wert}</text>',
                f'<text x="{x + balkenbreite / 2:.1f}" y="{rand_oben + diagramm_hoehe + 22}" text-anchor="middle" class="label">{html.escape(text)}</text>',
            ]
        )
    svg.append("</svg>\n")
    pfad.write_text("\n".join(svg), encoding="utf-8", newline="\n")


def main(
    ausgabedatei: Path = DEFAULT_OUTPUT,
    korpus: Path = DEFAULT_CORPUS,
    grafik: Path = DEFAULT_GRAPHIC,
) -> None:
    """Startet die interaktive Bigramm-Abfrage."""
    texte = lese_ausgabe(ausgabedatei)
    zeilenzahlen = zeilenzahlen_aus_ausgabe(ausgabedatei)
    print("Lemma-Bigramm-Häufigkeitsabfrage")
    print("Geben Sie zwei Lemmata ein; mit 'ende' wird das Programm beendet.")
    letzte_abfrage: tuple[str, str, dict[str, int]] | None = None
    while True:
        try:
            lemma_1 = input("\nLemma 1: ").strip()
        except EOFError:
            print()
            break
        if lemma_1.lower() in {"ende", "exit", "quit"}:
            if letzte_abfrage is not None:
                schreibe_svg(grafik, *letzte_abfrage[:2], letzte_abfrage[2], zeilenzahlen)
                print(f"Grafik gespeichert: {grafik}")
            break
        if not lemma_1:
            print("Bitte geben Sie ein nichtleeres erstes Lemma ein.")
            continue
        lemma_2 = input("Lemma 2: ").strip()
        if lemma_2.lower() in {"ende", "exit", "quit"}:
            if letzte_abfrage is not None:
                schreibe_svg(grafik, *letzte_abfrage[:2], letzte_abfrage[2], zeilenzahlen)
                print(f"Grafik gespeichert: {grafik}")
            break
        if not lemma_2:
            print("Bitte geben Sie ein nichtleeres zweites Lemma ein.")
            continue

        haeufigkeiten = {
            text: bigramm_haeufigkeiten(korpus, korpus_text, lemma_1, lemma_2)
            for text, korpus_text in TEXTS.items()
        }
        # Nur Texte aus Seltenheit.txt werden ausgegeben.
        haeufigkeiten = {
            text: haeufigkeit for text, haeufigkeit in haeufigkeiten.items() if text in texte
        }
        letzte_abfrage = (lemma_1, lemma_2, haeufigkeiten)
        print(formatiere_antwort(lemma_1, lemma_2, haeufigkeiten, zeilenzahlen))


if __name__ == "__main__":
    main()
