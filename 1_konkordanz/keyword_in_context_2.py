import csv
import gzip
import json
from collections.abc import Iterable
from pathlib import Path


ORDNER = Path(__file__).resolve().parent
DATENORDNER = ORDNER.parent / "daten"
CSV_ORDNER = ORDNER / "csv_belege"

OraccLemma = str | tuple[str, ...]
LemmaAuswahl = tuple[str, OraccLemma]
KWICTreffer = tuple[str, str, str, str]


def _lese_jsonl_gz(dateipfad: Path) -> Iterable[dict]:
    with gzip.open(dateipfad, "rt", encoding="utf-8") as datei:
        for zeile in datei:
            yield json.loads(zeile)


def _oracc_schluessel(oracc_lemma: str) -> tuple[str, str] | None:
    lemma, klammer, rest = oracc_lemma.partition("[")
    guideword, schlussklammer, _ = rest.partition("]")
    if not klammer or not schlussklammer:
        return None
    return lemma, guideword


def _oracc_lemma_liste(oracc_lemmata: object) -> tuple[str, ...]:
    if isinstance(oracc_lemmata, str):
        oracc_lemmata = (oracc_lemmata,)
    if not isinstance(oracc_lemmata, Iterable):
        raise TypeError("Oracc-Lemmata müssen Zeichenketten sein.")

    lemmata = tuple(oracc_lemmata)
    if any(not isinstance(lemma, str) for lemma in lemmata):
        raise TypeError("Oracc-Lemmata müssen Zeichenketten sein.")
    return tuple(dict.fromkeys(lemma for lemma in lemmata if lemma))


def _normalisiere_suchbegriffe(
    suchbegriffe: LemmaAuswahl | list[LemmaAuswahl],
) -> list[LemmaAuswahl]:
    if (
        isinstance(suchbegriffe, tuple)
        and len(suchbegriffe) == 2
        and isinstance(suchbegriffe[0], str)
    ):
        auswahl_liste = [suchbegriffe]
    elif isinstance(suchbegriffe, list):
        auswahl_liste = suchbegriffe
    else:
        raise TypeError(
            "Erwartet wird ein Lemma-Tuple oder eine Liste solcher Tupel."
        )

    if not auswahl_liste:
        raise ValueError("Mindestens ein Suchbegriff ist erforderlich.")

    normalisiert = []
    for auswahl in auswahl_liste:
        if (
            not isinstance(auswahl, tuple)
            or len(auswahl) != 2
            or not isinstance(auswahl[0], str)
            or not auswahl[0].strip()
        ):
            raise TypeError(
                "Jeder Suchbegriff muss aus EBL-Lemma und Oracc-Lemma bestehen."
            )
        ebl_lemma = auswahl[0].strip()
        oracc_lemmata = _oracc_lemma_liste(auswahl[1])
        normalisiert.append((ebl_lemma, oracc_lemmata))
    return normalisiert


def _ebl_lemma_praesent(eintrag: dict, ebl_lemma: str) -> bool:
    return any(
        ebl_lemma in wort.get("lemma", [])
        for wort in eintrag.get("woerter", [])
    )


def _oracc_schluessel_im_eintrag(eintrag: dict) -> set[tuple[str, str]]:
    schluessel = set()
    for wort in eintrag.get("woerter", []):
        raw_lemma = wort.get("oracc", "")
        if isinstance(raw_lemma, str):
            schluessel_eintrag = _oracc_schluessel(raw_lemma)
            if schluessel_eintrag is not None:
                schluessel.add(schluessel_eintrag)
    return schluessel


