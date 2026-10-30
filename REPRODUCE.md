# How this repository was made (Montana)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Montana Code Annotated 2025 (Legislative Services Division) | <https://mca.legmt.gov/bills/mca/index.html> | 2026-10-30 | MCA 1-11-304: the Montana Code Annotated, as published, is the property of the State and may not be copyrighted. Statute text is also not copyrightable (Georgia v. Public.Resource.Org, 2020). |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of the State of Montana | 1 | 2026-10-28 to 2026-10-28 |
| `title-35-corporations` | Montana Code Annotated, Title 35: Corporations, Partnerships, Associations | 1 | 2026-10-28 to 2026-10-28 |
| `title-45-crimes` | Montana Code Annotated, Title 45: Crimes | 1 | 2026-10-28 to 2026-10-28 |
| `title-70-property` | Montana Code Annotated, Title 70: Property | 1 | 2026-10-28 to 2026-10-28 |

The build made 4 commits:

| Commits | Kind |
| ---: | --- |
| 4 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 0 laws in the record.
- 4 tags.

## Dates

Each commit is dated at noon (America/Denver) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Mont. Code Ann. 1-2-201: an act takes effect on October 1 after passage unless it says otherwise; this first build holds only the 2025 edition as retrieved, dated by the day of retrieval https://mca.legmt.gov/bills/mca/index.html

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `bcc3518832fa29390e96d5638fda68aab0ce4e9361d024ba76586656a40a1160` (3351480 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3e59cb6f05eccb94a9ec14431a7f6781221e83ef`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- First build: the current 2025 edition (header "Updated August 2026") of the Constitution and Titles 35, 45 and 70 only. Each act has one version, dated 2026-10-28, the day the 2025 edition (updated August 2026) was first retrieved; the Constitution pages were retrieved two days later, on 2026-10-30, from the same edition (same header), and carry the edition date, credited to the publisher as the oldest version available.
- Each section keeps its History note (the session laws behind it) as its last line; no compiler's comments, cross-references or annotations are taken.
- Section pages are read in place; "Repealed" and "Reserved" pages the code prints are kept as the code prints them.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none
