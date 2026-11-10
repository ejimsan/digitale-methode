"""Local Oracc / eBL lemma resolution, Text ID loading, and KWIC search."""
from __future__ import annotations

from collections import Counter, defaultdict
from enhancements import related_suggestions, inspect_text_id, PERIOD_ORDER, LiveEBL
from difflib import SequenceMatcher
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Any
import gzip
import json
import os
import re
import sqlite3
import sys
import unicodedata
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
# Read all four source files from the SAME complete dataset.  A partially
# populated sibling `daten/` must not hide a complete bundled `data/` folder.
DATA_ROOTS = (ROOT.parent / "daten", ROOT / "data", ROOT / "daten")
REQUIRED_DATA_FILES = (
    "oracc.jsonl.gz", "ebl_korpus.jsonl.gz",
    "ebl_korpus_manuskripte.jsonl.gz", "ebl_woerterbuch.jsonl.gz",
)
DATA = next(
    (folder for folder in DATA_ROOTS if all((folder / name).is_file() for name in REQUIRED_DATA_FILES)),
    next((folder for folder in DATA_ROOTS if (folder / "oracc.jsonl.gz").is_file()), ROOT / "data"),
)
INDEX = ROOT / ".kwic_index.sqlite"
LEXICAL_CORE = ROOT / "lexical_core"
if str(LEXICAL_CORE) not in sys.path:
    sys.path.insert(0, str(LEXICAL_CORE))
from common import clean
from ebl_dictionary import Dictionary, load_dictionary
from lemma_mapping import LemmaTracer, lemma_spelling, forms_of
from ebl_links import fragment_url, corpus_url

INDEX_VERSION = "local-kwic-6"  # Same corpus schema as v0.2
DATA_NAMES = ["oracc", "ebl_korpus", "ebl_korpus_manuskripte"]


def normalized_form(value: str, editorial: bool = False) -> str:
    value = unicodedata.normalize("NFKC", clean(value)).casefold()
    if editorial:
        value = re.sub(r"[\[\]#!?]", "", value)
    return value



def convert_akkadian_input(value: str) -> str:
    """eBL-style plain keyboard spellings; do not erase scholarly distinctions."""
    value = unicodedata.normalize('NFC', clean(value))
    for old, new in [('sz','š'), ('SZ','Š'), ('Sz','Š'), ('s,','ṣ'), ('S,','Ṣ'),
                     ('t,','ṭ'), ('T,','Ṭ'), ('h,','ḫ'), ('H,','Ḫ')]:
        value=value.replace(old,new)
    for old,new in [('aa','ā'),('ee','ē'),('ii','ī'),('uu','ū'),
                    ('AA','Ā'),('EE','Ē'),('II','Ī'),('UU','Ū')]:
        value=value.replace(old,new)
    return value


def spelling_key(value: str, ignore_length: bool = False) -> str:
    value = normalized_form(convert_akkadian_input(value))
    if ignore_length:
        # Only vowel-length differences are ignored (not emphatics or shin).
        for old,new in [('ā','a'),('ē','e'),('ī','i'),('ū','u')]:
            value=value.replace(old,new)
    return value


def lexical_similarity(search: str, candidate: str) -> tuple[int,float] | None:
    """Exact, macron variants, prefixes, then conservative spelling suggestions."""
    a=spelling_key(search)
    b=spelling_key(candidate)
    if not a or not b:return None
    if a==b:return (0,1.0)
    if spelling_key(a,True)==spelling_key(b,True):return (1,.97)
    if len(a)>=2 and b.startswith(a):return (2, len(a)/len(b))
    if len(a)>=3 and a.startswith(b) and len(b)>=3:return (2, len(b)/len(a))
    ratio=SequenceMatcher(None,spelling_key(a,True),spelling_key(b,True)).ratio()
    if len(a)>=4 and ratio>=.72 and abs(len(a)-len(b))<=2:
        return (3,ratio)
    return None


def reference_url(source: str, text: str, project: str = '', manuscript: str = '') -> tuple[str,str]:
    """Specific public deep links only; unknown source IDs remain unlinked."""
    if source=='oracc' and project.startswith('Oracc/'):
        path=project.removeprefix('Oracc/').strip('/')
        if re.fullmatch(r'[a-z0-9/_-]+',path) and re.fullmatch(r'[PQX]\d{6}',text or ''):
            return (f'https://oracc.museum.upenn.edu/{path}/{text}', 'Open Oracc edition')
    if source=='ebl_korpus_manuskripte':
        url=fragment_url(manuscript)
        return (url, 'Open specific eBL Library manuscript') if url else ('','')
    if source=='ebl_korpus':
        url=corpus_url(text)
        return (url,'Open specific eBL Corpus chapter') if url else ('','')
    return ('','')

def oracc_parts(value: str) -> tuple[str, str, str] | None:
    # The guide word can contain spaces/commas. POS follows the closing bracket.
    m = re.match(r"^(.*?)\[(.*)\]([^\[\]]*)$", value or "")
    if not m or not m.group(1) or not m.group(2):
        return None
    return (m.group(1), m.group(2), m.group(3))


def source_fingerprint() -> str:
    parts = [INDEX_VERSION]
    for name in DATA_NAMES:
        p = DATA / (name + ".jsonl.gz")
        if not p.is_file():
            raise FileNotFoundError(f"Missing data file: {p.name}")
        h = sha256()
        with p.open("rb") as inp:
            for block in iter(lambda: inp.read(1024 * 1024), b""):
                h.update(block)
        parts.append(f"{name}:{h.hexdigest()}")
    return "|".join(parts)


