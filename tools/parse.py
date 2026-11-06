"""Read the cached Montana Code Annotated 2025 pages into corpus.json (no network; deterministic).

    python parse.py
Acts: the Constitution (title_0000), Title 35 (corporations), Title 45 (crimes), Title 70 (property). Each act has one
version, the edition as retrieved, credited to the Legislative Services Division as the oldest version available.
Each section is one unit: heading, then one paragraph per line, then the section's History note (the session laws
that enacted and amended it, which is part of the code as published).
"""
import hashlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
from text_preserving import clean, blocks, add_unit, write  # noqa: E402
from source_selection import choose_sections, require_date_plan, HeldSource
import lxml.html

ROOT = os.environ.get('GITLAW_SOURCE_CACHE') or os.path.join(HERE, '.cache', 'mca.legmt.gov', 'bills', 'mca')
ACTS = [('title_0000', 'constitution', 'Constitution of the State of Montana', 'Mont. Const.', None),
        ('title_0350', 'title-35-corporations', 'Montana Code Annotated, Title 35: Corporations, Partnerships, Associations', 'MCA 35', None),
        ('title_0450', 'title-45-crimes', 'Montana Code Annotated, Title 45: Crimes', 'MCA 45', None),
        ('title_0700', 'title-70-property', 'Montana Code Annotated, Title 70: Property', 'MCA 70', None)]
PARA = re.compile(r'<p\b[^>]*>(.*?)</p>', re.S)
CONTENT = re.compile(r'<div class="section-content">(.*?)</div>', re.S)
HIST = re.compile(r'<div class="history-content">(.*?)</div>', re.S)
TITLEH = re.compile(r'<h4 class="section-title-title">\s*(.*?)\s*</h4>', re.S)
ART = re.compile(r'<li><a href="\.\./\.\./chapters_index\.html"[^>]*>(.*?)</a></li>')


