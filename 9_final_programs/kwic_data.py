from __future__ import annotations

import gzip
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Tuple, Union


ORDNER = Path(__file__).resolve().parent
DATENORDNER = ORDNER.parent / "daten"
CSV_ORDNER = ORDNER / "csv_belege"

OraccLemma = Union[str, Tuple[str, ...]]
LemmaAuswahl = Tuple[str, OraccLemma]
KWICTreffer = Tuple[str, str, str, str]


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
        raise TypeError("Erwartet wird ein Lemma-Tuple oder eine Liste solcher Tupel.")
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
        normalisiert.append(
            (auswahl[0].strip(), _oracc_lemma_liste(auswahl[1]))
        )
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
    return [
        (
            beleg,
            " ".join(wort.get("wert", "") for wort in woerter[:index]),
            woerter[index].get("wert", ""),
            " ".join(wort.get("wert", "") for wort in woerter[index + 1:]),
        )
        for index in keyword_indizes
    ]
