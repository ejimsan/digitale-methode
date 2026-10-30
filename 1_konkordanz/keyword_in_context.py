import csv
import gzip
import json
from collections.abc import Iterable
from pathlib import Path


def _lemma_basis(lemma: str) -> str:
    """Entfernt eine abschließende römische Homonymnummer."""

    teile = lemma.rsplit(maxsplit=1)
    if len(teile) == 2 and all(
        zeichen in "IVXLCDM" for zeichen in teile[1]
    ):
        return teile[0]
    return lemma


def _lemma_passt(gesucht: str, vorhanden: str, feine_suche: bool) -> bool:
    if feine_suche and _lemma_basis(gesucht) == gesucht:
        return _lemma_basis(vorhanden) == gesucht
    if feine_suche:
        return gesucht == vorhanden
    return _lemma_basis(gesucht) == _lemma_basis(vorhanden)


def suche_belege(
    lemmata: str | Iterable[str], feine_suche: bool = True
) -> dict[str, list[dict]]:
    """Sucht Zeilen, die alle Lemmata enthalten, in beiden eBL-Korpora."""

    if not isinstance(feine_suche, bool):
        raise TypeError("feine_suche muss True oder False sein.")
    if isinstance(lemmata, str):
        lemmata = [lemmata]
    suchlemmata = list(lemmata)
    if any(not isinstance(lemma, str) for lemma in suchlemmata):
        raise TypeError("Alle Lemmata müssen Zeichenketten sein.")
    suchlemmata = list(dict.fromkeys(lemma.strip() for lemma in suchlemmata))
    if not suchlemmata or any(not lemma for lemma in suchlemmata):
        raise ValueError("Mindestens ein nichtleeres Lemma ist erforderlich.")

    datenordner = Path(__file__).resolve().parent.parent / "daten"
    dateien = {
        "ebl_korpus_manuskripte": datenordner / "ebl_korpus_manuskripte.jsonl.gz",
        "ebl_korpus": datenordner / "ebl_korpus.jsonl.gz",
    }
    belege = {}

    for datensatz, dateipfad in dateien.items():
        belege[datensatz] = []
        with gzip.open(dateipfad, "rt", encoding="utf-8") as datei:
            for zeile in datei:
                eintrag = json.loads(zeile)
                treffer_pro_suche = [
                    [
                        lemma
                        for wort in eintrag["woerter"]
                        for lemma in wort["lemma"]
                        if _lemma_passt(suchlemma, lemma, feine_suche)
                    ]
                    for suchlemma in suchlemmata
                ]
                if all(treffer_pro_suche):
                    beleg = dict(eintrag)
                    beleg["treffer"] = list(
                        dict.fromkeys(
                            lemma
                            for treffer in treffer_pro_suche
                            for lemma in treffer
                        )
                    )
                    beleg["kwic_treffer"] = list(
                        dict.fromkeys(treffer_pro_suche[0])
                    )
                    belege[datensatz].append(beleg)

    return belege


