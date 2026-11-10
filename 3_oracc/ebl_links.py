"""eBL deep links from actual public route patterns (never homepage substitutes).

Route ownership: ebl-frontend/src/router/fragmentariumRoutes.tsx and
corpusRoutes.tsx.  A link is shown only when enough identifier information exists.
"""
from __future__ import annotations

import re
from urllib.parse import quote

BASE = 'https://www.ebl.lmu.de'

_STAGES = {
    'Standard Babylonian': 'SB', 'Old Babylonian': 'OB',
    'Middle Babylonian': 'MB', 'Middle Assyrian': 'MA',
    'Neo-Assyrian': 'NA', 'Neo-Babylonian': 'NB',
    'Late Babylonian': 'LB', 'Persian': 'Per',
    'Hellenistic': 'Hel', 'Parthian': 'Par',
}


def fragment_url(number: str) -> str:
    """Link to a known museum tablet, never to an undifferentiated library page."""
    number = str(number or '').strip()
    # A corpus witness marker (1), (2a), etc. is NOT part of the museum number.
    number = re.sub(r'\s+\([^()]{1,24}\)$', '', number, flags=re.I)
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9.\- ]{1,65}', number):
        return ''
    if not re.search(r'\d', number):
        return ''
    return BASE + '/library/' + quote(number, safe='.')


def corpus_url(identity: str) -> str:
    """Only short, unambiguous chapter IDs; never link to Corpus home as a 'hit'."""
    value=str(identity or '').strip()
    m = re.fullmatch(r'([A-Za-z])\s+(\d+)\.(\d+)\s+(.+?)\s+(\S+)', value)
    if not m:
        # Some exported course IDs contain extra .0 metadata fields, e.g.
        # Erra 'L 1.0.5.0 Standard Babylonian I'. The known pattern may
        # safely be reduced to Corpus category / index.
        m2=re.fullmatch(r'([A-Za-z])\s+(\d+)\.0\.(\d+)\.0\s+(.+?)\s+(\S+)', value)
        if not m2:return ''
        genre,category,index,period,chapter=m2.groups()
    else:
        genre,category,index,period,chapter=m.groups()
    stage = _STAGES.get(period, period if period in _STAGES.values() else '')
    if not stage:
        return ''
    return BASE + '/corpus/' + '/'.join(quote(p, safe='') for p in (genre, category, index, stage, chapter))
