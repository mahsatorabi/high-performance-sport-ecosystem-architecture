# Method notes

Design decisions a reader is most likely to query, and why each was made. These are the
same points as Appendices B, C and D of the manuscript, collected here for the repository.

---

## Why assortativity and not a boundary-crossing ratio

The load-bearing test asks whether removing a domain changes the cohesion of the survivors.
The obvious measure is a boundary-crossing ratio, and it was rejected: its null expectation
shifts with the number of groups, so its z-score is not comparable between the three-group
and four-group partitions this question requires. Comparing "named domains only" against
"named plus unassigned" on a crossing ratio would be comparing two different statistics.

Newman's (2003) categorical assortativity is bounded and degree-standardised, so it can be
compared across subgraphs of 669 nodes and 352 without size dominating. It is absolute, not
relative, so a rise from 0.064 to 0.138 means the same thing at both corpus sizes.

## Why a weight-based assortativity variant was abandoned

Attempted and dropped. For a scalar-weighted undirected graph the mixing matrix is
symmetric, so permuting labels permutes only its rows and columns, the null collapses to a
point, and the null z is `nan`. The unweighted mixing matrix is asymmetric because each
edge is counted once, which is what makes it sensitive to the label assignment.

## Why sub-corpora analyses drop the bipartite significance filter

A 40-draw null cannot place a per-edge threshold on blocks of 28 to 229 documents. Under the
full filter the early-period blocks collapse to mean degree 0.5, far too sparse for a
participation coefficient to rank anything. Sub-corpora analyses therefore use a
co-occurrence threshold alone, and this is stated wherever a sub-corpus number appears.

## Why stability blocks are chronological quartiles

The first design used four natural year-bounded periods and seven national contexts, and
gave a mean correlation of 0.186. That figure is uninterpretable: the periods were wildly
unequal, with 229 of 448 documents in 2022–2025, so the pooled network was largely one
block and the correlation was partly circular.

Re-specifying as chronological quartiles of exactly 112 documents each raised the mean to
0.356 (range 0.299–0.411). Removing the circularity roughly doubled the correlation.

## Why the participation coefficient is reported both raw and null-centred

Because the two disagree about whether a bridge population exists, and that disagreement is
the substantive result rather than a nuisance. Reporting only the raw measure would have
produced 45 apparently sensible bridges. Reporting only the corrected one would hide that
the standard measure failed in a way worth documenting.

The coefficient is bounded at 0.750 for a four-group partition and its top decile clusters
between 0.735 and 0.750, so ranking *within* the decile is partly ranking noise. That is a
second reason to prefer the null-centred score.

## Why the domain assignment is audited rather than assumed

Domain labels come from centroid prototypes on the embedding space. A manual audit of ten
plausibly-synonymous pairs found four split across domains, all involving *intelligence*.
The audit is reported in §3.4 of the manuscript and its direction of error in §5.3, because
it bears on the technology-core finding: correcting it would move one more concept *into*
the innovation core, not out of it.

## Why two corpora

| Corpus | Used for | Reason |
|---|---|---|
| Full (604) | Load-bearing, domain mixing, coreness, participation | Every document maximises edge count |
| Window (448) | All temporal and national analyses, all bridge statistics | Sub-corpora require blocks; 2026 indexing incomplete, pre-2013 too sparse |

Where the two disagree, both are reported. Selecting the corpus that flatters a claim is
precisely the error the study is built to avoid, and the disagreement is itself a result
about measurement sensitivity.

## Why the role decomposition is reported as a null

It populates only two of its four roles (547 hub, 122 peripheral, 0 central, 0
least-connected), which is the expected outcome for a single-layer network. It carries no
substantive weight on its own. Its value is negative evidence: the method that would detect
a differentiated vertical ordering cannot apply here, because the network does not present
the layered structure the method assumes.

## Why core 6 is reported despite its small cell

Core 6 holds 26 concepts with an innovation enrichment of 1.46. With nine innovation
concepts in a cell of 26 it is the level most likely to move under a different
decomposition, so it is flagged as provisional in the table note rather than dropped. The
claim does not rest on it: the significant departure is core 12 only.

---

## Known limitations of the measures

- The national dimension is essentially absent. 55 lead countries appear, 2 are analysable.
  This is a property of the corpus, not the method: sport research is internationally
  distributed but not internationally co-indexed under this query.
- The edge null is the degree-preserving bipartite swap, which preserves document and
  concept degrees exactly while destroying topical association. 40 draws, so null means
  carry roughly 1.6 per cent Monte Carlo error.
- Permutation tests use 1,000 draws. Reported null means should be read to two decimals.
- The maximum corrected z of 1.43 is a maximum over 584 concepts and is biased upward by
  selection. That is the conservative direction for a null result: correcting for the
  selection would lower it.
- The 12-core boundary is one concept deep in a 24-cell sitting above a 233-cell layer. A
  different core implementation could move the boundary slightly. The enrichment finding
  survives that, because the nearest technology concepts sit at coreness 11 carrying the
  same labels.
- This is a model of concepts, not of institutions. Nothing here establishes that the
  knowledge structure corresponds to the organisational structure.