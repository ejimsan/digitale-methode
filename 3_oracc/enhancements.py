"""Text-ID loading, lexical suggestions, and manuscript period sorting."""
from __future__ import annotations
from collections import Counter
from difflib import SequenceMatcher
from functools import lru_cache
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PERIOD_ORDER = {
    'Old Babylonian':10, 'Middle Babylonian':20, 'Middle Assyrian':30,
    'Hittite':35, 'Neo-Assyrian':40, 'Neo-Babylonian':50,
    'Late Babylonian':60, 'Persian':70, 'Hellenistic':80, 'Parthian':90,
}

def period_rank(source,period):
    if source=='oracc':return (0,0)
    return (1,PERIOD_ORDER.get(period,999))

# Suggestions are purely exploratory: a shared word buried in an explanation is
# not enough evidence for synonymy. We compare PRIMARY dictionary glosses only.
# A high threshold may intentionally return zero suggestions.
STOP={'a','an','and','or','the','of','to','be','in','with','on','for','from'}
SYNONYM_MIN_SIMILARITY=0.70

def primary_gloss(entry):
    """Extract a short lexical gloss, never a whole lexicographic commentary."""
    raw=entry.get('meaning') or ''
    if isinstance(raw,list):raw=' '.join(str(x) for x in raw)
    raw=str(raw)
    quoted=re.findall(r'["“]([^"”]{2,140})["”]',raw)
    # Dictionary may include a grammatical label before the first quoted gloss.
    if quoted:
        phrase=quoted[0]
    else:
        phrase=str(entry.get('guideWord') or '')
    phrase=re.sub(r'\([^)]*\)', '',phrase.lower())
    phrase=phrase.split(';',1)[0].split(',',1)[0]
    phrase=re.sub(r'[^a-z\s-]', ' ',phrase)
    phrase=' '.join(phrase.split())
    # Common glosses like "by hand", "his hand", "hand by hand" describe
    # adverbial constructions, not interchangeable nouns.
    return phrase

def meaning_tokens(phrase):
    return {w for w in re.findall(r'[a-z]{3,}',phrase) if w not in STOP}

def related_suggestions(dictionary,selected,maximum=3,threshold=SYNONYM_MIN_SIMILARITY):
    """Up to three high-similarity UNVERIFIED proposals, never forced to three.

    The overlap check is only a heuristic. Each returned entry retains its
    dictionary meaning for human verification. Does not infer synonyms by AI.
    """
    if not dictionary or not selected:return []
    entries=dictionary.entries
    seeds=[x for x in selected if x in entries][:12]
    if not seeds:return []
    seed_data=[]
    for sid in seeds:
        phrase=primary_gloss(entries[sid]); tokens=meaning_tokens(phrase)
        if phrase and tokens:seed_data.append((sid,phrase,tokens,set(entries[sid].get('pos') or [])))
    if not seed_data:return []
    results=[]
    for id_,entry in entries.items():
        if id_ in selected:continue
        phrase=primary_gloss(entry); tokens=meaning_tokens(phrase)
        if not tokens:continue
        best=0.0; best_seed=''
        for sid,seed_phrase,seed_tokens,seed_pos in seed_data:
            # Avoid syntactic phrases or possessive extensions being presented
            # as synonyms of single-word glosses (e.g. "hand by hand").
            if len(seed_phrase.split())==1 and len(phrase.split())>2:continue
            entry_pos=set(entry.get('pos') or [])
            if seed_pos and entry_pos and not (seed_pos & entry_pos):continue
            overlap=len(seed_tokens & tokens)/len(seed_tokens | tokens)
            # A one-word gloss cannot match a longer phrase merely by sharing
            # that word. Compare the complete head-gloss phrase as well.
            phrase_match=SequenceMatcher(None,seed_phrase,phrase).ratio()
            score=min(overlap,phrase_match)
            if score>best:best=score;best_seed=sid
        if best>=threshold:
            results.append((best,id_,entry,best_seed))
    results.sort(key=lambda r:(-r[0],r[1]))
    return [{'id':id_,'type':'synonym','basis':'Unverified suggestion from dictionary meaning similarity',
             'meaning':entry.get('meaning') or '', 'score':round(score,3),'similar_to':seed}
            for score,id_,entry,seed in results[:maximum]]


