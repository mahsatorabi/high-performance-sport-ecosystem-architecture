"""
ARTICLE 2 - Stage C2: bridge stability on size-matched blocks, plus a reliability check.

Stage C reported a weak stability result: mean Spearman rho of 0.186 between block-level
participation coefficients and the pooled network. Two things could produce that, and they
mean very different things.

  1. BRIDGES GENUINELY CHANGE across periods and national contexts. A substantive finding.
  2. THE MEASUREMENT IS NOISY at small block sizes. A power artefact, and nothing to report.

They are not distinguishable from stage C as written, because the blocks were wildly unequal:
2022-2025 held 229 of 448 documents and the pooled network is largely that one block, so its
rho was partly circular. The five analysable national contexts ranged from 36 to 50 documents
and 260 to 324 edges, and rho tracked block size rather than context.

This stage separates the two explanations.

  D1  SIZE-MATCHED BLOCKS. Chronological quartiles with exactly 112 documents each, the same
      corpus volume every time. No block dominates the pooled network, so no block's rho can
      be circular. The natural year-bounded periods are retained alongside for comparability
      with Article 1's temporal claims, and reported as a separate, weaker design.

  D2  NATIONAL CONTEXTS. Cannot be size-matched, because the unit is a real context and its
      size is a property of the field, not a free parameter. Reported as observed, with the
      size range stated, and with the power confound quantified rather than hidden. Documents
      with no parseable lead country are pooled into one unclassified block.

  D3  SPLIT-HALF RELIABILITY. The decisive test, and it needs no cross-block comparison at all.
      Split each block's documents in half, build a network from each half, and correlate the
      two PC vectors. This asks how well PC replicates inside ONE context. If split-half
      reliability is also near 0.2, the cross-block instability is measurement noise and there
      is no substantive stability result to report. If split-half reliability is high while
      cross-block rho is low, the instability is real.

  D4  POWER DIAGNOSTIC. Regresses rho on block size across all blocks. If rho is largely
      explained by how many edges a block has, then every stability number in this paper is
      substantially a statement about statistical power.
"""
import os, json, csv, collections
import numpy as np
import networkx as nx
from scipy import stats

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")

MIN_COOC = 3
MIN_BLOCK_DEG = 3
DECILE = 0.10
P3 = ["GOVERNANCE", "INNOVATION", "TALENT"]

