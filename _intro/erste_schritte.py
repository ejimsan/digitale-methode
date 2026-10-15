# erste_schritte.py — Demonstration für die Sitzung am 16.10.2026
# Digitale Methoden in der Assyriologie (LMU München, WS 2026/27)
#
# Ausführen in VS Code: Datei öffnen, oben rechts auf ▷ klicken
# (oder im Terminal:  python erste_schritte.py)

import re          # re = "regular expressions", reguläre Ausdrücke
from collections import Counter

# ------------------------------------------------------------------
# 1. Variablen: ein Name für einen Wert
# ------------------------------------------------------------------
# Marduk-apla-iddina II., RIMB 2 B.6.21.1 Z. 34,
# in eBL-ATF (ohne den abgebrochenen Zeilenanfang).
# "#" = beschädigtes Zeichen, [ ] = ergänzt, { } = Determinativ.
zeile = ("LUGAL#.LUGAL#-MEŠ na-ki-ri-šu₂ nu-huš# kib-rat ar₂#-ba-ʾi-i "
         "[hi]-ṣib KUR-i u₃ tam-ti₃ GUN#-su#-nu DUGUD#-ta "
         "liš-du-du# a-na# qe₂#-reb šu-an-na{ki}")

print("Die Zeile:", zeile)
print("Sie hat", len(zeile), "Zeichen (Buchstaben, Leerzeichen usw.).")

# ------------------------------------------------------------------
# 2. Listen: die Zeile in Wörter zerlegen
# ------------------------------------------------------------------
woerter = zeile.split()            # trennt an den Leerzeichen
print("\nAnzahl der Wörter:", len(woerter))
print("Erstes Wort:", woerter[0])  # Python zählt ab 0!
print("Letztes Wort:", woerter[-1])

# ------------------------------------------------------------------
# 3. Schleifen und Bedingungen: welche Wörter sind beschädigt?
# ------------------------------------------------------------------
print("\nBeschädigte oder ergänzte Wörter:")
for wort in woerter:
    if "#" in wort or "[" in wort:
        print("  ", wort)

# ------------------------------------------------------------------
# 4. Reguläre Ausdrücke: Muster statt fester Zeichenfolgen
# ------------------------------------------------------------------
# Ein "Zeichen" ist hier alles zwischen Bindestrichen, Punkten oder Leerzeichen.
zeichen = re.split(r"[-.\s]+", zeile)
beschaedigt = [z for z in zeichen if z.endswith("#")]
print("\nZeichen insgesamt:", len(zeichen))
print("davon beschädigt (#):", len(beschaedigt), beschaedigt)

ergaenzt = re.findall(r"\[([^\]]*)\]", zeile)   # alles zwischen [ und ]
print("Ergänzt ([ ]):", ergaenzt)

determinative = re.findall(r"\{([^}]*)\}", zeile)  # alles zwischen { und }
print("Determinative ({ }):", determinative)

# Eine "saubere" Lesefassung: Schadensmarken entfernen
sauber = re.sub(r"[#\[\]]", "", zeile)
print("\nOhne Schadensmarken:", sauber)

# ------------------------------------------------------------------
# 5. Wörterbücher (dict): zählen
# ------------------------------------------------------------------
haeufigkeit = Counter(re.split(r"[-.\s]+", sauber))
print("\nHäufigste Zeichen dieser Zeile:", haeufigkeit.most_common(3))

# ------------------------------------------------------------------
# 6. Der Kern des Projekts in drei Zeilen: gemeinsame Lemmata
# ------------------------------------------------------------------
# Lemmata (Wörterbuchformen) zweier Stellen, vereinfacht:
#   Erra I 4: Išum, „dessen Hände geeignet sind“, die Waffen zu tragen
#   Assurbanipal 197 Rs. 24: {d}i-šum ša₂ ŠU.II-šu₂ as-ma
erra = {"Išum", "qātu", "asāmu"}
assurbanipal = {"Nergal", "qarrādu", "ilu", "Išum", "ša", "qātu", "asāmu"}

gemeinsam = sorted(erra & assurbanipal)   # & = Schnittmenge, sorted = geordnet
print("\nGemeinsame Lemmata:", gemeinsam)
# Frage für Sitzung 2: Wie selten ist diese Kombination im ganzen Korpus?
# Und: Stehen die Wörter in eBL und Oracc unter denselben Lemmata?
# (Nicht immer: Oracc führt as-ma hier unter wasmu, eBL in Erra I 4 unter asāmu.)
