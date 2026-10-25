import requests

antwort = requests.get("https://api.crossref.org/works/10.1093/llc/fqs033")
daten = antwort.json()                  # JSON → Python-Wörterbuch

print(daten["message"]["title"][0])     # Titel des Aufsatzes
for autor in daten["message"]["author"]:
    print(autor["family"])              # Nachnamen der Autoren