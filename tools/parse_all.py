"""Montana: the Constitution and every title of the Montana Code Annotated 2025, "Updated August 2026".
One act per title, with explicit source-backed version dates and date-aware source-block selection.

    python -X utf8 parse_all.py [N]    # N: only the first N new titles, in title order (publishing in parts)
"""
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse  # noqa: E402

def main():
    # Do not create new writes with the old baseline's unsupported retrieval-day dates.
    as_of = os.environ.get('GITLAW_CHECKED_ON')
    if not as_of:
        raise parse.HeldSource('GITLAW_CHECKED_ON is required')
    date_path = os.environ.get('GITLAW_DATE_PLAN')
    if not date_path:
        raise parse.HeldSource('"Updated August 2026" has month precision; no retrieval-day fallback is permitted')
    # Retain the first build's acts, but read all available source sections with the same preserving reader as other titles.
    # Published corrections are appended by the correction builder; the baseline is never edited here.
    c = json.load(open(os.path.join(HERE, 'corpus-first.json'), encoding='utf-8'))
    plan = parse.require_date_plan(date_path, [a['slug'] for a in c['acts']])
    for act in c['acts']:
        tdir = re.search(r'/(title_\d{4})/', act['url'])[1]
        units, digest = parse.parse_title(tdir, act['slug'] == 'constitution', as_of=as_of)
        v = act['versions'][0]
        missing = set(v['units']) - set(units)
        if missing:
            raise SystemExit(f'{act["slug"]}: source pages missing for {sorted(missing)}')
        v['units'] = units
        v['sha256'] = digest
        v['from'] = plan[act['slug']]['in_force']
    have = {t for t, *_ in parse.ACTS}
    idx = os.path.join(parse.ROOT, 'index.html')
    h = open(idx, 'rb').read().decode('utf-8', 'replace') if os.path.exists(idx) else ''
    names = {t: parse.clean(n) for t, n in re.findall(r'href="\./(title_\d{4})/chapters_index\.html">(.*?)</a>', h, re.S)}
    tdirs = sorted(d for d in os.listdir(parse.ROOT) if re.fullmatch(r'title_\d{4}', d) and d not in have)
    if sys.argv[1:]:
        tdirs = tdirs[:int(sys.argv[1])]
    nsec = 0
    for t in tdirs:
        units, digest = parse.parse_title(t, False, as_of=as_of)
        if not units:
            print('EMPTY', t)
            continue
        tn = int(t[6:]) // 10
        nm = re.sub(r'^TITLE\s+\d+\.\s*', '', names.get(t, '')).strip()
        nm = nm.title().replace(' And ', ' and ').replace(' Of ', ' of ').replace(' The ', ' the ').replace(' For ', ' for ').replace(' In ', ' in ') if nm else ''
        slug = f'title-{tn}' + ('-' + re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')[:40].strip('-') if nm else '')
        date_row = parse.require_date_plan(date_path, [slug])[slug]
        url = f'https://mca.legmt.gov/bills/mca/{t}/chapters_index.html'
        c['acts'].append({'slug': slug, 'short': f'MCA {tn}', 'title': f'Montana Code Annotated, Title {tn}' + (f': {nm}' if nm else ''), 'url': url,
                          'first_law': None, 'earlier_laws': [],
                          'versions': [{'from': date_row['in_force'], 'source_url': url, 'sha256': digest, 'units': units,
                                        'note': 'Montana Code Annotated 2025 (header: updated August 2026), as retrieved; earlier editions are not in this build.'}]})
        nsec += len(units)
        print(t, len(units), nm)
    log = json.load(open(os.path.join(HERE, '.cache', 'fetch-all-log.json')))
    c['sources'].append({'name': 'Montana Code Annotated 2025 (Legislative Services Division), every title', 'url': 'https://mca.legmt.gov/bills/mca/index.html',
                         'retrieved': log['fetched'], 'requests': log['live_requests'], 'licence': c['sources'][0]['licence'],
                         'notes': 'Static HTML, one page per section, retrieved 2026-10-28 (the pages a part index lists that were not then read were fetched on 2026-11-03). mca.legmt.gov has no robots.txt (404, re-read 2026-11-03).'})
    c['decisions'][0] = 'The source labels the edition "Updated August 2026". Every new In-force date requires its own exact source-backed plan; no retrieval-day fallback is used. Source alternatives are selected for the explicit as-of day, and unresolved contingencies hold the act.'
    c['country']['default_in_force_rule']['text'] = 'Version dates require exact source-backed evidence. The month-only edition label is not expanded to an exact day or replaced with retrieval day.'
    c['decisions'].append('Every act date comes from the explicit source-backed date plan. "Updated August 2026" is not silently expanded to an exact day. Dated source alternatives are selected for the supplied as-of date; unresolved source contingencies hold the act.')
    with open(os.path.join(HERE, 'corpus.json'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(c, ensure_ascii=False, indent=1) + '\n')
    print('titles', len(tdirs), 'sections', nsec, 'acts', len(c['acts']))


if __name__ == '__main__':
    main()