def split_catchline(p_html):
    """(catchline text, rest text) for a paragraph that opens with <span class="catchline">...</span>; else (None, text)."""
    m = re.match(r'\s*<span class="catchline">', p_html)
    if not m:
        return None, clean(p_html)
    i, depth, j = m.end(), 1, m.end()
    for t in re.finditer(r'<(/?)span[^>]*>', p_html[m.end():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return clean(p_html[m.end():m.end() + t.start()]), clean(p_html[m.end() + t.end():])
    return None, clean(p_html)


def pad(s):
    return re.sub(r'\d+', lambda m: m.group().zfill(4), s)


def read(p):
    return open(p, 'rb').read()


def sections(tdir):
    out = []
    for root, _, files in os.walk(os.path.join(ROOT, tdir)):
        for f in files:
            if re.match(r'^\d{4}-\w+-\w+-\w+\.html$', f):
                out.append(os.path.join(root, f))
    return sorted(out)


def parse_title(tdir, constitution, *, as_of=None, holds=None, selections=None):
    units, h = {}, hashlib.sha256()
    for p in sections(tdir):
        raw = read(p)
        h.update(os.path.basename(p).encode() + b'\0' + hashlib.sha256(raw).digest())
        html = raw.decode('utf-8', 'replace')
        doc = lxml.html.fromstring(html)
        content = doc.xpath('//div[@class="section-content"]')
        if not content:
            continue
        try:
            indexes, selection = choose_sections(content, as_of or os.environ.get('GITLAW_CHECKED_ON'))
        except HeldSource as exc:
            if holds is None:
                raise HeldSource(os.path.basename(p) + ': ' + str(exc)) from exc
            holds.append({'file': p, 'reason': str(exc)})
            continue
        if selections is not None:
            selections.append({'file': p, **selection})
        section = content[indexes[0]]
        catches = section.xpath('.//span[@class="catchline"]')
        catch = clean(lxml.html.tostring(catches[0], encoding='unicode', with_tail=False)) if catches else None
        if catches:
            catches[0].drop_tree()  # preserves its following text in place
        paras = blocks(section)
        for i in indexes[1:]:
            paras.extend(blocks(content[i]))
        if not catch and not paras:
            continue
        # A few pages put the catchline's closing punctuation just outside its span.
        if catch and paras:
            pm = re.match(r'^([.,;:!?]+)(.*)$', paras[0], re.S)
            if pm:
                catch += pm[1]
                paras[0] = pm[2].strip()
                paras = [x for x in paras if x]
        hist = [line for node in doc.xpath('//div[@class="history-content"]') for line in blocks(node)]
        fname = os.path.basename(p)[:-5]
        if constitution:
            art = re.search(r'<li><a href="\.\./\.\./parts_index\.html"[^>]*>(.*?)</a>', html)
            artname = clean(art.group(1)) if art else ''
            artname = re.sub(r'^ARTICLE\s+', 'Art. ', artname)
            sec = re.match(r'^Section\s+(\S+?)\.\s*(.*)$', catch or '')
            if sec:
                heading = f'# {artname}, Sec. {sec.group(1)}. {sec.group(2)}'.rstrip()
                label = f'{artname}, Sec. {sec.group(1)}'
            else:
                heading = '# ' + (catch or artname or fname)
                label = catch or artname or fname
        else:
            heading = '# ' + (catch or (paras.pop(0) if paras else fname))
            cm = re.match(r'^(\d+-\d+-\d+[A-Za-z]?)', heading[2:])
            label = cm.group(1) if cm else heading[2:60]
        key = 'sec-' + pad(fname.lower())
        add_unit(units, key, {'label': label, 'kind': 'section',
                              'text': '\n'.join([heading] + paras + hist) + '\n'})
    return units, h.hexdigest()


def main():
    plan = require_date_plan(os.environ.get('GITLAW_DATE_PLAN'), [a[1] for a in ACTS])
    as_of = os.environ.get('GITLAW_CHECKED_ON')
    if not as_of:
        raise HeldSource('GITLAW_CHECKED_ON is required; it selects source text, not its In-force date')
    acts = []
    for tdir, slug, title, short, day in ACTS:
        day = plan[slug]['in_force']
        units, digest = parse_title(tdir, tdir == 'title_0000', as_of=as_of)
        print(tdir, len(units), 'units', len([k for k in units if '-dup' in k]), 'dups')
        acts.append({'slug': slug, 'short': short, 'title': title,
                     'url': f'https://mca.legmt.gov/bills/mca/{tdir}/chapters_index.html',
                     'first_law': None, 'earlier_laws': [],
                     'versions': [{'from': day, 'source_url': f'https://mca.legmt.gov/bills/mca/{tdir}/chapters_index.html',
                                   'sha256': digest, 'units': units,
                                   'note': 'Montana Code Annotated 2025 (header: updated August 2026), as retrieved; earlier editions are not in this build.'}]})
    corpus = {
        'country': {'code': 'US-MT', 'name': 'Montana', 'slug': 'united-states-montana', 'lang': 'en', 'tz': 'America/Denver',
                    'future_branch': 'future',
                    'publisher': {'name': 'Montana Legislative Services Division', 'email': 'lsd@mca-montana.invalid'},
                    'default_in_force_rule': {'text': 'Mont. Code Ann. 1-2-201: an act takes effect on October 1 after passage unless it says otherwise; edition versions require an explicit source-backed date plan; a partial source date is held, not replaced by retrieval day',
                                              'source': 'https://mca.legmt.gov/bills/mca/index.html'},
                    'licence_note': 'Montana Code Annotated 2025, Legislative Services Division (Code Commissioner), https://mca.legmt.gov/.'},
        'sources': [{'name': 'Montana Code Annotated 2025 (Legislative Services Division)', 'url': 'https://mca.legmt.gov/bills/mca/index.html',
                     'retrieved': '2026-10-30', 'requests': 190,
                     'licence': 'MCA 1-11-304: the Montana Code Annotated, as published, is the property of the State and may not be copyrighted. Statute text is also not copyrightable (Georgia v. Public.Resource.Org, 2020).',
                     'notes': 'Static HTML, one page per section. mca.legmt.gov and archive.legmt.gov have no robots.txt (404, 2026-10-30).'}],
        'laws': {}, 'acts': acts, 'applies': [],
        'decisions': ['The source labels the edition "Updated August 2026", without a day. New versions require an exact source-backed date plan. Source alternatives are selected by their stated effective dates for the supplied as-of day; unresolved contingencies hold the act. Unlabelled continuation blocks are retained.',
                      'Each section keeps its History note (the session laws behind it) as its last line; no compiler\'s comments, cross-references or annotations are taken.',
                      'Section pages are read in place; "Repealed" and "Reserved" pages the code prints are kept as the code prints them.'],
        'ai_use': ['none']}
    write(os.path.join(HERE, 'corpus.json'), corpus)


if __name__ == '__main__':
    main()
