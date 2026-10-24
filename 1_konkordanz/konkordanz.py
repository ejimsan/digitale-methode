import gzip, json
from collections import defaultdict

def erstelle_woerterbuch():
    """Erstellt ein Dictionary mit den Lemmata als Keys und den Formen als Values"""

    woerterbuch = defaultdict(list)

    with gzip.open("daten/ebl_korpus.jsonl.gz", "rt", encoding="utf-8") as file:
        for zeile in file:
            eintrag = json.loads(zeile)
            for w in eintrag["woerter"]:
                if len(w["lemma"]) > 0:
                    woerterbuch[w["lemma"][0]].append(w["wert"])
    return woerterbuch

def erstelle_lemmata_liste():
    print(erstelle_woerterbuch().keys())

def suche_belege(wort):
    
    belege = defaultdict(list)
    
    with gzip.open("daten/ebl_korpus.jsonl.gz", "rt", encoding="utf-8") as file:
        
        for zeile in file:
            eintrag = json.loads(zeile)
            for w in eintrag["woerter"]:
                if len(w["lemma"]) > 0 and w["lemma"][0] == wort:
                    belege[eintrag["text"]].append(eintrag["zeile"])

    return belege

def erstelle_belegliste(wort):
    belege = suche_belege(wort)

    print(f"Suche nach Belegen für {wort}:\n---------------------------------")
    for beleg in belege.keys():
        print(f"{beleg}\n\t{belege[beleg]}")



erstelle_belegliste("eṣēru I")
