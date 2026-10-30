# Montana: law history in git

The statute law of Montana as a git repository: one file per section, committed with the official publisher named as author. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now (a first build, not complete)**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of the State of Montana (167 sections) | 1 | One version: the 2025 edition as the Legislative Services Division publishes it, retrieved 2026-10-28 |
| `title-35-corporations/` | Montana Code Annotated, Title 35: Corporations, Partnerships, Associations (1801 sections) | 1 | One version: the 2025 edition as the Legislative Services Division publishes it, retrieved 2026-10-28 |
| `title-45-crimes/` | Montana Code Annotated, Title 45: Crimes (390 sections) | 1 | One version: the 2025 edition as the Legislative Services Division publishes it, retrieved 2026-10-28 |
| `title-70-property/` | Montana Code Annotated, Title 70: Property (954 sections) | 1 | One version: the 2025 edition as the Legislative Services Division publishes it, retrieved 2026-10-28 |

Nothing else of Montana's law is in it yet.

## Where the text comes from

The text is read from the **Montana Code Annotated 2025** (the page header reads "Updated August 2026") on <https://mca.legmt.gov/bills/mca/index.html>, which the Legislative Services Division publishes as one static HTML page per section. The Constitution (about 190 requests, one a second) was fetched on 30 October 2026; Each section keeps its catchline, its text and the History note naming the session laws behind it. Compiler's comments and cross-references are not taken.

## Dates

- Each act has **one version**, dated 28 October 2026, the day the edition was first retrieved (the Constitution's pages were fetched on 30 October 2026 from the same edition). It is the oldest version available in this build: older MCA editions exist online (1995 to 2023) but are not in this first build.
- The first commit of each act is credited to the Legislative Services Division as "oldest version available".
- The session laws in each History note are part of the text, not the commit dates.

## What it does not show

- Any amendment history: the editions before 2025.
- The other 70-odd titles of the MCA, session laws and regulations.
- Compiler's comments, cross-references and other annotations.
- Nothing here is an official publication: the printed MCA prevails over the Internet version.

## How it is checked

- Every unit is read back from git on its day and compared with the corpus (`tools/check_repo.py`; results in `REPRODUCE.md`).
- Each source file is identified by its sha256, in `data/versions.json`.

## What "author" means

Each commit is authored by the publisher (the Montana Legislative Services Division) because this first build holds one version of each act, the oldest version available. The committer is always Lexifina.
