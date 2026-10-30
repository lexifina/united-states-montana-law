import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'world-law'))
from state_docs import write_docs

c = json.load(open(os.path.join(HERE, 'corpus.json'), encoding='utf-8'))
acts = []
for a in c['acts']:
    v = a['versions'][0]
    acts.append({'folder': a['slug'], 'title': a['title'] + f" ({len(v['units'])} sections)", 'versions': 1,
                 'history': f"One version: the 2025 edition as the Legislative Services Division publishes it, retrieved {v['from']}"})
write_docs(HERE, {
    'name': 'Montana', 'code': 'MT', 'slug': 'united-states-montana', 'date': '2026-10-30', 'domain': 'mca-montana',
    'publisher': 'the Montana Legislative Services Division',
    'acts': acts,
    'build': 'built: Constitution of Montana and MCA Titles 35, 45 and 70, 2025 edition (updated August 2026), current text only (one version each)',
    'source': ("The text is read from the **Montana Code Annotated 2025** (the page header reads \"Updated August 2026\") on "
              "<https://mca.legmt.gov/bills/mca/index.html>, which the Legislative Services Division publishes as one static HTML page per "
              "section. `mca.legmt.gov` and `archive.legmt.gov` publish no robots.txt (404). The Constitution (about 190 requests, one a "
              "second) was fetched on 30 October 2026; Titles 35, 45 and 70 are pages retrieved on 28 October 2026 by an earlier Lexifina "
              "fetch of the same site, copied from its cache. Each section keeps its catchline, its text and the History note naming the "
              "session laws behind it. Compiler's comments and cross-references are not taken."),
    'dates': ("- Each act has **one version**, dated 28 October 2026, the day the edition was first retrieved (the Constitution's pages were fetched on 30 October 2026 from the same edition). It is the oldest version available in this build: older MCA editions exist online (1995 to 2023) "
              "but are not in this first build.\n"
              "- The first commit of each act is credited to the Legislative Services Division as \"oldest version available\".\n"
              "- The session laws in each History note are part of the text, not the commit dates."),
    'limits': ("- Any amendment history: the editions before 2025.\n"
              "- The other 70-odd titles of the MCA, session laws and regulations.\n"
              "- Compiler's comments, cross-references and other annotations.\n"
              "- Nothing here is an official publication: the printed MCA prevails over the Internet version."),
    'licence': ("The legal text is the Constitution of the State of Montana and Titles 35, 45 and 70 of the Montana Code Annotated 2025, "
                "published by the Legislative Services Division at https://mca.legmt.gov/. MCA 1-11-304 provides that the Montana Code "
                "Annotated, as published, is the property of the State and may not be copyrighted; statutes are in any case not "
                "copyrightable (Georgia v. Public.Resource.Org, Inc., 590 U.S. 255 (2020)). The text is republished unaltered in its "
                "wording, with credit to the Legislative Services Division as its publisher."),
})
