"""Momentaufnahme für den Kurs „Digitale Methoden in der Assyriologie“.

Liest die lemmatisierten Texte direkt aus der eBL-Datenbank (Verbindung über die
Umgebungsvariable MONGODB_URI), lädt die Oracc-Archive herunter und schreibt
eine Zeile Text pro JSON-Zeile:

  {"quelle": "eBL-Fragment", "text": "BM.35407", "zeile": "13'",
   "gattung": [...], "periode": "...", "atf": "...",
   "woerter": [{"wert": "ša₂", "lemma": ["ša I"], "zustand": "erhalten"}, ...]}

Aufruf:
  python make_snapshot.py --out snapshot_2026-10-20
  python make_snapshot.py --out snapshot_2026-10-20 --db ebl          # falls die URI keinen Datenbanknamen enthält
  python make_snapshot.py --out snapshot_2026-10-20 --export export/  # statt der Datenbank: mongoexport-Dateien
  python make_snapshot.py --out snapshot_2026-10-20 --fragmente       # zusätzlich das Fragmentarium
"""
import argparse
import gzip
import json
import os
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

WORD_TYPES = {"Word", "LoneDeterminative", "AkkadianWord", "GreekWord"}
CHILD_KEYS = ("parts", "tokens", "nameParts", "surrogate")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def walk(token):
    """Alle Teil-Token eines Tokens, rekursiv."""
    for key in CHILD_KEYS:
        for child in token.get(key) or []:
            yield child
            yield from walk(child)
    if isinstance(token.get("sign"), dict):
        yield token["sign"]
        yield from walk(token["sign"])


def condition(token):
    """'ergänzt', wenn ein Zeichen in [ ] steht; 'beschädigt', wenn ein Zeichen # trägt; sonst 'erhalten'."""
    enclosures = set(token.get("enclosureType") or [])
    flags = set(token.get("flags") or []) | set(token.get("modifiers") or [])
    for part in walk(token):
        enclosures |= set(part.get("enclosureType") or [])
        flags |= set(part.get("flags") or [])
        if part.get("type") == "AkkadianWord":
            flags |= set(part.get("modifiers") or [])
    if "BROKEN_AWAY" in enclosures:
        return "ergänzt"
    if "#" in flags:
        return "beschädigt"
    return "erhalten"


def words(tokens):
    out = []
    for t in tokens or []:
        if t.get("type") in WORD_TYPES:
            out.append({"wert": t.get("value", ""),
                        "lemma": list(t.get("uniqueLemma") or []),
                        "zustand": condition(t)})
    return out


def atf(tokens):
    return " ".join(t.get("value", "") for t in tokens or [])


def museum_number(doc):
    if isinstance(doc.get("_id"), str):
        return doc["_id"]
    n = doc.get("museumNumber") or {}
    s = f"{n.get('prefix', '')}.{n.get('number', '')}"
    return s + (f".{n['suffix']}" if n.get("suffix") else "")


def line_label(number):
    """Zeilennummer eines Kapitels (LineNumber oder LineNumberRange) als Text."""
    if not isinstance(number, dict):
        return str(number)
    if number.get("type") == "LineNumberRange":
        return f"{line_label(number['start'])}-{line_label(number['end'])}"
    s = f"{number.get('prefixModifier') or ''}{number.get('number', '')}"
    s += "′" if number.get("hasPrime") else ""
    s += number.get("suffixModifier") or ""
    return s


def fragment_lines(docs):
    for doc in docs:
        text = museum_number(doc)
        genres = [" > ".join(g.get("category", [])) for g in doc.get("genres") or []]
        period = (doc.get("script") or {}).get("period", "")
        for line in (doc.get("text") or {}).get("lines") or []:
            if line.get("type") != "TextLine":
                continue
            w = words(line.get("content"))
            if not any(x["lemma"] for x in w):
                continue
            yield {"quelle": "eBL-Fragment", "text": text,
                   "zeile": (line.get("prefix") or "").rstrip("."),
                   "gattung": genres, "periode": period,
                   "atf": atf(line.get("content")), "woerter": w}


