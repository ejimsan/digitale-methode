"""Map Oracc lemma pairs and traverse evidenced dictionary word-family links."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path

from common import clean, read_json_records
from line_audit import summarize_lines


def reference_id(reference: dict) -> str:
    lemma = reference.get("lemma") or []
    if isinstance(lemma, str):
        lemma = [lemma]
    return clean(" ".join(lemma) + " " + str(reference.get("homonym") or ""))


def nested_references(value):
    """Recursively read lemma references from nested derived lists."""
    if isinstance(value, dict) and value.get("lemma"):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from nested_references(item)


class Dictionary:
    def __init__(self, entries: list[dict], coverage="provided", source=""):
        if not entries or any(not isinstance(x, dict) or not x.get("_id") for x in entries):
            raise ValueError("Dictionary entries need nonempty _id values. Supply an eBL API array or JSONL.")
        self.entries = {clean(entry["_id"]): entry for entry in entries}
        if len(self.entries) != len(entries):
            raise ValueError("The dictionary contains duplicate _id values.")
        self.coverage = coverage
        self.source = source
        self.reverse: dict[tuple[str, str], set[str]] = defaultdict(set)
        # Conservative secondary lookup: only the same spelling AND guide word.
        # Unlike a fuzzy lookup, this cannot silently equate unrelated homonyms.
        self.spelling_reverse: dict[tuple[str, str], set[str]] = defaultdict(set)
        self.aliases: dict[str, set[str]] = defaultdict(set)
        self.graph: dict[str, list[dict]] = defaultdict(list)
        self.unresolved: list[dict] = []
        self.logograms: dict[str, set[str]] = defaultdict(set)
        for lemma_id, entry in self.entries.items():
            for record in entry.get("logograms") or []:
                for logogram in record.get("logogram") or []:
                    self.logograms[clean(logogram)].add(lemma_id)
            self.aliases[lemma_id].add(lemma_id)
            entry_guide = clean(entry.get('guideWord', '')).casefold()
            for form in [entry, *(entry.get("forms") or [])]:
                # Some legacy forms are strings, as observed in the real Erua I entry.
                if isinstance(form, str):
                    form = {"lemma": [form]}
                if not isinstance(form, dict):
                    raise ValueError(f"Entry {lemma_id} contains an unreadable forms value.")
                # Forms may omit homonym; inherit it from the main entry.
                alias = dict(form, homonym=form.get("homonym") or entry.get("homonym") or "")
                self.aliases[reference_id(alias)].add(lemma_id)
                raw_form = form.get('lemma') or []
                spelling = clean(raw_form if isinstance(raw_form, str) else ' '.join(raw_form))
                if spelling and entry_guide:
                    self.spelling_reverse[(spelling, entry_guide)].add(lemma_id)
            for oracc_word in entry.get("oraccWords") or []:
                cf = clean(oracc_word.get("lemma", ""))
                gw = clean(oracc_word.get("guideWord", "")).casefold()
                if cf and gw:
                    self.reverse[(cf, gw)].add(lemma_id)
        self._build_families()

    def resolve(self, reference: dict) -> tuple[list[str], str]:
        name = reference_id(reference)
        if name in self.entries:
            return [name], "entry ID"
        candidates = sorted(self.aliases.get(name, set()))
        return candidates, "dictionary-listed form" if candidates else "unresolved reference"

    def _build_families(self):
        for source_id, entry in self.entries.items():
            for field, relation in [("derivedFrom", "base word"), ("derived", "derivative")]:
                for reference in nested_references(entry.get(field)):
                    targets, resolution = self.resolve(reference)
                    evidence = {"field": field, "reference": reference_id(reference),
                                "resolution": resolution, "ambiguous_reference": len(targets) > 1}
                    if not targets:
                        self.unresolved.append({"from": source_id, **evidence})
                    for target_id in targets:
                        if target_id == source_id:
                            continue
                        self.graph[source_id].append({"to": target_id, "relation": relation,
                                                      "weight": 0.7 if field == "derivedFrom" else 0.55,
                                                      "from": source_id, **evidence})
                        # Allow reverse traversal while retaining the entry that records the relationship.
                        self.graph[target_id].append({"from": target_id, "to": source_id,
                            "relation": "reverse: " + relation, "weight": 0.55,
                            "evidence_from": source_id, **evidence})

    def candidates_for(self, cf: str, gw: str) -> list[str]:
        """Return candidates, using explicit Oracc evidence to resolve homonyms.

        When multiple eBL MAIN entries have the same exact spelling and guide
        word, prefer the entry (or entries) with explicit cf+gw oraccWords.
        Other-form matches are retained, even if they disagree, so genuine
        dictionary correspondence conflicts remain visible for review.
        """
        key = (clean(cf), clean(gw).casefold())
        explicit = set(self.reverse.get(key, ()))
        spellings = set(self.spelling_reverse.get(key, ()))
        exact_main = {name for name in spellings
                      if clean(self.entries[name].get('lemma') if isinstance(self.entries[name].get('lemma'), str)
                               else ' '.join(self.entries[name].get('lemma') or [])) == key[0]}
        confirmed = exact_main & explicit
        if len(exact_main) > 1 and confirmed:
            # A matching cf+gw cross-reference resolves the same-spelling
            # homonym competition, without hiding other-form disagreements.
            spellings -= exact_main - confirmed
        return sorted(explicit | spellings)

    def direct(self, analyses: list[dict]) -> list[str]:
        found = set()
        for analysis in analyses:
            found.update(self.candidates_for(analysis['cf'], analysis['gw']))
        return sorted(found)

    def family_candidates(self, direct: list[str], max_depth=1) -> dict[str, dict]:
        result: dict[str, dict] = {}
        best: dict[tuple[str, int], float] = {}
        queue = deque((lemma_id, 0, 1.0, [], {lemma_id}) for lemma_id in direct)
        while queue:
            current, depth, weight, path, visited = queue.popleft()
            if depth >= max_depth:
                continue
            for edge in self.graph.get(current, []):
                target = edge["to"]
                if target in visited:
                    continue
                score = round(weight * edge["weight"], 6)
                new_path = [*path, edge]
                if target not in direct and score > result.get(target, {}).get("weight", -1):
                    result[target] = {"weight": score, "path": new_path}
                state = (target, depth + 1)
                if score > best.get(state, -1):
                    best[state] = score
                    queue.append((target, depth + 1, score, new_path, visited | {target}))
        return dict(sorted(result.items(), key=lambda item: (-item[1]["weight"], item[0])))

    def map_lines(self, lines: list[TextLine], family_depth=1) -> dict:
        counts = Counter({"unique": 0, "ambiguous": 0, "unmatched": 0, "unannotated": 0})
        names = Counter()
        for line in lines:
            for token in line.tokens:
                if token.is_gap:
                    token.status = "gap"
                    continue
                direct = self.direct(token.analyses)
                token.lemmas = tuple(direct)
                token.status = ("unannotated" if not token.analyses else
                                "unmatched" if not direct else
                                "unique" if len(direct) == 1 else "ambiguous")
                token.family = self.family_candidates(direct, family_depth)
                counts[token.status] += 1
                if any(a.get("pos") in {"PN", "DN", "GN", "RN", "TN", "SN", "MN", "WN", "EN", "QN", "AN"}
                       for a in token.analyses):
                    names[token.status] += 1
        total = sum(counts.values())
        line_audit = summarize_lines(lines)
        return {"words": total, "counts": dict(counts),
                "three_way_counts": {"unique": counts["unique"], "ambiguous": counts["ambiguous"],
                                     "unassigned": counts["unmatched"] + counts["unannotated"]},
                "percent": {key: round(100 * count / total, 2) if total else 0
                            for key, count in counts.items()},
                "proper_names": dict(names), "dictionary_coverage": self.coverage,
                "dictionary_entries": len(self.entries),
                "lines": line_audit["readable_labelled_lines"], "line_audit": line_audit}


def load_dictionary(path: Path) -> Dictionary:
    """Read the complete lecturer-provided local eBL dictionary."""
    path = Path(path)
    records = list(read_json_records(path))
    if len(records) == 1 and isinstance(records[0], dict) and 'entries' in records[0]:
        wrapper=records[0]
        return Dictionary(wrapper['entries'],wrapper.get('coverage','provided'),str(path))
    return Dictionary(records,'provided',str(path))
