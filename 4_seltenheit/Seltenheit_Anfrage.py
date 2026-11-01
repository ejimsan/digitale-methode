"""Interaktive Abfrage der Lemmahäufigkeiten aus Seltenheit.txt."""

from __future__ import annotations

import re
from pathlib import Path


DEFAULT_INPUT = Path(__file__).resolve().parent / "Seltenheit.txt"
HEADER_PATTERN = re.compile(r"^## (.+)$")
LINES_PATTERN = re.compile(r"^Ausgewertete lemmatisierte Manuskriptzeilen: (\d+)$")
LEMMA_PATTERN = re.compile(r"^(.+)\t(\d+)\t")
HOMONYM_PATTERN = re.compile(r"^(.+)\s+([IVXLCDM]+)$")


def lemma_basis(lemma: str) -> str:
    """Entfernt eine abschließende römische Homonymnummer."""
    treffer = HOMONYM_PATTERN.match(lemma)
    return treffer.group(1) if treffer else lemma


def normalisiere_lemma(lemma: str) -> str:
    """Vereinheitlicht Leerraum und Groß-/Kleinschreibung für Vergleiche."""
    return " ".join(lemma.split()).casefold()


def finde_haeufigkeit(gesucht: str, haeufigkeiten: dict[str, int]) -> int | None:
    """Findet ein Lemma exakt oder über seine Basisform ohne Homonymnummer."""
    gesucht = gesucht.strip()
    if gesucht in haeufigkeiten:
        return haeufigkeiten[gesucht]
    passende_lemmas = [
        haeufigkeit
        for lemma, haeufigkeit in haeufigkeiten.items()
        if normalisiere_lemma(lemma_basis(lemma)) == normalisiere_lemma(gesucht)
    ]
    if not passende_lemmas:
        return None
    return sum(passende_lemmas)


def lese_ausgabe(pfad: Path = DEFAULT_INPUT) -> dict[str, dict[str, int]]:
    """Liest Textnamen, Zeilenzahlen und Lemmahäufigkeiten aus Seltenheit.txt."""
    texte: dict[str, dict[str, int]] = {}
    aktueller_text: str | None = None
    zeilen: int | None = None

    with pfad.open(encoding="utf-8") as datei:
        for rohzeile in datei:
            zeile = rohzeile.rstrip("\n")
            kopf = HEADER_PATTERN.match(zeile)
            if kopf:
                aktueller_text = kopf.group(1)
                texte[aktueller_text] = {}
                zeilen = None
                continue

            if aktueller_text is None:
                continue

            zeilen_treffer = LINES_PATTERN.match(zeile)
            if zeilen_treffer:
                zeilen = int(zeilen_treffer.group(1))
                continue

            lemma_treffer = LEMMA_PATTERN.match(zeile)
            if lemma_treffer and zeilen is not None:
                lemma, haeufigkeit = lemma_treffer.groups()
                texte[aktueller_text][lemma] = int(haeufigkeit)

    if not texte:
        raise ValueError(f"Keine Textabschnitte in {pfad} gefunden.")
    if any(not eintraege for eintraege in texte.values()):
        raise ValueError(f"Mindestens ein Textabschnitt in {pfad} enthält keine Lemmata.")
    return texte


def formatiere_antwort(
    lemma: str, texte: dict[str, dict[str, int]], zeilenzahlen: dict[str, int]
) -> str:
    """Formatiert die Häufigkeitsantwort für ein Lemma."""
    ausgabe = [f'\nErgebnisse für Lemma "{lemma}":']
    for text, haeufigkeiten in texte.items():
        absolute_haeufigkeit = finde_haeufigkeit(lemma, haeufigkeiten)
        if absolute_haeufigkeit is None:
            ausgabe.append(f"- {text}: nicht gefunden")
            continue
        relative_haeufigkeit = absolute_haeufigkeit / zeilenzahlen[text]
        ausgabe.append(
            f"- {text}: absolut {absolute_haeufigkeit} Zeilen, "
            f"relativ {relative_haeufigkeit:.6f} "
            f"({relative_haeufigkeit:.2%})"
        )
    return "\n".join(ausgabe)


def zeilenzahlen_aus_ausgabe(pfad: Path = DEFAULT_INPUT) -> dict[str, int]:
    """Liest die Gesamtzahl der lemmatisierten Zeilen je Text."""
    zahlen: dict[str, int] = {}
    aktueller_text: str | None = None
    with pfad.open(encoding="utf-8") as datei:
        for rohzeile in datei:
            zeile = rohzeile.rstrip("\n")
            kopf = HEADER_PATTERN.match(zeile)
            if kopf:
                aktueller_text = kopf.group(1)
                continue
            treffer = LINES_PATTERN.match(zeile)
            if treffer and aktueller_text is not None:
                zahlen[aktueller_text] = int(treffer.group(1))
    if not zahlen:
        raise ValueError(f"Keine Zeilenzahlen in {pfad} gefunden.")
    return zahlen


def main(pfad: Path = DEFAULT_INPUT) -> None:
    """Startet die interaktive Lemma-Abfrage."""
    texte = lese_ausgabe(pfad)
    zeilenzahlen = zeilenzahlen_aus_ausgabe(pfad)
    print("Lemma-Häufigkeitsabfrage")
    print("Geben Sie ein Lemma ein; mit 'ende' wird das Programm beendet.")
    while True:
        try:
            lemma = input("\nLemma: ").strip()
        except EOFError:
            print()
            break
        if lemma.lower() in {"ende", "exit", "quit"}:
            break
        if not lemma:
            print("Bitte geben Sie ein nichtleeres Lemma ein.")
            continue
        print(formatiere_antwort(lemma, texte, zeilenzahlen))


if __name__ == "__main__":
    main()