def chapter_lines(docs):
    """Rekonstruierter Text der Kapitel im eBL-Korpus (eine Zeile je Variante)."""
    for doc in docs:
        tid = doc.get("textId") or {}
        text = f"{tid.get('genre', '')} {tid.get('category', '')}.{tid.get('index', '')} {doc.get('stage', '')} {doc.get('name', '')}".strip()
        for line in doc.get("lines") or []:
            label = line_label(line.get("number"))
            for k, variant in enumerate(line.get("variants") or []):
                rec = variant.get("reconstruction") or []
                w = words(rec)
                if not any(x["lemma"] for x in w):
                    continue
                yield {"quelle": "eBL-Korpus", "text": text,
                       "zeile": label + (f" (Var. {k + 1})" if k else ""),
                       "gattung": [tid.get("genre", "")], "periode": "",
                       "atf": atf(rec), "woerter": w}


def manuscript_label(m):
    num = m.get("museumNumber")
    if isinstance(num, dict) and num.get("number"):
        s = f"{num.get('prefix', '')}.{num.get('number', '')}" + (f".{num['suffix']}" if num.get("suffix") else "")
    else:
        s = m.get("accession") or f"Ms. {m.get('id')}"
    return s + (f" ({m['siglumDisambiguator']})" if m.get("siglumDisambiguator") else "")


def manuscript_lines(docs):
    """Die Zeilen der einzelnen Manuskripte der Kapitel, mit # und [ ] (für Modul 3)."""
    for doc in docs:
        tid = doc.get("textId") or {}
        text = f"{tid.get('genre', '')} {tid.get('category', '')}.{tid.get('index', '')} {doc.get('stage', '')} {doc.get('name', '')}".strip()
        mss = {m.get("id"): m for m in doc.get("manuscripts") or []}
        for line in doc.get("lines") or []:
            label = line_label(line.get("number"))
            for variant in line.get("variants") or []:
                for ml in variant.get("manuscripts") or []:
                    tl = ml.get("line") or {}
                    if tl.get("type") != "TextLine":
                        continue
                    w = words(tl.get("content"))
                    if not w:
                        continue
                    m = mss.get(ml.get("manuscriptId"), {})
                    yield {"quelle": "eBL-Korpus-Manuskript", "text": text, "zeile": label,
                           "manuskript": manuscript_label(m) if m else str(ml.get("manuscriptId")),
                           "manuskript_zeile": (tl.get("prefix") or "").rstrip("."),
                           "gattung": [tid.get("genre", "")], "periode": m.get("period", "") if m else "",
                           "atf": atf(tl.get("content")), "woerter": w}


def oracc_map(words):
    """(Zitierform, guide word) → Liste der eBL-Lemmata, aus dem Feld oraccWords."""
    m = defaultdict(list)
    for w in words:
        for ow in w.get("oraccWords") or []:
            m[(ow.get("lemma"), ow.get("guideWord"))].append(w["_id"])
    return m


def cdl_lines(node, state):
    """Durchläuft den CDL-Baum eines Oracc-Textes und sammelt Lemmata je Zeile."""
    if isinstance(node, list):
        for n in node:
            yield from cdl_lines(n, state)
        return
    if not isinstance(node, dict):
        return
    if node.get("node") == "d" and node.get("type") == "line-start":
        if state["words"]:
            yield state["label"], state["words"]
        state["label"], state["words"] = node.get("label", ""), []
    elif node.get("node") == "l":
        f = node.get("f") or {}
        state["words"].append(f)
    yield from cdl_lines(node.get("cdl", []), state)


def oracc_texts(z, label):
    """Alle Texte (corpusjson) in einem Oracc-Archiv, auch in verschachtelten ZIP-Dateien."""
    import io
    stats = {"dateien": 0, "texte": 0, "fehler": 0}
    for name in z.namelist():
        if name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(z.read(name))) as inner:
                yield from oracc_texts(inner, f"{label}/{name}")
            continue
        stats["dateien"] += 1
        if "corpusjson/" not in name or not name.endswith(".json"):
            continue
        try:
            doc = json.loads(z.read(name))
        except (json.JSONDecodeError, UnicodeDecodeError):
            stats["fehler"] += 1
            continue
        stats["texte"] += 1
        yield name, doc
    print(f"  {label}: {stats['dateien']} Dateien, {stats['texte']} Texte (corpusjson), {stats['fehler']} nicht lesbar")


