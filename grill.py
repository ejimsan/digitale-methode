
with open("_intro\\bm35407.txt", "r", encoding="utf-8") as f:
    text = f.read()

wort = "ma-ag-ri-tu₄"

def anzahl_zeichen(wort):
    return len(wort.split("-"))

print(anzahl_zeichen(wort))
