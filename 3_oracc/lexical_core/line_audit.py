"""Count distinct line references, preserving primes, columns, gaps and duplicates."""
from collections import Counter, defaultdict
import re


def surface_name(line) -> str:
    value = (line.surface or "").casefold()
    label = line.label.casefold().strip()
    if value in {"obverse", "o", "obv", "obv."} or re.match(r"^(?:o|obv\.?)\s*\d", label):
        return "Obverse"
    if value in {"reverse", "r", "rev", "rev.", "verso"} or re.match(r"^(?:r|rev\.?|v)\s*\d", label):
        return "Reverse"
    if "edge" in value or re.match(r"^(?:l\.e\.|r\.e\.|t\.e\.|b\.e\.)", label):
        return "Edge"
    return line.surface or "Surface unspecified"


def number_group(label: str) -> str:
    match = re.search(r"\d+([\u2032\u2033\u2034'’]*)", label)
    if not match:
        return "Numbering group unspecified"
    suffix = match[1].replace("′", "'").replace("’", "'").replace("″", "''").replace("‴", "'''")
    return {"": "Unprimed", "'": "Single prime", "''": "Double prime", "'''": "Triple prime"}.get(suffix, suffix + " group")


def summarize_lines(lines) -> dict:
    rows, by_surface, groups = [], Counter(), defaultdict(list)
    readable, unidentified, gap_only, repeated = 0, 0, 0, 0
    seen = set()
    for order, line in enumerate(lines, 1):
        word_count = sum(not token.is_gap for token in line.tokens)
        labelled = bool(re.search(r"\d", line.label)) and line.label != "Unlabelled"
        identity = (line.document, line.ref) if line.ref else (line.document, line.surface, line.column, line.label)
        group_name = (line.column + " column · " if line.column else "") + number_group(line.label)
        duplicate = bool(word_count and labelled and identity in seen)
        counted = bool(word_count and labelled and not duplicate)
        if counted:
            readable += 1
            seen.add(identity)
            by_surface[surface_name(line)] += 1
            groups[(surface_name(line), group_name)].append(line.label)
        elif duplicate:
            repeated += 1
        elif word_count:
            unidentified += 1
        else:
            gap_only += 1
        reason = ("Counted: readable words and a line label" if counted else "Separate: duplicate saved group for the same line" if duplicate else
                  "Separate: no explicit line label" if word_count else "Separate: empty or gap-only segment")
        rows.append({"order": order, "ref": line.ref, "label": line.label,
                     "surface": surface_name(line), "column": line.column, "number_group": group_name,
                     "section": line.section, "words": word_count, "counted": counted,
                     "reason": reason, "text": line.text, "notes": line.notes})
    events = getattr(lines, "parse_events", [])
    starts = [event for event in events if event.get("kind") == "line-start"]
    return {"readable_labelled_lines": readable, "unlabelled_segments": unidentified,
            "gap_or_empty_segments": gap_only, "parsed_groups": len(lines),
            "repeated_saved_groups": repeated,
            "line_start_events_in_file": len(starts) if events else None,
            "duplicate_line_markers_in_file": sum(bool(event.get("duplicate")) for event in starts),
            "duplicate_word_markers_in_file": sum(event.get("kind") == "duplicate-word" for event in events),
            "by_surface": dict(by_surface),
            "number_groups": [{"surface": surface, "group": group, "count": len(labels), "labels": labels}
                              for (surface, group), labels in groups.items()], "rows": rows,
            "structural_notes": [event for event in events if event.get("kind") == "structure-note"]}