def oracc_lines(oracc_dir, mapping):
    zips = sorted(Path(oracc_dir).glob("*.zip"))
    if not zips:
        print(f"  keine Oracc-Archive in {Path(oracc_dir).resolve()}")
    for zpath in zips:
        with zipfile.ZipFile(zpath) as z:
            n_lines = 0
            for name, doc in oracc_texts(z, zpath.name):
                text = doc.get("textid", Path(name).stem)
                project = doc.get("project", zpath.stem)
                state = {"label": "", "words": []}
                found = list(cdl_lines(doc.get("cdl", []), state))
                if state["words"]:
                    found.append((state["label"], state["words"]))
                for label, fs in found:
                    w = []
                    for f in fs:
                        cands = mapping.get((f.get("cf"), f.get("gw")), [])
                        w.append({"wert": f.get("form", ""),
                                  "oracc": f"{f.get('cf', '')}[{f.get('gw', '')}]{f.get('pos', '')}",
                                  "lemma": cands,
                                  "zuordnung": "eindeutig" if len(cands) == 1 else ("mehrdeutig" if cands else "keine")})
                    n_lines += 1
                    yield {"quelle": f"Oracc/{project}", "text": text, "zeile": label,
                           "gattung": [], "periode": "", "atf": "", "woerter": w}
            print(f"  {zpath.name}: {n_lines} Zeilen mit Lemmata")


FRAGMENT_QUERY = {"text.lines.content.uniqueLemma.0": {"$exists": True}}
FRAGMENT_FIELDS = {"museumNumber": 1, "genres": 1, "script": 1, "text.lines": 1}
CHAPTER_FIELDS = {"textId": 1, "stage": 1, "name": 1, "lines": 1, "manuscripts": 1}
WORD_FIELDS = {"lemma": 1, "homonym": 1, "guideWord": 1, "pos": 1, "oraccWords": 1}

# Oracc-Projekte mit Königsinschriften und Staatsarchiven. Die Unterprojekte (Bände)
# werden aus dem Hauptarchiv jedes Projekts ermittelt; die Listen unten dienen nur als Rückfall.
ORACC_PROJECTS = ["rinap", "riao", "ribo", "saao", "suhu"]
ORACC_FALLBACK = {
    "rinap": [f"rinap/rinap{n}" for n in range(1, 6)],
    "saao": [f"saao/saa{n:02d}" for n in range(1, 22)],
}


def open_database(db_name=None, tls_ca_file=None, tls_insecure=False):
    from pymongo import MongoClient
    uri = os.environ["MONGODB_URI"]
    options = {}
    if tls_ca_file:
        options["tlsCAFile"] = tls_ca_file
    if tls_insecure:
        options["tlsAllowInvalidCertificates"] = True
    client = MongoClient(uri, **options)
    if db_name:
        return client[db_name]
    try:
        return client.get_default_database()
    except Exception:
        return client[os.environ.get("MONGODB_DB", "ebl")]


def ssl_context(insecure=False):
    import ssl
    if insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    try:
        import certifi                       # aktuelle Liste der Zertifizierungsstellen
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def fetch(url, dest, ctx):
    try:
        with urllib.request.urlopen(url, context=ctx, timeout=300) as r, open(dest, "wb") as f:
            f.write(r.read())
        print(f"geladen: {url}")
        return True
    except Exception as e:
        print(f"nicht geladen: {url} ({e})")
        if dest.exists():
            dest.unlink()
        return False


def subprojects(zpath, project):
    """Liest aus dem Hauptarchiv eines Projekts die Namen seiner Unterprojekte (z. B. rinap/rinap4)."""
    import re
    found = set()
    pat = re.compile(r'"(' + re.escape(project) + r'/[A-Za-z0-9_]+)"')
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            if name.endswith(".json") and "corpusjson/" not in name:
                found |= set(pat.findall(z.read(name).decode("utf-8", "ignore")))
    return sorted(found)


