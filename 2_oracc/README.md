# Modul 2: Zwei Korpora, zwei Lemmatisierungen: die Königsinschriften aus Oracc

Vorstellung: 13.11.2026 · Gemeinsame Lektüre der Sitzung: Bach 2024; Cobanoglu et al. 2024

## Leitfrage

Die Zitate des Erra-Epos stehen in Königsinschriften, die in Oracc ediert sind (RINAP, RIBo, SAAo); das Epos selbst steht im eBL. Wie zuverlässig lassen sich die beiden Korpora über die Zuordnung verbinden, die das eBL-Wörterbuch zu jedem Lemma bereithält (Oracc-Zitierform und *guide word*, abrufbar über die eBL-API)?

## Programm und Vorführung

Ein Programm, das eine Oracc-Inschrift lädt und ihre Lemmata (z. B. *šarru[king]*) über die eBL-API in eBL-Lemmata (z. B. *šarru I*) überführt, mit einer Statistik: Wie viele Wörter lassen sich eindeutig, mehrdeutig oder gar nicht zuordnen? Vorführung: Sargons Bericht über den achten Feldzug, Zeile für Zeile in eBL-Lemmata.

## Lektüre

- **Philologie:** Bach 2024; Bach 2020b
- **Methode:** [Oracc ATF Primer](https://oracc.museum.upenn.edu/doc/help/editinginatf/primer/); Sahala/Lindén 2023

Vollständige Angaben in der [Kursbeschreibung](../Kursbeschreibung.md#bibliographie).

## Zur Diskussion

Die Zuordnung ist zum Teil mehrdeutig (zu *šarru I* gehören auch Oracc-Einträge wie *abat šarri*): Wann schadet das der Suche? Wie behandelt man Eigennamen? Was, wenn eine Seite falsch lemmatisiert?

## Prüffall

Assurbanipal 197 Rs. 24: Werden *ŠU-MIN* und *as-ma* denselben eBL-Lemmata (*qātu*, *asāmu*) zugeordnet wie in Erra I 4?

## Abgabe

Nach der Sitzung, überarbeitet nach den Rückmeldungen: der Programmcode als Python-Modul in diesem Ordner, eine Anleitung zum Ausführen in dieser Datei und eine kurze Notiz dazu, wofür KI-Werkzeuge verwendet wurden.
