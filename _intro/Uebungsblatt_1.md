# Übungsblatt 1: Reguläre Ausdrücke und ein erstes Programm
*Digitale Methoden in der Assyriologie, 16.10.2026*

Enrique Jiménez  
enrique.jimenez@lmu.de  

## Der Text

Ein Auszug aus BM.35407, einem astro-mythologischen Kalendertraktat aus Babylon (Abschnitt zum Monat Simānu), in eBL-ATF. In eBL-ATF steht *h* für *ḫ*. Die Datei `bm35407.txt` (Ordner `_intro`) enthält dieselben Zeilen; Zeilennummer und Umschrift sind durch einen Tabulator getrennt.

```
i 13′   [k]i-i ša₂ ru-bu-u₂ {d}AMAR.UTU a-na ša₂-kan a-b[u-bu ...]
i 15′   e-liš u₂ šap-liš le-mut-tu₄ u₂-šah-haz-ma i-kap-pu-du sur-ra-[a-tu₄]
i 18′   DINGIR-MEŠ ma-ha-zi KUR URI{ki} UN-MEŠ-šu₂-nu u₂-šah-ha-zu nu-ul-la-a-tu₄
i 19′   a-mat šu-uš-tu₄ i-dab-bu-bu i-qab-bu-u₂ ma-ag-ri-tu₄
i 20′   mi-il-ki la ku-šir im-tal-lik i-te-ep-šu₂ sur-ra-a-tu₄
i 21′   ig-ga-ag-ma {d}EN u₂-hal-laq eš-re-e-tu₄
i 22′   e-la-ma-a ṭe₃-e-mu i-šak-kan-ma i-sap-pan ma-a-tu₄
i 23′   a-na ku-um ša₂-kan a-bu-bu a-na šul-mu giš-kim-mu DU₃-uš NAM.BUR₂.BI
```

**In dieser Sitzung arbeiten wir ohne KI-Assistenten.** Wer die Grundlagen selbst beherrscht, kann später beurteilen, was ein Assistent vorschlägt.

## Teil A: Reguläre Ausdrücke

Öffnen Sie [regex101.com](https://regex101.com/), wählen Sie links „Python“ und fügen Sie den Text in das untere Feld ein. Schreiben Sie oben ein Muster, das genau das Verlangte findet. Die Tabelle im Handout (Abschnitt 4) hilft.

1. Alle Vorkommen der Zeichenfolge *tu₄*. Wie viele sind es?
2. Alle Zeichen mit Indexziffer (*u₂*, *tu₄*, *DU₃* …). Tipp: Die Indexziffern lassen sich als Bereich `[₀-₉]` schreiben; `\d` findet sie nicht.
3. Alle Logogramme, also alles in Großbuchstaben (*AMAR*, *UTU*, *DINGIR* …).
4. Den Inhalt aller Determinative, also nur *d* und *ki*, ohne die Klammern. Tipp: runde Klammern ( ) bilden eine Gruppe.
5. Alle ergänzten Stellen, d. h. alles zwischen eckigen Klammern.
6. Alle Wörter, die auf *-tu₄* enden. Was geschieht mit *sur-ra-[a-tu₄]*?
7. Alle Wörter, die mit *u₂-* beginnen (*u₂-hal-laq* usw.), aber nicht die Konjunktion *u₂* in *e-liš u₂ šap-liš* und nicht das Ende von *UN-MEŠ-šu₂-nu*. Es sind drei.
8. **Zusatz:** Alle Stellen, an denen ein Konsonant über die Zeichengrenze hinweg doppelt geschrieben ist (*ig-ga-ag-ma*, *im-tal-lik*). Nur Konsonanten, auch *h* (= *ḫ*). Tipp: `\1` verweist auf den Inhalt der ersten Gruppe.

## Teil B: Ein erstes Programm

Legen Sie `bm35407.txt` in Ihren Ordner „seminar“, erstellen Sie dort eine neue Datei `zeilen.py` und bauen Sie das Programm Schritt für Schritt auf. Führen Sie es nach jedem Schritt aus.

1. Die Datei öffnen und jede Zeile ausgeben:

```
for zeile in open("bm35407.txt", encoding="utf-8"):
    print(zeile.strip())
```

2. Zeilennummer und Umschrift trennen: `nummer, umschrift = zeile.strip().split("\t")`
3. Für jede Zeile ausgeben: die Nummer, die Anzahl der Wörter und ob sie eine Ergänzung enthält, etwa so: `i 23′: 9 Wörter, Ergänzung: nein`
4. Alle Logogramme des Textes in einer Liste sammeln (mit `re.findall` und Ihrem Muster aus A3) und am Ende alphabetisch und ohne Doppelte ausgeben. Tipp: `sorted(set(liste))`.
5. Die fünf häufigsten Zeichen des Textes ermitteln. Entfernen Sie vorher die Schadensmarken und zerlegen Sie an Bindestrichen, Punkten und Leerzeichen. Tipp: `Counter` aus dem Modul `collections`, wie in `erste_schritte.py`.
6. **Zusatz:** Das Ergebnis in eine Datei `bericht.txt` schreiben, oder das Programm auf eine andere Tafel aus dem eBL anwenden.

**Zur Kontrolle:** Zeile i 23′ hat neun Wörter; der Text enthält zwölf verschiedene Logogramme, darunter MEŠ, DU₃ und BUR₂.

## Bis zum 30.10.2026

- Das Programm fertigstellen und in die Sitzung mitbringen.
- Über GitHub Education den Studierendenstatus bestätigen lassen (für GitHub Copilot ab der zweiten Sitzung).
- Wer am 30.10. sein Modul vorstellt: erste Literatur und einen ersten Programmentwurf mitbringen.
