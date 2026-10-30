import gzip

woerterbuch = "daten\\ebl_woerterbuch.jsonl.gz"
ebl_manuskripte = "daten\\ebl_korpus_manuskripte.jsonl.gz"
ebl_texte = "daten\\ebl_korpus.jsonl.gz"
oracc = "daten\\oracc.jsonl.gz"
daten = [woerterbuch, ebl_manuskripte, ebl_texte, oracc]

for datei in daten:
    with gzip.open(datei, "rt", encoding="utf-8") as f:
        daten = f.readlines()
        print(daten[200],"\n\n")