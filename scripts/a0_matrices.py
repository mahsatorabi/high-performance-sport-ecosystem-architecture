"""
ARTICLE 2 - Stage A: construct the analysis matrices for the model paper.

Article 2 needs quantities Article 1 did not compute:
  * the concept x pillar network  (already in T5_pillars.csv)
  * concept x TIME and concept x COUNTRY membership, needed for RQ7 (are bridges
    stable across periods and national contexts, or context-specific?)
  * within-community co-occurrence structure by period and by country, needed to test
    whether the SEGREGATION finding of Article 1 holds inside each sub-corpus or is
    an artefact of pooling.
"""
import os, json, csv, collections
import numpy as np

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")
os.makedirs(DATA, exist_ok=True); os.makedirs(TAB, exist_ok=True)

blob = json.load(open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8"))
docs = blob["docs"]
fam_label = blob["fam_label"]
fams_L1, fams_L2, fams_L3 = blob["fams_L1"], blob["fams_L2"], blob["fams_L3"]
fam_of = {int(k): v for k, v in blob["fam_of_concept"].items()}
W0, W1 = 2013, 2025
PERIODS = [(2013, 2016), (2017, 2019), (2020, 2021), (2022, 2025)]

# ---- pillars from article 1 stage 5
pillar = {}
cluster = {}
for r in csv.DictReader(open(os.path.join(A1, "tables", "T5_pillars.csv"), encoding="utf-8-sig")):
    pillar[int(r["family_id"])] = r["pillar"]
    cluster[int(r["family_id"])] = int(r["cluster"])

print("=" * 78)
print("ARTICLE 2 - STAGE A  matrices")
print("=" * 78)
print("families %d | network families %d | window %d-%d"
      % (len(fam_label), len(pillar), W0, W1))

sel = [i for i, d in enumerate(docs) if W0 <= d["year"] <= W1]
print("windowed documents: %d" % len(sel))


def fam_matrix(present, idxs):
    """(n_docs x n_fams) binary over the given document indices."""
    nf = len(fam_label)
    M = np.zeros((len(idxs), nf), dtype=np.uint8)
    for r, i in enumerate(idxs):
        for f in present[i]:
            M[r, f] = 1
    return M


M = fam_matrix(fams_L3, sel)
years = np.array([docs[i]["year"] for i in sel])
country = [docs[i]["lead_country"] for i in sel]

np.save(os.path.join(DATA, "M_window.npy"), M)
np.save(os.path.join(DATA, "years_window.npy"), years)
json.dump(country, open(os.path.join(DATA, "country_window.json"), "w"))

# ---- network node mask
nodes = sorted(pillar)
print("network nodes: %d" % len(nodes))
json.dump({str(k): v for k, v in pillar.items()},
          open(os.path.join(DATA, "pillar_of.json"), "w"))

# ---- co-occurrence within each sub-corpus (for segregation stability)
def cooc(idx_rows):
    sub = M[idx_rows][:, nodes].astype(np.float32)
    C = (sub.T @ sub)
    np.fill_diagonal(C, 0)
    return C, sub.sum(0).astype(float)


C_all, deg_all = cooc(np.arange(len(sel)))
print("\nco-occurrence matrices built on the %d network nodes" % len(nodes))

# period blocks
print("\nPERIOD BLOCKS")
per_rows = {}
for a, b in PERIODS:
    idx = np.where((years >= a) & (years <= b))[0]
    per_rows["%d-%d" % (a, b)] = idx
    C, deg = cooc(idx)
    np.save(os.path.join(DATA, "C_period_%d_%d.npy" % (a, b)), C)
    np.save(os.path.join(DATA, "deg_period_%d_%d.npy" % (a, b)), deg)
    nz = int((deg > 0).sum())
    print("  %d-%d  docs %4d  nodes with df>0 %4d  mean df %6.1f  edges(df>=3) %5d"
          % (a, b, len(idx), nz, deg.mean(), int((C >= 3).sum() // 2)))

# country blocks (top countries only, min 25 docs in window for a usable network)
ccount = collections.Counter(c for c in country if c)
top_c = [c for c, n in ccount.most_common(8) if n >= 25]
print("\nCOUNTRY BLOCKS (>=25 windowed docs, top 8)")
for c in top_c:
    idx = np.array([k for k in range(len(sel)) if country[k] == c])
    C, deg = cooc(idx)
    np.save(os.path.join(DATA, "C_country_%s.npy" % c.replace(" ", "_")), C)
    np.save(os.path.join(DATA, "deg_country_%s.npy" % c.replace(" ", "_")), deg)
    nz = int((deg > 0).sum())
    print("  %-20s docs %4d  nodes with df>0 %4d  mean df %6.1f  edges(df>=3) %5d"
          % (c, len(idx), nz, deg.mean(), int((C >= 3).sum() // 2)))

# ---- segregation of Article 1 re-tested inside sub-corpora (a key Article 2 claim)
print("\n" + "=" * 78)
print("Article 1's segregation finding re-tested within each sub-corpus")
print("=" * 78)


def segregation(C, deg, pillar_map, reps=200, seed=3):
    """Re-run the Article 1 boundary-crossing test on a given co-occurrence matrix.
    Returns observed share of shortest paths crossing a pillar boundary + null."""
    import networkx as nx
    keep = [i for i in range(len(nodes)) if deg[i] > 0]
    As = C[np.ix_(keep, keep)]
    d = deg[keep]
    W = As / np.maximum(np.sqrt(np.outer(d, d)), 1e-9)
    G = nx.from_numpy_array(W)
    idx_of = {i: nodes[i] for i in range(len(nodes))}
    G = nx.relabel_nodes(G, {i: idx_of[i] for i in range(len(nodes))}, copy=True)
    G = G.subgraph(keep).copy()
    mem = {i: pillar_map[i] for i in G.nodes()}
    piv = sorted(np.random.default_rng(seed).choice(sorted(G.nodes()),
                                                  size=min(150, G.number_of_nodes()),
                                                  replace=False).tolist())
    tot = cross = 0
    for s in piv:
        for dst, path in nx.single_source_shortest_path(G, s, cutoff=6).items():
            if dst == s:
                continue
            tot += 1
            pl = [mem[n] for n in path]
            if any(pl[i] != pl[i + 1] for i in range(len(pl) - 1)):
                cross += 1
    obs = cross / tot if tot else float("nan")
    rng = np.random.default_rng(seed)
    null = []
    g0 = sorted(G.nodes())
    for t in range(reps):
        perm = dict(zip(g0, rng.permutation([mem[n] for n in g0])))
        tt = tc = 0
        for s in piv:
            for dst, path in nx.single_source_shortest_path(G, s, cutoff=6).items():
                if dst == s:
                    continue
                tt += 1
                pl = [perm[n] for n in path]
                if any(pl[i] != pl[i + 1] for i in range(len(pl) - 1)):
                    tc += 1
        null.append(tc / tt if tt else np.nan)
    null = np.array(null, dtype=float)
    z = (obs - null.mean()) / null.std() if null.std() > 0 else np.nan
    return obs, float(null.mean()), float(null.std()), float(z), int(len(G)), int(tot)


rows = []
res = segregation(C_all, deg_all, pillar, reps=200)
print("\nfull corpus      observed %.4f  null %.4f +/- %.4f  z = %+.2f  (nodes %d, pairs %d)"
      % (res[0], res[1], res[2], res[3], res[4], res[5]))
rows.append(dict(scope="full corpus", observed=res[0], null_mean=res[1],
                 null_sd=res[2], z=res[3], nodes=res[4], pairs=res[5]))
for a, b in PERIODS:
    C = np.load(os.path.join(DATA, "C_period_%d_%d.npy" % (a, b)))
    dg = np.load(os.path.join(DATA, "deg_period_%d_%d.npy" % (a, b)))
    r = segregation(C, dg, pillar, reps=120)
    print("period %d-%d   observed %.4f  null %.4f +/- %.4f  z = %+.2f  (nodes %d, pairs %d)"
          % (a, b, r[0], r[1], r[2], r[3], r[4], r[5]))
    rows.append(dict(scope="period %d-%d" % (a, b), observed=r[0], null_mean=r[1],
                     null_sd=r[2], z=r[3], nodes=r[4], pairs=r[5]))
for c in top_c:
    C = np.load(os.path.join(DATA, "C_country_%s.npy" % c.replace(" ", "_")))
    dg = np.load(os.path.join(DATA, "deg_country_%s.npy" % c.replace(" ", "_")))
    r = segregation(C, dg, pillar, reps=120)
    print("country %-13s observed %.4f  null %.4f +/- %.4f  z = %+.2f  (nodes %d, pairs %d)"
          % (c, r[0], r[1], r[2], r[3], r[4], r[5]))
    rows.append(dict(scope="country %s" % c, observed=r[0], null_mean=r[1],
                     null_sd=r[2], z=r[3], nodes=r[4], pairs=r[5]))

with open(os.path.join(TAB, "A2_segregation_by_scope.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

# ---- concept co-occurrence restricted to assigned pillars (the 3-pillar system view)
json.dump(dict(periods=["%d-%d" % p for p in PERIODS], countries=top_c,
               n_window=len(sel), n_nodes=len(nodes)),
          open(os.path.join(DATA, "blocks.json"), "w"), indent=1)
print("\nWrote matrices + A2_segregation_by_scope.csv")