def lemma_eingabe() -> str | list[str]:
    """Fragt nach Wortformen und lässt passende eBL-Lemmata auswählen."""

    woerterbuch_datei = (
        Path(__file__).resolve().parent.parent
        / "daten"
        / "ebl_woerterbuch.jsonl.gz"
    )
    with gzip.open(woerterbuch_datei, "rt", encoding="utf-8") as datei:
        woerterbuch = [json.loads(zeile) for zeile in datei]

    ausgewaehlte_lemmata = []
    while True:
        wort = input("Akkadisches Wort oder Form: ").strip().casefold()
        while not wort:
            print("Bitte gib ein Wort ein.")
            wort = input("Akkadisches Wort oder Form: ").strip().casefold()

        passende_eintraege = []
        for eintrag in woerterbuch:
            formen = [
                formlemma
                for form in eintrag.get("forms", [])
                if isinstance(form, dict)
                for formlemma in form.get("lemma", [])
                if isinstance(formlemma, str)
            ]
            lemmaformen = [
                lemma
                for lemma in eintrag.get("lemma", [])
                if isinstance(lemma, str)
            ]
            if any(
                form.casefold() == wort
                for form in (*lemmaformen, *formen)
            ):
                passende_eintraege.append(eintrag)

        if not passende_eintraege:
            print(f"Keine passenden Lemmata für {wort!r} gefunden.")
            continue

        print("Lemmata im EBL-Dictionary:")
        for nummer, eintrag in enumerate(passende_eintraege, start=1):
            print(f"{nummer}. {eintrag['_id']}")

        while True:
            auswahl = input(
                "Nummer des gesuchten Lemmas (info = Bedeutungen anzeigen): "
            ).strip().casefold()
            if auswahl == "info":
                for nummer, eintrag in enumerate(passende_eintraege, start=1):
                    bedeutung = eintrag.get("meaning", "").strip()
                    if bedeutung:
                        print(f"{nummer}. {eintrag['_id']} ({bedeutung})")
                    else:
                        print(f"{nummer}. {eintrag['_id']} (Keine Bedeutungsangabe)")
                continue
            try:
                nummer = int(auswahl)
            except ValueError:
                print("Bitte gib eine Nummer aus der Liste ein.")
                continue
            if 1 <= nummer <= len(passende_eintraege):
                ausgewaehlte_lemmata.append(
                    passende_eintraege[nummer - 1]["_id"]
                )
                break
            print("Bitte gib eine Nummer aus der Liste ein.")

        while True:
            weiter = input("Ein weiteres Wort suchen? (j/n): ").strip().casefold()
            if weiter in {"j", "ja"}:
                break
            if weiter in {"n", "nein"}:
                return (
                    ausgewaehlte_lemmata[0]
                    if len(ausgewaehlte_lemmata) == 1
                    else ausgewaehlte_lemmata
                )
            print("Bitte antworte mit ja oder nein.")


def erstelle_konkordanz(
    belege: dict[str, list[dict]], kontextwoerter: int | None = None
) -> list[dict]:
    """Erstellt pro Lemma-Beleg einen KWIC-Eintrag mit Kontext in Wortformen."""

    if kontextwoerter is not None and (
        not isinstance(kontextwoerter, int) or isinstance(kontextwoerter, bool)
    ):
        raise TypeError(
            "kontextwoerter muss None oder eine nichtnegative ganze Zahl sein."
        )
    if kontextwoerter is not None and kontextwoerter < 0:
        raise ValueError("kontextwoerter darf nicht negativ sein.")

    konkordanz = []
    for datensatz, zeilen in belege.items():
        for eintrag in zeilen:
            woerter = eintrag["woerter"]
            kwic_treffer = eintrag.get("kwic_treffer", eintrag["treffer"])
            for index, wort in enumerate(woerter):
                for lemma in dict.fromkeys(wort["lemma"]):
                    if lemma not in kwic_treffer:
                        continue

                    start = (
                        0
                        if kontextwoerter is None
                        else max(0, index - kontextwoerter)
                    )
                    ende = (
                        len(woerter)
                        if kontextwoerter is None
                        else index + 1 + kontextwoerter
                    )
                    kwic = dict(eintrag)
                    kwic.update(
                        {
                            "datensatz": datensatz,
                            "suchlemma": lemma,
                            "links": " ".join(
                                w["wert"] for w in woerter[start:index]
                            ),
                            "stichwort": wort["wert"],
                            "rechts": " ".join(
                                w["wert"] for w in woerter[index + 1:ende]
                            ),
                        }
                    )
                    konkordanz.append(kwic)

    return konkordanz


