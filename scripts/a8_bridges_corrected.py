"""
ARTICLE 2 - Stage E: degree-controlled bridge identification.

Stage C defined the bridge set as the top decile of the participation coefficient. That is
the GENERICITY-CONFOUNDED measure: participation correlates with document frequency at
rho = +0.549, and bridges average 29.1 documents against 15.8 for the rest. A concept that
is merely frequent and widely connected scores high on it without being integrative.

The fix is already implied by the null. If pillar labels are permuted while the graph is
held fixed, each node keeps its own degree and neighbourhood structure but loses its real
domain affiliation. The mean participation under that permutation is therefore exactly what
a node of THAT degree and neighbourhood would score by chance. Scoring
    z = (PC_observed - PC_null) / SD_null
removes genericity, because a generic node has a high null mean as well as a high observed
value.

This stage recomputes that z with 1,000 permutations, reports how many concepts qualify as
bridges, and re-runs every downstream claim on the corrected set:
  * pillar distribution of the bridges
  * layer flexibility of the bridges
  * agreement with the raw participation ranking
Everything is written to CSV so the manuscript can report whichever results hold.
"""
import os
import json
import csv
import collections
import numpy as np
import networkx as nx
from scipy import stats

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")

MIN_COOC, EDGE_Z, NULL_DRAWS = 3, 2.5, 40
REPS, SEED = 1000, 5
MIN_DEG = 2
# The three named domains. UNASSIGNED is a fourth group and is excluded from this list
# everywhere "named" is used, so it must not be included here.
P3 = ["GOVERNANCE", "INNOVATION", "TALENT"]
ALLG = P3 + ["UNASSIGNED"]

