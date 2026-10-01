# Neither a Hierarchy nor a Bridging Elite: The Conceptual Architecture of the High-Performance Sport Ecosystem

Replication repository for a test of the structural assumption behind the nine-pillar
(SPLISS) model of high-performance sport. The question is not whether the field has
domains, which it does, but whether those domains stand in a hierarchy, with some
foundational for others. Three predictions were specified in advance and tested against
a concept network built from 448 Scopus documents (2013–2025). **None of the three
produced the vertical picture, and two produced nothing at all.** The paper reports
that, and treats it as the finding.

> **Manuscript:** "Neither a hierarchy nor a bridging elite: the conceptual
> architecture of the high-performance sport ecosystem"
>
> **Companion paper:** "Mapping the Intellectual Structure of High-Performance Sport
> Ecosystem Research", [`high-performance-sport-concept-network`](https://github.com/mahsatorabi/high-performance-sport-concept-network)

---

## ⚠️ Data availability — read first

The bibliographic records analysed here were retrieved from **Scopus** under a single
structured query. **Scopus licensing does not permit redistribution of the raw export,
and no Scopus-derived record text (titles, abstracts, author keywords, affiliations) is
included in this repository.**

The query below, together with the retrieval date, is sufficient to reproduce the corpus:

```
TITLE-ABS-KEY(
  ( "sport ecosystem" OR "sport system" OR "sport network" OR "sport value chain"
    OR "innovation ecosystem" OR "entrepreneurial ecosystem" )
  AND
  ( "elite sport" OR "high performance sport" OR "professional sport" OR "athlete*" )
)
```
**Retrieved:** 30 September 2026 → **623 records** → 604 analytic → 448 in window

This repository is **second-order**: it reads the concept families, network and domain
labels produced by the companion paper's pipeline. Three inputs are therefore withheld
— `corpus.json`, `network_edges.csv` and `pillar_of.json` — because each is derived
from record text. See [`docs/scopus_query.md`](docs/scopus_query.md) for the full
dependency map and how to regenerate them.

All *derived* artefacts are included: every result table, every figure, the domain
assignment audit, and the manuscript verifier's report. These are aggregate outputs of
the analysis, not bibliographic records.

---

## What this repository contains

| Path | Description |
|---|---|
| `manuscript/` | Full manuscript (`.docx`) |
| `scripts/` | Analysis pipeline, executed in order by `run_all.py` |
| `tables/` | 24 result tables (CSV) — every statistic quoted in the manuscript |
| `figures/` | 7 publication-resolution figures (300 dpi PNG) |
| `verification/` | Verifier report supporting the manuscript's validation claims |
| `docs/` | Scopus retrieval record and dependency map |

### Explicitly excluded

| Excluded | Reason |
|---|---|
| `data.csv` (Scopus export) | Scopus licence — no redistribution |
| `corpus.json` | Contains abstracts — Scopus licence |
| `network_edges.csv` | Derived from record text |
| `pillar_of.json` | Derived from record text |
| `country_window.json` | One country per document: a per-record projection |
| `*.npy` | Document-concept matrices, embeddings, degree and adjacency arrays |
| `a4_manuscript_docx.py` | Superseded draft builder — regenerates abandoned claims |

`scripts/build_repo.py` enforces the exclusions and **exits non-zero** if any withheld
file survives into the tree, so a stale copy cannot be committed by accident.

---

## Pipeline

Twelve analysis stages plus document build and verification, run in order. Runtime is
about four minutes once the Article 1 inputs exist.

```bash
pip install -r requirements.txt
python scripts/run_all.py
```

| Stage | Script | Purpose |
|---|---|---|
| 0 | `a0_matrices.py` | Windowed matrix; period and national blocks; segregation by scope |
| 0.5 | `a0b_sensitivity.py` | Segregation re-tested across seven constructions |
| 1 | `a1_hierarchy.py` | Coreness decomposition; role decomposition; full-corpus load-bearing |
| 2 | `a2_bridges.py` | Participation coefficient on the window; raw bridge candidates |
| 2.5 | `a2b_stability.py` | Size-matched blocks; split-half reliability; power diagnostic |
| 3 | `a3_spliss_validity.py` | Convergent validity against SPLISS, Benjamini–Hochberg corrected |
| 4 | `a8_bridges_corrected.py` | **Null-centred bridge measure, 1,000 label permutations** |
| 5 | `a9_load_bearing_window.py` | Load-bearing on the analysis window (two-corpus comparison) |
| 6 | `a7_genericity_diagnostic.py` | Participation–frequency confound; frequency-band control |
| 7 | `a10_core_composition.py` | Core composition by domain; core frequency profile; assignment audit |
| 8 | `a6_figures.py` | Figures 1–6; domain-mixing matrix |
| 8.5 | `a11_figure7.py` | Figure 7, core composition |
| 9 | `b1_manuscript.py` | Builds the manuscript with embedded figures and real Word tables |
| 10 | `a5_verify_manuscript.py` | **Verifies the manuscript; fails loudly on any inconsistency** |

`run_all.py` has a preflight check that reports exactly which inputs are missing and
points at the script that produces them, rather than failing with a `FileNotFoundError`
four stages in.

---

## Method in brief

**Three predictions, each stated before the data were seen** (§2.3). If governance were
structurally prior, removing it should reduce the connectivity of the remainder. If the
field were flat, removing any domain should leave the others as connected. If the field
had a foundation, the integrative population should sit in the foundational domain.