blob = json.load(open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8"))
fam_label = blob["fam_label"]
pillar = {int(k): v for k, v in
           json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
nodes = sorted(pillar)
nn = len(nodes)
M = np.load(os.path.join(DATA, "M_window.npy")).astype(np.float32)
X = M[:, nodes]
N = X.shape[0]
year = np.load(os.path.join(DATA, "years_window.npy"))
country = json.load(open(os.path.join(DATA, "country_window.json")))
member = {i: pillar[nodes[i]] for i in range(nn)}

print("=" * 78)
print("ARTICLE 2 - STAGE C2  size-matched stability and split-half reliability")
print("=" * 78)
print("windowed documents %d | concepts %d" % (N, nn))
print("all sub-corpora use the count rule (co-occurrence >= %d); the Article 1 z filter" % MIN_COOC)
print("cannot be placed by a null fitted on %d documents" % N)


# ---------------------------------------------------------------- helpers
def build(idx):
    Xb = X[idx]
    Cb = (Xb.T @ Xb).astype(float)
    np.fill_diagonal(Cb, 0)
    kb = Xb.sum(0).astype(float)
    A = Cb / np.maximum(kb[:, None] + kb[None, :] - Cb, 1e-9)
    A = A * (Cb >= MIN_COOC)
    np.fill_diagonal(A, 0)
    G = nx.from_numpy_array(A)
    for i in range(nn):
        G.nodes[i]["df"] = float(kb[i])
    return G


def participation(G):
    P = {}
    for i in G.nodes():
        k = G.degree(i)
        if k == 0:
            P[i] = np.nan
            continue
        acc = collections.Counter()
        for j in G.neighbors(i):
            acc[member[j]] += 1
        P[i] = 1.0 - sum((c / k) ** 2 for c in acc.values())
    return P


def eligible(G, min_deg=MIN_BLOCK_DEG):
    P = participation(G)
    return P, [i for i in G.nodes() if G.degree(i) >= min_deg and not np.isnan(P[i])]


def top_decile(P, el):
    if len(el) < 20:
        return set()
    t = np.quantile([P[i] for i in el], 1 - DECILE)
    return set(i for i in el if P[i] >= t)


# ---------------------------------------------------------------- D1 size-matched blocks
print("\n" + "-" * 78)
print("D1  SIZE-MATCHED CHRONOLOGICAL QUARTILES (%d documents each)" % (N // 4))
print("-" * 78)

order = np.argsort(year, kind="stable")
q = N // 4
QUART = {}
for b in range(4):
    lo, hi = b * q, (b + 1) * q if b < 3 else N
    QUART["Q%d %d-%d" % (b + 1, year[order[lo]], year[order[hi - 1]])] = order[lo:hi]
    idx = order[lo:hi]
    print("   Q%d  %d docs  %d-%d  (years: %s)"
          % (b + 1, len(idx), year[idx].min(), year[idx].max(),
             ", ".join(str(v) for v in sorted(set(year[idx].tolist())))))

# pooled network, rebuilt on the same count rule so the two are comparable
Gpool = build(np.arange(N))
Ppool, epool = eligible(Gpool)
top_pool = top_decile(Ppool, epool)
print("\n   pooled reference: %d edges, %d eligible concepts, %d in the top decile"
      % (Gpool.number_of_edges(), len(epool), len(top_pool)))


def cross_block(idx, label):
    G = build(idx)
    P, el = eligible(G)
    if len(el) < 50:
        return dict(block=label, docs=len(idx), edges=G.number_of_edges(),
                    n_elig=len(el), analysed=0)
    both = [i for i in epool if i in P and G.degree(i) >= MIN_BLOCK_DEG
            and not np.isnan(P[i])]
    if len(both) < 30:
        return dict(block=label, docs=len(idx), edges=G.number_of_edges(),
                    n_elig=len(el), analysed=0)
    rho = stats.spearmanr([P[i] for i in both], [Ppool[i] for i in both])
    tb = top_decile(P, el)
    ov = len(top_pool & tb) / max(len(tb), 1)
    ex = collections.Counter(member[i] for i in el)
    ob = collections.Counter(member[i] for i in tb)
    g = [q for q in P3 + ["UNASSIGNED"] if ex.get(q)]
    if len(g) > 1:
        c2 = stats.chisquare([ob.get(q, 0) for q in g],
                             np.array([ex[q] * len(tb) / sum(ex[q] for q in g) for q in g]))
        p2 = float(c2.pvalue)
    else:
        p2 = np.nan
    return dict(block=label, docs=len(idx), edges=G.number_of_edges(),
                n_elig=len(el), analysed=1, n_cmp=len(both),
                rho=round(float(rho.statistic), 3), rho_p=float(rho.pvalue),
                overlap=round(ov, 3), chi2_p=round(p2, 3))


print("\n   %-22s %5s %6s %7s %9s %9s %8s" % ("block", "docs", "edges", "n_cmp",
                                              "rho(PC)", "p", "overlap"))
rows = [cross_block(idx, lb) for lb, idx in QUART.items()]
for r in rows:
    if r["analysed"]:
        print("   %-22s %5d %6d %7d %9.3f %9.1e %7.0f%%"
              % (r["block"], r["docs"], r["edges"], r["n_cmp"], r["rho"],
                 r["rho_p"], 100 * r["overlap"]))
    else:
        print("   %-22s %5d %6d %7d   not analysable (n_elig %d)"
              % (r["block"], r["docs"], r["edges"], r["n_elig"], r["n_elig"]))
ok = [r for r in rows if r["analysed"]]
if ok:
    print("   size-matched mean rho %.3f  (range %.3f to %.3f)"
          % (np.mean([r["rho"] for r in ok]), min(r["rho"] for r in ok),
             max(r["rho"] for r in ok)))

# ---------------------------------------------------------------- D2 national contexts
print("\n" + "-" * 78)
print("D2  NATIONAL CONTEXTS  (not size-matchable; sizes are a property of the field)")
print("-" * 78)
nat = []
# lead_country is None for documents with no parseable affiliation; those are pooled
# separately as an unclassified block rather than dropped silently.
ALL_CTX = sorted(set(country), key=lambda v: (v is None, v or ""))
for c in ALL_CTX:
    idx = np.array([r for r in range(N) if country[r] == c])
    r = cross_block(idx, c if c else "(no lead country)")
    nat.append(r)
    if r["analysed"]:
        print("   %-22s %5d %6d %7d %9.3f %9.1e %7.0f%%"
              % (r["block"], r["docs"], r["edges"], r["n_cmp"], r["rho"],
                 r["rho_p"], 100 * r["overlap"]))
    else:
        print("   %-22s %5d %6d   not analysable (n_elig %d)"
              % (r["block"], r["docs"], r["edges"], r["n_elig"]))
n_none = sum(1 for r in nat if r["block"] == "(no lead country)")
nok = [r for r in nat if r["analysed"]]
print("   %d of %d contexts analysable; document counts range %d to %d"
      % (len(nok), len(nat), min(r["docs"] for r in nat), max(r["docs"] for r in nat)))

# ---------------------------------------------------------------- D3 split-half reliability
print("\n" + "-" * 78)
print("D3  SPLIT-HALF RELIABILITY  (does PC replicate inside ONE context?)")
print("-" * 78)
print("   each block split in half by document, independent network per half, PC vectors")
print("   correlated. This is the ceiling on any cross-block stability claim.")
print("   %-22s %14s %14s %9s" % ("block", "half docs", "edges per half", "rho_half"))


def split_half(idx, label, seed=21):
    rng = np.random.default_rng(seed)
    idx = np.asarray(idx)
    perm = rng.permutation(len(idx))
    h1, h2 = idx[perm[:len(idx) // 2]], idx[perm[len(idx) // 2:]]
    G1, G2 = build(h1), build(h2)
    P1, e1 = eligible(G1)
    P2, e2 = eligible(G2)
    both = [i for i in e1 if i in P2 and not np.isnan(P2[i])]
    if len(both) < 30:
        return dict(block=label, half_docs=len(h1), edges=min(G1.number_of_edges(),
                                                               G2.number_of_edges()),
                    n_cmp=len(both), rho_half=np.nan, analysed=0)
    rho = stats.spearmanr([P1[i] for i in both], [P2[i] for i in both])
    return dict(block=label, half_docs=len(h1),
                edges=min(G1.number_of_edges(), G2.number_of_edges()),
                n_cmp=len(both), rho_half=round(float(rho.statistic), 3),
                rho_p=float(rho.pvalue), analysed=1)


rel = [split_half(idx, lb) for lb, idx in QUART.items()]
for r in rel:
    print("   %-22s %14d %14d %9s"
          % (r["block"], r["half_docs"], r["edges"],
             "%.3f" % r["rho_half"] if r["analysed"] else "n/a"))
for c in ALL_CTX:
    idx = np.array([r for r in range(N) if country[r] == c])
    r = split_half(idx, c if c else "(no lead country)")
    rel.append(r)
    if r["analysed"]:
        print("   %-22s %14d %14d %9.3f"
              % (r["block"], r["half_docs"], r["edges"], r["rho_half"]))
r_ok = [r for r in rel if r["analysed"]]
print("\n   split-half rho: mean %.3f  median %.3f  range %.3f to %.3f  (%d blocks)"
      % (np.mean([r["rho_half"] for r in r_ok]),
         np.median([r["rho_half"] for r in r_ok]),
         min(r["rho_half"] for r in r_ok), max(r["rho_half"] for r in r_ok), len(r_ok)))

# ---------------------------------------------------------------- D4 power diagnostic
print("\n" + "-" * 78)
print("D4  POWER DIAGNOSTIC  (is rho just a function of block size?)")
print("-" * 78)
allb = [r for r in rows + nat if r["analysed"]]
if len(allb) >= 4:
    lg = np.log([r["edges"] for r in allb])
    rh = np.array([r["rho"] for r in allb])
    pr = stats.pearsonr(lg, rh)
    sp = stats.spearmanr(lg, rh)
    print("   Pearson  rho vs log(edges)  r = %+.3f  p = %.3f" % (pr.statistic, pr.pvalue))
    print("   Spearman rho vs log(edges)  r = %+.3f  p = %.3f" % (sp.statistic, sp.pvalue))
    fit = np.polyfit(lg, rh, 1)
    print("   fitted slope %+.3f per log-edge; an e-fold more edges buys %+.3f rho"
          % (fit[0], fit[0]))
    print("   variance in rho explained by block size: R2 = %.3f"
          % (1 - np.var(rh - np.polyval(fit, lg)) / np.var(rh)))
    print("\n   %-22s %7s %9s %10s" % ("block", "edges", "rho", "rho fitted"))
    for lb, g, o in zip([r["block"] for r in allb], lg, rh):
        print("   %-22s %7d %9.3f %10.3f" % (lb, int(np.exp(g)), o, np.polyval(fit, g)))

# ---------------------------------------------------------------- verdict
print("\n" + "=" * 78)
print("VERDICT")
print("=" * 78)
xs = np.mean([r["rho"] for r in ok]) if ok else np.nan
half = np.median([r["rho_half"] for r in r_ok]) if r_ok else np.nan
print("   cross-block rho (size-matched quartiles) : %.3f" % xs)
print("   split-half rho (same block, no split by context): %.3f" % half)
if np.isnan(half):
    print("   -> split-half reliability not estimable; no stability claim is supportable.")
elif half <= xs * 1.5:
    print("   -> cross-block correlation is within reach of what the measure achieves on a")
    print("      single context. The stability result is dominated by measurement noise and")
    print("      must be reported as a limitation, not as a finding.")
else:
    print("   -> PC replicates far better within a context than across contexts, so the")
    print("      cross-block instability is substantive.")

# ---------------------------------------------------------------- export
with open(os.path.join(TAB, "A2_bridge_stability_sizematched.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=sorted({k for r in rows + nat
                                             for k in r}),
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(rows + nat)

with open(os.path.join(TAB, "A2_bridge_splithalf_reliability.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=sorted({k for r in rel for k in r}),
                       extrasaction="ignore")
    w.writeheader()
    w.writerows(rel)

print("\nWrote A2_bridge_stability_sizematched.csv, A2_bridge_splithalf_reliability.csv")