def bestimme_lemma() -> LemmaAuswahl | list[LemmaAuswahl]:
    """Lässt Lemmata wählen; mehrere Oracc-Zuordnungen bleiben gemeinsam erhalten."""

    woerterbuch = list(
        _lese_jsonl_gz(DATENORDNER / "ebl_woerterbuch.jsonl.gz")
    )
    ausgewaehlte_lemmata: list[LemmaAuswahl] = []

    while True:
        wort = input("Akkadisches Wort in der Grundform: ").strip().casefold()
        if not wort:
            print("Bitte gib ein Wort ein.")
            continue

        passende_eintraege = []
        for eintrag in woerterbuch:
            grundformen = [
                lemma
                for lemma in eintrag.get("lemma", [])
                if isinstance(lemma, str)
            ]
            formen = [
                formlemma
                for form in eintrag.get("forms", [])
                if isinstance(form, dict)
                for formlemma in form.get("lemma", [])
                if isinstance(formlemma, str)
            ]
            if any(
                form.casefold() == wort
                for form in (*grundformen, *formen)
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
                "Nummer des gewünschten Lemmas (info = Bedeutungen): "
            ).strip().casefold()
            if auswahl == "info":
                for nummer, eintrag in enumerate(passende_eintraege, start=1):
                    bedeutung = eintrag.get("meaning", "").strip()
                    if bedeutung:
                        print(f"{nummer}. {eintrag['_id']} ({bedeutung})")
                    else:
                        print(f"{nummer}. {eintrag['_id']} (keine Bedeutung)")
                continue
            try:
                nummer = int(auswahl)
            except ValueError:
                print("Bitte gib eine Nummer aus der Liste ein.")
                continue
            if 1 <= nummer <= len(passende_eintraege):
                eintrag = passende_eintraege[nummer - 1]
                oracc_lemmata = tuple(
                    f"{zuordnung['lemma']}[{zuordnung['guideWord']}]"
                    for zuordnung in eintrag.get("oraccWords", [])
                    if isinstance(zuordnung, dict)
                    and isinstance(zuordnung.get("lemma"), str)
                    and isinstance(zuordnung.get("guideWord"), str)
                )
                ausgewaehlte_lemmata.append(
                    (eintrag["_id"], tuple(dict.fromkeys(oracc_lemmata)))
                )
                if not oracc_lemmata:
                    print("Für dieses EBL-Lemma ist kein Oracc-Lemma zugeordnet.")
                break
            print("Bitte gib eine Nummer aus der Liste ein.")

        while True:
            weiter = input("Ein weiteres Wort suchen? (j/n): ").strip().casefold()
            if weiter in {"j", "ja"}:
                break
            if weiter in {"n", "nein"}:
                if len(ausgewaehlte_lemmata) == 1:
                    return ausgewaehlte_lemmata[0]
                return ausgewaehlte_lemmata
            print("Bitte antworte mit ja oder nein.")


def _belegangabe(datensatz: str, eintrag: dict) -> str:
    if datensatz == "ebl_korpus_manuskripte":
        teile = (
            eintrag.get("periode", ""),
            eintrag.get("manuskript", ""),
            eintrag.get("manuskript_zeile", eintrag.get("zeile", "")),
        )
    else:
        teile = (eintrag.get("text", ""), eintrag.get("zeile", ""))
    return ", ".join(str(teil) for teil in teile if teil not in (None, ""))


def _kwic_zeilen(
    datensatz: str, eintrag: dict, keyword_indizes: list[int]
) -> list[KWICTreffer]:
    woerter = eintrag.get("woerter", [])
    beleg = _belegangabe(datensatz, eintrag)
    treffer = []
    for index in keyword_indizes:
        treffer.append(
            (
                beleg,
                " ".join(wort.get("wert", "") for wort in woerter[:index]),
                woerter[index].get("wert", ""),
                " ".join(wort.get("wert", "") for wort in woerter[index + 1:]),
            )
        )
    return treffer


