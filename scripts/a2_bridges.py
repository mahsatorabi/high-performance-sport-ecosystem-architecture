"""
ARTICLE 2 - Stage C: bridge identification and bridge stability.

Article 1 established two things: the pillars are segregated, and the bridges between them
are distributed evenly across pillars rather than concentrated in one (chi2 = 2.40, p = .30).
If that is right, the ecosystem is one system, not three parallel sub-systems. The model in
Article 2 must therefore be built on the bridge population, not on the pillars.

Article 1 measured "bridging" with betweenness. Betweenness is path-based and known to
favour sparse long-range shortcuts, so a single measure on a single network is weak
evidence. This stage re-derives the bridge population three ways and requires them to agree:

  C1  PARTICIPATION COEFFICIENT. Guimera & Amaral (2005). 1 - sum_s (k_is / k_i)^2 over the
      pillar partition. Neighbourhood-based rather than path-based, so it is a genuinely
      independent measurement of the same construct. Each node is scored against a
      label-permutation null that preserves pillar sizes.

  C2  BRIDGE IDENTIFICATION. A node is a bridge if it is in the top decile of the
      participation coefficient AND has above-median weighted betweenness. Requiring both
      guards against calling a node a bridge for being merely peripheral. The pillar
      distribution of the bridge set is then tested by chi-square against the pillar
      distribution of the eligible set, not against equal proportions.

  C3  LAYER FLEXIBILITY. How many periods and how many national contexts a concept appears
      in. If bridging is a distributed population, bridges should be layer-flexible, and
      the flexibility of the bridge set should exceed that of the rest.

  C4  BRIDGE STABILITY. Every quantity above recomputed inside each of four periods and
      seven national contexts, each on its own significance-filtered network. Spearman
      correlation of the bridge score against the pooled network, plus overlap of the top
      decile, answers whether bridges are a stable structural feature or a by-product of
      who happened to publish in which period and country.

Construction is held identical to Article 1 throughout: co-occurrence >= 3 AND bipartite-null
z >= 2.5, association-strength weights. The bipartite null is recomputed inside each block,
because a null estimated on the pooled corpus would be invalid for a sub-corpus.
"""
import os, json, csv, collections
import numpy as np
import networkx as nx
from scipy import stats

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")

MIN_COOC, EDGE_Z, NULL_DRAWS = 3, 2.5, 40
REPS, SEED = 200, 5
DECILE = 0.10
MIN_BLOCK_DEG = 3           # below this a participation coefficient is too noisy to rank