**Why assortativity for the load-bearing test.** The obvious measure, boundary-crossing
ratio, has a null that shifts with the number of groups, so its z-score is not
comparable between the three-group and four-group partitions this test requires.
Newman's categorical assortativity is bounded and degree-standardised, so it can be
compared across subgraphs of 669 nodes and 352 without size dominating.

**Why a null-centred bridge score.** The participation coefficient is the standard
instrument for "where does connectivity concentrate", and it was chosen because it is
what the ecosystem metaphor implies. Scored against a per-node label-permutation null,
which holds each concept's own degree and neighbourhood fixed while destroying its
domain affiliation, the observed participation can be compared with what a concept of
that degree scores by chance.

---

## Headline results

| Finding | Statistic |
|---|---|
| Field is segmented, modestly | Assortativity 0.072 full / 0.064 window, **z = +8.88 / +6.92**; replicates on all 5 significance-filtered constructions |
| **No domain is load-bearing** | Removing each named domain moves assortativity in **inconsistent directions between corpora** |
| The unlabelled population holds it together | Removing it: **0.064 → 0.138** window, **0.072 → 0.137** full (replicates) |
| **There is a technical centre** | 13 of 24 concepts in the 12-core are innovation (enrichment **2.28**, **p = 0.003**); governance enrichment 0.20 |
| …and it is structural, not frequency | Core mean df **15.8 vs 15.3** (Welch p = 0.90); within-core df↔degree ρ = 0.17 |
| Participation measures **genericity** | Participation ↔ document frequency **ρ = +0.549** (p = 2×10⁻⁴⁷) |
| **No bridging elite exists** | Max corrected z = **1.43** across 584 concepts; threshold 1.96. **0 of 584** reach significance |
| Layer flexibility was frequency | Periods 3.41 vs 3.37 (p = 0.77); contexts 3.97 vs 4.18 (p = 0.28) |
| Innovation is invisible to SPLISS | Only **8.2%** of innovation concepts match SPLISS vocabulary vs 33.7% talent, 13.6% governance |
| Bridge identity is unmeasurable | Split-half reliability **ρ = 0.100**; block ρ vs log edges **r = 0.956**, R² = 0.913 |

**The proposed model: a segmented field with a technical centre and diffuse
integration.** Three domains are distinguishable, none is structurally prior, a small
rare technology-centred population occupies the deepest layer, a large general
population carries the connective work, and no concept plays a structurally necessary
bridging role.

---

## Verification

`a5_verify_manuscript.py` checks four things that can silently break a manuscript of
this kind, and its report is committed at
[`verification/verification_report.txt`](verification/verification_report.txt):

1. **Every statistic quoted in prose traces to a CSV in `tables/`** — no free-floating
   numbers. 43 quoted, 43 traceable.
2. **Every citation resolves and every reference is cited** — no padding. 26 citations,
   0 unresolved, 0 uncited entries, 0 undated narrative citations.
3. **Word count is exact and internally consistent** — 9,000 countable words by Article 1's
   rule, with the builder's count and an independent walk of the .docx agreeing exactly.
4. **Structure holds** — 7 embedded figures, 7 real Word tables, every caption referenced
   in the text, no duplicate headings.

The check in (1) is the one worth having. A manuscript that reports a field-level
finding in prose without a table backing it is the normal failure mode of this kind of
paper, and the verifier makes it a build failure.

---

## Bugs found and fixed during analysis

Recorded because each one changed a reported number, and because a reader comparing
against an earlier draft needs to know which is which.

| Where | Error | Effect on the claims |
|---|---|---|
| `a8_bridges_corrected.py` | `P3` wrongly included `UNASSIGNED`, so named-vs-unassigned comparisons filtered nothing | Corrected; the decisive null survives either way |
| `a2_bridges.py` | `flex_p`/`flex_c` summed document counts instead of counting layers | Period count was 108, not 4 |
| `a2_bridges.py` | `block_graph` defaulted to `mode="count"`, silently stripping the z-filter from the pooled network | Pooled bridge scores were computed on a different graph than reported |
| `a6_figures.py` | Figure 1 panel (b) zeroed the diagonal, erasing real within-domain edges | Fixed; the 0.88 ratio is unchanged |
| `a6_figures.py` | Caption said "45 bridges removed" while quoting the 212-unassigned statistic | Relabelled |
| `a6_figures.py` | Spring-layout hairball replaced by domain-mixing matrix | A hairball cannot show segregation, which here is genuinely weak |

The full-corpus and window results for the named domains disagree. That is reported as a
finding about corpus sensitivity, not resolved by choosing one.

---

## Citation

See [`CITATION.cff`](CITATION.cff), or cite the manuscript directly once published.

## Licence

- **Code:** MIT ([`LICENSE`](LICENSE))
- **Derived outputs** (tables, figures, verification): CC BY 4.0
- **Bibliographic records:** *not distributed* — see Data availability above

## Citation of methods used

- Fortunato (2010) — coreness decomposition
- Batagelj & Zaveršnik (2003) — efficient core decomposition
- Lancichinetti & Fortunato (2008) — role decomposition on the modularity matrix
- Guimerà & Nunes Amaral (2005a, 2005b) — participation coefficient and functional cartography
- Newman (2003) — categorical assortativity and mixing matrices
- Danon et al. (2005); Fortunato & Barthélemy (2007) — resolution limit in community detection
- Reimers & Gurevych (2019) — sentence embeddings
- Benjamini & Hochberg (1995) — false discovery rate control
- Fisher (1922) — exact test on the contingency table
- Gallagher, Young & Foucault Welles (2021) — core-periphery typology