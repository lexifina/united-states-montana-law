"""Parse dated historical MCA titles from retained official section pages.

Usage: python parse_historical_titles.py --source <edition-page-folder>
       --manifest <source-response-manifest> --dates <date-evidence.json> --out <json>
Only title editions with explicit reviewed date evidence are included.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import lxml.html

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import parse_mca


def parse(source, manifest, dates):
    versions = {}
    for key, proof in sorted(dates.items()):
        rec = manifest[key]
        ed, title = rec['edition'], rec['title']
        if rec['errors']:
            raise ValueError(f'{key}: collection errors')
        units = {}
        digest = hashlib.sha256()
        prefix = f'https://mca.legmt.gov/bills/{ed}/mca/'
        for url, retained in sorted(rec['sections'].items()):
            path = source / ed / url.removeprefix(prefix)
            with gzip.open(str(path) + '.gz', 'rb') as f:
                raw = f.read()
            if hashlib.sha256(raw).hexdigest() != retained['sha256']:
                raise ValueError('source hash mismatch: ' + url)
            if retained['images'] or retained['effective_clauses']:
                raise ValueError('image or dated alternate form needs separate handling: ' + url)
            doc = lxml.html.fromstring(raw)
            nodes = doc.xpath('//div[@class="section-content"]')
            if len(nodes) != 1:
                raise ValueError('expected exactly one statutory form: ' + url)
            stem = path.stem
            unit = parse_mca.unit_of(doc, raw.decode('utf-8'), nodes, [0], stem, False)
            if not unit:
                raise ValueError('empty section: ' + url)
            unit_key = 'sec-' + parse_mca.pad(stem.lower())
            if unit_key in units:
                raise ValueError('duplicate section: ' + unit_key)
            units[unit_key] = unit
            digest.update(stem.encode() + b'\0' + hashlib.sha256(raw).digest())
        versions.setdefault(str(title), []).append({'from': proof['from'], 'source_url': prefix +
            f'title_{title * 10:04d}/chapters_index.html', 'sha256': digest.hexdigest(),
            'units': units, 'credits': {}, 'in_force_basis': proof['in_force_basis'],
            'note': proof['note'], 'correction': {'reason': 'Historical official MCA edition found after publication',
                'in_force_basis': proof['in_force_basis']}})
    for vs in versions.values():
        vs.sort(key=lambda v: v['from'])
    return versions


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'manifest', 'dates', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    a = ap.parse_args()
    result = parse(a.source, json.loads(a.manifest.read_text(encoding='utf-8')),
                   json.loads(a.dates.read_text(encoding='utf-8')))
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('titles', len(result), 'versions', sum(len(vs) for vs in result.values()),
          'sections', sum(len(v['units']) for vs in result.values() for v in vs))


if __name__ == '__main__':
    main()
