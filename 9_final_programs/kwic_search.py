from kwic_data import (
    DATENORDNER,
    KWICTreffer,
    LemmaAuswahl,
    _ebl_lemma_praesent,
    _kwic_zeilen,
    _lese_jsonl_gz,
    _normalisiere_suchbegriffe,
    _oracc_schluessel,
    _oracc_schluessel_im_eintrag,
)


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
            ergebnisse.extend(_kwic_zeilen(datensatz, eintrag, keyword_indizes))

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
            ergebnisse.extend(_kwic_zeilen("oracc", eintrag, keyword_indizes))
    return ergebnisse
