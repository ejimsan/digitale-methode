# Notizen für Prompts in Github Copilot
## Übersicht
### Ziel

Ein Programm, das zu einem oder mehreren Lemmata alle Zeilen des lemmatisierten eBL-Korpus mit ihrem Kontext ausgibt (Konkordanz, *keyword in context*), dazu eine Übersicht über das Korpus: Texte, Gattungen, Anteil der lemmatisierten Zeilen. (1_konkordanz\README.md)

### Daten

Enthält Daten von Oracc und EBL, die via `daten\make_snapshot.py` ins Repository geladen werden:
- daten\ebl_korpus_manuskripte.jsonl.gz
- daten\ebl_korpus.jsonl.gz
- daten\oracc.jsonl.gz

### Wörterbuch

Enthält über `oraccWords` die Verknüpfung von EBL-Lemma zu Oracc-Lemma
daten\ebl_woerterbuch.jsonl.gz

### .gz-komprimierte .json-Dateien öffnen
```python
import gzip, json

with gzip.open("daten/ebl_korpus.jsonl.gz", "rt", encoding="utf-8") as f:
    for zeile in f:
```

## Prompts
### 1. Definiere Ziel und schreibe erste Funktionen

Ziel: Ein Programm, das zu einem oder mehreren Lemmata alle Zeilen des lemmatisierten eBL-Korpus mit ihrem Kontext ausgibt (Konkordanz, *keyword in context*), dazu eine Übersicht über das Korpus: Texte, Gattungen, Anteil der lemmatisierten Zeilen. (1_konkordanz\README.md)

Datei: Schreibe die Funktionen in konkordanz.py. Verändere ausschließlich konkordanz.py

Beginne mit einer Funktion, die die Belege in EBL findet
- Erstelle eine Funktion, die ein EBL-Lemma als str nimmt und alle Belege im EBL-Korpus als dictionary ausgibt 
    - daten\ebl_korpus_manuskripte.jsonl.gz
    - daten\ebl_korpus.jsonl.gz

Schlage weiteres Vorgehen vor

### 2. Funktionen zu mehreren Lemmata, Keyword in Context und der Darstellung

Schreibe die Funktionen in konkordanz.py. Verändere ausschließlich konkordanz.py

1. Erstelle Funktionen, die:
    1. Mehrere Lemmata in einer Suche unterstützen.
    2. Aus den Treffern eine Konkordanz mit dem Lemma im Kontext (*keyword in context*) erzeugen.

2. Gib Vorschläge für ein übersichtliches Interface für die Suche und die Darstellung:
    1. Basierend auf Python
    2. Optionen mit HTML und JavaScript

3. Schlage weiteres Vorgehen vor

### 3. Anpassen von suche_belege(), keyword in context-Funktion

Schreibe die Funktionen in konkordanz.py. Verändere ausschließlich konkordanz.py
Nutze vorhandene Funktionen

1. Anpassung an suche_belege()
    - Eine Suche mit mehreren Lemmata, bspw. suche_belege(["ina", "uznu I"]) findet nur Belege mit ina UND uznu I
    - Möglichkeit einer feinen und einer groben suche. Bsp.: Wenn feine_suche == True findet suche_belege("banû I") ausschließlich Belege für "banû I". Wenn feine_suche == False findet Belege mit banû I, banû II, banû III, etc.
    - Default ist feine_suche == True

2. Schreibe eine Funktion lemma_eingabe(), 
    - die nach einem akkadischen Wort fragt und eine Liste an Lemmata ausgibt, die mit diesem Wort verbunden werden kann
        - Nutze dafür daten\ebl_woerterbuch.jsonl.gz
    - Aus dieser Liste kann das gewünschte Lemma ausgewählt werden
    - Die Funktion fragt, ob die Suche ein weiteres Wort einschließen soll
        - Wenn ja, wird das Vorgehen wiederholt
    - Bei einer einzelnen Suche wird das gewünschte Lemma als ein str zurückgegeben
    - Bei mehreren Suchen werden die gewünschten Lemmata als list zurückgegeben

3. Schreibe eine Funktion keyword_in_context(), die die Belege nimmt und als Keyword in context im Terminal ausgibt
    - Format: Angaben zum Beleg: Zeile in Normalisierung im Keyword in context-Format
        - Angaben zum Beleg:
            - Für Belege aus daten\ebl_korpus_manuskripte.jsonl.gz: Period, Manuskript, Zeile
            - Für Belege aus daten\ebl_korpus.jsonl.gz: Komposition, Zeile

4. Schreibe eine Funktion, die die vorhandenen Funktionen miteinander Verknüpft
    - Beginnt mit einer Eingabe in lemma_eingabe()
    - Gibt die Belege über keyword_in_context() aus

5. Überprüfe den Code:
    - Tests mit verschiedenen Lemma
    - Verbessungsvorschläge
    - Weiteres Vorgehen

### 4. Anpassen der Ergebnisse

1. Probleme mit gegenwärtigem Arbeitsstand
    - Ausgabe ist unübersichtlich. Keyword muss in der Mitte der Zeile sein (vgl. https://en.wikipedia.org/wiki/Key_Word_in_Context) und die Keywords der verschiedenen Einträge sollen in der gleichen Spalte sein
    - <<>> kann nicht zur Markierung von KWIC genutzt werden, weil in Assyriologie bereits genutzt. Hervorhebung durch KWIC genügt
    - In der Ausgabe: Belege aus daten\ebl_korpus_manuskripte.jsonl.gz und daten\ebl_korpus.jsonl.gz sollten für die Übersichtlichkeit durch mehrere Absätze getrennt werden
        - Überschrift über Belege aus daten\ebl_korpus.jsonl.gz: Korpus-Belege
        - Überschrift über Belege aus daten\ebl_korpus_manuskripte.jsonl.gz: Library-Belege

2. Lösungen für diese Probleme: Lösungen finden und umsetzen

3. Vorschläge für die Übersichtlichere Gestaltung der Ausgabe

### 5. Anpassen der Ergebnisse

- Füge vor dem KWIC ebenfalls ein Tabulator ein
- Kontextbreite: als Standart die gesamte Zeile, Kontextbreite als Benutzereinstellung anbieten
- Belege optional nach Komposition oder Manuskript sortieren
- Exportfunktion für CSV ergänzen. Nach der Ausgabe die Möglichkeit bieten, das Ergebnis als CSV-Datei zu exportieren

### 6. Anpassen der Ergebnisse

- Belege optional nach Komposition oder Manuskript sortieren → mache diese Funktion rückgängig

