# Programm für Modul 4: Seltenheit

## Leitfrage
Seltene Wörter und seltene Verbindungen gewöhnlicher Wörter sind die wichtigsten Kriterien für eine Anspielung. Aber selten wo: im ganzen Korpus, in der Literatur, in einer Epoche? Ist ein Wort selten, oder nur selten überliefert? Und wann ist eine Verbindung seltener, als die Häufigkeit ihrer Teile erwarten lässt?
## Programm
Ein Programm, das die Häufigkeit jedes Lemmas zählt, daraus ein Seltenheitsgewicht berechnet (z. B. den negativen Logarithmus der relativen Häufigkeit) und die Häufigkeitsverteilung als Diagramm zeigt; dazu für Lemmapaare die Zahl der Zeilen, in denen beide vorkommen, und ein Vergleich der Gewichte in verschiedenen Teilkorpora. Vorführung: der Wortschatz eines Textes nach Seltenheit geordnet, etwa die Theodizee neben dem Erra-Epos.

## Prüffall
ina und ša gehören zu den häufigsten Lemmata und erhalten ein Gewicht nahe null. qātu steht in über 2.400 Zeilen der Momentaufnahme, qātu zusammen mit asāmu nur in Erra I 4.

## meine Prompts - 1. Teil: für Erra und Išum sowie die Theodizee die Lemmata einlesen, nach Häufigkeit sortieren, die relative Häufigkeit berechnen und als Graphen ausgeben (auch als Textdatei)
was ist eine python datei mit der extension md

lies die Daten aus daten/ebl_korpus_manuskripte.jsonl.gz ein und gib sie in ein programm seltenheit.py aus. Speichere die Daten unter dem Verzeichnis 4_seltenheit. Verändere die Quelldatei nicht. Gib die Daten in eine Datei Seltenheit.txt in das Verzeichnis 4_seltenheit aus.
erstelle eine Liste aus dem Text ## I.5 Erra and Išum und schreibe sie in die Ausgabedatei Seltenheit.txt
Lies ebenfalls die Theodizee ein und lass die Lemmapaare erstmal weg. Ordne für beide Texte die Lemmata nach Häufigkeit und gib in die Ausgabedatei Seltenheit.txt nur die 15% der seltenen Lemmas aus.
Erzeuge eine graphische Ausgabe für seltenheit.txt, für jeden Text separat und speichere die Ausgabe in einer neuen Datei.
Nimm jetzt wieder alle Lemmata und berechne als Seltenheitsgewicht den negativen Logarithmus der relativen Häufigkeit. Schreibe die Häufigkeitsverteilung als Diagramm in die bereits vorhandenen Ausgabedateien. Beschrifte die X und Y Achsen. 
Ordne den Wortschatz jeweils nach Seltenheit und beschrifte die graphische Ausgabe 
Das Programm ist relativ lang geworden. Optimiere den Programmcode, achte dabei auf Übersichtlichkeit. Teste alle Funktionen.

## prompts für ein zweites Programm, in dem man für einzelne Lemmata die relative und absolute Häufigkeit interaktiv abfragen kann
Wir schreiben jetzt ein neues Programm, Seltenheit_Anfrage.py. Dieses Programm nutzt die Ausgabedatei Seltenheit.txt, um Antworten auf Anfragen von Lemmata zu geben. Im ersten Schritt wird nach der Eingabe eines Lemmas gefragt, die Ausgabe erhält die Angabe der absoluten und relativen Häufigkeit des Lemmas je Eingabetext. Die Ausgabe erfolgt interaktiv im Terminal.
ina und ša sind sehr häufige Wörter und müssten in beiden Texten vorkommen. Warum werden sie nicht gefunden?
Antwort copilot: Das Programm suchte bisher nur nach einer exakten Übereinstimmung. In Seltenheit_Anfrage.py wird jetzt auch die Basisform ohne römische Homonymnummer erkannt.
Warum findet man erra nicht?
Antwort copilot:
Der Grund war die Groß-/Kleinschreibung:

In Seltenheit.txt steht das Lemma als Erra I.
Die Eingabe war erra.
Die Suche verglich bisher Groß-/Kleinschreibung exakt.
Die Suche in Seltenheit_Anfrage.py ist jetzt unabhängig von Groß-/Kleinschreibung.

## prompts für ein drittes Programm, das die Häufigkeit von Bigrammen innerhalb einer Zeile untersucht und pro Text ausgibt
Schreibe jetzt ein drittes Programm Seltenheit_Bigramme.py. Es soll ebenfalls interaktiv Lemmata und ihre Homonyme erkennen, es wird nach Lemma 1 und Lemma 2 gefragt, beide ergeben ein Bigramm (eine Nennung beider Lemmata innerhalb einer Zeile). Gib wieder getrennt nach Eingabetext die absolute und relative Häufigkeit aus.
Für das Programm Seltenheit_Bigramme erzeuge zusätzlich eine graphische Ausgabe in eine Datei Bigramme_output.svg, wenn die Eingabe mit ende abgeschlossen wurde.
Beschrifte die Ausgabe in der output-Datei.

## Beispiel für ein Ergebnis (Beendigung der Eingabe mit: ende): 
Lemma 1: qātu
Lemma 2: ša

Ergebnisse für Bigramm "qātu + ša":
- I.5 Erra and Išum: absolut 6 Zeilen, relativ 0.010017 (1.00%)
- II.1 The Babylonian Theodicy: absolut 0 Zeilen, relativ 0.000000 (0.00%)

# Qualitätskontrolle und Optimierungen
Berechnest du in allen drei Programmen den Seltenheitswert, d.h. negativen Logarithmus der relativen Häufigkeit? Dann schreibe bei der Ausgabe nicht nur "relativ" sondern "relative Seltenheit"

Anpassung: u.a.
gibt absolute Häufigkeit und relative Seltenheit aus
Beispiel: relative Seltenheit 1.770289 (-ln(102/599))
Beispiel für das Bigramm ina + ina:
I.5 Erra and Išum:
absolut 63 Zeilen, relative Seltenheit 2.252127 (-ln(63/599))

II.1 The Babylonian Theodicy:
absolut 33 Zeilen, relative Seltenheit 3.196816 (-ln(33/807))