def suche_belege(
    suchbegriffe: LemmaAuswahl | list[LemmaAuswahl],
) -> list[KWICTreffer]:
    """Sucht AND-Belege in EBL und Oracc; KWIC-Keyword ist das erste Lemma."""

    lemmata = _normalisiere_suchbegriffe(suchbegriffe)
    keyword_ebl = lemmata[0][0]
    ergebnisse: list[KWICTreffer] = []

    ebl_dateien = (
        ("ebl_korpus", DATENORDNER / "ebl_korpus.jsonl.gz"),
        (
            "ebl_korpus_manuskripte",
            DATENORDNER / "ebl_korpus_manuskripte.jsonl.gz",
        ),
    )
    for datensatz, dateipfad in ebl_dateien:
        for eintrag in _lese_jsonl_gz(dateipfad):
            if not all(
                _ebl_lemma_praesent(eintrag, ebl_lemma)
                for ebl_lemma, _ in lemmata
            ):
                continue
            keyword_indizes = [
                index
                for index, wort in enumerate(eintrag.get("woerter", []))
                if keyword_ebl in wort.get("lemma", [])
            ]
            ergebnisse.extend(
                _kwic_zeilen(datensatz, eintrag, keyword_indizes)
            )

    oracc_suchmengen = [
        {
            schluessel
            for oracc_lemma in oracc_lemmata
            if (schluessel := _oracc_schluessel(oracc_lemma)) is not None
        }
        for _, oracc_lemmata in lemmata
    ]
    keyword_oracc_schluessel = oracc_suchmengen[0]
    if all(oracc_suchmengen):
        for eintrag in _lese_jsonl_gz(DATENORDNER / "oracc.jsonl.gz"):
            schluessel_im_eintrag = _oracc_schluessel_im_eintrag(eintrag)
            if not all(
                schluessel_im_eintrag.intersection(suchmenge)
                for suchmenge in oracc_suchmengen
            ):
                continue

            keyword_indizes = [
                index
                for index, wort in enumerate(eintrag.get("woerter", []))
                if (
                    isinstance(wort.get("oracc"), str)
                    and _oracc_schluessel(wort["oracc"])
                    in keyword_oracc_schluessel
                )
            ]
            ergebnisse.extend(
                _kwic_zeilen("oracc", eintrag, keyword_indizes)
            )

    return ergebnisse


def _kontextbreite_eingabe() -> int | None:
    while True:
        eingabe = input(
            "Kontextbreite in Wörtern je Seite (leer = ganze Zeile): "
        ).strip()
        if not eingabe:
            return None
        try:
            breite = int(eingabe)
        except ValueError:
            print("Bitte gib eine nichtnegative ganze Zahl ein.")
            continue
        if breite >= 0:
            return breite
        print("Die Kontextbreite darf nicht negativ sein.")


def keyword_in_context_ausgabe(
    belege: list[KWICTreffer],
    kontextwoerter: int | None = None,
) -> list[KWICTreffer]:
    """Zeigt Belege als KWIC und gibt die mit Kontextbreite formatierten Zeilen zurück."""

    if kontextwoerter is None:
        kontextwoerter = _kontextbreite_eingabe()
    if kontextwoerter is not None and (
        not isinstance(kontextwoerter, int) or isinstance(kontextwoerter, bool)
    ):
        raise TypeError("kontextwoerter muss None oder eine ganze Zahl sein.")
    if kontextwoerter is not None and kontextwoerter < 0:
        raise ValueError("kontextwoerter darf nicht negativ sein.")

    formatierte_belege = []
    for beleg, links, keyword, rechts in belege:
        links_woerter = links.split()
        rechts_woerter = rechts.split()
        if kontextwoerter is not None:
            links_woerter = links_woerter[-kontextwoerter:] if kontextwoerter else []
            rechts_woerter = rechts_woerter[:kontextwoerter]
        formatierte_belege.append(
            (beleg, " ".join(links_woerter), keyword, " ".join(rechts_woerter))
        )

    keyword_breite = max(
        (len(keyword) for _, _, keyword, _ in formatierte_belege), default=1
    )
    linksbreite = max(
        (len(links) for _, links, _, _ in formatierte_belege), default=0
    )
    print("KWIC-Belege")
    if not formatierte_belege:
        print("Keine Belege gefunden.")
        return formatierte_belege
    for beleg, links, keyword, rechts in formatierte_belege:
        print(f"  {beleg}")
        print(f"\t{links:>{linksbreite}} {keyword:<{keyword_breite}} {rechts}")
    return formatierte_belege


def exportiere_csv(
    belege: list[KWICTreffer], dateipfad: str | Path, ueberschreiben: bool = False
) -> Path:
    """Exportiert formatierte KWIC-Belege in eine CSV-Datei."""

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
        schreiber.writerow(("Beleg", "Wörter vor Keyword", "Keyword", "Wörter nach Keyword"))
        schreiber.writerows(belege)
    return ziel


def suche_und_zeige_kwic() -> list[KWICTreffer]:
    """Führt Lemma-Auswahl, Suche, Anzeige und optionalen CSV-Export aus."""

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


if __name__ == "__main__":
    suche_und_zeige_kwic()