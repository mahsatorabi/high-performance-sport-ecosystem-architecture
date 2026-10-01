# Scopus retrieval record

## Query (verbatim)

```
TITLE-ABS-KEY(
  ( "sport ecosystem" OR "sport system" OR "sport network" OR "sport value chain"
    OR "innovation ecosystem" OR "entrepreneurial ecosystem" )
  AND
  ( "elite sport" OR "high performance sport" OR "professional sport" OR "athlete*" )
)
```

## Retrieval

| Field | Value |
|---|---|
| Database | Scopus |
| Field searched | TITLE-ABS-KEY (title, abstract, author keywords) |
| Retrieval date | 30 September 2026 |
| Records returned | **623** |

This is the same query and the same retrieval date used in the companion paper (*Mapping
the Intellectual Structure of High-Performance Sport Ecosystem Research*). The two studies
analyse one corpus at different levels: the companion asks what the field's conceptual
structure looks like, this paper asks what that structure implies for how the field is
organised. Re-running this query reproduces both.

## Pre-filtering

**None applied by the researcher.** All 623 records were exported unfiltered from Scopus.
Every exclusion is an *analytical* decision made inside the pipeline, not a step taken
before data collection.

## Analytical exclusions

| Exclusion | n | Reason |
|---|---|---|
| Retracted | 3 | Withdrawn during data processing |
| Note | 7 | Not peer-reviewed articles |
| Editorial | 2 | Non-empirical |
| Erratum | 1 | Correction notice |
| Degenerate title/abstract | 6 | Empty or < 80 characters after boilerplate stripping |
| **Analytic corpus** | **604** | |
| of which in analysis window 2013–2025 | 448 | Retained for all inference |
| of which pre-2013 | 50 | Descriptive reporting only |
| of which 2026 (partial indexing) | 106 | Excluded from all inference |

## Two corpora, and why

This paper reports some results on 604 documents and some on the 448-document window, and
where the two disagree it reports both. That is deliberate and is not an inconsistency.

| Corpus | Used for | Reason |
|---|---|---|
| **Full (604)** | Load-bearing test, domain mixing, coreness, participation | Every available document maximises edge count, which the stability analysis shows is the quantity these statistics are most sensitive to |
| **Window (448)** | All temporal and national analyses, all bridge statistics | Sub-corpora analyses require blocks; 2026 indexing is incomplete and pre-2013 is too sparse to form them |

The two corpora disagree on the direction of the load-bearing effect for each named domain,
and agree closely only on the unassigned population. The manuscript reports this as a
limitation rather than selecting the corpus that gives the cleaner answer.

## Dependency on the companion repository

This analysis is second-order. It reads:

| Input | Produced by | Withheld here? |
|---|---|---|
| `corpus.json` | Companion repo, `s0_corpus.py` | **Yes** — Scopus licence |
| `network_edges.csv` | Companion repo, `s3_network.py` | **Yes** — Scopus licence |
| `pillar_of.json` | Companion repo, `s5_multiplex.py` | **Yes** — derived from record text |

To reproduce: clone the companion repository, run its `scripts/run_all.py` to regenerate
these three files, then run this repository's `scripts/run_all.py`. The preflight check in
`run_all.py` reports exactly which inputs are missing rather than failing later with a
`FileNotFoundError`.

## Note on the 2026 records

2026 contributed 106 records, more than any single year after 2021, because Scopus
indexing for 2026 was incomplete at the retrieval date. Including them in temporal
inference would produce a spurious recent-topic surge, so all temporal and period-block
analysis is restricted to 2013–2025.

## Note on Scopus Index Keywords

Scopus Index Keywords (MeSH-derived) are excluded from concept mining entirely. They are
clinical taxonomy terms and produce a physiology cluster in this corpus unrelated to the
research object.

## Licence

Scopus records are **not redistributed** in this repository, in whole or in part. The query
and retrieval date above are sufficient to reproduce the corpus for users with
institutional Scopus access.