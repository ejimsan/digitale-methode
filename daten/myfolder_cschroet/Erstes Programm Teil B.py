import re          # re = "regular expressions", reguläre Ausdrücke
from collections import Counter

liste = []
listesilben = []
listebeschädigt = []

for zeile in open("daten/myfolder_cschroet/bm35407.txt", encoding="utf-8"):
    print(zeile.strip()) #druckt jedes Zeile über die Schleife aus
    nummer, umschrift = zeile.strip().split("\t") #trennt die Zeilenummer vorne vom Text über Tab
    #print(f"Nummer: {nummer}, Umschrift: {umschrift}")
    woerter = umschrift.split()            # trennt Text an den Leerzeichen
    print("\nAnzahl der Wörter:", len(woerter))     #print mit \n macht eine Leerzeile davor

    print("\nBeschädigte oder ergänzte Wörter:")
    for wort in woerter:                    #Schleife in der Schleife, jetzt innerhalb vom Wort suchen
        if "#" in wort or "[" in wort:
            print("  ", wort)               #das beschädigte Wort mit Leerzeichen vorne ausgeben
            listebeschädigt.append(wort)

        sauber = re.split(r"[.-]", re.sub(r"[#\[\]]", "", wort))   #re.split kann im Gegensatz zum einfachen split mehrere Trennzeichen haben, hier Bindestrich und Punkt. re.sub entfernt davor die Schadensmarken in wort 
        listesilben.extend(sauber)    #split hat die Liste 'sauber' erzeugt, die wird jetzt in die Listesilben akkumuliert mit extend

    liste.extend(re.findall(r"[A-Z]+", umschrift)) #immer noch in der Schleife pro Zeile, sucht nach allen Logogrammen, + addiert die Zeichen
      

print("\nOhne Schadensmarken:", listesilben)
print("\nLogogramme:", sorted(set(liste))) #Logogramme ohne Doppelte und nach Alphabet sortiert 
print("alle bschädigten Wörter:", sorted(set(listebeschädigt))) #beschädigte Wörter im Gesamttext

haeufigkeit = Counter(listesilben) #die Silben sind schon oben getrennt worden
print("\nHäufigste Zeichen des Textes:", haeufigkeit.most_common(3))

with open("daten/myfolder_cschroet/bm35407_Teil B.txt", "w", encoding="utf-8") as f:
    f.write("\nHäufigste Zeichen des Textes: " + str(haeufigkeit.most_common(3))) #Ausgabe der Häufigkeit in Datei
