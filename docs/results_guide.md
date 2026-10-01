# Results guide

Twenty-four CSVs. Every statistic quoted in the manuscript traces to one of these; that is
enforced mechanically by `scripts/a5_verify_manuscript.py`, which fails the build if a
decimal figure in the prose cannot be found here (or rounded onto a value here).

Read this file before using any of them.

---

## The result that changed the paper

`A2_bridges_corrected.csv`, `A2_bridges_corrected_summary.csv`

The participation coefficient was the original integrative-position measure. It correlates
with document frequency at **ρ = +0.549** (p = 2×10⁻⁴⁷), so a concept that is merely common
scores high on it. Scoring each concept against a per-node label-permutation null, which
holds that concept's own degree and neighbourhood fixed while destroying its domain
affiliation, gives a null-centred z.

**Maximum corrected z = 1.43 across 584 eligible concepts. Threshold 1.96. Zero concepts
reach significance.** The top decile of the corrected score overlaps the raw participation
decile by 25 of 59; the two rankings correlate at 0.64.

There is no bridge population. This is the paper's central null.

---

## The most reproducible structural result

`A2_load_bearing.csv`, `A2_load_bearing_window.csv`

Assortativity for the domain attribute after removing each group, on both corpora.

| Removed | Full (604 docs) | Window (448 docs) |
|---|---|---|
| none | 0.0723 | 0.0640 |
| GOVERNANCE | 0.0773 | **0.0574** |
| INNOVATION | 0.1061 | **0.1031** |
| TALENT | 0.0669 | **0.0472** |
| UNASSIGNED | **0.1367** | **0.1380** |

The three named domains **disagree in direction between corpora**, which is why the
manuscript does not claim that every removal raises segregation. Only the unassigned
population replicates, and it does so closely.

---

## The technology core

`A2_core_composition.csv`, `A2_core12_list.csv`, `A2_core12_profile.csv`,
`A2_domain_top_degree.csv`

Domain composition of each coreness level. Core 12 holds 24 concepts and is **13 innovation
concepts (enrichment 2.28), 1 governance concept (enrichment 0.20)**. The departure from the
node base rate is significant (χ² = 14.03, df = 3, p = 0.003); core 11 immediately below
shows nothing (χ² = 4.81, p = 0.19).

The core is **rare, not frequent**: mean document frequency 15.75 against 15.35 for
everything below it (Welch p = 0.90). Within the core, frequency is unrelated to degree
(ρ = 0.17) though across the network the two are strongly related (ρ = 0.59). Coreness is
reading structure here, not word commonness — the opposite of the participation measure.

`A2_core12_list.csv` gives the full membership. Twelve of the 24 are technology concepts:
wearable, artificial intelligence, ai, algorithm, smart, digital, devices, monitoring,
analytics, technologies, prediction, innovation.

---

## Measure diagnostics

| File | What it settles |
|---|---|
| `A2_genericity_diagnostic.csv` | Participation ↔ df ρ = +0.549; bridge mean df 29.1 vs 15.8 (Welch t = 5.03); frequency band 10–24, n = 260 |
| `A2_bridge_splithalf_reliability.csv` | Split-half reliability median **0.100** — the measure barely replicates when nothing changes |
| `A2_bridge_stability_sizematched.csv` | Block correlation vs log edges **r = 0.956**, R² = 0.913. Every stability number is mostly a statement about block size |
| `A2_bridge_stability_unsized_periods.csv` | The unequal natural periods (229 of 448 docs in 2022–2025) that made the first design circular |
| `A2_segregation_construction_sensitivity.csv` | Segregation on all 5 significance-filtered constructions (z = −3.54 to −5.84); the unfiltered graph is degenerate at mean degree 232 |

---

## Structure and composition

| File | Contents |
|---|---|
| `A2_hierarchy_roles.csv` | All 669 concepts: pillar, df, degree, coreness, spectral, role, betweenness |
| `A2_domain_mixing_matrix.csv` | Edge-weight share for each ordered domain pair, with and without the unassigned population. Named-domain diagonal 0.0462 vs off-diagonal 0.0524, **ratio 0.882** — the domains are *not* internally clustered by edge weight |
| `A2_mixing_summary.csv` | The mixing summary statistics, including the 0.882 ratio |
| `A2_segregation_by_scope.csv` | Segregation by period and by national context |
| `A2_bridge_pillar_distribution.csv` | Domain distribution of raw bridge candidates (χ² = 4.60, p = .20) |
| `A2_bridge_scores.csv` | Raw participation for all eligible concepts |
| `A2_bridge_summary_statistics.csv` | Per-concept participation and layer-flexibility statistics |
| `A2_bridge_stability.csv` | Block-level participation correlation |

---

## Convergent validity against SPLISS

`A2_spliss_convergent_validity.csv`, `A2_contingency_derived_spliss.csv`

117 of 669 concepts (17.5%) matched at least one SPLISS pillar. Of 27 domain-by-pillar
associations, 7 survive Benjamini–Hochberg correction at .05.

**Match rates: talent 33.7%, governance 13.6%, innovation 8.2%.** Innovation is depleted
from every pillar it could plausibly match. The structurally deepest domain is the one the
nine-pillar framework has no vocabulary for.

---

## Assignment audit

`A2_assignment_conflicts.csv`

Four same-referent pairs split across domains, all involving the word *intelligence* (in
TALENT; *artificial intelligence* and *ai* in INNOVATION). Of ten pairs checked, six were
comparable and consistent; two could not be tested because one member fell below the node
threshold.

This is reported as a limitation on the technology-core result rather than fixed, because
the direction of the error is known and it **dilutes** the innovation core rather than
creating it.

---

## Reproducibility note

These are aggregate outputs of the analysis. Two files (`A2_hierarchy_roles.csv`,
`A2_bridges_corrected.csv`) carry concept labels, which are derived from record text but do
not reproduce any record's text. No bibliographic record — title, abstract, author keyword,
affiliation, or country-of-document — appears in any file in this directory. See
[`scopus_query.md`](scopus_query.md).