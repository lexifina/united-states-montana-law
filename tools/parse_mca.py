"""Montana, 2026-11-10: every title of the Montana Code Annotated, 2023 and 2025 editions, from saved copies of the
official pages: $MT_SOURCE_CACHE/<edition>/<path below /bills/mca/ (2025) or /bills/2023/mca/ (2023)>.gz, gzipped
HTML, one file per page. Reads saved pages only; deterministic.

    python -X utf8 parse_mca.py [--titles title_0010,...] [--out corpus.json]

Dates (decisions, printed in REPRODUCE.md):
- Each edition holds the law as enacted through that year's regular session. MCA 1-2-201(1): a law takes effect on the
  first day of October following its passage and approval unless it prescribes another time. So the 2023 edition's
  version is dated 2023-10-01 and the 2025 edition's 2025-10-01 (the 2025 edition's page says "Updated August 2026";
  it gives no day). Laws that took effect earlier in the year are dated October 1 (later than they took effect, never
  earlier).
- A section the edition prints in two forms, with an effective clause in the catchline ("(Temporary -- effective until
  June 30, 2027)" / "(Effective July 1, 2027)"), is read as of each day: the edition's version takes the form in
  force on its day, and the act gets a further version on each later day a printed form takes effect, up to the next
  edition's day. Forms "effective on occurrence of contingency" are left out while another form exists (the code does
  not say whether the contingency occurred); a section printed only in a contingent form is left out.
- The 2021 edition is not on the host (404), and the 2017 and 2019 editions would leave October 2021 to October 2023
  without text, so history starts with the 2023 edition.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lxml.html  # noqa: E402
from text_preserving import clean, blocks, add_unit, write  # noqa: E402

CACHE = os.environ.get('MT_SOURCE_CACHE') or os.path.join(HERE, 'source')
EDITIONS = [('2023', '2023-10-01', 'https://mca.legmt.gov/bills/2023/mca/'),
            ('2025', '2025-10-01', 'https://mca.legmt.gov/bills/mca/')]
DATE = r'([A-Z][a-z]+\s+\d{1,2},\s*\d{4})'


def read(p):
    with gzip.open(p, 'rb') as g:
        return g.read()


def pad(s):
    return re.sub(r'\d+', lambda m: m.group().zfill(4), s)


def section_files(ed, tdir):
    out = []
    for root, _, files in os.walk(os.path.join(CACHE, ed, tdir)):
        for f in files:
            if re.match(r'^\d{4}-\w+-\w+-\w+\.html\.gz$', f):
                out.append(os.path.join(root, f))
    return sorted(out)


def catch_of(node):
    c = node.xpath('.//span[contains(concat(" ", normalize-space(@class), " "), " catchline ")]')
    return c[0] if c else None


def effective_of(node):
    """('none'|'from'|'until'|'contingent'|'other', date or None, label)"""
    c = catch_of(node)
    if c is None:
        return 'none', None, ''
    labels = c.xpath('.//span[contains(concat(" ", normalize-space(@class), " "), " effective-clause ")]')
    lab = ' '.join(re.sub(r'\s+', ' ', x.text_content()).strip() for x in labels)
    if not re.search(r'\beffective\b', lab, re.I):
        return 'none', None, lab
    if re.search(r'contingen', lab, re.I):
        return 'contingent', None, lab
    m = re.search(r'effective\s+until\s+' + DATE, lab, re.I)
    if m:
        return 'until', dt.datetime.strptime(re.sub(r'\s+', ' ', m[1]), '%B %d, %Y').date().isoformat(), lab
    m = re.search(r'\beffective\s+(?:on\s+)?' + DATE, lab, re.I)
    if m:
        return 'from', dt.datetime.strptime(re.sub(r'\s+', ' ', m[1]), '%B %d, %Y').date().isoformat(), lab
    return 'other', None, lab


def pick(nodes, day):
    """Indexes of the source blocks in force on `day`, or None (no form in force / undecidable)."""
    forms, cont = [], []
    for i, n in enumerate(nodes):
        if catch_of(n) is None:
            cont.append(i)
            continue
        kind, d, lab = effective_of(n)
        forms.append((i, kind, d))
    if not forms:
        return cont or None
    live = [f for f in forms if f[1] != 'contingent']
    if not live:
        return None
    if len(live) == 1:
        i, kind, d = live[0]
        if kind == 'from' and d > day:
            return None
        if kind == 'until' and d <= day:
            return None
        return [i] + cont
    dated_from = [f for f in live if f[1] == 'from' and f[2] <= day]
    if dated_from:
        best = max(f[2] for f in dated_from)
        m = [f for f in dated_from if f[2] == best]
        return [m[0][0]] + cont if len(m) == 1 else None
    rest = [f for f in live if (f[1] == 'until' and f[2] > day) or f[1] == 'none']
    if len(rest) == 1:
        return [rest[0][0]] + cont
    return None


def edition_days(nodes_by_file):
    days = set()
    for nodes in nodes_by_file.values():
        if len(nodes) < 2:
            continue
        for n in nodes:
            kind, d, _ = effective_of(n)
            if kind in ('from', 'until') and d:
                days.add(d)
    return days


def unit_of(doc, html, nodes, idx, fname, constitution):
    section = nodes[idx[0]]
    catches = section.xpath('.//span[@class="catchline"]')
    catch = clean(lxml.html.tostring(catches[0], encoding='unicode', with_tail=False)) if catches else None
    if catches:
        catches[0].drop_tree()
    paras = blocks(section)
    for i in idx[1:]:
        paras.extend(blocks(nodes[i]))
    if not catch and not paras:
        return None
    if catch and paras:
        pm = re.match(r'^([.,;:!?]+)(.*)$', paras[0], re.S)
        if pm:
            catch += pm[1]
            paras[0] = pm[2].strip()
            paras = [x for x in paras if x]
    hist = [line for node in doc.xpath('//div[@class="history-content"]') for line in blocks(node)]
    if constitution:
        art = re.search(r'<li><a href="\.\./\.\./parts_index\.html"[^>]*>(.*?)</a>', html)
        artname = re.sub(r'^ARTICLE\s+', 'Art. ', clean(art.group(1)) if art else '')
        sec = re.match(r'^Section\s+(\S+?)\.\s*(.*)$', catch or '')
        if sec:
            heading, label = f'# {artname}, Sec. {sec.group(1)}. {sec.group(2)}'.rstrip(), f'{artname}, Sec. {sec.group(1)}'
        else:
            heading, label = '# ' + (catch or artname or fname), catch or artname or fname
    else:
        heading = '# ' + (catch or (paras.pop(0) if paras else fname))
        cm = re.match(r'^(\d+-\d+-\d+[A-Za-z]?)', heading[2:])
        label = cm.group(1) if cm else heading[2:60]
    return {'label': label, 'kind': 'section', 'text': '\n'.join([heading] + paras + hist) + '\n'}


def title_versions(tdir, stats):
    constitution = tdir == 'title_0000'
    vers = []
    for k, (ed, start, base) in enumerate(EDITIONS):
        end = EDITIONS[k + 1][1] if k + 1 < len(EDITIONS) else '9999-12-31'
        files = section_files(ed, tdir)
        if not files:
            continue
        h = hashlib.sha256()
        pages = {}
        for p in files:
            raw = read(p)
            h.update(os.path.basename(p).encode() + b'\0' + hashlib.sha256(raw).digest())
            html = raw.decode('utf-8', 'replace')
            pages[p] = html
        nodes_by = {p: lxml.html.fromstring(html).xpath('//div[@class="section-content"]') for p, html in pages.items()}
        days = [start] + sorted(d for d in edition_days(nodes_by) if start < d < end)
        for day in days:
            units = {}
            for p in files:
                doc = lxml.html.fromstring(pages[p])
                nodes = doc.xpath('//div[@class="section-content"]')
                if not nodes:
                    continue
                idx = pick(nodes, day)
                if idx is None:
                    if day == start:
                        stats.setdefault('left_out', []).append(f'{ed} {os.path.basename(p)[:-8]}')
                    continue
                fname = os.path.basename(p)[:-8]
                u = unit_of(doc, pages[p], nodes, idx, fname, constitution)
                if u:
                    add_unit(units, 'sec-' + pad(fname.lower()), u)
            note = (f'Montana Code Annotated {ed}' + (' (page header: "Updated August 2026")' if ed == '2025' else '')
                    + (', as in force on its general effective day, 1 October (MCA 1-2-201).' if day == start else
                       f', with the forms the edition prints as taking effect on {day}.'))
            vers.append({'from': day, 'source_url': base + tdir + '/chapters_index.html', 'sha256': h.hexdigest(),
                         'units': units, 'credits': {}, 'note': note})
    # drop a later version identical to the one before it
    out = []
    for v in vers:
        if out and out[-1]['units'] == v['units']:
            continue
        out.append(v)
    return out


def title_names():
    p = os.path.join(CACHE, '2025', 'index.html.gz')
    h = read(p).decode('utf-8', 'replace')
    return {t: clean(n) for t, n in re.findall(r'href="\./(title_\d{4})/chapters_index\.html">(.*?)</a>', h, re.S)}


def slug_of(tdir, names):
    tn = int(tdir[6:]) // 10
    nm = re.sub(r'^TITLE\s+\d+\.\s*', '', names.get(tdir, '')).strip()
    nm = nm.title().replace(' And ', ' and ').replace(' Of ', ' of ').replace(' The ', ' the ').replace(' For ', ' for ').replace(' In ', ' in ') if nm else ''
    slug = f'title-{tn}' + ('-' + re.sub(r'[^a-z0-9]+', '-', nm.lower()).strip('-')[:40].strip('-') if nm else '')
    return tn, nm, slug


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--titles', default='')
    ap.add_argument('--out', default=os.path.join(HERE, 'corpus.mca.json'))
    a = ap.parse_args()
    names = title_names()
    done = {ed: json.load(open(os.path.join(CACHE, ed, 'done.json'))) for ed, _, _ in EDITIONS}
    tdirs = sorted(t for t in names if all(t in done[ed] for ed, _, _ in EDITIONS))
    if a.titles:
        tdirs = [t for t in tdirs if t in a.titles.split(',')]
    acts, stats = [], {}
    for t in tdirs:
        vers = title_versions(t, stats)
        if not vers:
            print('EMPTY', t, flush=True)
            continue
        if t == 'title_0000':
            slug, short, title = 'constitution', 'Mont. Const.', 'Constitution of the State of Montana'
        else:
            tn, nm, slug = slug_of(t, names)
            short, title = f'MCA {tn}', f'Montana Code Annotated, Title {tn}' + (f': {nm}' if nm else '')
        acts.append({'slug': slug, 'short': short, 'title': title, 'url': f'https://mca.legmt.gov/bills/mca/{t}/chapters_index.html',
                     'first_law': None, 'earlier_laws': [], 'versions': vers})
        print(t, slug, [(v['from'], len(v['units'])) for v in vers], flush=True)
    write(a.out, {'acts': acts, 'left_out': stats.get('left_out', [])})
    print('acts', len(acts), 'left out', len(stats.get('left_out', [])))


if __name__ == '__main__':
    main()
