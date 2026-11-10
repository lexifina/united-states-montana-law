"""Montana, 2026-11-10: corpus.json = the published first build (acts-first.json) + the acts parse_mca.py read
(corpus.mca.json: every title both editions of which are cached).

    python -X utf8 mt_corpus.py [--fix-published]

Acts not yet published are added with their versions as parse_mca.py gives them (2023 edition from 2023-10-01, 2025
edition from 2025-10-01, later printed forms on their days). The four published acts (constitution, titles 35, 45, 70)
keep their first-build version unless --fix-published: then they get the edition versions before it, and their
2026-10-28 version holds the text in force that day as parse_mca.py reads it (published with append.py --corrections:
the earlier versions are back-filled corrections and the 2026-10-28 one a text correction).
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from text_preserving import write  # noqa: E402

PUBLISHED_DAY = '2026-10-28'
RULE = ('MCA 1-2-201(1)(a): every statute "takes effect on the first day of October following its passage and approval '
        'unless a different time is prescribed in the enacting legislation"')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fix-published', action='store_true')
    a = ap.parse_args()
    c = json.load(open(os.path.join(HERE, 'acts-first.json'), encoding='utf-8'))
    m = json.load(open(os.path.join(HERE, 'corpus.mca.json'), encoding='utf-8'))
    mca = {x['slug']: x for x in m['acts']}
    for act in c['acts']:
        new = mca.pop(act['slug'], None)
        if not (a.fix_published and new):
            continue
        before = [v for v in new['versions'] if v['from'] < PUBLISHED_DAY]
        after = [v for v in new['versions'] if v['from'] > PUBLISHED_DAY]
        on = copy.deepcopy(before[-1])
        on.update({'from': PUBLISHED_DAY, 'note': 'The 2025 edition as retrieved on 2026-10-28 (the first build\'s day); it records no change in the law.'})
        old = act['versions'][0]
        on['source_url'], on['sha256'] = old['source_url'], old['sha256']
        act['versions'] = before + [on] + after
    c['acts'] += sorted(mca.values(), key=lambda x: (x['slug'] != 'constitution', int(x['short'].split()[-1]) if x['short'].startswith('MCA') else 0))
    c['country']['default_in_force_rule'] = {
        'text': RULE + '. Each edition is dated 1 October of its year; forms an edition prints with a later effective day are dated that day.',
        'source': 'https://mca.legmt.gov/bills/mca/title_0010/chapter_0020/part_0020/section_0010/0010-0020-0020-0010.html'}
    c['sources'] = c['sources'][:1] + [
        {'name': 'Montana Code Annotated 2025 (Legislative Services Division), every title', 'url': 'https://mca.legmt.gov/bills/mca/index.html',
         'retrieved': '2026-11-10', 'licence': c['sources'][0]['licence'],
         'notes': 'Static HTML, one page per section ("Updated August 2026"). mca.legmt.gov has no robots.txt (404, 2026-11-10); one request in flight, at most 2 a second.'},
        {'name': 'Montana Code Annotated 2023 (Legislative Services Division), every title', 'url': 'https://mca.legmt.gov/bills/2023/mca/index.html',
         'retrieved': '2026-11-10', 'licence': c['sources'][0]['licence'],
         'notes': 'The archived 2023 edition on the same host, same page layout. The 2021 edition is not on the host (404); 2017 and 2019 are.'}]
    c['decisions'] = [
        'Every title of the Montana Code Annotated and the Constitution, from the 2023 and 2025 editions on mca.legmt.gov. Each edition holds the law '
        'enacted through that year\'s regular session; under MCA 1-2-201(1)(a) a law takes effect on 1 October after its passage unless it says '
        'otherwise, so each edition is dated 1 October of its year (2023-10-01, 2025-10-01). Laws that took effect earlier in the year are dated '
        'later than they took effect, never earlier. The 2025 edition\'s page says "Updated August 2026" and gives no day.',
        'Where an edition prints a section in two forms with an effective clause in the catchline ("(Temporary -- effective until June 30, 2027)", '
        '"(Effective July 1, 2027)"), each version takes the form in force on its day, and the act gets a further version on each later day a '
        'printed form takes effect, up to the next edition. Forms "effective on occurrence of contingency" are left out while another form exists, '
        f'and a section printed only in a contingent form is left out ({len(m.get("left_out", []))} section pages): the code does not say whether '
        'the contingency occurred.',
        'History starts with the 2023 edition: the 2021 edition is not on the host (404), and the 2017 and 2019 editions would leave October 2021 '
        'to October 2023 without text. Changes made between editions (special sessions, constitutional amendments approved at an election) are '
        'dated by the next edition, later than they took effect.',
    ] + ([
        'The four acts of the first build (the Constitution, Titles 35, 45 and 70; one version dated 2026-10-28, the retrieval day) keep that '
        'commit; correction commits add the 2023 and 2025 editions before it and set its text to the text the shipped parser reads from the pages.',
    ] if a.fix_published else [
        'The four acts of the first build (the Constitution, Titles 35, 45 and 70) keep their one version, dated 2026-10-28 (the retrieval day), '
        'as first published, until their editions are read again.',
    ]) + [
        'Each section keeps its History note (the session laws behind it) as its last line; no compiler\'s comments, cross-references or annotations are taken.',
        'Section pages are read in place; "Repealed" and "Reserved" pages the code prints are kept as the code prints them.',
    ]
    write(os.path.join(HERE, 'corpus.json'), c)
    print('acts', len(c['acts']), 'versions', sum(len(x['versions']) for x in c['acts']))


if __name__ == '__main__':
    main()
