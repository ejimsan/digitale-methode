import csv
from pathlib import Path

from kwic_data import KWICTreffer


def exportiere_csv(
    belege: list[KWICTreffer], dateipfad: str | Path, ueberschreiben: bool = False
) -> Path:
    """Exportiert KWIC-Belege in eine CSV-Datei."""
    if not isinstance(ueberschreiben, bool):
        raise TypeError("ueberschreiben muss True oder False sein.")
    ziel = Path(dateipfad)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if ziel.exists() and not ueberschreiben:
        raise FileExistsError(f"Die Datei existiert bereits: {ziel}")
    with ziel.open(
        "w" if ueberschreiben else "x",
        newline="",
        encoding="utf-8-sig",
    ) as datei:
        schreiber = csv.writer(datei)
        schreiber.writerow(
            ("Beleg", "Wörter vor Keyword", "Keyword", "Wörter nach Keyword")
        )
        schreiber.writerows(belege)
    return ziel
