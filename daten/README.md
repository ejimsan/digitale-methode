# Daten: Momentaufnahme von eBL und Oracc

Stand: 15.10.2026. Alle Module arbeiten mit diesen Dateien, damit die Ergebnisse vergleichbar sind.

| Datei | Inhalt |
|---|---|
| `ebl_korpus.jsonl.gz` | rekonstruierter Text der Kapitel im Korpus des [eBL](https://www.ebl.lmu.de/) (z. B. Erra I) |
| `ebl_korpus_manuskripte.jsonl.gz` | dieselben Zeilen in den einzelnen Manuskripten, mit Beschädigungen (`#`) und Ergänzungen (`[ ]`) |
| `oracc.jsonl.gz` | Königsinschriften und Staatsarchive aus [Oracc](https://oracc.museum.upenn.edu/) (RINAP, RIAo, RIBo, SAAo, Suhu); jedes Wort mit seinen eBL-Lemmata |
| `ebl_woerterbuch.jsonl.gz` | das Wörterbuch des eBL, ein Eintrag pro Zeile |

## Aufbau

Jede Zeile der Textdateien ist ein JSON-Objekt und steht für eine Zeile Text:

```json
{"quelle": "eBL-Korpus-Manuskript", "text": "L 1.2 Standard Babylonian I", "zeile": "4",
 "manuskript": "K.1282", "manuskript_zeile": "4", "periode": "Neo-Assyrian",
 "atf": "{d}i-šum [as]-ma",
 "woerter": [{"wert": "{d}i-šum", "lemma": ["Išum I"], "zustand": "beschädigt"},
             {"wert": "[as]-ma", "lemma": ["asāmu I"], "zustand": "ergänzt"}]}
```

- `lemma`: die eBL-Lemmata des Wortes (meist eines; leer, wenn das Wort nicht lemmatisiert ist)
- `zustand` (nur eBL): `erhalten`, `beschädigt` oder `ergänzt`
- In `oracc.jsonl.gz` stehen außerdem `oracc` (Zitierform, *guide word* und Wortart, z. B. `qātu[hand]N`) und `zuordnung`: `eindeutig`, `mehrdeutig` (mehrere eBL-Lemmata kommen in Frage) oder `keine`.

In `ebl_woerterbuch.jsonl.gz` steht jede Zeile für einen Eintrag des Wörterbuchs, so wie er in der eBL-Datenbank gespeichert ist. Das Feld `_id` ist das Lemma in derselben Form wie in `lemma` der Textdateien (z. B. `qātu I`); dazu kommen u. a. `guideWord`, `pos` und `oraccWords`.

## Lesen in Python

```python
import gzip, json

with gzip.open("daten/ebl_korpus.jsonl.gz", "rt", encoding="utf-8") as f:
    for zeile in f:
        eintrag = json.loads(zeile)
        print(eintrag["text"], eintrag["zeile"], [w["lemma"] for w in eintrag["woerter"]])
        break        # nur die erste Zeile
```

## Quellen und Zitierung

Die Texte stammen aus dem Electronic Babylonian Library und aus den genannten Oracc-Projekten; deren Lizenzbedingungen gelten weiter. Bei jeder Verwendung, auch im gemeinsamen Aufsatz, sind eBL und die einzelnen Projekte und Editionen zu zitieren.

## Wie die Dateien entstanden sind

Mit `make_snapshot.py` in diesem Ordner: Es liest die Kapitel und das Wörterbuch aus der eBL-Datenbank, speichert das Wörterbuch unverändert, lädt die Oracc-Archive und ordnet die Oracc-Lemmata über das Feld `oraccWords` des eBL-Wörterbuchs den eBL-Lemmata zu. Die Zuordnung ist ein erster, automatischer Durchgang; sie zu prüfen und zu verbessern ist Aufgabe von Modul 2.
