# Handout 1: Erste Schritte
*Digitale Methoden in der Assyriologie, 16.10.2026*

Enrique Jiménez  
enrique.jimenez@lmu.de  

## 1. Worum es geht

Das eBL enthält rund 370.000 edierte Zeilen, die Oracc-Projekte viele weitere. Niemand kann sie alle im Kopf haben, aber ein Programm kann sie in Sekunden durchsuchen und zählen. Die Arbeitsteilung in diesem Kurs ist deshalb einfach: **Der Computer zählt, die Philologin und der Philologe urteilen.** Ein Programm findet, dass zwei Zeilen dieselben seltenen Wörter enthalten. Ob es sich um ein Zitat, eine Formel oder einen Zufall handelt, entscheiden wir.

Programmieren heißt dabei vor allem: eine Aufgabe so genau beschreiben, dass eine Maschine sie ausführen kann. Diese Beschreibung schreiben Sie in der Sprache **Python**, einer der am weitesten verbreiteten Programmiersprachen, auch in den Geisteswissenschaften. Ein **KI-Assistent** hilft Ihnen beim Schreiben, aber verstehen müssen Sie das Ergebnis selbst.

## 2. Einrichtung

1. **Python** installieren: [python.org/downloads](https://www.python.org/downloads/). Unter Windows im ersten Fenster des Installationsprogramms unbedingt das Häkchen bei „Add python.exe to PATH“ setzen.
2. **Visual Studio Code** (VS Code) installieren: [code.visualstudio.com](https://code.visualstudio.com/). VS Code ist der Editor, in dem Sie Programme schreiben, ausführen und mit dem KI-Assistenten besprechen.
3. In VS Code die Erweiterung **Python** (Herausgeber: Microsoft) installieren: Seitenleiste → Erweiterungen (Strg+Umschalt+X, auf dem Mac Cmd+Umschalt+X) → „Python“ suchen → Installieren.
4. Prüfen, ob Python gefunden wird: In VS Code Terminal → Neues Terminal, dann `python --version` eingeben (auf dem Mac: `python3 --version`). Es sollte eine Versionsnummer erscheinen, z. B. „Python 3.13“.
5. **GitHub Copilot** einrichten: GitHub-Konto mit LMU-Adresse anlegen, über [GitHub Education](https://education.github.com/) den Studierendenstatus bestätigen lassen (dauert einige Tage), dann in VS Code über das Kontosymbol unten links mit GitHub anmelden. Den Chat öffnet das Sprechblasen-Symbol; falls es fehlt, die Erweiterung „GitHub Copilot Chat“ installieren. Bis zur Bestätigung funktioniert die kostenlose Stufe „Copilot Free“ mit begrenztem Kontingent.
6. **Datenschutz:** In den Copilot-Einstellungen Ihres GitHub-Kontos die Verwendung Ihrer Eingaben für das Training der Modelle abschalten.
7. Einen Ordner „seminar“ anlegen, in VS Code öffnen (Datei → Ordner öffnen), die Datei `erste_schritte.py` aus dem Ordner `_intro` des Kurs-Repositoriums hineinkopieren, öffnen und mit dem Dreieck ▷ oben rechts ausführen.

## 3. Welcher KI-Assistent?

Alle verbreiteten Assistenten können Code schreiben, erklären und Dateien bearbeiten. Für den Kurs ist entscheidend, dass alle dasselbe Werkzeug kostenlos benutzen können (Stand: Oktober 2026; die Angebote ändern sich schnell):

| Werkzeug | Kosten | Bemerkung |
|---|---|---|
| **GitHub Copilot** | kostenlos für Studierende (über GitHub Education) | In VS Code eingebaut; kann Dateien bearbeiten und Befehle ausführen. **Kurswerkzeug.** |
| Claude Code (Anthropic) | ab ca. 17–20 US$ im Monat (Claude Pro) | Erweiterung für VS Code; zeigt jede Änderung vor dem Übernehmen. Sehr gut, aber kostenpflichtig. |
| Codex (OpenAI) | im Abo ChatGPT Plus (ca. 20 US$ im Monat) | Erweiterung für VS Code. Kostenpflichtig. |
| Google | — | Gemini Code Assist für Privatpersonen wurde im Juni 2026 eingestellt; der Nachfolger „Antigravity“ ist ein eigener Editor. |

Wichtiger als die Wahl des Werkzeugs ist der Umgang damit (siehe Abschnitt 8).

## 4. Regular Expressions

Ein regulärer Ausdruck (*regular expression*, kurz *regex*) beschreibt ein Muster statt einer festen Zeichenfolge: nicht „finde *šu₂*“, sondern „finde jedes Zeichen mit einer Indexziffer“. Damit lassen sich ATF-Zeilen zerlegen, Schadensmarken entfernen oder Determinative finden.

| Muster | bedeutet | Beispiel |
|---|---|---|
| `.` | ein beliebiges Zeichen | `d.r` findet *dar*, *dur*, *dir* … |
| `\w` | Buchstabe, Ziffer oder _, auch š, ḫ und ₂ | `\w+` findet ganze Wörter |
| `\d` | eine Ziffer 0–9 | Achtung: findet die Indexziffer ₂ nicht! |
| `\s` | Leerzeichen, Tabulator |  |
| `+`  `*`  `?` | ein- oder mehrmals · null- oder mehrmals · optional | `ša₂?` findet *ša* und *ša₂* |
| `[…]`  `[^…]` | eines dieser Zeichen · alles außer diesen | `[^\s.\-]+#` findet beschädigte Zeichen |
| `\` | Sonderzeichen wörtlich nehmen | `\[` sucht eine eckige Klammer |
| `( )` | Gruppe: dieser Teil soll herausgeholt werden | `\{([^}]*)\}` holt Determinative |
| `\|` | oder | `šarru\|šarrū` |
| `^`  `$` | Anfang · Ende der Zeichenkette | `^#lem` findet Lemmatisierungszeilen |

Muster lassen sich bequem auf [regex101.com](https://regex101.com/) ausprobieren (links „Python“ als *flavor* wählen). Eine gute Einführung ist Knox 2013 im *Programming Historian*.

## 5. Python in elf Begriffen

| Begriff | Beispiel | Erklärung |
|---|---|---|
| **Variable** | `gott = "Erra"` | Ein Name für einen Wert. Das Gleichheitszeichen bedeutet „wird zu“, nicht „ist gleich“. |
| **String** (Zeichenkette) | `"ša naqba īmuru"` | Text, immer in Anführungszeichen. Sonderzeichen wie š, ḫ, ₂ sind kein Problem. |
| **Number** (`int`, `float`) | `zeilen = 37` | Ganze Zahlen und Dezimalzahlen (mit Punkt: `0.5`). |
| **List** (Liste) | `["Erra", "Išum", "Marduk"]` | Geordnete Folge. Python zählt ab 0: `liste[0]` ist „Erra“, `liste[-1]` das letzte Element. |
| **Set** (Menge) | `{"qātu", "asāmu"}` | Ungeordnet, ohne Doppelte. `a & b` ergibt die gemeinsamen Elemente. |
| **Dictionary** (`dict`, Wörterbuch) | `{"Erra": 5, "Enūma eliš": 7}` | Schlüssel → Wert (hier: Anzahl der Tafeln). Ideal zum Nachschlagen und Zählen. |
| **Loop** (Schleife) | `for wort in woerter:` | Wiederholt die eingerückten Zeilen darunter für jedes Element. Die Einrückung gehört zur Syntax! |
| **Condition** (Bedingung) | `if "#" in wort:` | Führt die eingerückten Zeilen nur aus, wenn die Bedingung zutrifft. |
| **Function** (Funktion) | `len(woerter)`, `zeile.split()` | Ein benannter Arbeitsschritt. Eigene Funktionen definiert man mit `def`. |
| **Module** (Modul, Bibliothek) | `import re` | Fertige Werkzeuge anderer, z. B. `re` (reguläre Ausdrücke), `json`, `requests`. |
| **Error** (Fehlermeldung) | `NameError: name 'wort' is not defined` | Kein Grund zur Sorge. Die letzte Zeile nennt die Art des Fehlers, die Zeilen darüber den Ort. Ganz in den Chat kopieren. |

## 6. Was ist eine API?

Eine API (*application programming interface*) ist eine Tür, durch die ein Programm Daten von einem anderen Rechner holt. Statt eine Webseite für Menschen zu öffnen, ruft das Programm eine Adresse auf und erhält Daten in einem maschinenlesbaren Format zurück, meist **JSON**. JSON besteht aus genau den Bausteinen, die Sie aus Python kennen: Wörterbüchern `{ }` und Listen `[ ]`, beliebig ineinander geschachtelt.

Ein Beispiel mit der öffentlichen API von Crossref, die bibliographische Daten zu jeder DOI liefert. Vorher einmal im Terminal die Bibliothek *requests* installieren: `python -m pip install requests`.

```
import requests

antwort = requests.get("https://api.crossref.org/works/10.1093/llc/fqs033")
daten = antwort.json()                  # JSON → Python-Wörterbuch

print(daten["message"]["title"][0])     # Titel des Aufsatzes
for autor in daten["message"]["author"]:
    print(autor["family"])              # Nachnamen der Autoren
```

Das Ergebnis sind Titel und Autoren des Tesserae-Aufsatzes von 2013. Nach demselben Prinzip stellen eBL und Oracc ihre Texte und Lemmatisierungen bereit; damit beschäftigt sich die zweite Sitzung.

## 7. Die Demonstration: eine eBL-Zeile zerlegen

Das Skript `erste_schritte.py` (Ordner `_intro`) nimmt eine Zeile aus einer Inschrift Marduk-apla-iddinas II. (RIMB 2 B.6.21.1 Z. 34), so wie sie im eBL-ATF steht, und zerlegt sie Schritt für Schritt. Der Kern:

```
zeile = "LUGAL#.LUGAL#-MEŠ na-ki-ri-šu₂ nu-huš# kib-rat ar₂#-ba-ʾi-i [hi]-ṣib ..."

zeichen     = re.split(r"[-.\s]+", zeile)          # in Zeichen zerlegen
beschaedigt = [z for z in zeichen if z.endswith("#")]
ergaenzt    = re.findall(r"\[([^\]]*)\]", zeile)    # alles zwischen [ und ]
sauber      = re.sub(r"[#\[\]]", "", zeile)          # Schadensmarken entfernen
```

Am Ende steht der Kern des ganzen Projekts in drei Zeilen. Erra I 4 nennt Išum einen, „dessen Hände geeignet sind“, die Waffen zu tragen; dasselbe Epitheton steht in einer Inschrift Assurbanipals (Nr. 197 Rs. 24: *{d}i-šum ša₂ ŠU.II-šu₂ as-ma*):

```
erra = {"Išum", "qātu", "asāmu"}                     # Erra I 4 (Auszug)
assurbanipal = {"Nergal", "qarrādu", "ilu", "Išum",
                "ša", "qātu", "asāmu"}             # Assurbanipal 197 Rs. 24
print(sorted(erra & assurbanipal))   # → ['Išum', 'asāmu', 'qātu']
```

Zwei Fragen nehmen wir in die nächste Sitzung mit. Erstens: Wie selten ist diese Verbindung im ganzen Korpus, und wie misst man das? Zweitens: Stehen die Wörter in eBL und Oracc wirklich unter denselben Lemmata? Wenn nicht, sieht das Programm die Parallele nicht, und das wäre kein Fehler der Statistik, sondern der Lemmatisierung.

## 8. Mit dem KI-Assistenten arbeiten

- **Klein anfangen.** Nicht „Schreibe ein Programm, das Zitate findet“, sondern „Lies die Datei erra.json und zähle, wie oft jedes Lemma vorkommt“.
- **Erklären lassen.** Zum Beispiel: „Erkläre jede Zeile auf Deutsch. Verwende nur die Standardbibliothek von Python.“ Code, den Sie nicht erklären können, gehört nicht in Ihre Abgabe.
- **An einem bekannten Fall prüfen.** Wenn das Programm Erra I 4 und Assurbanipal 197 Rs. 24 nicht zusammenbringt, stimmt etwas nicht, ganz gleich, wie überzeugend der Code aussieht.
- **Fehlermeldungen vollständig einfügen**, nicht nacherzählen.
- **Änderungen lesen, bevor Sie sie übernehmen**, und keine Befehle ausführen lassen, deren Wirkung Sie nicht kennen (vor allem nichts, was Dateien löscht).
- **Protokoll führen.** Eine Datei `protokoll.md`, in der Sie wichtige Anfragen und Entscheidungen notieren. Sie brauchen sie für den Bericht.

## 9. Fachliteratur außerhalb der Altorientalistik finden

Ihr Modul berührt fast immer ein Gebiet, in dem andere schon gearbeitet haben: Computerlinguistik, Statistik, digitale Klassische Philologie, Bibelwissenschaft. Diese Literatur ist fast ausschließlich englisch. Nützliche Suchbegriffe sind etwa *text reuse detection*, *intertextuality detection*, *allusion detection*, *lemmatization of low-resource languages*, *collocation statistics*, *formulaic language*, *false discovery rate*.

| Wo? | Wofür? |
|---|---|
| [Google Scholar](https://scholar.google.com/) | Breiteste Suche. Phrasen in Anführungszeichen; „Zitiert von“ führt zu neuerer Literatur; „Ähnliche Artikel“. |
| [Semantic Scholar](https://www.semanticscholar.org/) | Gute Empfehlungen und Kurzfassungen; zeigt, welche Zitate einflussreich sind. |
| [ACL Anthology](https://aclanthology.org/) | Fast die gesamte Computerlinguistik, frei zugänglich. |
| [DBLP](https://dblp.org/) | Bibliographie der Informatik; gut, um alle Arbeiten einer Person zu finden. |
| [arXiv](https://arxiv.org/) | Vorabdrucke (*preprints*): aktuell, aber noch nicht begutachtet. |
| Zeitschriften | *Digital Scholarship in the Humanities*, *Digital Humanities Quarterly*, *Journal of Open Humanities Data*, Tagungsbände *Computational Humanities Research*. |
| Altorientalistik | KeiBi online (Keilschriftbibliographie); Bibliographien von eBL und Oracc. |
| UB der LMU | Volltexte lizenzierter Zeitschriften über die LMU-Kennung (bei Verlagen „Zugang über Institution“ wählen). |

**Strategie „Schneeball“:** Von einem guten Aufsatz aus rückwärts (seine Bibliographie) und vorwärts („Zitiert von“) gehen. Vor dem ganzen Aufsatz zuerst Zusammenfassung, Abbildungen und Schluss lesen. Fundstellen mit [Zotero](https://www.zotero.org/) sammeln (die Browser-Erweiterung übernimmt die Angaben mit einem Klick).

**Warnung:** KI-Chatbots erfinden Literatur, mit plausiblen Autoren, Titeln und Seitenzahlen. Jeden Titel, den ein Chatbot nennt, über die DOI oder im Katalog prüfen, bevor Sie ihn zitieren.

## 10. Bis zum 30.10.2026

1. Einrichtung abschließen; `erste_schritte.py` ausführen und eine Sache ändern (z. B. eine andere Zeile aus dem eBL einsetzen).
2. Für Ihr Modul drei Titel finden, die nicht in der Bibliographie der Kursbeschreibung stehen, und im Katalog überprüfen.
3. Wer am 30.10. sein Modul vorstellt (Module 1 und 2): Literatur, Ansatz und einen ersten Programmentwurf mitbringen, dazu die Fragen, bei denen Sie Hilfe brauchen.
4. Lektüre: Leonard 2008 (*Identifying Inner-Biblical Allusions*), Jiménez 2017, 79–82 (*Literary Quotations*) und Coffee et al. 2013 (*The Tesserae Project*).