def has_texts(zpath):
    with zipfile.ZipFile(zpath) as z:
        return any("corpusjson/" in n and n.endswith(".json") for n in z.namelist())


def download_oracc(target, projects=ORACC_PROJECTS, insecure=False):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    ctx = ssl_context(insecure)
    base = "https://oracc.museum.upenn.edu/json/"
    for p in projects:
        main = target / f"{p}.zip"
        if not main.exists() and not fetch(base + main.name, main, ctx):
            subs = ORACC_FALLBACK.get(p, [])
        elif has_texts(main):
            subs = []                       # Texte liegen schon im Hauptarchiv
        else:
            subs = subprojects(main, p) or ORACC_FALLBACK.get(p, [])
            print(f"  {p}: {len(subs)} Unterprojekte")
        for sp in subs:
            dest = target / (sp.replace("/", "-") + ".zip")
            if not dest.exists():
                fetch(base + dest.name, dest, ctx)


def write(records, path):
    n = 0
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    print(f"{path}: {n} Zeilen")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Zielordner, z. B. snapshot_2026-10-20")
    ap.add_argument("--db", help="Datenbankname, falls nicht in MONGODB_URI enthalten")
    ap.add_argument("--export", help="statt der Datenbank: Ordner mit fragments.jsonl, chapters.jsonl, words.jsonl (mongoexport)")
    ap.add_argument("--oracc", default="oracc", help="Ordner für die Oracc-Archive (Standard: oracc)")
    ap.add_argument("--no-download", action="store_true", help="Oracc-Archive nicht herunterladen, nur vorhandene verwenden")
    ap.add_argument("--tls-ca-file", help="Zertifikat (PEM) der Zertifizierungsstelle des Datenbankservers")
    ap.add_argument("--tls-insecure", action="store_true", help="Zertifikate von Datenbank und Oracc nicht prüfen (nur im Notfall)")
    ap.add_argument("--nur-oracc", action="store_true", help="nur den Oracc-Teil erzeugen (eBL-Dateien nicht neu schreiben)")
    ap.add_argument("--fragmente", action="store_true", help="auch das Fragmentarium exportieren (Vorsicht: Manuskripte der Kapitel erscheinen dann doppelt)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if a.export:
        exp = Path(a.export).resolve()
        if not exp.exists():
            raise SystemExit(f"Nicht gefunden: {exp}\nBitte den Ordner (oder eine Datei darin) angeben, "
                             "in dem fragments.jsonl, chapters.jsonl und words.jsonl liegen.")
        if exp.is_file():          # auch eine einzelne Datei ist erlaubt: dann deren Ordner
            exp = exp.parent
        print(f"Exportordner: {exp}")

        def source(name):
            path = exp / f"{name}.jsonl"
            if path.exists():
                return lambda: read_jsonl(path)
            print(f"übersprungen: {path} nicht gefunden")
            return None

        fragments = source("fragments") if a.fragmente else None
        chapters, words = source("chapters"), source("words")
    else:
        db = open_database(a.db, a.tls_ca_file, a.tls_insecure)
        print(f"Datenbank: {db.name}")
        fragments = (lambda: db["fragments"].find(FRAGMENT_QUERY, FRAGMENT_FIELDS)) if a.fragmente else None
        chapters = lambda: db["chapters"].find({}, CHAPTER_FIELDS)
        words = lambda: db["words"].find({"oraccWords.0": {"$exists": True}}, WORD_FIELDS)

    if a.nur_oracc:
        fragments = chapters = None
    if fragments:
        write(fragment_lines(fragments()), out / "ebl_fragmente.jsonl.gz")
    if chapters:
        write(chapter_lines(chapters()), out / "ebl_korpus.jsonl.gz")
        write(manuscript_lines(chapters()), out / "ebl_korpus_manuskripte.jsonl.gz")
    if not words:
        print("übersprungen: Oracc (ohne words.jsonl keine Zuordnung zu eBL-Lemmata)")
        return
    if not a.no_download:
        download_oracc(a.oracc, insecure=a.tls_insecure)
    write(oracc_lines(a.oracc, oracc_map(words())), out / "oracc.jsonl.gz")


if __name__ == "__main__":
    main()
