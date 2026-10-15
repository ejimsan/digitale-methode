# Digitale Methoden in der Assyriologie
*Gruppenprojekt: Zitate und Anspielungen in akkadischen Texten automatisch finden*

Enrique Jiménez  
enrique.jimenez@lmu.de  

Blockseminar, Fr. 9–13 Uhr, Schellingstr. 5, 307

Termine: 16.10.2026; 30.10.2026; 13.11.2026; 11.12.2026; 15.01.2027

**BA Alter Orient:** P 2.2, WP 2.2, WP 7.2

**MA Altorientalistik:** WP 2.1, WP 3.1, WP 9.1, WP 10.1, WP 12.1, WP 13.1

## Beschreibung des Kurses

Material: [github.com/ejimsan/digitale-methode](https://github.com/ejimsan/digitale-methode) (Ordner 1._sitzung usw.)

Das Blockseminar führt Studierende in die Grundlagen der Programmierung sowie in den Einsatz digitaler Werkzeuge für die assyriologische Forschung ein. Ein besonderes Augenmerk gilt dabei den Möglichkeiten und Grenzen aktueller Werkzeuge der Künstlichen Intelligenz im Umgang mit keilschriftlichen Quellen. Vorkenntnisse in der Programmierung oder Informatik werden ausdrücklich nicht vorausgesetzt.

In diesem Semester arbeitet die Gruppe an einer gemeinsamen Forschungsfrage: Wie lassen sich Zitate und Anspielungen in akkadischen Texten automatisch aufspüren? Die Philologie hat dafür seit langem ein Kriterium: Eine Entlehnung ist dann wahrscheinlich, wenn zwei Stellen nicht bloß ein Wort, sondern eine Wendung teilen und wenn diese Wendung aus seltenen Wörtern oder aus einer seltenen Verbindung gewöhnlicher Wörter besteht. So ist der Ausdruck *ina ḫīṭi maḫrî*, „in der früheren Plage“, aus dem Erra-Epos (V 6) in den Wörterbüchern nur noch einmal belegt, nämlich im Bericht über den achten Feldzug Sargons II. (Z. 95). Bislang findet solche Fälle nur, wer beide Texte im Kopf hat. Die lemmatisierten Korpora des eBL und von Oracc erlauben es zum ersten Mal, die Suche systematisch über Hunderttausende von Zeilen zu führen.

Die Frage wird in acht Module zerlegt (siehe unten); jede Teilnehmerin und jeder Teilnehmer übernimmt eines davon. Jedes Modul ist in sich geschlossen und verbindet drei Dinge: eine philologische Studie zur Intertextualität in der Keilschriftliteratur, die methodische Literatur zum jeweiligen Verfahren (aus Computerlinguistik, Statistik oder der digitalen Klassischen Philologie, wo das Problem für das Lateinische bereits untersucht worden ist) und ein eigenes Programm, das mit Hilfe eines KI-Assistenten entwickelt und in der Sitzung vorgeführt wird. Als Prüfstein dient das Erra-Epos, das in Königsinschriften des 8. und 7. Jh. v. Chr. mehrfach zitiert wird. Die Ergebnisse fließen in einen gemeinsamen Aufsatz ein, zu dem alle Teilnehmenden beitragen.

**Teilnahmevoraussetzung:** Keine Vorkenntnisse in Programmierung erforderlich. Grundkenntnisse des Akkadischen empfohlen. Bitte zu jeder Sitzung einen Laptop mitbringen (Windows, macOS oder Linux; ein Tablet genügt nicht).

## Vor der ersten Sitzung

- Ein Konto bei [GitHub](https://github.com/signup) anlegen, und zwar mit der LMU-Adresse.
- Über [GitHub Education](https://education.github.com/) den Studierendenstatus bestätigen lassen. Damit steht der KI-Assistent GitHub Copilot kostenlos zur Verfügung. Die Prüfung kann einige Tage dauern; bitte deshalb sofort beantragen.
- Wer möchte, installiert vorab [Visual Studio Code](https://code.visualstudio.com/) und [Python](https://www.python.org/downloads/). In der ersten Sitzung wird beides gemeinsam eingerichtet.

## Arbeitsweise und Leistungsnachweis

Die erste Sitzung führt in Python, reguläre Ausdrücke, APIs, GitHub und die Literatursuche ein. Ab der zweiten Sitzung leiten jeweils zwei Teilnehmende die Sitzung und stellen ihr Modul im jeweiligen Stand vor:

1. **Literatur:** die philologische Studie und die methodische Literatur zum Modul, mit den Kriterien, nach denen dort Parallelen erkannt oder gemessen werden.
2. **Ansatz:** wie das Problem angegangen wurde und warum so.
3. **Vorführung:** das Programm live, auch mit Beispielen, die die Gruppe vorschlägt.
4. **Offene Fragen:** wo es nicht weitergeht und wo Hilfe gebraucht wird. Die Gruppe diskutiert und schlägt andere Wege vor; zu jedem Modul sind unten Fragen „Zur Diskussion“ genannt.

Nach der Sitzung wird das Modul, überarbeitet nach den Rückmeldungen, in das gemeinsame Repositorium eingestellt: [github.com/ejimsan/digitale-methode](https://github.com/ejimsan/digitale-methode). Kein Modul braucht die Ergebnisse eines anderen; alle arbeiten mit derselben Momentaufnahme der Daten von eBL und Oracc, und jedes hat einen eigenen Prüffall.

Der Leistungsnachweis besteht aus (1) dem Programmcode des eigenen Moduls im Repositorium, mit einer kurzen Anleitung, und (2) dem Beitrag zum gemeinsamen Aufsatz über das eigene Modul. Abgabe: [Datum wird ergänzt].

**KI-Werkzeuge** dürfen und sollen verwendet werden, mit drei Regeln: Nur Code einreichen, den man selbst Zeile für Zeile erklären kann; jedes Ergebnis an einem Fall prüfen, dessen Lösung man kennt; in einer kurzen Notiz beim Code offenlegen, wofür und wie KI verwendet wurde. Von KI genannte Literatur ist grundsätzlich im Katalog zu überprüfen, da Sprachmodelle Titel erfinden.

## Zeitplan

**1. 16.10.2026 — Einführung: Python, reguläre Ausdrücke, APIs, GitHub**

- **Inhalt:** Was ist ein Programm? Variablen, Datentypen, Listen, Funktionen, Schleifen, Module. Reguläre Ausdrücke. APIs und JSON. Git und GitHub. Literatur finden (Google Scholar, Semantic Scholar, ACL Anthology, KeiBi; Zotero). Nach jedem Block eine Übung, meist an Enūma eliš I 1–4; zum Schluss ein erstes Programm. Verteilung der Module.
- **Material:** Folien, Übungsblatt 1, bm35407.txt, Handout „Erste Schritte“

**2. 30.10.2026 — Werkzeuge; Module 1 und 3**

- **Inhalt:** Arbeiten mit einem KI-Assistenten (GitHub Copilot): Aufgaben formulieren, Code lesen, Ergebnisse prüfen. Die Daten von eBL und Oracc.
- **Module:** 1 (Konkordanz), 3 (Erhaltung und Ergänzung)
- **Lektüre:** Leonard 2008; Coffee et al. 2013

**3. 13.11.2026 — Module 2 und 4**

- **Module:** 2 (Königsinschriften aus Oracc), 4 (Seltenheit)
- **Lektüre:** Bach 2024; Cobanoglu et al. 2024

**4. 11.12.2026 — Module 5 und 6**

- **Module:** 5 (Tesserae für das Akkadische), 6 (Zufall oder Zitat?)
- **Lektüre:** Wisnom 2019; Forstall et al. 2015

**5. 15.01.2027 — Module 7 und 8; der gemeinsame Aufsatz**

- **Module:** 7 (Prüfstein), 8 (Formel oder Anspielung?)
- **Inhalt:** Abschlussdiskussion: Was ergibt sich, wenn man die Module verbindet, und was kann ein solches Verfahren nicht leisten? Plan des gemeinsamen Aufsatzes.
- **Lektüre:** Seri 2014; Monroe 2018

## Module

Die Module sind so angelegt, dass jedes für sich bearbeitet werden kann. Bei weniger als acht Teilnehmenden entfallen einzelne Module.

### Modul 1 — Ein Wort, alle Stellen: eine Konkordanz des eBL

- **Leitfrage:** Wie hat die Philologie bisher Parallelen gefunden? Mit Wörterbuch, Konkordanz und Gedächtnis. Kann ein Programm diese Arbeit für das ganze eBL-Korpus übernehmen, und was entgeht ihm?
- **Programm und Vorführung:** Ein Programm, das zu einem oder mehreren Lemmata alle Zeilen des lemmatisierten eBL-Korpus mit ihrem Kontext ausgibt (Konkordanz, *keyword in context*), dazu eine Übersicht über das Korpus: Texte, Gattungen, Anteil der lemmatisierten Zeilen. Vorführung: Suche nach Wendungen, die die Gruppe vorschlägt.
- **Philologische Lektüre:** Hurowitz 2002; Rozzi 2024
- **Methodische Lektüre:** Cobanoglu et al. 2024; Karsdorp et al. 2021
- **Zur Diskussion:** Was übersieht eine Suche nach Lemmata (nicht lemmatisierte Texte, Synonyme, Wortspiele)? Was leistet sie im Vergleich zu CAD und AHw?
- **Prüffall:** Die Suche nach *ḫīṭu* zusammen mit *maḫrû* findet Erra V 6.

### Modul 2 — Zwei Korpora, zwei Lemmatisierungen: die Königsinschriften aus Oracc

- **Leitfrage:** Die Zitate des Erra-Epos stehen in Königsinschriften, die in Oracc ediert sind (RINAP, RIBo, SAAo); das Epos selbst steht im eBL. Wie zuverlässig lassen sich die beiden Korpora über die Zuordnung verbinden, die das eBL-Wörterbuch zu jedem Lemma bereithält (Oracc-Zitierform und *guide word*, abrufbar über die eBL-API)?
- **Programm und Vorführung:** Ein Programm, das eine Oracc-Inschrift lädt und ihre Lemmata (z. B. *šarru[king]*) über die eBL-API in eBL-Lemmata (z. B. *šarru I*) überführt, mit einer Statistik: Wie viele Wörter lassen sich eindeutig, mehrdeutig oder gar nicht zuordnen? Vorführung: Sargons Bericht über den achten Feldzug, Zeile für Zeile in eBL-Lemmata.
- **Philologische Lektüre:** Bach 2024; Bach 2020b
- **Methodische Lektüre:** [Oracc ATF Primer](https://oracc.museum.upenn.edu/doc/help/editinginatf/primer/); Sahala/Lindén 2023
- **Zur Diskussion:** Die Zuordnung ist zum Teil mehrdeutig (zu *šarru I* gehören auch Oracc-Einträge wie *abat šarri*): Wann schadet das der Suche? Wie behandelt man Eigennamen? Was, wenn eine Seite falsch lemmatisiert?
- **Prüffall:** Sargon II 65 Z. 95: Wird *ḫiṭâtu* demselben eBL-Lemma zugeordnet wie *ḫīṭu* in Erra V 6, oder einem anderen?

### Modul 3 — Erhalten, beschädigt, ergänzt

- **Leitfrage:** Viele Ergänzungen in Editionen stammen gerade aus Parallelstellen. Ein Programm, das ergänzte Wörter wie erhaltene behandelt, „entdeckt“ also Parallelen, die der Editor selbst hineingeschrieben hat. Wie groß ist dieses Problem?
- **Programm und Vorführung:** Ein Programm, das aus der eBL-ATF mit regulären Ausdrücken für jedes Wort bestimmt, ob es erhalten, beschädigt (#) oder ergänzt ([ ]) ist, und den Anteil ergänzter Wörter je Text berechnet. Vorführung: eine Tafel des Erra-Epos, eingefärbt nach Erhaltungszustand; welche bekannten Erra-Parallelen beruhen ganz oder teilweise auf Ergänzungen?
- **Philologische Lektüre:** Worthington 2012 (in Auswahl)
- **Methodische Lektüre:** [eBL-ATF-Spezifikation](https://github.com/ElectronicBabylonianLiterature/ebl-api/blob/master/docs/ebl-atf.md); Knox 2013; Jurafsky/Martin 2026, Kap. 2
- **Zur Diskussion:** Ergänzte Wörter ganz ausschließen oder nur geringer gewichten? Und beschädigte? Wie gehen Papyrologie und griechische Epigraphik mit diesem Zirkel um?
- **Prüffall:** Marduk-apla-iddina II., RIMB 2 B.6.21.1 Z. 34: zehn beschädigte Zeichen und ein ergänztes ([hi]), wie im Handout.

### Modul 4 — Was ist selten?

- **Leitfrage:** „Seltene Wörter“ sind das wichtigste Kriterium für eine Anspielung. Aber selten wo: im ganzen Korpus, in der Literatur, in einer Epoche? Und ist ein Wort selten, oder nur selten überliefert?
- **Programm und Vorführung:** Ein Programm, das die Häufigkeit jedes Lemmas zählt, daraus ein Seltenheitsgewicht berechnet (z. B. den negativen Logarithmus der relativen Häufigkeit) und die Häufigkeitsverteilung als Diagramm zeigt; dazu ein Vergleich der Gewichte in verschiedenen Teilkorpora. Vorführung: der Wortschatz eines Textes nach Seltenheit geordnet, etwa die Theodizee neben dem Erra-Epos.
- **Philologische Lektüre:** Leonard 2008; Jiménez 2018
- **Methodische Lektüre:** Piantadosi 2014; Jurafsky/Martin 2026, Kap. 3
- **Zur Diskussion:** Wie behandelt man Eigennamen und Hapax legomena? Zählt man Lemmata oder Schreibungen? Wie groß ist der Einfluss des Überlieferungszufalls?
- **Prüffall:** *ina* und *ša* gehören zu den häufigsten Lemmata und erhalten ein Gewicht nahe null.

### Modul 5 — Parallelen finden: Tesserae für das Akkadische

- **Leitfrage:** Findet ein einfaches Verfahren nach dem Vorbild von Tesserae (gemeinsame Lemmata zweier Zeilen, gewichtet nach Seltenheit, unabhängig von der Wortfolge) die Anspielungen, die Wisnom und Seri zwischen Anzû, Enūma eliš und Erra beschrieben haben?
- **Programm und Vorführung:** Ein Programm, das für eine gegebene Zeile alle Zeilen anderer Texte des eBL-Korpus findet, die mindestens zwei Lemmata mit ihr teilen, und sie nach einem Wert ordnet; die Seltenheit berechnet es selbst. Damit nicht Milliarden von Zeilenpaaren verglichen werden müssen, arbeitet es über einen Index, der zu jedem Lemma seine Zeilen kennt. Vorführung: Abfrage beliebiger Zeilen durch die Gruppe.
- **Philologische Lektüre:** Wisnom 2019; Seri 2014; dazu Bach 2021
- **Methodische Lektüre:** Coffee et al. 2013; Forstall et al. 2015; Monroe 2018
- **Zur Diskussion:** Ist die Zeile die richtige Einheit, oder das Verspaar? Sollen Wortfolge und Abstand zählen? Wie viele Treffer sind bloße Formeln?
- **Prüffall:** Mindestens eine der von Wisnom 2019 besprochenen Parallelen erscheint unter den ersten zehn Treffern ihrer Zeile.

### Modul 6 — Zufall oder Zitat?

- **Leitfrage:** Wie wahrscheinlich ist es, dass zwei Zeilen ihre Lemmata rein zufällig teilen? Lässt sich das philologische „Das kann kein Zufall sein“ beziffern?
- **Programm und Vorführung:** Ein Programm, das für ein gegebenes Zeilenpaar die Wahrscheinlichkeit einer zufälligen Übereinstimmung schätzt, entweder durch Simulation (die Lemmata werden tausendfach zufällig neu auf Zeilen verteilt) oder mit einer Formel; weil sehr viele Paare geprüft werden, mit einer Korrektur für multiples Testen. Vorführung: Werte für bekannte Zitate im Vergleich mit zufällig gewählten Zeilenpaaren.
- **Philologische Lektüre:** Hays 1989, 29–32; Sommer 1998 (Einleitung)
- **Methodische Lektüre:** Dunning 1993; Church/Hanks 1990; Benjamini/Hochberg 1995
- **Zur Diskussion:** Was ist das richtige Zufallsmodell für eine Literatur voller Formeln und Gattungskonventionen? Kann Statistik die Richtung der Abhängigkeit bestimmen?
- **Prüffall:** Erra V 6 und Sargon II 65 Z. 95 erhalten einen deutlich kleineren Wert als ein Zeilenpaar, das nur *ina* und *ša* teilt.

### Modul 7 — Was die Philologie schon weiß: ein Prüfstein

- **Leitfrage:** Woran misst man ein Programm, das Zitate finden soll? An den Zitaten, die Philologen bereits erkannt haben. Aber was gilt dabei als Treffer?
- **Programm und Vorführung:** Eine maschinenlesbare Tabelle der bekannten Zitate des Erra-Epos (Erra-Stelle, zitierender Text und Zeile, Art der Beziehung, Nachweis), z. B. Erra V 35 bei Marduk-apla-iddina II., V 58 bei Nabû-šumu-ibbi, III 175 (*pašīra ṣabātu*) bei Sargon II.; dazu ein Programm, das jede beliebige Trefferliste gegen diese Tabelle prüft (Präzision und Recall). Vorführung: die Bewertung eines einfachen Verfahrens, z. B. „mindestens zwei gemeinsame Lemmata“.
- **Philologische Lektüre:** Frahm 2019; Gabriel 2024
- **Methodische Lektüre:** Coffee et al. 2013 (Abschnitt zur Evaluation)
- **Zur Diskussion:** Zählt die Nachbarzeile als Treffer? Wie bewertet man Funde, die nicht in der Tabelle stehen? Was ist wichtiger, Präzision oder Recall?
- **Prüffall:** Eine von Hand erstellte Trefferliste ergibt genau die Werte, die man von Hand nachrechnet.

### Modul 8 — Formel oder Anspielung?

- **Leitfrage:** Viele gemeinsame Wendungen sind keine Zitate, sondern Formeln, die vielen Texten gemeinsam sind. Lassen sich Formeln automatisch erkennen und von Anspielungen trennen?
- **Programm und Vorführung:** Ein Programm, das Verbindungen von Lemmata findet, die in vielen verschiedenen Texten wiederkehren, und sie nach Verbreitung und Assoziationsstärke ordnet (z. B. *Pointwise Mutual Information*). Vorführung: die verbreitetsten „Formeln“ des Korpus; welche davon würde eine Philologin als Formel anerkennen?
- **Philologische Lektüre:** Wasserman 2003 (in Auswahl); Ballesteros 2023; Conte 1986 (in Auswahl)
- **Methodische Lektüre:** Church/Hanks 1990; Coffee et al. 2012
- **Zur Diskussion:** Wo endet die Formel und beginnt die Anspielung (Conte: „Code“ und „Modell“)? Kann man auf eine Formel anspielen?
- **Prüffall:** Die gängige Redeeinleitung *pâšu īpuš-ma iqabbi* erscheint unter den gefundenen Formeln.

## Bibliographie

Bach, J. (2020a): Untersuchungen zur transtextuellen Poetik assyrischer herrschaftlich-narrativer Texte. State Archives of Assyria Studies 30. Helsinki.

Bach, J. (2020b): Transtextual Stylization of Neo-Assyrian Accounts of War, in: K. Gavagnin/R. Palermo (ed.), Imperial Connections 2. West & East Monografie 3. Trieste, 29–41 (Open Access: <https://hdl.handle.net/10077/31096>).

Bach, J. (2021): From the Armory of Narrative Art: The Intertextuality of Mythological Epics in Ancient Mesopotamia, Bibliotheca Orientalis 78, 24–38.

Bach, J. (2024): A Methodology for the Transtextual Analysis of Assyrian Royal Narrative Texts, in: D. Shehata/K. Sonik (ed.), Contemporary Approaches to Mesopotamian Literature: How to Tell a Story. Cuneiform Monographs 56. Leiden/Boston, 213–234 (DOI: <https://doi.org/10.1163/9789004697577_010>).

Ballesteros, B. (2023): Naming the Gods: Traditional Verse-Making in Homer and Old Babylonian Akkadian Poetry, Manuscript and Text Cultures 2/2 (DOI: <https://doi.org/10.56004/v2.2bb>).

Benjamini, Y./Y. Hochberg (1995): Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing, Journal of the Royal Statistical Society, Series B 57, 289–300 (DOI: <https://doi.org/10.1111/j.2517-6161.1995.tb02031.x>).

Church, K. W./P. Hanks (1990): Word Association Norms, Mutual Information, and Lexicography, Computational Linguistics 16, 22–29 (<https://aclanthology.org/J90-1003/>).

Cobanoglu, Y. [e. a.] (2024): Transliterated Cuneiform Tablets of the Electronic Babylonian Library Platform, Journal of Open Humanities Data 10, 19 (DOI: <https://doi.org/10.5334/johd.148>).

Coffee, N. [e. a.] (2012): Intertextuality in the Digital Age, Transactions of the American Philological Association 142, 383–422 (DOI: <https://doi.org/10.1353/apa.2012.0010>).

Coffee, N. [e. a.] (2013): The Tesserae Project: Intertextual Analysis of Latin Poetry, Literary and Linguistic Computing 28, 221–228 (DOI: <https://doi.org/10.1093/llc/fqs033>).

Conte, G. B. (1986): The Rhetoric of Imitation: Genre and Poetic Memory in Virgil and Other Latin Poets. Cornell Studies in Classical Philology 44. Ithaca.

Dunning, T. (1993): Accurate Methods for the Statistics of Surprise and Coincidence, Computational Linguistics 19, 61–74 (<https://aclanthology.org/J93-1003/>).

Forstall, C. [e. a.] (2015): Modeling the Scholars: Detecting Intertextuality through Enhanced Word-Level N-Gram Matching, Digital Scholarship in the Humanities 30, 503–515 (DOI: <https://doi.org/10.1093/llc/fqu014>).

Frahm, E. (2019): The Neo-Assyrian Royal Inscriptions as Text: History, Ideology, and Intertextuality, in: G. B. Lanfranchi/R. Mattila/R. Rollinger (ed.), Writing Neo-Assyrian History: Sources, Problems, and Approaches. State Archives of Assyria Studies 29. Helsinki.

Gabriel, G. I. (2024): Allusion or No Allusion: Commenting on the Interpretations of SB Gilgamesh Epic v 1–26 and ix 171–194, in: D. Shehata/K. Sonik (ed.), Contemporary Approaches to Mesopotamian Literature: How to Tell a Story. Cuneiform Monographs 56. Leiden/Boston, 183 ff.

Hays, R. B. (1989): Echoes of Scripture in the Letters of Paul. New Haven.

Hurowitz, V. A. (2002): An Overlooked Allusion to Ludlul in Urad-Gula’s Letter to Assurbanipal, State Archives of Assyria Bulletin 14, 129–132.

Jiménez, E. (2018): An Almost Irresistible Target: Parodying the Theodicy in Babylonian Literature, in: T. M. Oshima (ed.), Teaching Morality in Antiquity: Wisdom Texts, Oral Traditions, and Images. Orientalische Religionen in der Antike. Tübingen, 124–134 (DOI des Bandes: <https://doi.org/10.1628/978-3-16-156481-9>).

Jurafsky, D./J. H. Martin (2026): Speech and Language Processing. 3. Aufl., Entwurf vom 19.08.2026 (<https://web.stanford.edu/~jurafsky/slp3/>), Kap. 2 „Words and Tokens“; Kap. 3 „N-gram Language Models“.

Karsdorp, F./M. Kestemont/A. Riddell (2021): Humanities Data Analysis: Case Studies with Python. Princeton (frei online: <https://www.humanitiesdataanalysis.org/>).

Knox, D. (2013): Understanding Regular Expressions, Programming Historian 2 (DOI: <https://doi.org/10.46430/phen0033>).

Leonard, J. M. (2008): Identifying Inner-Biblical Allusions: Psalm 78 as a Test Case, Journal of Biblical Literature 127, 241–265 (DOI: <https://doi.org/10.2307/25610119>).

Monroe, M. W. (2018): Using Quantitative Methods for Measuring Inter-Textual Relations in Cuneiform, in: V. Bigot Juloux [e. a.] (ed.), CyberResearch on the Ancient Near East and Neighboring Regions. Digital Biblical Studies 2. Leiden/Boston, 257–281.

Piantadosi, S. T. (2014): Zipf’s Word Frequency Law in Natural Language: A Critical Review and Future Directions, Psychonomic Bulletin & Review 21, 1112–1130 (DOI: <https://doi.org/10.3758/s13423-014-0585-6>).

Rozzi, G. (2024): A Mosaic of Quotations: Intertextual Relationships in the Great Hymns and Prayers, in: dies., The Akkadian Great Hymns and Prayers. Antichistica 42 / Studi orientali 15. Venezia, 215–248 (Open Access, DOI: <https://doi.org/10.30687/978-88-6969-752-4/004>).

Sahala, A./K. Lindén (2023): A Neural Pipeline for POS-tagging and Lemmatizing Cuneiform Languages, in: Proceedings of the Ancient Language Processing Workshop. Varna, 203–212 (<https://aclanthology.org/2023.alp-1.23/>).

Seri, A. (2014): Borrowings to Create Anew: Intertextuality in the Babylonian Poem of “Creation” (Enūma eliš), Journal of the American Oriental Society 134, 89–106 (DOI: <https://doi.org/10.7817/jameroriesoci.134.1.0089>).

Sommer, B. D. (1998): A Prophet Reads Scripture: Allusion in Isaiah 40–66. Stanford.

Wasserman, N. (2003): Style and Form in Old-Babylonian Literary Texts. Cuneiform Monographs 27. Leiden/Boston.

Wisnom, S. (2019): Blood on the Wind and the Tablet of Destinies: Intertextuality in Anzû, Enūma eliš, and Erra and Išum, Journal of the American Oriental Society 139, 269–286 (DOI: <https://doi.org/10.7817/jameroriesoci.139.2.0269>).

Worthington, M. (2012): Principles of Akkadian Textual Criticism. Studies in Ancient Near Eastern Records 1. Boston/Berlin.

### Weiterführend

Genette, G. (1982): Palimpsestes. La littérature au second degré. Paris (engl.: Palimpsests: Literature in the Second Degree. Lincoln/London 1997).

Hinds, S. (1998): Allusion and Intertext: Dynamics of Appropriation in Roman Poetry. Cambridge.

Kristeva, J. (1967): Bakhtine, le mot, le dialogue et le roman, Critique 239, 438–465.

Machinist, P. (1983): Assyria and Its Image in the First Isaiah, Journal of the American Oriental Society 103, 719–737.

Sommerschield, T. [e. a.] (2023): Machine Learning for Ancient Languages: A Survey, Computational Linguistics 49, 703–747 (DOI: <https://doi.org/10.1162/coli_a_00481>).

Thomas, R. F. (1986): Virgil’s Georgics and the Art of Reference, Harvard Studies in Classical Philology 90, 171–198.

Tigay, J. H. (1982): The Evolution of the Gilgamesh Epic. Philadelphia.

Wisnom, S. (2020): Weapons of Words: Intertextual Competition in Babylonian Poetry. A Study of Anzû, Enūma eliš, and Erra and Išum. Culture and History of the Ancient Near East 106. Leiden/Boston.
