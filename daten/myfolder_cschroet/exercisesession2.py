import re          # re = "regular expressions", reguläre Ausdrücke
from collections import Counter
wort = "mu-al-lim-da-at"
output = wort.split("-")
print(output)
anzahl_silben = len(output)
print ("Anzahl Silben 1: " + str(anzahl_silben))
def silben_zaehlen(wort):
    output = wort.split("-")
    return len((output))  
print("Anzahl Silben 2: " + str(silben_zaehlen(wort)))