def keyword_in_context(
    belege: dict[str, list[dict]],
    kontextwoerter: int | None = None,
) -> list[dict]:
    """Gibt Treffer im KWIC-Format aus und liefert die Einträge zusätzlich zurück."""

    konkordanz = erstelle_konkordanz(belege, kontextwoerter)
    gruppen = (
        ("ebl_korpus", "Korpus-Belege"),
        ("ebl_korpus_manuskripte", "Library-Belege"),
    )
    keyword_breite = max(
        (len(eintrag["stichwort"]) for eintrag in konkordanz), default=1
    )
    linksbreite = max(
        (len(eintrag["links"]) for eintrag in konkordanz), default=0
    )

    for nummer, (datensatz, ueberschrift) in enumerate(gruppen):
        if nummer:
            print()
        print(ueberschrift)
        treffer = [
            eintrag
            for eintrag in konkordanz
            if eintrag["datensatz"] == datensatz
        ]
        if not treffer:
            print("  Keine Belege gefunden.")
            continue

        for eintrag in treffer:
            if datensatz == "ebl_korpus_manuskripte":
                angaben = ", ".join(
                    (
                        eintrag.get("periode", ""),
                        eintrag.get("manuskript", ""),
                        eintrag.get("manuskript_zeile", eintrag.get("zeile", "")),
                    )
                )
            else:
                angaben = ", ".join(
                    (eintrag.get("text", ""), eintrag.get("zeile", ""))
                )
            print(f"  {angaben}")
            print(
                f"\t{eintrag['links']:>{linksbreite}} "
                f"{eintrag['stichwort']:<{keyword_breite}} "
                f"{eintrag['rechts']}"
            )
    return konkordanz


def exportiere_csv(
    konkordanz: list[dict], dateipfad: str | Path, ueberschreiben: bool = False
) -> Path:
    """Exportiert KWIC-Einträge als CSV-Datei."""

    if not isinstance(ueberschreiben, bool):
        raise TypeError("ueberschreiben muss True oder False sein.")
    ziel = Path(dateipfad)
    if ziel.exists() and not ueberschreiben:
        raise FileExistsError(f"Die Datei existiert bereits: {ziel}")

    felder = (
        "datensatz",
        "suchlemma",
        "text",
        "zeile",
        "periode",
        "manuskript",
        "manuskript_zeile",
        "links",
        "stichwort",
        "rechts",
    )
    with ziel.open(
        "w" if ueberschreiben else "x",
        newline="",
        encoding="utf-8-sig",
    ) as datei:
        schreiber = csv.DictWriter(datei, fieldnames=felder, extrasaction="ignore")
        schreiber.writeheader()
        schreiber.writerows(konkordanz)
    return ziel


def suche_konkordanz(
    feine_suche: bool = True,
    kontextwoerter: int | None = None,
) -> dict[str, list[dict]]:
    """Fragt Lemmata ab, sucht Belege und gibt sie als KWIC aus."""

    if kontextwoerter is None:
        eingabe = input(
            "Kontextbreite in Wörtern je Seite (leer = ganze Zeile): "
        ).strip()
        if eingabe:
            try:
                kontextwoerter = int(eingabe)
            except ValueError as fehler:
                raise ValueError(
                    "Die Kontextbreite muss eine nichtnegative ganze Zahl sein."
                ) from fehler
            if kontextwoerter < 0:
                raise ValueError("Die Kontextbreite darf nicht negativ sein.")

    lemmata = lemma_eingabe()
    belege = suche_belege(lemmata, feine_suche=feine_suche)
    konkordanz = keyword_in_context(
        belege,
        kontextwoerter=kontextwoerter,
    )
    while True:
        exportieren = input("Ergebnis als CSV exportieren? (j/n): ").strip().casefold()
        if exportieren in ("n", "nein"):
            break
        if exportieren in ("j", "ja"):
            dateiname = input(
                "Dateiname [konkordanz.csv]: "
            ).strip() or "konkordanz.csv"
            ziel = Path("1_konkordanz\\csv_belege") / f"csv_belege_{dateiname}"
            ueberschreiben = False
            if ziel.exists():
                antwort = input(f"{ziel} existiert. Überschreiben? (j/n): ")
                if antwort.strip().casefold() not in ("j", "ja"):
                    print("CSV-Export abgebrochen.")
                    break
                ueberschreiben = True
            exportiere_csv(konkordanz, ziel, ueberschreiben=ueberschreiben)
            print(f"CSV-Datei geschrieben: {ziel}")
            break
        print("Bitte antworte mit ja oder nein.")

    return belege

if __name__ == "__main__":
    suche_konkordanz()