"""Conservative Oracc→eBL dictionary lookup with upward-only etymology tracing.

Types describe routes, never linguistic certainty:
  1. Oracc citation form agrees with the eBL main lemma: show the entry, stop.
  2. Oracc form maps to an eBL alternative form / explicit Oracc cross-reference;
     inspect its derivedFrom reference. Stop if it names an independent entry.
  3. An upward derivedFrom reference needs alternative-form resolution (or an
     additional upward step). Continue only through such recovered entries.

Derivatives are DISPLAYED, never traversed. A reference whose target cannot be
opened as an independent eBL entry is noted even if alternative-form resolution
succeeds. The direct dictionary mapping is never overwritten by the traced root.
"""
from __future__ import annotations
from collections import Counter
from common import clean
from ebl_dictionary import nested_references, reference_id

MAX_UPWARD_STEPS = 8  # safety limit, not a claim about linguistic genealogy


def lemma_spelling(value):
    if isinstance(value, dict):
        value = value.get('lemma') or []
    if isinstance(value, str):
        return clean(value)
    return clean(' '.join(value or []))


def forms_of(entry):
    values = []
    for form in entry.get('forms') or []:
        spelling = lemma_spelling(form)
        if spelling and spelling not in values:
            values.append(spelling)
    return values


class LemmaTracer:
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self._traces = {}
        self._classifications = {}

    def entry_summary(self, lemma_id):
        e = self.dictionary.entries[lemma_id]
        return {'id': lemma_id, 'main_lemma': lemma_spelling(e),
                'guide_word': e.get('guideWord') or '', 'meaning': e.get('meaning') or '',
                'forms': forms_of(e),
                'derived': list(dict.fromkeys(reference_id(ref) for ref in nested_references(e.get('derived')))),
                'derivedFrom': list(dict.fromkeys(reference_id(ref) for ref in nested_references(e.get('derivedFrom'))))}

    def main_only(self, lemma_id):
        entry = self.entry_summary(lemma_id)
        return {'entry': entry, 'entries': [entry], 'paths': [],
                'final_entries': [lemma_id], 'link_notes': []}

    def trace_up(self, lemma_id):
        """Follow derivedFrom upward; resolve broken direct IDs as other forms.

        An independent derivedFrom entry is a terminal point of THIS search,
        as requested. If it resolves only via forms, inspect that recovered
        entry's own derivedFrom; never traverse `derived` or reverse links.
        All branches and spelling evidence are retained when lookup is ambiguous.
        """
        if lemma_id in self._traces:
            return self._traces[lemma_id]
        issues, paths, touched = {}, [], {lemma_id}

        def save_path(current, steps, reason):
            paths.append({'steps': steps, 'final': current, 'stop_reason': reason})

        def walk(current, steps, seen):
            if len(steps) >= MAX_UPWARD_STEPS:
                save_path(current, steps, 'safety depth limit')
                return
            entry = self.dictionary.entries[current]
            refs = list(nested_references(entry.get('derivedFrom')))
            if not refs:
                save_path(current, steps, 'no further derivedFrom')
                return
            for ref in refs:
                name = reference_id(ref)
                direct = name in self.dictionary.entries
                targets, _ = self.dictionary.resolve(ref)
                if not direct:
                    issues[(current, 'derivedFrom', name)] = {
                        'from': current, 'field': 'derivedFrom', 'reference': name,
                        'resolved_to': targets, 'kind': 'no_independent_entry'}
                if not targets:
                    save_path(current, steps + [{
                        'from': current, 'field': 'derivedFrom', 'reference': name,
                        'resolution': 'unresolved', 'to': None}], 'unresolved reference')
                    continue
                for target in targets:
                    touched.add(target)
                    edge = {'from': current, 'field': 'derivedFrom', 'reference': name,
                            'resolution': 'independent entry' if direct else 'other form',
                            'to': target}
                    new_steps = steps + [edge]
                    if target in seen:
                        save_path(current, new_steps, 'cycle detected')
                    elif direct:
                        # An already-independent base word ends this upward path.
                        save_path(target, new_steps, 'independent base entry')
                    else:
                        walk(target, new_steps, seen | {target})

        walk(lemma_id, [], {lemma_id})
        # Normalize duplicate paths (some dictionaries repeat references).
        unique_paths = {}
        for p in paths:
            fingerprint = (p['final'], p['stop_reason'], tuple(
                (s['from'], s['reference'], s['resolution'], s['to']) for s in p['steps']))
            unique_paths[fingerprint] = p
        paths = list(unique_paths.values())
        result = {'entry': self.entry_summary(lemma_id),
                  'entries': [self.entry_summary(name) for name in sorted(touched)],
                  'paths': paths,
                  'final_entries': sorted({p['final'] for p in paths}),
                  'link_notes': list(issues.values())}
        self._traces[lemma_id] = result
        return result

    def classify(self, lemma_id, cf):
        key = (lemma_id, clean(cf))
        if key in self._classifications:
            return self._classifications[key]
        e = self.dictionary.entries[lemma_id]
        if clean(cf) == lemma_spelling(e):
            level, basis = 1, 'main lemma'
            trace = self.main_only(lemma_id)
        else:
            level = 2
            basis = 'other form' if clean(cf) in forms_of(e) else 'Oracc correspondence (not a listed other form)'
            trace = self.trace_up(lemma_id)
            # A second lookup layer arises when a base-word link must be
            # resolved through Other forms, or any path contains >= 2 hops.
            if any(len(p['steps']) >= 2 or any(
                    s['resolution'] == 'other form' for s in p['steps']) for p in trace['paths']):
                level = 3
        result = {'level': level, 'basis': basis, 'main_entry': lemma_id,
                  'final_entries': trace['final_entries'], 'trace': trace}
        self._classifications[key] = result
        return result

    def process(self, lines):
        cases = {}
        conflicts = {}
        tiers = Counter({'level_1': 0, 'level_2': 0, 'level_3': 0})
        unique_types = set()
        for line in lines:
            for token in line.tokens:
                if token.is_gap or not token.lemmas:
                    continue
                results = []
                token.correspondence_conflicts = []
                for analysis in token.analyses:
                    cf, gw = clean(analysis.get('cf')), clean(analysis.get('gw')).casefold()
                    key = (cf, gw)
                    by_oracc = set(self.dictionary.reverse.get(key, ()))
                    by_forms = set(self.dictionary.spelling_reverse.get(key, ()))
                    # A missing Other forms record is not a conflict.
                    # A conflict requires two distinct, nonempty candidate sets.
                    if by_oracc and by_forms and by_oracc.isdisjoint(by_forms):
                        issue = {'cf': cf, 'guide_word': clean(analysis.get('gw')),
                                 'oracc_correspondence': sorted(by_oracc),
                                 'form_match': sorted(by_forms)}
                        conflicts[key] = issue
                        if issue not in token.correspondence_conflicts:
                            token.correspondence_conflicts.append(issue)
                for lemma_id in token.lemmas:
                    for a in token.analyses:
                        if lemma_id in self.dictionary.reverse.get((clean(a.get('cf')), clean(a.get('gw')).casefold()), ()) or lemma_id in self.dictionary.spelling_reverse.get((clean(a.get('cf')), clean(a.get('gw')).casefold()), ()):
                            cf = clean(a.get('cf'))
                            case = self.classify(lemma_id, cf)
                            cases[(lemma_id, cf)] = case
                            results.append({'id': lemma_id, 'cf': cf, 'level': case['level'],
                                            'basis': case['basis'], 'final_entries': case['final_entries']})
                token.mapping_types = sorted({(r['id'], r['cf'], r['level'], r['basis']) for r in results})
                token.traced_entries = sorted({name for r in results for name in r['final_entries']})
                if results:
                    tiers[f"level_{max(r['level'] for r in results)}"] += 1
                    unique_types.update((clean(a.get('cf')), clean(a.get('gw')).casefold()) for a in token.analyses)
        issues = {(n['from'], n['field'], n['reference']): n
                  for case in cases.values() for n in case['trace']['link_notes']}
        return {'cases': cases, 'type_counts': dict(tiers),
                'distinct_oracc_types': len(unique_types), 'link_notes': list(issues.values()),
                'correspondence_conflicts': list(conflicts.values())}
