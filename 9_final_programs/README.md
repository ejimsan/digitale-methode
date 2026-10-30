# Finale Konkordanz

Das Programm ist in kleine Module gegliedert. Für die Suche werden die
komprimierten JSONL-Dateien aus dem übergeordneten Ordner `daten` benötigt.

Ausführung aus dem Repository-Hauptordner:

```powershell
python .\9_final_programs\keyword_in_context.py
```

Tests ausführen:

```powershell
python -m unittest discover -s .\9_final_programs -p "test_*.py" -v
```