def inspect_text_id(con,text_id,project=None,resolve_lemma=None):
    """Display teacher's Oracc line annotations PLUS dictionary-evidenced chains."""
    text_id=str(text_id or '').strip().upper()
    if not re.fullmatch(r'[PQX]\d{6}',text_id):
        raise ValueError('Enter a valid Oracc text ID, such as Q005719 or X600005.')
    rows=con.execute("SELECT project,COUNT(*) AS n FROM lines WHERE source='oracc' AND text=? GROUP BY project ORDER BY project",(text_id,)).fetchall()
    projects=[{'project':row['project'],'lines':row['n']} for row in rows]
    if not projects:
        return {'text_id':text_id,'projects':[],'lines':[], 'statistics':{},'error':'This Text ID is not present in the local Oracc data.'}
    if project is None or project=='':
        if len(projects)>1:return {'text_id':text_id,'projects':projects,'selection_required':True,'lines':[]}
        project=projects[0]['project']
    if project not in [p['project'] for p in projects]:
        raise ValueError('The chosen source project does not contain this Text ID.')
    result=[]; counts=Counter(); cache={}
    for row in con.execute("SELECT label,words FROM lines WHERE source='oracc' AND text=? AND project=? ORDER BY id",(text_id,project)):
        words=[]
        for word in json.loads(row['words']):
            status=word.get('zuordnung') or 'not annotated'
            counts[status]+=1
            analysis=word.get('oracc') or ''
            if analysis not in cache:
                try:cache[analysis]=resolve_lemma(analysis) if analysis and resolve_lemma else []
                except (ValueError,KeyError,TypeError):cache[analysis]=[]
            entries={entry['id']:dict(entry) for entry in cache[analysis]}
            # Keep every mapping from the instructor's snapshot as evidence,
            # but don't pretend an unverified snapshot ID has Type 1 evidence.
            for id_ in word.get('lemma') or []:
                if id_ not in entries:
                    entries[id_]={'id':id_,'type':None,'basis':'Local data correspondence',
                                  'route':'','origin':'snapshot'}
            matches=sorted(entries.values(),key=lambda x:(x.get('type') is None,x.get('type') or 99,x['id']))
            words.append({'form':word.get('wert') or '', 'oracc':analysis,
                         'ebl':[e['id'] for e in matches], 'matches':matches,
                         'snapshot_ebl':word.get('lemma') or [],'status':status})
        result.append({'line':row['label'],'words':words})
    return {'text_id':text_id,'project':project,'projects':projects,'lines':result,
            'statistics':dict(counts),'total_lines':len(result),'total_tokens':sum(counts.values()),
            'note':'Counts describe the local Oracc data.'}

# One public eBL endpoint family is documented, but the response schema can change.
# Fail closed rather than fabricating KWIC rows or treating a network error as absence.
class LiveEBL:
    def __init__(self,base='https://www.ebl.lmu.de/api',timeout=7):
        self.base=base.rstrip('/');self.timeout=timeout

    def dictionary_lookup(self,lemma):
        if not isinstance(lemma,str) or len(lemma)>100:return []
        url=self.base+'/words?'+urlencode({'lemma':lemma})
        request=Request(url,headers={'Accept':'application/json','User-Agent':'Oracc-eBL-course-project/0.4'})
        with urlopen(request,timeout=self.timeout) as r:
            if r.status!=200:raise ValueError('eBL response not successful')
            raw=r.read(2_000_001)
            if len(raw)>2_000_000:raise ValueError('eBL response too large')
        obj=json.loads(raw)
        if isinstance(obj,list):values=obj
        elif isinstance(obj,dict):
            if obj.get('_id') or obj.get('id'):values=[obj]
            else:values=next((obj[k] for k in ('words','results','items','data') if isinstance(obj.get(k),list)),[])
        else:values=[]
        return [x for x in values if isinstance(x,dict) and (x.get('_id') or x.get('id'))][:30]
