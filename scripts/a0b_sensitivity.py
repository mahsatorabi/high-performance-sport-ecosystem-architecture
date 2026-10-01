"""
ARTICLE 2 - Stage A2: construction-sensitivity of the segregation finding.

Article 1 reported z = -4.16 for pillar segregation. That value was computed on ONE
specific network construction: co-occurrence >= 3, bipartite-null z >= 2.5, association-strength
weights. A re-test on an unfiltered co-occurrence graph returned z = +0.11.

Before any Article 2 claim rests on segregation, this stage establishes which result is a
property of the data and which is a property of the threshold. It rebuilds the graph under
several constructions and re-runs the identical boundary-crossing test on each.
"""
import os, json, csv, collections
import numpy as np
import networkx as nx

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")

M = np.load(os.path.join(DATA, "M_window.npy")).astype(np.float32)
years = np.load(os.path.join(DATA, "years_window.npy"))
country = json.load(open(os.path.join(DATA, "country_window.json")))
pillar = {int(k): v for k, v in json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
nodes = sorted(pillar)
X = M[:, nodes]
N = X.shape[0]
P3 = ["GOVERNANCE", "INNOVATION", "TALENT"]

print("=" * 78)
print("ARTICLE 2 - STAGE A2  construction sensitivity of the segregation finding")
print("=" * 78)
print("windowed docs %d | nodes %d" % (N, len(nodes)))

C = (X.T @ X).astype(float)
np.fill_diagonal(C, 0)
k = X.sum(0).astype(float)
AS = C / np.maximum(k[:, None] + k[None, :] - C, 1e-9)
np.fill_diagonal(AS, 0)


def bipartite_null_z(C, k, draws=60, seed=11, min_cooc=3):
    """Per-pair z of association strength against a degree-preserving bipartite swap null.
    X is (n_docs, n_nodes); swaps exchange a node between two documents, preserving both
    document and node degrees exactly."""
    n_docs, n_nodes = X.shape
    inv = [list(np.nonzero(X[d])[0].tolist()) for d in range(n_docs)]
    rng = np.random.default_rng(seed)
    acc = np.zeros_like(C)
    acc2 = np.zeros_like(C)
    for t in range(draws):
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
        Mn = np.zeros((n_docs, n_nodes), dtype=np.float32)
        for d in range(n_docs):
            for c in cur[d]:
                Mn[d, c] = 1.0
        Cn = (Mn.T @ Mn).astype(float)
        np.fill_diagonal(Cn, 0)
        Sn = Cn / np.maximum(k[:, None] + k[None, :] - Cn, 1e-9)
        acc += Sn; acc2 += Sn ** 2
    mu = acc / draws
    sd = np.sqrt(np.maximum(acc2 / draws - mu ** 2, 1e-12))
    return (AS - mu) / sd


def build(mode, zthr=None, minc=3):
    if mode == "unfiltered":
        adj = AS.copy()
    elif mode == "filtered":
        Z = Zb
        adj = AS * ((C >= minc) & (Z >= zthr))
    elif mode == "count-threshold":
        adj = AS * (C >= minc)
    np.fill_diagonal(adj, 0)
    return nx.from_numpy_array(adj)


def boundary_test(G, member, reps=200, seed=5, n_piv=200):
    if G.number_of_nodes() < 20 or G.number_of_edges() < 40:
        return None
    piv = sorted(np.random.default_rng(seed).choice(sorted(G.nodes()),
                                                 size=min(n_piv, G.number_of_nodes()),
                                                 replace=False).tolist())
    def load(mem):
        tot = cross = 0
        for s in piv:
            for dst, path in nx.single_source_shortest_path(G, s, cutoff=6).items():
                if dst == s:
                    continue
                tot += 1
                pl = [mem[n] for n in path]
                if any(pl[i] != pl[i + 1] for i in range(len(pl) - 1)):
                    cross += 1
        return (cross / tot) if tot else np.nan, tot
    obs, tot = load(member)
    rng = np.random.default_rng(seed)
    g0 = sorted(G.nodes())
    null = []
    for t in range(reps):
        perm = dict(zip(g0, rng.permutation([member[n] for n in g0])))
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
    return obs, float(null.mean()), float(null.std()), float(z), int(G.number_of_edges())


print("\ncomputing bipartite null for edge admission ...")
Zb = bipartite_null_z(C, k, draws=60)
print("done.")

rows = []
member = {i: pillar[nodes[i]] for i in range(len(nodes))}

CONSTRUCTIONS = [
    ("unfiltered (all co-occurring pairs)", "unfiltered", None, 3),
    ("count >= 3 only", "count-threshold", None, 3),
    ("count >= 3 and null z >= 1.0", "filtered", 1.0, 3),
    ("count >= 3 and null z >= 2.0", "filtered", 2.0, 3),
    ("count >= 3 and null z >= 2.5  [ARTICLE 1]", "filtered", 2.5, 3),
    ("count >= 3 and null z >= 3.0", "filtered", 3.0, 3),
    ("count >= 5 and null z >= 2.5", "filtered", 2.5, 5),
]

print("\n%-44s %8s %9s %9s %8s %7s" % ("construction", "edges", "observed", "null",
                                       "z", "meanDeg"))
for label, mode, zthr, minc in CONSTRUCTIONS:
    G = build(mode, zthr, minc)
    r = boundary_test(G, member, reps=200)
    if r is None:
        print("%-44s  too sparse" % label)
        continue
    obs, nm, ns, z, ne = r
    md = 2 * G.number_of_edges() / G.number_of_nodes()
    print("%-44s %8d %9.4f %9.4f %+8.2f %7.1f" % (label, ne, obs, nm, z, md))
    rows.append(dict(construction=label, mode=mode, z_threshold=(zthr or ""),
                     min_cooc=minc, edges=ne, mean_degree=round(md, 1),
                     observed=round(obs, 4), null_mean=round(nm, 4),
                     null_sd=round(ns, 4), z=round(z, 2),
                     null_draws=200, null_reps=200))

with open(os.path.join(TAB, "A2_segregation_construction_sensitivity.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

zs = [r["z"] for r in rows]
print("\nz across constructions: %s" % ", ".join("%+.2f" % z for z in zs))
print("all negative (segregated): %s" % (max(zs) < 0))
print("all |z| > 1.96          : %s" % (all(abs(z) > 1.96 for z in zs)))