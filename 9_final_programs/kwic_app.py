from __future__ import annotations

from pathlib import Path

from kwic_data import CSV_ORDNER, KWICTreffer
from kwic_display import keyword_in_context_ausgabe
from kwic_export import exportiere_csv
from kwic_search import suche_belege
from kwic_selection import bestimme_lemma


def suche_und_zeige_kwic() -> list[KWICTreffer]:
    """Führt Auswahl, Suche, Anzeige und optionalen CSV-Export aus."""
    suchbegriffe = bestimme_lemma()
    belege = suche_belege(suchbegriffe)
    kwic_belege = keyword_in_context_ausgabe(belege)
    antwort = input("KWIC-Belege als CSV exportieren? (j/n): ").strip().casefold()
    if antwort in {"j", "ja"}:
        dateiname = input("Dateiname [konkordanz.csv]: ").strip()
        dateiname = dateiname or "konkordanz.csv"
        if Path(dateiname).name != dateiname:
            raise ValueError("Bitte nur einen Dateinamen ohne Ordnerpfad angeben.")
        if Path(dateiname).suffix.casefold() != ".csv":
            dateiname += ".csv"
        ziel = CSV_ORDNER / dateiname
        ueberschreiben = False
        if ziel.exists():
            bestaetigung = input(
                f"{ziel.name} existiert bereits. Überschreiben? (j/n): "
            ).strip().casefold()
            if bestaetigung not in {"j", "ja"}:
                print("CSV-Export abgebrochen.")
                return kwic_belege
            ueberschreiben = True
        exportiere_csv(kwic_belege, ziel, ueberschreiben=ueberschreiben)
        print(f"CSV-Datei geschrieben: {ziel}")
    elif antwort not in {"n", "nein", ""}:
        print("CSV-Export übersprungen; bitte mit j oder n antworten.")
    return kwic_belege
