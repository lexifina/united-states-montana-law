# How this repository was made (Montana)

This file is written by the build on 2026-11-10, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Montana Code Annotated 2025 (Legislative Services Division) | <https://mca.legmt.gov/bills/mca/index.html> | 2026-10-30 | MCA 1-11-304: the Montana Code Annotated, as published, is the property of the State and may not be copyrighted. Statute text is also not copyrightable (Georgia v. Public.Resource.Org, 2020). |
| Montana Code Annotated 2025 (Legislative Services Division), every title | <https://mca.legmt.gov/bills/mca/index.html> | 2026-11-10 | MCA 1-11-304: the Montana Code Annotated, as published, is the property of the State and may not be copyrighted. Statute text is also not copyrightable (Georgia v. Public.Resource.Org, 2020). |
| Montana Code Annotated 2023 (Legislative Services Division), every title | <https://mca.legmt.gov/bills/2023/mca/index.html> | 2026-11-10 | MCA 1-11-304: the Montana Code Annotated, as published, is the property of the State and may not be copyrighted. Statute text is also not copyrightable (Georgia v. Public.Resource.Org, 2020). |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of the State of Montana | 3 | 2023-10-01 to 2026-10-28 |
| `title-35-corporations` | Montana Code Annotated, Title 35: Corporations, Partnerships, Associations | 1 | 2026-10-28 to 2026-10-28 |
| `title-45-crimes` | Montana Code Annotated, Title 45: Crimes | 1 | 2026-10-28 to 2026-10-28 |
| `title-70-property` | Montana Code Annotated, Title 70: Property | 1 | 2026-10-28 to 2026-10-28 |
| `title-1-general-laws-and-definitions` | Montana Code Annotated, Title 1: General Laws and Definitions | 2 | 2023-10-01 to 2025-10-01 |
| `title-2-government-structure-and-administration` | Montana Code Annotated, Title 2: Government Structure and Administration | 6 | 2023-10-01 to 2031-07-01 |
| `title-3-judiciary-courts` | Montana Code Annotated, Title 3: Judiciary, Courts | 3 | 2023-10-01 to 2035-07-01 |
| `title-5-legislative-branch` | Montana Code Annotated, Title 5: Legislative Branch | 2 | 2023-10-01 to 2025-10-01 |
| `title-7-local-government` | Montana Code Annotated, Title 7: Local Government | 3 | 2023-10-01 to 2025-10-01 |
| `title-10-military-affairs-and-disaster-and-emerge` | Montana Code Annotated, Title 10: Military Affairs and Disaster and Emergency Services | 4 | 2023-10-01 to 2031-07-02 |
| `title-13-elections` | Montana Code Annotated, Title 13: Elections | 2 | 2023-10-01 to 2025-10-01 |
| `title-15-taxation` | Montana Code Annotated, Title 15: Taxation | 12 | 2023-10-01 to 2038-07-01 |
| `title-16-alcohol-tobacco-and-marijuana` | Montana Code Annotated, Title 16: Alcohol, Tobacco, and Marijuana | 3 | 2023-10-01 to 2025-10-01 |
| `title-17-state-finance` | Montana Code Annotated, Title 17: State Finance | 4 | 2023-10-01 to 2031-07-01 |
| `title-18-public-contracts` | Montana Code Annotated, Title 18: Public Contracts | 3 | 2023-10-01 to 2033-07-02 |

The build made 38 commits:

| Commits | Kind |
| ---: | --- |
| 15 | first version of an act |
| 0 | one law on its in-force day |
| 20 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-11-10.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 0 laws in the record.
- 35 tags.

## Dates

Each commit is dated at noon (America/Denver) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: MCA 1-2-201(1)(a): every statute "takes effect on the first day of October following its passage and approval unless a different time is prescribed in the enacting legislation". Each edition is dated 1 October of its year; forms an edition prints with a later effective day are dated that day. https://mca.legmt.gov/bills/mca/title_0010/chapter_0020/part_0020/section_0010/0010-0020-0020-0010.html

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `ddd74bd4ef0daafec78f64549ad7535094ea202d180e13ab2b4aee1cb78d2903` (61482793 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `3024ff164c261807dfc4d5b7b1b4a2cde4357da1`, `check.py` `5d719354ea4c62d240c93d2cae446307d81d9e81`, `on.py` `aff48cf1b68d50c7ba8f399ca32261871c301824`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- Every title of the Montana Code Annotated and the Constitution, from the 2023 and 2025 editions on mca.legmt.gov. Each edition holds the law enacted through that year's regular session; under MCA 1-2-201(1)(a) a law takes effect on 1 October after its passage unless it says otherwise, so each edition is dated 1 October of its year (2023-10-01, 2025-10-01). Laws that took effect earlier in the year are dated later than they took effect, never earlier. The 2025 edition's page says "Updated August 2026" and gives no day.
- Where an edition prints a section in two forms with an effective clause in the catchline ("(Temporary -- effective until June 30, 2027)", "(Effective July 1, 2027)"), each version takes the form in force on its day, and the act gets a further version on each later day a printed form takes effect, up to the next edition. Forms "effective on occurrence of contingency" are left out while another form exists, and a section printed only in a contingent form is left out (26 section pages): the code does not say whether the contingency occurred.
- History starts with the 2023 edition: the 2021 edition is not on the host (404), and the 2017 and 2019 editions would leave October 2021 to October 2023 without text. Changes made between editions (special sessions, constitutional amendments approved at an election) are dated by the next edition, later than they took effect.
- The four acts of the first build (the Constitution, Titles 35, 45 and 70; one version dated 2026-10-28, the retrieval day) keep that commit; as their pages are read again, correction commits add the 2023 and 2025 editions before it and set its text to the text the shipped parser reads from the pages.
- Each section keeps its History note (the session laws behind it) as its last line; no compiler's comments, cross-references or annotations are taken.
- Section pages are read in place; "Repealed" and "Reserved" pages the code prints are kept as the code prints them.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- none
