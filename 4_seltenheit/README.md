# Modul 4: Was ist selten?

Vorstellung: 13.11.2026 · Gemeinsame Lektüre der Sitzung: [Bach 2024](../Kursbeschreibung.md#bach-2024); [Cobanoglu et al. 2024](../Kursbeschreibung.md#cobanoglu-2024)

## Leitfrage

Seltene Wörter und seltene Verbindungen gewöhnlicher Wörter sind die wichtigsten Kriterien für eine Anspielung. Aber selten wo: im ganzen Korpus, in der Literatur, in einer Epoche? Ist ein Wort selten, oder nur selten überliefert? Und wann ist eine Verbindung seltener, als die Häufigkeit ihrer Teile erwarten lässt?

## Programm und Vorführung

Ein Programm, das die Häufigkeit jedes Lemmas zählt, daraus ein Seltenheitsgewicht berechnet (z. B. den negativen Logarithmus der relativen Häufigkeit) und die Häufigkeitsverteilung als Diagramm zeigt; dazu für Lemmapaare die Zahl der Zeilen, in denen beide vorkommen, und ein Vergleich der Gewichte in verschiedenen Teilkorpora. Vorführung: der Wortschatz eines Textes nach Seltenheit geordnet, etwa die Theodizee neben dem Erra-Epos.

## Lektüre

- **Philologie:** [Leonard 2008](../Kursbeschreibung.md#leonard-2008); [Jiménez 2018](../Kursbeschreibung.md#jimenez-2018)
- **Methode:** [Piantadosi 2014](../Kursbeschreibung.md#piantadosi-2014); [Jurafsky/Martin 2026](../Kursbeschreibung.md#jurafsky-2026), Kap. 3

Vollständige Angaben in der [Kursbeschreibung](../Kursbeschreibung.md#bibliographie).

## Zur Diskussion

Wie behandelt man Eigennamen und Hapax legomena? Zählt man Lemmata oder Schreibungen? Wie groß ist der Einfluss des Überlieferungszufalls?

## Prüffall

*ina* und *ša* gehören zu den häufigsten Lemmata und erhalten ein Gewicht nahe null. *qātu* steht in über 2.400 Zeilen der Momentaufnahme, *qātu* zusammen mit *asāmu* nur in Erra I 4.

## Abgabe

Nach der Sitzung, überarbeitet nach den Rückmeldungen: der Programmcode als Python-Modul in diesem Ordner, eine Anleitung zum Ausführen in dieser Datei und eine kurze Notiz dazu, wofür KI-Werkzeuge verwendet wurden.

## Ausführen

Vom Projektverzeichnis aus erzeugt

```text
python 4_seltenheit/seltenheit.py
```

die Datei `4_seltenheit/Seltenheit.txt`. Das Programm liest
`daten/ebl_korpus_manuskripte.jsonl.gz` nur lesend ein. Die Ausgabe enthält
für `## I.5 Erra and Išum` und `## II.1 The Babylonian Theodicy` jeweils
davon alle Lemmata, nach Häufigkeit sortiert, mit der relativen Seltenheit
`-ln(relative Häufigkeit)`. Lemmapaare werden nicht ausgegeben. Zusätzlich
entstehen die beiden skalierbaren SVG-Grafiken `4_seltenheit/erra_isum.svg`
und `4_seltenheit/theodizee.svg`. Diese zeigen die Häufigkeitsverteilung mit
dem Seltenheitsgewicht auf der X-Achse und dem nach Seltenheit geordneten
Wortschatz auf der Y-Achse. Die seltensten Lemmata stehen oben.

Die Funktionen können mit

```text
python -m unittest discover -s 4_seltenheit -p "test_*.py" -v
```

getestet werden.

Für eine interaktive Lemma-Abfrage:

```text
python 4_seltenheit/Seltenheit_Anfrage.py
```

Das Programm liest `Seltenheit.txt` und gibt die absolute Häufigkeit sowie die
relative Seltenheit (`-ln(relative Häufigkeit)`) des eingegebenen Lemmas für
beide Texte aus. Mit `ende` wird die Abfrage beendet.

Für Bigramm-Abfragen:

```text
python 4_seltenheit/Seltenheit_Bigramme.py
```

Das Programm fragt zwei Lemmata ab und zählt Zeilen, in denen beide Lemmata
vorkommen. Es erkennt auch Eingaben ohne Homonymnummer, etwa `ina` für
`ina I`. Für die gemeinsame Zeilenzählung liest es das unveränderte
`daten/ebl_korpus_manuskripte.jsonl.gz`; die relativen Häufigkeiten beziehen
sich auf die Zeilenzahlen aus `Seltenheit.txt`. Nach `ende` wird die Grafik
des zuletzt abgefragten Bigramms als `4_seltenheit/Bigramme_output.svg`
gespeichert.