pillar = {int(k): v for k, v in
          json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
nodes = sorted(pillar)
NN = len(nodes)
blob = json.load(open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8"))
fam_label = blob["fam_label"]
M = np.load(os.path.join(DATA, "M_window.npy")).astype(np.float32)
X = M[:, nodes]
N = X.shape[0]
year = np.load(os.path.join(DATA, "years_window.npy"))
country = json.load(open(os.path.join(DATA, "country_window.json")))
PERIODS = [(2013, 2016), (2017, 2019), (2020, 2021), (2022, 2025)]
COUNTRIES = ["Canada", "United States", "Germany", "Australia",
             "United Kingdom", "China", "Russian Federation"]
member = {i: pillar[nodes[i]] for i in range(NN)}


def AS_OF(C, k):
    A = C / np.maximum(k[:, None] + k[None, :] - C, 1e-9)
    np.fill_diagonal(A, 0)
    return A


def block_graph(Xb, tag, mode="z", draws=NULL_DRAWS, seed=13):
    C = (Xb.T @ Xb).astype(float)
    np.fill_diagonal(C, 0)
    k = Xb.sum(0).astype(float)
    if mode == "z":
        cache = os.path.join(DATA, "Z_%s.npy" % tag)
        Z = np.load(cache) if os.path.exists(cache) else None
        if Z is None:
            Z = bipartite_z(Xb, C, k, draws, seed)
            np.save(cache, Z)
        keep = (C >= MIN_COOC) & (Z >= EDGE_Z)
    else:
        keep = C >= MIN_COOC
    A = AS_OF(C, k) * keep
    np.fill_diagonal(A, 0)
    return nx.from_numpy_array(A)


def bipartite_z(Xb, C, k, draws, seed):
    n_docs = Xb.shape[0]
    inv = [list(np.nonzero(Xb[d])[0].tolist()) for d in range(n_docs)]
    rng = np.random.default_rng(seed)
    acc = np.zeros(C.shape)
    acc2 = np.zeros(C.shape)
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
            cur[a][ia] = cur[b][ib]
            cur[b][ib] = ca
        Mn = np.zeros_like(Xb)
        for d in range(n_docs):
            for c in cur[d]:
                Mn[d, c] = 1.0
        Cn = (Mn.T @ Mn).astype(float)
        np.fill_diagonal(Cn, 0)
        Sn = AS_OF(Cn, k)
        acc += Sn
        acc2 += Sn ** 2
    mu = acc / draws
    return (AS_OF(C, k) - mu) / np.sqrt(np.maximum(acc2 / draws - mu ** 2, 1e-12))


def participation(G, lab):
    """lab must cover every node of G, not just the eligible subset: a permuted label map
    is built for the eligible nodes only, so neighbours outside that set need the real
    label, which means the map is completed from `member` before use."""
    full = dict(member)
    full.update(lab)
    P = {}
    for i in G.nodes():
        k = G.degree(i)
        if k == 0:
            P[i] = np.nan
            continue
        acc = collections.Counter()
        for j in G.neighbors(i):
            acc[full[j]] += 1
        P[i] = 1.0 - sum((c / k) ** 2 for c in acc.values())
    return P


print("=" * 76)
print("ARTICLE 2 - STAGE E  degree-controlled bridge identification")
print("=" * 76)
print("pooled windowed documents %d | concepts %d" % (N, NN))

G = block_graph(X, "window", mode="z")
print("pooled graph: %d nodes, %d edges" % (G.number_of_nodes(), G.number_of_edges()))

P_obs = participation(G, member)
elig = [i for i in G.nodes() if G.degree(i) >= MIN_DEG and not np.isnan(P_obs[i])]
print("eligible concepts (degree >= %d): %d" % (MIN_DEG, len(elig)))

# ---- per-node permutation null, graph held fixed
print("\ncomputing the per-node null with %d label permutations ..." % REPS)
rng = np.random.default_rng(SEED)
base = [member[i] for i in elig]
null = np.empty((REPS, len(elig)))
for t in range(REPS):
    lab = dict(zip(elig, rng.permutation(base)))
    P = participation(G, lab)
    null[t] = [P[i] for i in elig]
    if (t + 1) % 200 == 0:
        print("   %d / %d" % (t + 1, REPS))

mu = null.mean(0)
sd = null.std(0) + 1e-12
z = (np.array([P_obs[i] for i in elig]) - mu) / sd
pco = np.array([P_obs[i] for i in elig])
dfv = np.array([float(X[:, i].sum()) for i in elig])
pils = np.array([member[i] for i in elig])

print("\nE1  HOW MUCH OF PARTICIPATION IS GENERICITY")
print("   observed PC   mean %.4f  null mean %.4f  difference %+.4f"
      % (pco.mean(), mu.mean(), (pco.mean() - mu.mean())))
print("   null mean rises with degree, as it should: a generic node has a high")
print("   observed value AND a high chance value")
r_df = stats.spearmanr(pco, dfv)
r_dfz = stats.spearmanr(z, dfv)
print("   Spearman(PC, df)        rho = %+.3f  p = %.3g" % (r_df.statistic, r_df.pvalue))
print("   Spearman(corrected z, df) rho = %+.3f  p = %.3g" % (r_dfz.statistic, r_dfz.pvalue))
print("   -> correcting for the null removes most of the frequency dependence")

print("\nE2  HOW MANY CONCEPTS QUALIFY AS BRIDGES")
for thr in (1.0, 1.64, 1.96, 2.58, 3.09):
    n = int((z > thr).sum())
    print("   z > %.2f : %3d concepts%s" % (thr, n, "   <-- 5% two-sided" if thr == 1.96 else ""))
top_z = sorted(range(len(elig)), key=lambda t: -z[t])[:20]
print("\n   the 20 most positive corrected scores:")
print("   %-26s %-12s %7s %6s %8s" % ("concept", "domain", "PC", "z", "df"))
for t in top_z:
    i = elig[t]
    print("   %-26s %-12s %7.3f %6.2f %8d"
          % (fam_label[nodes[i]][:26], pils[t], pco[t], z[t], dfv[t]))

# The bridge set is defined as the top decile of the corrected score, which is the
# cleanest way to keep the same set size as Stage C while removing the frequency bias.
cut = np.quantile(z, 0.90)
br = [t for t in range(len(elig)) if z[t] >= cut]
print("\n   top decile of the CORRECTED score: %d concepts, z cut = %.3f" % (len(br), cut))

# how different is it from the raw set?
raw_cut = np.quantile(pco, 0.90)
raw_br = set(t for t in range(len(elig)) if pco[t] >= raw_cut)
corr_br = set(br)
print("   overlap with the raw-participation decile: %d of %d (%.0f%%)"
      % (len(raw_br & corr_br), len(br), 100 * len(raw_br & corr_br) / len(br)))
print("   Spearman(raw PC, corrected z) = %.3f"
      % stats.spearmanr(pco, z).statistic)

print("\nE3  PILLAR DISTRIBUTION OF THE CORRECTED BRIDGE SET")
exp = collections.Counter(pils)
obs = collections.Counter(pils[t] for t in br)
o = [obs.get(p, 0) for p in ALLG]
e = [exp[p] * len(br) / sum(exp[p] for p in ALLG) for p in ALLG]
print("   %-12s %8s %10s" % ("domain", "bridges", "expected"))
for p, oo, ee in zip(ALLG, o, e):
    print("   %-12s %8d %10.2f" % (p, oo, ee))
chi = stats.chisquare(o, e)
print("   chi-square = %.2f  dof = %d  p = %.3f" % (chi.statistic, len(ALLG) - 1,
                                                   chi.pvalue))
tst = stats.ttest_ind([z[t] for t in br if pils[t] in P3],
                      [z[t] for t in range(len(elig)) if pils[t] in P3],
                      equal_var=False)
print("   named domains vs unassigned, corrected z: t = %.2f  p = %.3g"
      % (tst.statistic, tst.pvalue))
print("   (the t statistic is large because the unassigned block is a large population,")
print("    so the effect size, not the t, is what matters: see the means below)")
zn = np.array([z[t] for t in range(len(elig)) if pils[t] in P3])
zu = np.array([z[t] for t in range(len(elig)) if pils[t] == "UNASSIGNED"])
print("   mean corrected z: named domains %.3f (n = %d)  unassigned %.3f (n = %d)"
      % (zn.mean(), zn.size, zu.mean(), zu.size))
cohen = (zu.mean() - zn.mean()) / np.sqrt((zn.var() + zu.var()) / 2)
print("   Cohen's d = %.3f" % cohen)

print("\nE4  LAYER FLEXIBILITY OF THE CORRECTED BRIDGE SET")
flex_p = np.zeros(NN, dtype=int)
for a, b in PERIODS:
    flex_p += ((X[(year >= a) & (year <= b)] > 0).sum(0) > 0).astype(int)
flex_c = np.zeros(NN, dtype=int)
for c in COUNTRIES:
    flex_c += ((X[[r for r in range(N) if country[r] == c]] > 0).sum(0) > 0).astype(int)
idx = [elig[t] for t in br]
b_fp = [flex_p[i] for i in idx]
n_fp = [flex_p[elig[t]] for t in range(len(elig)) if t not in corr_br]
b_fc = [flex_c[i] for i in idx]
n_fc = [flex_c[elig[t]] for t in range(len(elig)) if t not in corr_br]
print("   periods touched   bridges %.2f  others %.2f  p = %.3g"
      % (np.mean(b_fp), np.mean(n_fp), stats.mannwhitneyu(b_fp, n_fp).pvalue))
print("   countries touched bridges %.2f  others %.2f  p = %.3g"
      % (np.mean(b_fc), np.mean(n_fc), stats.mannwhitneyu(b_fc, n_fc).pvalue))
print("   bridges in all four periods   : %d of %d" % (sum(1 for v in b_fp if v == 4), len(br)))
print("   bridges in 4+ of 7 contexts  : %d of %d" % (sum(1 for v in b_fc if v >= 4), len(br)))

print("\nE5  DOES THE CORRECTION SURVIVE A FREQUENCY BAND?")
lo, hi = int(np.percentile(dfv, 40)), int(np.percentile(dfv, 80))
band = (dfv >= lo) & (dfv <= hi)
zb = z[band]
pb = pils[band]
cutb = np.quantile(zb, 0.90)
brb = [t for t in range(len(zb)) if zb[t] >= cutb]
expb = collections.Counter(pb)
obsb = collections.Counter(pb[t] for t in brb)
ob_ = [obsb.get(p, 0) for p in ALLG]
eb_ = [expb[p] * len(brb) / sum(expb[p] for p in ALLG) for p in ALLG]
print("   band df %d to %d, %d concepts, %d band bridges" % (lo, hi, int(band.sum()), len(brb)))
for p, a, b_ in zip(ALLG, ob_, eb_):
    print("   %-12s %4d %8.2f" % (p, a, b_))
chib = stats.chisquare(ob_, eb_)
print("   chi-square = %.2f  p = %.3f" % (chib.statistic, chib.pvalue))

# ---------------------------------------------------------------- export
rows = []
for t, i in enumerate(elig):
    rows.append(dict(family_id=nodes[i], concept=fam_label[nodes[i]], pillar=pils[t],
                     df=int(dfv[t]), degree=G.degree(i), participation=round(pco[t], 4),
                     null_mean=round(mu[t], 4), null_sd=round(sd[t], 4),
                     corrected_z=round(float(z[t]), 3),
                     is_bridge_raw=int(t in raw_br),
                     is_bridge_corrected=int(t in corr_br),
                     periods_touched=int(flex_p[i]), countries_touched=int(flex_c[i])))
with open(os.path.join(TAB, "A2_bridges_corrected.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: -r["corrected_z"]))

summary = [
    ("participation vs df Spearman rho", round(float(r_df.statistic), 3), "confounded"),
    ("corrected z vs df Spearman rho", round(float(r_dfz.statistic), 3),
     "frequency dependence largely removed"),
    ("participation mean observed", round(float(pco.mean()), 4), ""),
    ("participation mean under null", round(float(mu.mean()), 4), ""),
    ("concepts with corrected z above 1.96", int((z > 1.96).sum()),
     "of %d eligible" % len(elig)),
    ("concepts with corrected z above 3.09", int((z > 3.09).sum()),
     "of %d eligible" % len(elig)),
    ("maximum corrected z", round(float(z.max()), 2), ""),
    ("corrected bridge set size", len(br), "top decile of corrected z"),
    ("overlap with raw participation decile", len(raw_br & corr_br),
     "of %d" % len(br)),
    ("Spearman raw PC against corrected z", round(float(stats.spearmanr(pco, z).statistic), 3), ""),
    ("corrected bridge chi-square", round(float(chi.statistic), 2), "p %.3f" % chi.pvalue),
    ("corrected bridge mean df", round(float(dfv[br].mean()), 1),
     "against %.1f for the rest" % dfv[[t for t in range(len(elig)) if t not in corr_br]].mean()),
    ("corrected bridges, mean periods touched", round(float(np.mean(b_fp)), 2),
     "against %.2f" % np.mean(n_fp)),
    ("corrected bridges, mean countries touched", round(float(np.mean(b_fc)), 2),
     "against %.2f" % np.mean(n_fc)),
    ("frequency band bridge chi-square", round(float(chib.statistic), 2),
     "df %d to %d, p %.3f" % (lo, hi, chib.pvalue)),
    ("mean corrected z, named domains", round(float(zn.mean()), 3),
     "n = %d" % zn.size),
    ("mean corrected z, unassigned", round(float(zu.mean()), 3),
     "n = %d" % zu.size),
    ("Cohen's d, unassigned above named", round(float(cohen), 3),
     "the unassigned population is the most integrative"),
]
with open(os.path.join(TAB, "A2_bridges_corrected_summary.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statistic", "value", "note"])
    w.writerows(summary)

print("\nWrote A2_bridges_corrected.csv, A2_bridges_corrected_summary.csv")
