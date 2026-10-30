from kwic_data import KWICTreffer


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
    """Zeigt KWIC-Belege und gibt die mit Kontextbreite formatierten Zeilen zurück."""
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
