from __future__ import annotations

from kwic_data import DATENORDNER, LemmaAuswahl, _lese_jsonl_gz


def _passende_eintraege(woerterbuch: list[dict], wort: str) -> list[dict]:
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
        if any(form.casefold() == wort for form in (*grundformen, *formen)):
            passende_eintraege.append(eintrag)
    return passende_eintraege


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
        passende_eintraege = _passende_eintraege(woerterbuch, wort)
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
                    text = bedeutung or "keine Bedeutung"
                    print(f"{nummer}. {eintrag['_id']} ({text})")
                continue
            try:
                nummer = int(auswahl)
            except ValueError:
                print("Bitte gib eine Nummer aus der Liste ein.")
                continue
            if not 1 <= nummer <= len(passende_eintraege):
                print("Bitte gib eine Nummer aus der Liste ein.")
                continue
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