def connect(db: Path = INDEX):
    con = sqlite3.connect(db, timeout=30, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=30000")
    return con


def init_index(progress=print, db: Path = INDEX):
    """Build a durable SQLite index once, atomically, from the three course snapshots."""
    fingerprint = source_fingerprint()
    if db.exists():
        try:
            check_conn = connect(db)
            try:
                row = check_conn.execute("SELECT value FROM meta WHERE key='fingerprint'").fetchone()
                if row and row["value"] == fingerprint:
                    return "ready"
            finally:
                check_conn.close()
        except sqlite3.DatabaseError:
            pass
    progress("Indexing local corpora (first start only)…")
    temporary = db.with_name(db.name + ".building")
    temporary.unlink(missing_ok=True)
    con = connect(temporary)
    try:
        con.execute("PRAGMA journal_mode=DELETE")
        con.execute("PRAGMA synchronous=NORMAL")
        con.executescript("""
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE lines (
                id INTEGER PRIMARY KEY, source TEXT NOT NULL, text TEXT,
                label TEXT, manuscript TEXT, manuscript_line TEXT, period TEXT,
                project TEXT,
                words TEXT NOT NULL
            );
            CREATE TABLE occurrences (
                kind TEXT NOT NULL, key TEXT NOT NULL, line_id INTEGER NOT NULL,
                pos INTEGER NOT NULL
            );
            CREATE TABLE forms (
                spelling TEXT NOT NULL, editorial_spelling TEXT NOT NULL,
                oracc TEXT NOT NULL, frequency INTEGER NOT NULL,
                example_text TEXT, example_line TEXT,
                PRIMARY KEY(spelling,oracc)
            );
            CREATE TABLE lemmas (
                oracc TEXT PRIMARY KEY, cf TEXT, gw TEXT, pos TEXT,
                frequency INTEGER NOT NULL, example_text TEXT, example_line TEXT
            );
            CREATE TABLE mappings (
                oracc TEXT, ebl TEXT, frequency INTEGER NOT NULL,
                PRIMARY KEY(oracc,ebl)
            );
            CREATE TABLE ebl_names (ebl TEXT PRIMARY KEY);
        """)
        forms_count: Counter = Counter()
        forms_example = {}
        lemmas_count: Counter = Counter()
        lemmas_example = {}
        map_count: Counter = Counter()
        occ_buffer = []
        ebl_names = set()
        n_lines = 0
        for source in DATA_NAMES:
            with gzip.open(DATA / (source + ".jsonl.gz"), "rt", encoding="utf-8") as f:
                for raw in f:
                    if not raw.strip():
                        continue
                    record = json.loads(raw)
                    words = record.get("woerter") or []
                    cursor = con.execute("INSERT INTO lines(source,text,label,manuscript,manuscript_line,period,project,words) VALUES(?,?,?,?,?,?,?,?)", (
                        source, record.get("text", ""), record.get("zeile", ""),
                        record.get("manuskript", ""), record.get("manuskript_zeile", ""),
                        record.get("periode", ""), record.get("quelle", ""), json.dumps(words, ensure_ascii=False, separators=(",", ":"))
                    ))
                    line_id = cursor.lastrowid
                    n_lines += 1
                    for pos, word in enumerate(words):
                        raw_ebl = word.get("lemma") or []
                        for ebl in set(x for x in raw_ebl if isinstance(x,str) and x):
                            ebl_names.add(ebl)
                            occ_buffer.append(("mapped" if source=="oracc" else "ebl", ebl, line_id, pos))
                        if source != "oracc":
                            continue
                        lemma = word.get("oracc") or ""
                        form = word.get("wert") or ""
                        if not lemma or not oracc_parts(lemma):
                            continue
                        occ_buffer.append(("oracc", lemma, line_id, pos))
                        lemmas_count[lemma] += 1
                        lemmas_example.setdefault(lemma, (record.get("text", ""),record.get("zeile", "")))
                        if form:
                            key=(normalized_form(form), lemma)
                            forms_count[key]+=1
                            forms_example.setdefault(key,(record.get("text", ""),record.get("zeile", ""), normalized_form(form, True)))
                        for ebl in set(x for x in raw_ebl if isinstance(x,str) and x):
                            map_count[(lemma,ebl)]+=1
                    if len(occ_buffer)>=20000:
                        con.executemany("INSERT INTO occurrences(kind,key,line_id,pos) VALUES(?,?,?,?)",occ_buffer)
                        occ_buffer.clear()
                    if n_lines%50000==0:
                        progress(f"  Indexed {n_lines:,} text lines…")
            progress(f"  Completed {source}.")
        if occ_buffer:
            con.executemany("INSERT INTO occurrences(kind,key,line_id,pos) VALUES(?,?,?,?)",occ_buffer)
        con.executemany("INSERT INTO lemmas VALUES(?,?,?,?,?,?,?)", ((
            lemma, *oracc_parts(lemma), count, *lemmas_example[lemma]) for lemma,count in lemmas_count.items()))
        con.executemany("INSERT INTO forms VALUES(?,?,?,?,?,?)", ((
            spelling, extra[2], lemma, count, extra[0], extra[1]) for (spelling,lemma),count in forms_count.items() for extra in [forms_example[(spelling,lemma)]]))
        con.executemany("INSERT INTO mappings VALUES(?,?,?)", ((lemma,ebl,count) for (lemma,ebl),count in map_count.items()))
        con.executemany("INSERT INTO ebl_names VALUES(?)", ((x,) for x in sorted(ebl_names)))
        progress("Creating indexes…")
        con.executescript("""
            CREATE INDEX idx_occ_kind_key ON occurrences(kind,key,line_id);
            CREATE INDEX idx_occ_line ON occurrences(line_id);
            CREATE INDEX idx_forms_edit ON forms(editorial_spelling);
            CREATE INDEX idx_lemmas_cf ON lemmas(cf);
            CREATE INDEX idx_map_lemma ON mappings(oracc);
            CREATE INDEX idx_lines_source ON lines(source);
        """)
        con.execute("INSERT INTO meta VALUES('fingerprint',?)", (fingerprint,))
        con.execute("INSERT INTO meta VALUES('lines',?)",(str(n_lines),))
        con.commit()
    except Exception:
        con.close()
        temporary.unlink(missing_ok=True)
        raise
    con.close()
    os.replace(temporary,db)
    progress(f"Index ready: {n_lines:,} lines.")
    return "rebuilt"


class Resolver:
    def __init__(self, db: Path = INDEX):
        self.db = db
        self.dictionary = None
        self.dictionary_error = ""
        self._attempted = False
        self._dictionary_lock = Lock()
        self.tracer = None
        self.offline = False
        self.live = LiveEBL()

    def _dictionary(self) -> Dictionary | None:
        if self._attempted:
            return self.dictionary
        with self._dictionary_lock:
            if self._attempted:
                return self.dictionary
            local = DATA / 'ebl_woerterbuch.jsonl.gz'
            try:
                self.dictionary = load_dictionary(local)
                self.tracer = LemmaTracer(self.dictionary)
                self.dictionary_error = ''
            except Exception as exc:
                self.dictionary = None
                self.dictionary_error = str(exc)
            self._attempted = True
        return self.dictionary

    def text_id(self, text_id: str, project: str | None = None) -> dict:
        con=connect(self.db)
        try:
            dictionary=self._dictionary()
            def mapping(analysis):
                return self._propose_entries(analysis,dictionary,con)
            return inspect_text_id(con,text_id,project,mapping)
        finally:con.close()

    def suggestions(self, ids: list[str]) -> dict:
        if not isinstance(ids,list) or len(ids)>24 or not all(isinstance(x,str) for x in ids):
            raise ValueError('Invalid lemma selection')
        dictionary=self._dictionary()
        return {'suggestions':related_suggestions(dictionary,set(ids),3),
                'method':'Dictionary meaning similarity; suggestions are not verified synonyms.'}

    def online_dictionary_fallback(self,lemma: str) -> dict:
        if self.offline:return {'entries':[], 'status':'offline'}
        try:
            entries=self.live.dictionary_lookup(lemma)
            return {'entries':[{'id':x.get('_id') or x.get('id'), 'meaning':x.get('meaning',''),
                               'lemma':x.get('lemma',[])} for x in entries], 'status':'live'}
        except Exception as exc:
            return {'entries':[], 'status':'unavailable', 'note':type(exc).__name__}

    def identify(self, mode: str, terms: list[str]) -> list[dict]:
        if mode not in ('lemma','transliteration'):
            raise ValueError('Choose Lemma or Transliteration.')
        if not 1<=len(terms)<=12 or any(not isinstance(t,str) or not t.strip() or len(t)>180 for t in terms):
            raise ValueError('Enter 1–12 nonempty items, one per line.')
        dictionary=self._dictionary() if mode=='lemma' else None
        con=connect(self.db)
        answers=[]
        try:
            for original in terms:
                word=convert_akkadian_input(original)
                if mode=='transliteration':
                    key=normalized_form(word)
                    rows=con.execute('SELECT oracc,frequency,example_text,example_line FROM forms WHERE spelling=? ORDER BY frequency DESC,oracc LIMIT 50',(key,)).fetchall()
                    how='exact attestation'
                    if not rows:
                        how='editorial-normalized attestation'
                        key=normalized_form(word,True)
                        rows=con.execute('SELECT oracc,frequency,example_text,example_line FROM forms WHERE editorial_spelling=? ORDER BY frequency DESC,oracc LIMIT 50',(key,)).fetchall()
                    results=[]
                    for r in rows:
                        parts=oracc_parts(r['oracc'])
                        results.append({'oracc':r['oracc'],'label':r['oracc'],'meaning':parts[1] if parts else '',
                            'count':r['frequency'],'kind':'Oracc analysis', 'match':how,
                            'example':f"{r['example_text']} : {r['example_line']}"})
                else:
                    # Distinguish the known eBL ID (including its homonym numeral)
                    # from a literal Oracc citation form or an incomplete spelling.
                    candidates={}
                    def add(oracc,label,kind,cf,meaning,count=0,example='',score_adjust=0):
                        match=lexical_similarity(word,cf)
                        if oracc==word or (kind=='eBL main entry' and spelling_key(word)==spelling_key(label)):
                            match=(0,1.0)
                        if match is None:return
                        tier,ratio=match
                        if tier==3 and len(word)<4:return
                        kind_rank={'Oracc lemma':0,'eBL main entry':1,'eBL alternative form':2,'Oracc dictionary cross-reference':3,'eBL corpus entry':4}.get(kind,5)
                        common=0
                        for ca,cb in zip(spelling_key(word,True),spelling_key(cf,True)):
                            if ca!=cb:break
                            common+=1
                        rank=(tier+score_adjust,-common,kind_rank,-ratio,-int(count),label.casefold())
                        record={'oracc':oracc,'label':label,'meaning':meaning or '', 'count':count,
                                'kind':kind,'match':['exact','vowel-length variant','partial spelling','similar spelling'][tier],
                                'example':example,'_rank':rank}
                        if oracc not in candidates or rank<candidates[oracc]['_rank']:
                            candidates[oracc]=record
                    for r in con.execute('SELECT oracc,cf,gw,frequency,example_text,example_line FROM lemmas'):
                        add(r['oracc'],r['oracc'],'Oracc lemma',r['cf'],r['gw'],r['frequency'],
                            f"{r['example_text']} : {r['example_line']}")
                    if dictionary:
                        for id_,entry in dictionary.entries.items():
                            lemma=lemma_spelling(entry)
                            add('ebl:'+id_,id_,'eBL main entry',lemma,entry.get('meaning') or entry.get('guideWord') or '')
                            for alt in forms_of(entry):
                                add('eblform:'+id_+'|'+alt,id_+' (form: '+alt+')','eBL alternative form',alt,entry.get('meaning') or entry.get('guideWord') or '',score_adjust=0)
                        # Additional Oracc citation forms can be in the eBL dictionary
                        # even when that Oracc lemma is absent from the course snapshot.
                        for (cf,gw),ids in dictionary.reverse.items():
                            entryid=sorted(ids)[0]
                            add(f'{cf}[{gw}]',f'{cf}[{gw}]','Oracc dictionary cross-reference',cf,gw)
                    else:
                        for r in con.execute('SELECT ebl FROM ebl_names'):
                            name=r['ebl']; base=name.rsplit(' ',1)[0]
                            add('ebl:'+name,name,'eBL corpus entry',base,'')
                    # Exact matches plus transparent spelling/partial suggestions,
                    # capped for a manageable selection screen.
                    results=sorted(candidates.values(),key=lambda x:x['_rank'])[:40]
                    for result in results:result.pop('_rank',None)
                    how='dictionary & Oracc lemma suggestions'
                answers.append({'input':word,'original':original,'options':results,'found':bool(results),
                                'method':how,'truncated':len(results)>=40})
        finally:
            con.close()
        return answers

    def identify_unified(self, terms: list[str]) -> list[dict]:
        """Simultaneously search Oracc citation lemmata and attested written forms.

        eBL dictionary headwords/forms are an additional *fallback*, not a
        substitute for an Oracc analysis. Never predict an unattested inflection.
        Candidate ordering is lexical evidence, not philological probability.
        """
        if not isinstance(terms, list) or not 1 <= len(terms) <= 12 or any(
                not isinstance(t, str) or not t.strip() or len(t)>180 for t in terms):
            raise ValueError('Enter 1–12 nonempty words, one per line.')
        dictionary = self._dictionary()
        if dictionary is None:
            raise RuntimeError(
                "eBL Dictionary could not be loaded from "
                + str(DATA / 'ebl_woerterbuch.jsonl.gz')
                + ": " + (self.dictionary_error or 'unknown error')
            )
        con = connect(self.db)
        output = []
        try:
            # A lemma inventory is small enough to read once per request.
            lemma_rows = con.execute('SELECT oracc,cf,gw,frequency,example_text,example_line FROM lemmas').fetchall()
            for original in terms:
                term = convert_akkadian_input(original.strip())
                query = normalized_form(term)
                candidates = {}
                def add(key, label, kind, gloss, count, match, example='', matched_form=''):
                    if match is None:
                        return
                    tier, sim = match
                    source_priority={'Oracc lemma':0,'Oracc written form':1,
                        'eBL main entry':2,'eBL Other form':3,'eBL Oracc correspondence':4}.get(kind,5)
                    if term.upper()==term and any(c.isalpha() for c in term):
                        if kind=='Oracc written form':source_priority=0
                        elif kind=='Oracc lemma':source_priority=1
                    prefix = 0
                    for x,y in zip(spelling_key(term,True),spelling_key(matched_form or label,True)):
                        if x != y:break
                        prefix += 1
                    # Preserve exact written vowels as the first suggestion, but
                    # rank length-only variants immediately afterward. Attested
                    # frequency distinguishes common qātu from obscure lookalikes.
                    # Keep the proven fuzzy-candidate order; frequency only
                    # reorders credible exact and macron-only alternatives.
                    rank=((tier,source_priority,-count,-sim,-prefix,label.casefold())
                          if tier<=1 else
                          (tier,-prefix,source_priority,-sim,-count,label.casefold()))
                    previous=candidates.get(key)
                    evidence={'kind':kind,'match':('exact' if tier==0 else
                        'vowel-length variant' if tier==1 else 'partial' if tier==2 else 'similar'),
                        'matched_form':matched_form or label}
                    if previous is None or rank < previous['_rank']:
                        entry={'key':key,'label':label,'kind':kind,'meaning':gloss or '',
                               'count':count,'match':evidence['match'],'matched_form':matched_form,
                               'example':example,'_rank':rank,'_evidence':[evidence]}
                        if previous:
                            entry['_evidence'].extend(previous['_evidence'])
                        candidates[key]=entry
                    elif previous and evidence not in previous['_evidence']:
                        previous['_evidence'].append(evidence)

                # Directly accept a fully specified Oracc cf[guide word]POS.
                for r in lemma_rows:
                    key=r['oracc']; cf=r['cf']
                    match=(0,1.) if spelling_key(term)==spelling_key(key) else lexical_similarity(term,cf)
                    if match is not None:
                        add(key,key,'Oracc lemma',r['gw'],r['frequency'],match,
                            f"{r['example_text']} : {r['example_line']}",cf)
                # Written forms are actual surface attestations in the supplied
                # Oracc snapshot, not the full remote glossary or normalized forms.
                for field,lookup,desc in (
                    ('spelling',query,'exact'),
                    ('editorial_spelling',normalized_form(term,True),'editorial')):
                    rows=con.execute('SELECT spelling,oracc,frequency,example_text,example_line '
                        f'FROM forms WHERE {field}=? ORDER BY frequency DESC LIMIT 300',(lookup,)).fetchall()
                    for row in rows:
                        parts=oracc_parts(row['oracc'])
                        add(row['oracc'],row['oracc'],'Oracc written form',parts[1] if parts else '',
                            row['frequency'],(0,1.) if desc=='exact' else (1,.96),
                            f"{row['example_text']} : {row['example_line']}",row['spelling'])
                # Prefix suggestions are only considered when there are few
                # direct matches. Avoid expensive fuzzy scans over all 900k tokens.
                if len(candidates)<12 and len(query)>=3:
                    prefix_rows=con.execute('SELECT spelling,oracc,frequency,example_text,example_line '
                        'FROM forms WHERE spelling >= ? AND spelling < ? LIMIT 2500',
                        (query,query+'\uffff')).fetchall()
                    for row in prefix_rows:
                        match=lexical_similarity(term,row['spelling'])
                        if match is None or match[0]<2:continue
                        parts=oracc_parts(row['oracc'])
                        add(row['oracc'],row['oracc'],'Oracc written form',parts[1] if parts else '',
                            row['frequency'],match,
                            f"{row['example_text']} : {row['example_line']}",row['spelling'])
                # eBL is also checked, so a known eBL headword works even if it
                # is not represented in this limited Oracc teaching corpus.
                if dictionary:
                    for id_,entry in dictionary.entries.items():
                        main=lemma_spelling(entry)
                        gloss=entry.get('meaning') or entry.get('guideWord') or ''
                        exact_id=(spelling_key(term)==spelling_key(id_))
                        match=(0,1.) if exact_id else lexical_similarity(term,main)
                        if match:
                            add('ebl:'+id_,id_,'eBL main entry',gloss,0,match,'',main)
                        for alt in forms_of(entry):
                            match=lexical_similarity(term,alt)
                            if match:
                                add('eblform:'+id_+'|'+alt,
                                    id_+' (form: '+alt+')','eBL Other form',gloss,0,match,'',alt)
                    for (cf,gw),ids in dictionary.reverse.items():
                        if lexical_similarity(term,cf):
                            add(f'{cf}[{gw}]',f'{cf}[{gw}]','eBL Oracc correspondence',gw,0,
                                lexical_similarity(term,cf),'',cf)
                # Separate real Oracc lexical analyses from eBL dictionary
                # entries.  A glossary correspondence is not a second Oracc
                # lemma if the same cf+guideword is already in the corpus.
                ordered=sorted(candidates.values(),key=lambda item:item['_rank'])
                oracc_all=[]
                ebl_raw=[]
                attested_pairs={
                    (str(row['cf']).casefold(),str(row['gw']).casefold())
                    for row in lemma_rows
                }
                for candidate in ordered:
                    key=candidate['key']
                    if key.startswith(('ebl:','eblform:')):
                        ebl_raw.append(candidate)
                    else:
                        parts=oracc_parts(key)
                        if not parts:
                            continue
                        cf,gw,pos=parts
                        if (not pos and candidate['kind']=='eBL Oracc correspondence'
                            and (cf.casefold(),gw.casefold()) in attested_pairs):
                            continue
                        oracc_all.append(candidate)

                # The ranking is per database: a long Oracc list must not
                # crowd every eBL entry out of the first page.
                # Reserve visible capacity for length-only variants so they
                # cannot be pushed out by many short-vowel exact candidates.
                exact=[x for x in oracc_all if x['match']=='exact']
                length=[x for x in oracc_all if x['match']=='vowel-length variant']
                other=[x for x in oracc_all if x['match'] not in ('exact','vowel-length variant')]
                oracc_selected=(exact[:12]+length[:12]+other[:11])[:35]
                ebl_selected_raw=ebl_raw[:50]
                ebl_by_id={}
                def record_ebl(entry, rank, route_from=None):
                    id_=entry.get('id')
                    if not id_:
                        return
                    relation=entry.get('type')
                    existing=ebl_by_id.get(id_)
                    if existing is None:
                        ebl_by_id[id_]={
                            'id':id_, 'type':relation,
                            'basis':entry.get('basis',''),
                            'route':entry.get('route',''),
                            'meaning':entry.get('meaning',''),
                            '_rank':rank, 'evidence':[],
                            'linked_oracc':[]}
                        existing=ebl_by_id[id_]
                    else:
                        existing['_rank']=min(existing['_rank'],rank)
                        if relation is not None and (
                            existing['type'] is None or relation<existing['type']):
                            existing.update(type=relation,basis=entry.get('basis',''),
                                            route=entry.get('route',''))
                    detail=entry.get('basis','')
                    if detail and detail not in existing['evidence']:
                        existing['evidence'].append(detail)
                    if route_from and route_from not in existing['linked_oracc']:
                        existing['linked_oracc'].append(route_from)
                    if not existing['meaning'] and entry.get('meaning'):
                        existing['meaning']=entry['meaning']

                shown_oracc=[]
                for candidate in oracc_selected:
                    item={k:v for k,v in candidate.items() if k not in ('_rank','_evidence')}
                    item['evidence']=candidate['_evidence']
                    mapped=self._propose_entries(item['key'],dictionary,con)
                    item['linked_ebl']=[e['id'] for e in mapped]
                    # These are shown only after this Oracc analysis is checked.
                    # This prevents fuzzy Oracc candidates from flooding the
                    # eBL selection list with unrelated Type 1 entries.
                    item['linked_ebl_entries']=mapped
                    shown_oracc.append(item)
                    # An *exactly matching* Oracc citation form is evidence for
                    # showing its direct + upward dictionary matches immediately.
                    # Approximate spelling suggestions still require an explicit
                    # Oracc selection before their mappings appear.
                    if candidate['_rank'][0] <= 1:
                        # Spelling with or without macrons is equivalent only
                        # for candidate discovery. Actual Type 1/2/3 still comes
                        # from _propose_entries and dictionary evidence.
                        for entry in mapped:
                            record_ebl(entry,candidate['_rank'],route_from=item['key'])

                for candidate in ebl_selected_raw:
                    match_tier=candidate['_rank'][0]
                    for entry in self._propose_entries(candidate['key'],dictionary,con):
                        # A fuzzy spelling suggestion is not an attested
                        # correspondence. Types 1/2 require exact evidence.
                        if match_tier>0:
                            entry=dict(entry)
                            entry['type']=None
                            entry['basis']='Similar eBL spelling — verify before selecting'
                        record_ebl(entry,candidate['_rank'])

                ebl_shown=sorted(
                    ebl_by_id.values(),
                    key=lambda item:(item['type'] is None,item['_rank'],item['type'] or 99,item['id'])
                )[:25]
                for item in ebl_shown:
                    item.pop('_rank',None)
                output.append({
                    'input':term,'original':original,
                    'oracc_options':shown_oracc,'ebl_options':ebl_shown,
                    'found':bool(shown_oracc or ebl_shown),
                    'oracc_total':len(oracc_all),
                    'ebl_total':len(ebl_by_id),
                    'truncated':len(oracc_all)>len(shown_oracc)
                                or len(ebl_by_id)>len(ebl_shown)})
        finally:
            con.close()
        return output

    def reverse_oracc_candidates(self, ids: list[str]) -> dict:
        """Return attested Oracc analyses for selected eBL dictionary entries."""
        if not isinstance(ids, list) or len(ids)>30 or any(not isinstance(x,str) for x in ids):
            raise ValueError("Invalid eBL selection")
        dictionary=self._dictionary()
        if dictionary is None:
            raise RuntimeError("eBL Dictionary unavailable")
        con=connect(self.db)
        found={}
        try:
            for id_ in set(ids):
                entry=dictionary.entries.get(id_)
                if not entry:
                    continue
                pairs=set()
                for word in entry.get("oraccWords") or []:
                    if isinstance(word,dict):
                        cf=clean(word.get("lemma",""))
                        gw=clean(word.get("guideWord",""))
                        if cf and gw:
                            pairs.add((cf,gw))
                rows={}
                for cf,gw in pairs:
                    for row in con.execute("SELECT oracc,cf,gw,frequency FROM lemmas WHERE cf=? AND lower(gw)=lower(?)",(cf,gw)):
                        rows[row["oracc"]]=(row,"Explicit eBL oraccWords")
                for row in con.execute("SELECT l.oracc,l.cf,l.gw,l.frequency FROM lemmas l JOIN mappings m ON m.oracc=l.oracc WHERE m.ebl=?",(id_,)):
                    rows.setdefault(row["oracc"],(row,"Attested Oracc/eBL mapping"))
                for key,(row,evidence) in rows.items():
                    if key not in found:
                        found[key]={"key":key,"label":key,"kind":"Oracc lemma","meaning":row["gw"] or "",
                            "count":row["frequency"],"match":"reverse eBL match","matched_form":row["cf"],
                            "evidence":[],"linked_ebl":[],"linked_ebl_entries":self._propose_entries(key,dictionary,con)}
                    found[key]["evidence"].append({"kind":evidence,"matched_form":id_})
            return {"candidates":sorted(found.values(),key=lambda x:(-x["count"],x["label"]))[:100]}
        finally:
            con.close()

    def _propose_entries(self, analysis: str, dictionary: Dictionary | None, con) -> list[dict]:
        """Return direct matches (Types 1/2) and separate upstream family links (Type 3).

        The Type labels describe the *candidate eBL entry's relation* to the
        selected Oracc analysis. They are intentionally not the single overall
        v1.9 route-depth label (which would label wasmu → asmu I as Type 3).
        """
        records={}
        def put(id_,type_,basis,route='',origin='dictionary'):
            if not id_:return
            entry={'id':id_,'type':type_,'basis':basis,'route':route,'origin':origin,
                   'meaning':(dictionary.entries[id_].get('meaning') or dictionary.entries[id_].get('guideWord') or '')
                   if dictionary and id_ in dictionary.entries else ''}
            old=records.get(id_)
            if old is None or (type_ is not None and (old['type'] is None or type_<old['type'])):
                records[id_]=entry
        if not dictionary:
            if not analysis.startswith(('ebl:','eblform:')):
                for row in con.execute('SELECT ebl FROM mappings WHERE oracc=?',(analysis,)):
                    put(row['ebl'],None,'Local data match',origin='snapshot')
            elif analysis.startswith('ebl:'):
                id_=analysis[4:]
                if con.execute('SELECT 1 FROM ebl_names WHERE ebl=?',(id_,)).fetchone():
                    put(id_,None,'Attested eBL corpus lemma',origin='corpus')
            return list(records.values())
        if analysis.startswith('ebl:'):
            id_=analysis[4:]
            if id_ in dictionary.entries:
                put(id_,1,'Exact eBL dictionary entry')
        elif analysis.startswith('eblform:'):
            payload=analysis[len('eblform:'):]
            id_,separator,form=payload.partition('|')
            if separator and id_ in dictionary.entries and form in forms_of(dictionary.entries[id_]):
                put(id_,2,'eBL Other form: '+form)
        else:
            parts=oracc_parts(analysis)
            if parts:
                cf,gw,_=parts
                direct=dictionary.candidates_for(cf,gw)
                for id_ in direct:
                    main=lemma_spelling(dictionary.entries[id_])
                    is_main=(clean(cf)==main)
                    basis=('Exact main lemma' if is_main else
                        'eBL Other form' if cf in forms_of(dictionary.entries[id_]) else
                        'Explicit oraccWords correspondence')
                    put(id_,1 if is_main else 2,basis)
                    # Follow ONLY upward derivedFrom, and mark related eBL
                    # entries as Type 3. Preserve the direct entry separately.
                    if not is_main:
                        trace=self.tracer.trace_up(id_)
                        for path in trace['paths']:
                            if not path['steps']:continue
                            final=path['final']
                            if final not in dictionary.entries or final==id_:continue
                            sequence=' → '.join(str(step['reference'])+' → '+str(step['to'])
                                if step['resolution']=='other form' else str(step['to'])
                                for step in path['steps'])
                            put(final,3,'Related upstream via derivedFrom',id_+' → '+sequence)
        return sorted(records.values(),key=lambda e:(e['type'] is None,e['type'] or 9,e['id']))

    def resolve(self, chosen: list[dict]) -> dict:
        """Automatically resolve every user-approved step-2 analysis.

        All dictionary-supported candidates are retained as an explicitly
        ambiguous OR set, never forced to a single undocumented sense.
        """
        if not 1<=len(chosen)<=12:
            raise ValueError('Provide between one and twelve selected inputs.')
        dictionary=self._dictionary()
        conn=connect(self.db)
        results=[]
        try:
            for query in chosen:
                names=query.get('oracc')
                if isinstance(names,str):names=[names]
                if not isinstance(names,list) or not names or any(not isinstance(n,str) or not n for n in names):
                    raise ValueError('Select at least one candidate in step 2 for every input.')
                options={}
                def add_option(entry_id,match_type,basis,related=(),trace=(),source='v1.9 dictionary'):
                    record={'id':entry_id,'type':match_type,'basis':basis,'related':list(related),
                            'trace':trace, 'source':source}
                    old=options.get(entry_id)
                    if old is None or (old['type'] is None and match_type is not None) or (
                        old['type'] is not None and match_type is not None and match_type<old['type']):
                        options[entry_id]=record
                for name in names:
                    if name.startswith('eblform:'):
                        payload=name[len('eblform:'):]
                        id_,separator,form=payload.partition('|')
                        if separator and dictionary and id_ in dictionary.entries and form in forms_of(dictionary.entries[id_]):
                            info=self.tracer.classify(id_,form)
                            add_option(id_,info['level'],'Matched eBL Other form: '+form,
                                [x for x in info['final_entries'] if x!=id_],info['trace']['paths'])
                    elif name.startswith(('ebl:','lookup:')):
                        spelling=clean(name.split(':',1)[1]); queryspelling=spelling
                        if dictionary:
                            if spelling in dictionary.entries:
                                add_option(spelling,1,'eBL main entry (exact dictionary ID)')
                            else:
                                for id_,entry in dictionary.entries.items():
                                    main=lemma_spelling(entry)
                                    if spelling_key(main)==spelling_key(queryspelling):
                                        add_option(id_,1,'eBL main lemma spelling')
                                    elif any(spelling_key(form)==spelling_key(queryspelling) for form in forms_of(entry)):
                                        add_option(id_,2,'eBL Other forms')
                        else:
                            for r in conn.execute('SELECT ebl FROM ebl_names WHERE ebl=?',(spelling,)):
                                add_option(r['ebl'],None,'Attested eBL corpus lemma; dictionary unavailable',source='local corpus')
                    else:
                        parts=oracc_parts(name)
                        if not parts:raise ValueError(f'Unparseable Oracc lemma: {name}')
                        cf,gw,_=parts
                        if dictionary:
                            for id_ in dictionary.candidates_for(cf,gw):
                                info=self.tracer.classify(id_,cf)
                                add_option(id_,info['level'],info['basis'],
                                    [x for x in info['final_entries'] if x!=id_],info['trace']['paths'])
                        for r in conn.execute('SELECT ebl,frequency FROM mappings WHERE oracc=? ORDER BY frequency DESC',(name,)):
                            add_option(r['ebl'],None,'Local data mapping',source='local data')
                ranked=sorted(options.values(),key=lambda x:(x['type'] is None,x['type'] or 99,x['id']))
                results.append({'input':query.get('input',', '.join(names)), 'oracc':names,
                                'options':ranked,'ebl':[o['id'] for o in ranked],
                                'ambiguous':len(ranked)>1,'found':bool(ranked)})
        finally:conn.close()
        return {'queries':results,'dictionary':{'available':bool(dictionary),
            'coverage':dictionary.coverage if dictionary else 'snapshot-only',
            'warning':self.dictionary_error if not dictionary else ''}}

    def search(self, chosen: list[dict], context: int | None = None, limit: int = 300, offset: int = 0, source_scope: str = 'both', source_offsets: dict[str, int] | None = None) -> dict:
        """AND across inputs, OR across the selected analyses of each input.

        KWIC includes the full line by default, highlighting all searched terms,
        centering the first searched input and preserving the other highlights.
        Distinct query concepts cannot all match one solitary token.
        """
        if source_scope not in ('both','ebl','oracc'):
            raise ValueError('Search source must be both, ebl, or oracc.')
        if not 1<=len(chosen)<=12 or (context is not None and (not isinstance(context,int) or not 0<=context<=100)) or not 1<=limit<=10000 or offset<0:
            raise ValueError('Invalid search parameters.')
        # The legacy API uses one global offset. The browser uses independent
        # source offsets so a large Oracc result set cannot hide the eBL hits.
        if source_offsets is not None:
            if (not isinstance(source_offsets, dict) or
                    any(k not in DATA_NAMES or not isinstance(v, int) or isinstance(v, bool) or v < 0
                        for k, v in source_offsets.items())):
                raise ValueError('Invalid per-corpus pagination offsets.')
            source_offsets={source:source_offsets.get(source,0) for source in DATA_NAMES}
        normalized=[]
        for item in chosen:
            ids=item.get('ebl',[])
            ora=item.get('oracc',[])
            if isinstance(ids,str):ids=[ids]
            if isinstance(ora,str):ora=[ora]
            if (not isinstance(ids,list) or not isinstance(ora,list) or
                    (not ids and not ora) or
                    not all(isinstance(x,str) and x for x in ids+ora)):
                raise ValueError('Each input must have selected eBL or Oracc analyses.')
            normalized.append({'ebl':set(ids),'oracc':set(ora)})
        con=connect(self.db)
        try:
            line_sets=[]
            for group in normalized:
                selected=set()
                if source_scope != 'oracc':
                    for ebl in group['ebl']:
                        selected.update(r['line_id'] for r in con.execute(
                            "SELECT DISTINCT line_id FROM occurrences WHERE kind='ebl' AND key=?",(ebl,)))
                if source_scope != 'ebl':
                    for oracc in group['oracc']:
                        if oracc.startswith(('ebl:','eblform:','lookup:')):continue
                        selected.update(r['line_id'] for r in con.execute(
                            "SELECT DISTINCT line_id FROM occurrences WHERE kind='oracc' AND key=?",(oracc,)))
                line_sets.append(selected)
            ids=sorted(set.intersection(*line_sets)) if line_sets else []
            # Global chronological ordering BEFORE KWIC pagination. Oracc keeps its
            # original index order; unknown eBL dates follow all dated manuscripts.
            if ids and source_scope != 'oracc':
                sortrows={}
                for batch in range(0,len(ids),800):
                    chunk=ids[batch:batch+800]
                    for row in con.execute('SELECT id,source,period FROM lines WHERE id IN ('+','.join('?' for _ in chunk)+')',chunk):
                        sortrows[row['id']]=(row['source'],row['period'])
                ids.sort(key=lambda i:(0,i) if sortrows[i][0]=='oracc' else
                         (1,PERIOD_ORDER.get(sortrows[i][1],999),i))
            source_counts=Counter()
            results=[]
            total_hits=0; total_lines=0
            source_kwic_counts=Counter()
            seen_source_lines=set()
            for begin in range(0,len(ids),400):
                chunk=ids[begin:begin+400]
                raw_rows=con.execute('SELECT * FROM lines WHERE id IN ('+','.join('?' for _ in chunk)+')',chunk).fetchall()
                rows={row['id']:row for row in raw_rows}
                for line in (rows[i] for i in chunk):
                    source=line['source']
                    if source_scope=='ebl' and source=='oracc':continue
                    if source_scope=='oracc' and source!='oracc':continue
                    words=json.loads(line['words']); match_sets=[]
                    for group in normalized:
                        positions=[]
                        for i,w in enumerate(words):
                            # Explicitly separate the two annotation systems.
                            # Choosing an eBL dictionary entry does not silently
                            # imply searching an Oracc corpus mapping.
                            if ((source!='oracc' and set(w.get('lemma') or []).intersection(group['ebl'])) or
                                (source=='oracc' and w.get('oracc','') in group['oracc'])):
                                positions.append(i)
                        match_sets.append(positions)
                    if any(not m for m in match_sets):continue
                    # A small bipartite matching avoids treating one word token as
                    # two distinct searched terms when entries overlap.
                    def distinct_assignment(k,used):
                        if k==len(match_sets):return True
                        for pos in match_sets[k]:
                            if pos not in used and distinct_assignment(k+1,used|{pos}):return True
                        return False
                    if not distinct_assignment(0,set()):continue
                    # One physical/source line is one concordance hit even when
                    # the first searched lemma occurs repeatedly in that line.
                    # Only genuinely identical records are deduplicated: keep
                    # differing corpus editions, witnesses, and readings.
                    line_identity=(source,line['text'],line['label'],line['manuscript'],
                                   line['manuscript_line'],line['period'],line['words'])
                    if line_identity in seen_source_lines:
                        continue
                    seen_source_lines.add(line_identity)
                    total_lines+=1;source_counts[source]+=1
                    tagged=defaultdict(list)
                    for k,positions in enumerate(match_sets):
                        for pos in positions:tagged[pos].append(k)
                    # Represent one entire matching line, with every matched
                    # token highlighted; do not generate a second hit just
                    # because LUGAL (etc.) appears twice in this same line.
                    i=match_sets[0][0]
                    source_hit=source_kwic_counts[source]
                    if ((source_offsets is None and total_hits>=offset and len(results)<limit) or
                        (source_offsets is not None and
                         source_offsets[source]<=source_hit<source_offsets[source]+limit)):
                        start=0 if context is None else max(0,i-context)
                        end=len(words) if context is None else min(len(words),i+context+1)
                        all_matched=[position for positions in match_sets for position in positions]
                        if all_matched:
                            start=min(start,min(all_matched))
                            end=max(end,max(all_matched)+1)
                        display=[{'form':w.get('wert') or '', 'groups':tagged.get(pos,[]), 'center':pos==i}
                                 for pos,w in enumerate(words[start:end],start)]
                        ref_url,ref_label=reference_url(source,line['text'],line['project'] or '',line['manuscript'] or '')
                        results.append({'source':source,'text':line['text'],'line':line['label'],
                            'project':line['project'] or '',
                            'manuscript':line['manuscript'],'manuscript_line':line['manuscript_line'],
                            'period':line['period'],'words':display,
                            'left':' '.join((w.get('wert') or '') for w in words[start:i]),
                            'right':' '.join((w.get('wert') or '') for w in words[i+1:end]),
                            'keyword':words[i].get('wert') or '',
                            'atf':' '.join(w.get('wert') or '' for w in words),
                            'source_url':ref_url,'source_url_label':ref_label})
                    total_hits+=1
                    source_kwic_counts[source]+=1
            return {'total_lines':total_lines,'total_kwic_hits':total_hits,'results':results,
                    'source_counts':dict(source_counts),
                    'source_kwic_counts':dict(source_kwic_counts),
                    'source_offsets':source_offsets,
                    'offset':offset,'limit':limit,
                    'method':'Same-line AND across inputs; selected candidates within one input are OR.'}
        finally:
            con.close()