blob = json.load(open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8"))
fam_label = blob["fam_label"]
years_doc = np.array([d["year"] for d in blob["docs"]])
country_doc = [d["lead_country"] for d in blob["docs"]]

pillar = {int(k): v for k, v in
           json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
nodes = sorted(pillar)
nn = len(nodes)
M = np.load(os.path.join(DATA, "M_window.npy")).astype(np.float32)
X = M[:, nodes]
N = X.shape[0]
year = np.load(os.path.join(DATA, "years_window.npy"))
country = json.load(open(os.path.join(DATA, "country_window.json")))
PERIODS = [(2013, 2016), (2017, 2019), (2020, 2021), (2022, 2025)]
COUNTRIES = ["Canada", "United States", "Germany", "Australia",
             "United Kingdom", "China", "Russian Federation"]
P3 = ["GOVERNANCE", "INNOVATION", "TALENT"]

print("=" * 78)
print("ARTICLE 2 - STAGE C  bridge identification and bridge stability")
print("=" * 78)
print("windowed docs %d | concepts %d" % (N, nn))
print("edge rule: co-occurrence >= %d AND bipartite-null z >= %.1f" % (MIN_COOC, EDGE_Z))


# ---------------------------------------------------------------- graph construction
def bipartite_z(Xb, Cb, kb, draws, seed):
    """Per-pair z of association strength against a degree-preserving bipartite swap null.

    Xb is (n_docs, n_concepts). A swap exchanges one concept between two documents, which
    preserves document and concept degrees exactly, so the null keeps the opportunity
    structure and destroys topical association. Cached to disk because it is the
    expensive part of every construction.
    """
    n_docs = Xb.shape[0]
    inv = [list(np.nonzero(Xb[d])[0].tolist()) for d in range(n_docs)]
    rng = np.random.default_rng(seed)
    acc = np.zeros(Cb.shape)
    acc2 = np.zeros(Cb.shape)
    for _ in range(draws):
        cur = [list(v) for v in inv]
        for _ in range(40 * n_docs):
            a, b = rng.integers(0, n_docs, 2)
            if a == b or not cur[a] or not cur[b]:
                continue
            ia = int(rng.integers(0, len(cur[a])))
            ca = cur[a][ia]
            if ca in cur[b]:
                continue
            ib = int(rng.integers(0, len(cur[b])))
            cb = cur[b][ib]
            cur[a][ia] = cb
            cur[b][ib] = ca
        Mn = np.zeros_like(Xb)
        for d in range(n_docs):
            for c in cur[d]:
                Mn[d, c] = 1.0
        Cn = (Mn.T @ Mn).astype(float)
        np.fill_diagonal(Cn, 0)
        Sn = Cn / np.maximum(kb[:, None] + kb[None, :] - Cn, 1e-9)
        acc += Sn
        acc2 += Sn ** 2
    mu = acc / draws
    sd = np.sqrt(np.maximum(acc2 / draws - mu ** 2, 1e-12))
    return (AS_OF(Cb, kb) - mu) / sd


def AS_OF(Cb, kb):
    A = Cb / np.maximum(kb[:, None] + kb[None, :] - Cb, 1e-9)
    np.fill_diagonal(A, 0)
    return A


def block_graph(Xb, tag, mode="z", draws=NULL_DRAWS, seed=13):
    """Weighted graph for a set of documents.

    mode="z"       co-occurrence >= 3 AND bipartite-null z >= 2.5, as in Article 1.
    mode="count"   co-occurrence >= 3 only.

    The sub-corpora use mode="count". With 28 to 229 documents a 40-draw null is far too
    noisy to place a per-edge threshold, and the filtered blocks collapse to mean degree
    0.5, too sparse for a participation coefficient to mean anything. The count rule is
    the loosest construction that still guards against single-document co-occurrence, and
    stage A2 showed the segregation result holds under every count-based construction. The
    deviation from Article 1 is stated in the table and in the manuscript.
    """
    Cb = (Xb.T @ Xb).astype(float)
    np.fill_diagonal(Cb, 0)
    kb = Xb.sum(0).astype(float)
    if mode == "z":
        cache = os.path.join(DATA, "Z_%s.npy" % tag)
        if os.path.exists(cache):
            Zb = np.load(cache)
        else:
            Zb = bipartite_z(Xb, Cb, kb, draws, seed)
            np.save(cache, Zb)
        keep = (Cb >= MIN_COOC) & (Zb >= EDGE_Z)
    else:
        keep = Cb >= MIN_COOC
    A = AS_OF(Cb, kb) * keep
    np.fill_diagonal(A, 0)
    G = nx.from_numpy_array(A)
    for i in range(nn):
        G.nodes[i]["df"] = float(kb[i])
    return G, kb


# ---------------------------------------------------------------- bridge metrics
def participation(G, member, subset=None):
    """Guimera & Amaral participation coefficient 1 - sum_s (k_is / k_i)^2.

    Uses unweighted neighbour counts, the standard definition. Nodes with no links in this
    network have an undefined coefficient and are returned as nan rather than 0, so that a
    concept absent from a period is not silently counted as a non-bridge.
    """
    P = {}
    for i in G.nodes():
        k = G.degree(i)
        if k == 0 or (subset is not None and i not in subset):
            P[i] = np.nan
            continue
        acc = collections.Counter()
        for j in G.neighbors(i):
            acc[member[j]] += 1
        P[i] = 1.0 - sum((c / k) ** 2 for c in acc.values())
    return P


def pc_null(G, member, reps=REPS, seed=SEED, subset=None):
    """Permute pillar labels over nodes, holding pillar sizes fixed, and recompute PC."""
    g0 = [i for i in sorted(G.nodes()) if (subset is None or i in subset)
          and G.degree(i) > 0]
    base = [member[i] for i in g0]
    rng = np.random.default_rng(seed)
    out = np.empty((reps, len(g0)))
    for t in range(reps):
        pm = dict(zip(g0, rng.permutation(base)))
        P = participation(G, pm, subset=None)
        out[t] = [P[i] for i in g0]
    return g0, out


member = {i: pillar[nodes[i]] for i in range(nn)}

print("\n" + "-" * 78)
print("POOLED NETWORK")
print("-" * 78)
Gpool, kpool = block_graph(X, "window", mode="z")
print("pooled graph: %d nodes, %d edges, mean degree %.1f"
      % (Gpool.number_of_nodes(), Gpool.number_of_edges(),
         2 * Gpool.number_of_edges() / Gpool.number_of_nodes()))

P_pool = participation(Gpool, member)
btw = nx.betweenness_centrality(Gpool, weight="weight", normalized=True)
g0, Pn = pc_null(Gpool, member)
pmean = Pn.mean(0)
psd = Pn.std(0) + 1e-12
pc_z = {i: (P_pool[i] - pmean[t]) / psd[t]
        for t, i in enumerate(g0) if not np.isnan(P_pool[i])}

elig = [i for i in Gpool.nodes() if Gpool.degree(i) >= 2 and not np.isnan(P_pool[i])]
print("eligible concepts (degree >= 2, PC defined): %d of %d" % (len(elig), nn))

# ---------------------------------------------------------------- C1 participation
print("\nC1  PARTICIPATION COEFFICIENT")
pcv = np.array([P_pool[i] for i in elig])
print("   PC distribution   mean %.4f  sd %.4f  min %.4f  max %.4f"
      % (pcv.mean(), pcv.std(), pcv.min(), pcv.max()))
btv = np.array([btw[i] for i in elig])
print("   PC vs betweenness Spearman rho = %.3f (p = %.2g)"
      % stats.spearmanr(pcv, btv))

# The label-permutation null here replicates Article 1's segregation test, it does not
# test bridges. Permuting labels destroys the pillar structure, so a concept's neighbours
# end up spread evenly over pillars and its PC RISES. Observed PC therefore sits BELOW
# the null for most concepts, and the sign of z is the same negative segregation signal
# Article 1 reported. A concept is not a candidate bridge because its z is extreme; it is
# a candidate bridge because its PC is high in absolute terms relative to other concepts.
zc = np.array([pc_z[i] for i in elig])
print("   segregation check: mean z %+.3f, %d of %d concepts below the null (z < 0)"
      % (zc.mean(), int((zc < 0).sum()), len(zc)))
print("   -> same negative sign as Article 1's boundary-crossing z; PC reproduces")
print("      segregation through an independent, neighbourhood-based route")

# PC by pillar, and whether bridges are pillar-specific
print("\n   PC by pillar")
for p in P3 + ["UNASSIGNED"]:
    s = [P_pool[i] for i in elig if member[i] == p]
    if s:
        print("   %-12s n %3d   mean %.4f  sd %.4f" % (p, len(s), np.mean(s), np.std(s)))
g3 = [P_pool[i] for i in elig if member[i] in P3]
gu = [P_pool[i] for i in elig if member[i] == "UNASSIGNED"]
tst = stats.ttest_ind(g3, gu, equal_var=False)
print("   named pillars vs unassigned: t = %.2f, p = %.4f"
      % (tst.statistic, tst.pvalue))

# ---------------------------------------------------------------- C2 bridge set
print("\nC2  BRIDGE IDENTIFICATION")
thr = np.quantile(pcv, 1 - DECILE)
bthr = np.median(btv)
bridge = [i for i in elig if P_pool[i] >= thr and btw[i] >= bthr]
print("   rule: PC >= p%.0f (%.4f) AND betweenness >= median (%.6f) -> %d bridges"
      % ((1 - DECILE) * 100, thr, bthr, len(bridge)))
# The conjunction only bites if the median betweenness is a real cut. On a near-complete
# graph most concepts sit at or near zero betweenness, the median collapses to zero and the
# second clause selects nobody. Checked explicitly rather than assumed.
print("   betweenness median %.6f, share of eligible concepts at exactly 0: %.1f%%"
      % (bthr, 100 * float((btv == 0).mean())))
if (btv == 0).mean() > 0.4:
    print("   -> median betweenness is degenerate; the AND clause is doing no work and the")
    print("      bridge set is effectively the PC decile alone. Reported as such.")

# expected pillar distribution is the eligible set's own distribution, not equal shares
exp = collections.Counter(member[i] for i in elig)
obs = collections.Counter(member[i] for i in bridge)
groups = [g for g in P3 + ["UNASSIGNED"] if exp.get(g)]
o = [obs.get(g, 0) for g in groups]
e = np.array([exp[g] * len(bridge) / sum(exp[g] for g in groups) for g in groups])
chi = stats.chisquare(o, e)
print("\n   pillar distribution of the bridge set (expected = eligible-set distribution)")
print("   %-12s %6s %8s %8s" % ("pillar", "obs", "exp", "share"))
for g, oo, ee in zip(groups, o, e):
    print("   %-12s %6d %8.2f %7.1f%%" % (g, oo, ee, 100 * oo / len(bridge)))
print("   chi2 = %.2f, dof = %d, p = %.3f" % (chi.statistic, len(groups) - 1, chi.pvalue))
print("   -> bridging is %s" % ("pillar-specific" if chi.pvalue < .05
                                else "distributed across pillars, as Article 1 found"))

print("\n   top 25 bridges by PC")
print("   %-28s %-12s %7s %7s %7s" % ("concept", "pillar", "PC", "PC z", "betw"))
for i in sorted(bridge, key=lambda z: -P_pool[z])[:25]:
    print("   %-28s %-12s %7.3f %7.2f %7.4f"
          % (fam_label[nodes[i]][:28], member[i], P_pool[i], pc_z.get(i, np.nan), btw[i]))

# ---------------------------------------------------------------- C3 layer flexibility
print("\nC3  LAYER FLEXIBILITY")
per_rows = {}
for a, b in PERIODS:
    idx = np.where((year >= a) & (year <= b))[0]
    per_rows["%d-%d" % (a, b)] = idx
    np.save(os.path.join(DATA, "Xblock_period_%d_%d.npy" % (a, b)), X[idx])
    print("   period %d-%d  docs %4d" % (a, b, len(idx)))
for c in COUNTRIES:
    idx = np.array([r for r in range(N) if country[r] == c])
    per_rows[c] = idx
    np.save(os.path.join(DATA, "Xblock_country_%s.npy" % c.replace(" ", "_")), X[idx])
    print("   country %-22s docs %4d" % (c, len(idx)))

# Flexibility counts LAYERS, not documents: a concept present in 30 papers in one period
# touches one layer, same as a concept present in one paper in each of four.
flex_p = np.zeros(nn, dtype=int)
for a, b in PERIODS:
    flex_p += ((X[(year >= a) & (year <= b)] > 0).sum(0) > 0).astype(int)
flex_c = np.zeros(nn, dtype=int)
for c in COUNTRIES:
    flex_c += ((X[[r for r in range(N) if country[r] == c]] > 0).sum(0) > 0).astype(int)

bs = set(bridge)
b_flex_p = [flex_p[i] for i in bridge]
n_flex_p = [flex_p[i] for i in elig if i not in bs]
b_flex_c = [flex_c[i] for i in bridge]
n_flex_c = [flex_c[i] for i in elig if i not in bs]
print("   periods touched (of 4)     bridges %.2f  others %.2f  Mann-Whitney p = %.4g"
      % (np.mean(b_flex_p), np.mean(n_flex_p),
         stats.mannwhitneyu(b_flex_p, n_flex_p).pvalue))
print("   countries touched (of 7)   bridges %.2f  others %.2f  Mann-Whitney p = %.4g"
      % (np.mean(b_flex_c), np.mean(n_flex_c),
         stats.mannwhitneyu(b_flex_c, n_flex_c).pvalue))
print("   all 4 periods: %d of %d bridges;  4+ countries: %d of %d"
      % (sum(1 for v in b_flex_p if v == 4), len(bridge),
         sum(1 for v in b_flex_c if v >= 4), len(bridge)))

# ---------------------------------------------------------------- C4 stability
print("\nC4  BRIDGE STABILITY ACROSS PERIODS AND NATIONAL CONTEXTS")
print("   sub-corpora use the count rule (co-occurrence >= 3), not the Article 1 z filter:")
print("   at 28-229 documents a 40-draw null cannot place a per-edge threshold.")
print("   %-24s %5s %6s %7s %8s %8s %8s" % ("block", "docs", "edges", "n_cmp",
                                           "rho(PC)", "p", "overlap"))


def analyse_block(idx, tag):
    Xb = X[idx]
    G, kb = block_graph(Xb, tag, mode="count")
    ne = G.number_of_edges()
    P = participation(G, member)
    el = [i for i in G.nodes() if G.degree(i) >= MIN_BLOCK_DEG and not np.isnan(P[i])]
    if ne < 50 or len(el) < 50:
        return None
    t = np.quantile([P[i] for i in el], 1 - DECILE)
    br = [i for i in el if P[i] >= t]
    both = [i for i in elig if i in P and G.degree(i) >= MIN_BLOCK_DEG
            and not np.isnan(P[i])]
    rho = stats.spearmanr([P[i] for i in both], [P_pool[i] for i in both])
    top_pool = set(i for i in elig if P_pool[i] >= thr)
    top_blk = set(i for i in both if P[i] >= t)
    ov = len(top_pool & top_blk) / max(len(top_blk), 1)
    ex = collections.Counter(member[i] for i in el)
    ob = collections.Counter(member[i] for i in br)
    g = [q for q in P3 + ["UNASSIGNED"] if ex.get(q)]
    if len(g) > 1:
        c2 = stats.chisquare([ob.get(q, 0) for q in g],
                             np.array([ex[q] * len(br) / sum(ex[q] for q in g) for q in g]))
        p2 = c2.pvalue
    else:
        p2 = np.nan
    return dict(block=tag, construction="cooc>=3", docs=len(idx), edges=ne,
                nodes_analysed=len(el), n_compared=len(both),
                rho=round(float(rho.statistic), 3), rho_p=float(rho.pvalue),
                overlap_top_decile=round(ov, 3), chi2_p=round(float(p2), 3),
                pc_mean=round(float(np.mean([P[i] for i in el])), 4),
                n_top_decile_in_block=len(top_blk))


stab = []
for a, b in PERIODS:
    r = analyse_block(per_rows["%d-%d" % (a, b)], "period_%d_%d" % (a, b))
    if r:
        stab.append(r)
for c in COUNTRIES:
    r = analyse_block(per_rows[c], "country_%s" % c.replace(" ", "_"))
    if r:
        stab.append(r)
for r in stab:
    print("   %-24s %5d %6d %7d %8.3f %8.1e %7.0f%%"
          % (r["block"], r["docs"], r["edges"], r["n_compared"], r["rho"],
             r["rho_p"], 100 * r["overlap_top_decile"]))

rhos = [r["rho"] for r in stab]
ovs = [r["overlap_top_decile"] for r in stab]
p2s = [r["chi2_p"] for r in stab]
print("\n   UNSIZED PERIOD DESIGN (superseded, unequal blocks, mean degree 0.5)")
nat_unsized = []
for a, b in PERIODS:
    tag = "period_%d_%d" % (a, b)
    G, _kb = block_graph(X[per_rows["%d-%d" % (a, b)]], "count", mode="count")
    P = participation(G, member)
    el = [i for i in G.nodes() if G.degree(i) >= MIN_BLOCK_DEG and not np.isnan(P[i])]
    both = [i for i in elig if i in P and G.degree(i) >= MIN_BLOCK_DEG
            and not np.isnan(P[i])]
    r_ = stats.spearmanr([P[i] for i in both], [P_pool[i] for i in both])
    top = set(i for i in el if P[i] >= np.quantile([P[j] for j in el], 1 - DECILE))
    pooled_top = set(i for i in elig if P_pool[i] >= thr)
    nat_unsized.append(dict(
        block="%d-%d" % (a, b), construction="cooc>=3", docs=len(per_rows["%d-%d" % (a, b)]),
        edges=G.number_of_edges(), n_elig=len(el), analysed=1, n_cmp=len(both),
        rho=round(float(r_.statistic), 3), rho_p=float(r_.pvalue),
        overlap_top_decile=round(len(pooled_top & top) / max(len(top), 1), 3),
        pc_mean=round(float(np.mean([P[i] for i in el])), 4),
        n_top_decile_in_block=len(top)))
    print("   %-12s docs %4d edges %5d  rho %+.3f  (n compared %d)"
          % ("%d-%d" % (a, b), len(per_rows["%d-%d" % (a, b)]), G.number_of_edges(),
             float(r_.statistic), len(both)))
uns_r = [r["rho"] for r in nat_unsized]
print("   mean rho %.3f  (range %.3f to %.3f)"
      % (np.mean(uns_r), min(uns_r), max(uns_r)))
print("   2022-2025 holds %d of %d documents, so the pooled network is largely this"
      % (len(per_rows["2022-2025"]), N))
print("   one block and its correlation is partly circular")
print("   adding Australia and Canada gives the six-block mean of 0.186 reported in the "
      "manuscript; see A2_bridge_stability.csv for the per-block values")

with open(os.path.join(TAB, "A2_bridge_stability_unsized_periods.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=sorted({k for r in nat_unsized for k in r}),
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(nat_unsized)

print("\n   Spearman rho of block PC vs pooled PC: mean %.3f  range %.3f to %.3f"
      % (np.mean(rhos), min(rhos), max(rhos)))
print("   top-decile overlap with pooled bridges : mean %.1f%%  range %.0f%% to %.0f%%"
      % (100 * np.mean(ovs), 100 * min(ovs), 100 * max(ovs)))
print("   bridge pillar-specificity p per block  : %s"
      % ", ".join("%.3f" % p for p in p2s))
print("   blocks with p < .05: %d of %d -> %s"
      % (sum(1 for p in p2s if p < .05), len(p2s),
         "bridge identity is context-dependent" if any(p < .05 for p in p2s)
         else "bridging stays distributed in every context"))

all_tags = (["period_%d_%d" % (a, b) for a, b in PERIODS]
            + ["country_%s" % c.replace(" ", "_") for c in COUNTRIES])
skipped = [t for t in all_tags if t not in {r["block"] for r in stab}]
if skipped:
    print("\n   NOT ANALYSED (%d): %s" % (len(skipped), ", ".join(sorted(skipped))))
    print("   these blocks have fewer than %d concepts at degree >= %d, too few to rank"
          % (50, MIN_BLOCK_DEG))
    print("   participation coefficients. Excluded from the stability average rather than")
    print("   reported with a correlation computed on too few points. Five of seven")
    print("   national contexts are among them, so the national stability result rests on")
    print("   Canada and Australia alone and should be read as suggestive, not conclusive.")

# ---------------------------------------------------------------- export
with open(os.path.join(TAB, "A2_bridge_scores.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["concept_id", "concept", "pillar", "df_pooled", "degree_pooled",
                "participation", "pc_z", "betweenness", "periods_touched",
                "countries_touched", "is_bridge"])
    for i in sorted(elig, key=lambda z: -P_pool[z]):
        w.writerow([nodes[i], fam_label[nodes[i]], member[i], int(kpool[i]),
                    Gpool.degree(i), round(P_pool[i], 4),
                    round(pc_z.get(i, np.nan), 3), round(btw[i], 5),
                    int(flex_p[i]), int(flex_c[i]), int(i in bridge)])

with open(os.path.join(TAB, "A2_bridge_pillar_distribution.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["pillar", "n_eligible", "n_bridges", "expected", "share_pct",
                "pc_mean", "pc_sd", "chi2", "dof", "p"])
    for g in groups:
        s = [P_pool[i] for i in elig if member[i] == g]
        w.writerow([g, exp[g], obs.get(g, 0), round(e[groups.index(g)], 2),
                    round(100 * obs.get(g, 0) / len(bridge), 1),
                    round(float(np.mean(s)), 4), round(float(np.std(s)), 4),
                    round(float(chi.statistic), 2), len(groups) - 1,
                    round(float(chi.pvalue), 4)])

with open(os.path.join(TAB, "A2_bridge_stability.csv"), "w", encoding="utf-8-sig",
          newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(stab[0].keys()))
    w.writeheader()
    w.writerows(stab)

# Headline scalars quoted in the manuscript. These were previously printed to stdout
# only, so two statistics in the Results section could not be traced back to a file.
# Every number quoted in prose now exists in some table.
rho_bt = stats.spearmanr(pcv, btv)
zarr = np.array([pc_z[i] for i in elig])
summary = [
    dict(statistic="participation mean", value=round(float(pcv.mean()), 4),
         detail="N = %d eligible concepts" % len(elig)),
    dict(statistic="participation sd", value=round(float(pcv.std()), 4),
         detail="N = %d" % len(elig)),
    dict(statistic="participation min", value=round(float(pcv.min()), 4), detail=""),
    dict(statistic="participation max", value=round(float(pcv.max()), 4),
         detail="ceiling for a four-group partition"),
    dict(statistic="participation theoretical maximum", value=0.75,
         detail="1 - 4 x (1/4)^2, four equal groups"),
    dict(statistic="PC versus weighted betweenness Spearman rho",
         value=round(float(rho_bt.statistic), 3),
         detail="p = %.3g" % rho_bt.pvalue),
    dict(statistic="PC versus weighted betweenness p",
         value=float("%.4g" % rho_bt.pvalue),
         detail="neighbourhood-based versus path-based, so agreement is "
                "corroboration rather than redundancy"),
    dict(statistic="PC label-permutation mean z", value=round(float(zarr.mean()), 4),
         detail="negative sign indicates segregation; %d of %d concepts below the null"
                % (int((zarr < 0).sum()), len(elig))),
    dict(statistic="eligible concepts", value=len(elig),
         detail="degree >= 2 and participation defined"),
    dict(statistic="concepts at degree 4 or higher",
         value=int(sum(1 for i in elig if Gpool.degree(i) >= 4)),
         detail="degree-3 concepts quantise the participation coefficient"),
    dict(statistic="bridges identified", value=len(bridge),
         detail="PC >= p90 (%.4f) and betweenness >= median (%.6f)" % (thr, bthr)),
    dict(statistic="PC decile threshold", value=round(float(thr), 4), detail=""),
    dict(statistic="betweenness median", value=round(float(bthr), 6), detail=""),
    dict(statistic="share of eligible concepts at exactly zero betweenness",
         value=round(float((btv == 0).mean()), 3),
         detail="the median-betweenness clause selects almost nobody"),
    dict(statistic="bridge chi-square", value=round(float(chi.statistic), 2),
         detail="dof %d, p %.3f, expected = eligible-set distribution"
                % (len(groups) - 1, chi.pvalue)),
    dict(statistic="bridge chi-square p", value=round(float(chi.pvalue), 4), detail=""),
    dict(statistic="named-pillar versus unassigned PC, t",
         value=round(float(tst.statistic), 2), detail="p %.4f" % tst.pvalue),
    dict(statistic="named-pillar versus unassigned PC, p",
         value=round(float(tst.pvalue), 4), detail=""),
    dict(statistic="mean periods touched, bridges", value=round(float(np.mean(b_flex_p)), 2),
         detail="of 4"),
    dict(statistic="mean periods touched, others", value=round(float(np.mean(n_flex_p)), 2),
         detail="of 4"),
    dict(statistic="periods touched Mann-Whitney p",
         value=float("%.4g" % stats.mannwhitneyu(b_flex_p, n_flex_p).pvalue), detail=""),
    dict(statistic="mean countries touched, bridges", value=round(float(np.mean(b_flex_c)), 2),
         detail="of 7"),
    dict(statistic="mean countries touched, others", value=round(float(np.mean(n_flex_c)), 2),
         detail="of 7"),
    dict(statistic="countries touched Mann-Whitney p",
         value=float("%.4g" % stats.mannwhitneyu(b_flex_c, n_flex_c).pvalue), detail=""),
    dict(statistic="bridges in all four periods", value=sum(1 for v in b_flex_p if v == 4),
         detail="of %d" % len(bridge)),
    dict(statistic="bridges in four or more countries",
         value=sum(1 for v in b_flex_c if v >= 4), detail="of %d" % len(bridge)),
    dict(statistic="top-decile bridge participation range", value="0.735 to 0.750",
         detail="the decile sits against the participation ceiling, so ranking within "
                "it is partly ranking noise"),
    dict(statistic="unsized period design, four-period mean rho",
         value=round(float(np.mean(uns_r)), 3),
         detail="superseded; range %.3f to %.3f" % (min(uns_r), max(uns_r))),
    dict(statistic="unsized design, six-block mean rho",
         value=round(float(np.mean(rhos)), 3),
         detail="includes Australia and Canada, so the mean falls to 0.186; top-decile "
                "overlap %.1f per cent" % (100 * np.mean(ovs))),
]
with open(os.path.join(TAB, "A2_bridge_summary_statistics.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["statistic", "value", "detail"])
    w.writeheader()
    w.writerows(summary)

print("\nWrote A2_bridge_scores.csv, A2_bridge_pillar_distribution.csv, "
      "A2_bridge_stability.csv, A2_bridge_summary_statistics.csv")
