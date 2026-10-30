
with open("_intro\\bm35407.txt", mode="r", encoding="utf-8", errors="replace") as f:
    text = [i.split()[2:] for i in f.readlines()]

def anzahl_zeichen(wort):
    return len(wort.split("-"))

for line in text:
    for wort in line[2:]:
        print(f"Die Länge des Wortes {wort} ist {anzahl_zeichen(wort)}")