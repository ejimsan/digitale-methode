"""Local text normalization and JSON/JSONL reader for the lecturer's dictionary."""
from __future__ import annotations
from pathlib import Path
import gzip
import json
import unicodedata

def clean(value: str) -> str:
    return "" if value is None else " ".join(unicodedata.normalize("NFC", str(value)).split())

def read_json_records(path: Path):
    path=Path(path)
    opener=gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as source:
        if path.name.endswith('.json') or path.name.endswith('.json.gz'):
            value=json.load(source)
            if isinstance(value, list):
                yield from value
            else:
                yield value
        else:
            for line in source:
                if line.strip():
                    yield json.loads(line)
