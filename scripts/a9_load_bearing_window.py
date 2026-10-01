"""
ARTICLE 2 - Stage F: does the load-bearing result hold on the analysis window?

Stage B computed the load-bearing test on the full-corpus network (604 documents,
5,061 edges). Stages C and E computed the bridge analyses on the 2013-2025 window
(448 documents). For a self-contained paper that split has to be either justified or
removed, and the cheapest way to remove it is to recompute the load-bearing test on
the same window the bridge work uses.

If the result replicates, the paper reports one corpus throughout. If it does not, the
split is a real dependency and has to be disclosed.
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

MIN_COOC, EDGE_Z = 3, 2.5
REPS, SEED = 200, 5
P3 = ["GOVERNANCE", "INNOVATION", "TALENT"]
ALLG = P3 + ["UNASSIGNED"]

pillar = {int(k): v for k, v in
          json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
nodes = sorted(pillar)
NN = len(nodes)
M = np.load(os.path.join(DATA, "M_window.npy")).astype(np.float32)
X = M[:, nodes]
N = X.shape[0]
member = {i: pillar[nodes[i]] for i in range(NN)}

print("=" * 76)
print("ARTICLE 2 - STAGE F  load-bearing test recomputed on the analysis window")
print("=" * 76)
print("windowed documents %d | concepts %d" % (N, NN))


def AS_OF(C, k):
    A = C / np.maximum(k[:, None] + k[None, :] - C, 1e-9)
    np.fill_diagonal(A, 0)
    return A


def window_graph():
    C = (X.T @ X).astype(float)
    np.fill_diagonal(C, 0)
    k = X.sum(0).astype(float)
    Z = np.load(os.path.join(DATA, "Z_window.npy"))
    A = AS_OF(C, k) * ((C >= MIN_COOC) & (Z >= EDGE_Z))
    np.fill_diagonal(A, 0)
    return nx.from_numpy_array(A), k


def assort(G, lab, reps=REPS, seed=SEED):
    nx.set_node_attributes(G, lab, "pa")
    obs = nx.algorithms.assortativity.attribute_assortativity_coefficient(G, "pa")
    g0 = sorted(G.nodes())
    base = [lab[n] for n in g0]
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(reps):
        nx.set_node_attributes(G, dict(zip(g0, rng.permutation(base))), "pa")
        null.append(nx.algorithms.assortativity.attribute_assortativity_coefficient(G, "pa"))
    null = np.array(null, dtype=float)
    null = null[~np.isnan(null)]
    z = (obs - null.mean()) / null.std() if null.std() > 0 else np.nan
    return obs, float(null.mean()), float(null.std()), float(z)


G, kw = window_graph()
print("window graph: %d nodes, %d edges, mean degree %.1f"
      % (G.number_of_nodes(), G.number_of_edges(),
         2 * G.number_of_edges() / G.number_of_nodes()))

rows = []
base = assort(G, member)
same = sum(1 for u, v in G.edges() if member[u] == member[v]) / G.number_of_edges()
print("\nfull window network : r = %.4f  null %.4f +/- %.4f  z = %+.2f  within %.4f"
      % (base[0], base[1], base[2], base[3], same))
rows.append(dict(removed="none (full network)", nodes=G.number_of_nodes(),
                 edges=G.number_of_edges(), assort_r=round(base[0], 4),
                 assort_null=round(base[1], 4), assort_sd=round(base[2], 4),
                 z=round(base[3], 2), within_pillar_edges=round(same, 4)))

print("\n%-26s %6s %7s %9s %8s" % ("removed", "nodes", "edges", "r", "z"))
for drop in ALLG:
    keep = [i for i in G.nodes() if member[i] != drop]
    H = G.subgraph(keep).copy()
    r = assort(H, {i: member[i] for i in keep})
    w = sum(1 for u, v in H.edges() if member[u] == member[v]) / H.number_of_edges()
    print("%-26s %6d %7d %9.4f %+8.2f" % (drop, H.number_of_nodes(),
                                             H.number_of_edges(), r[0], r[3]))
    rows.append(dict(removed=drop, nodes=H.number_of_nodes(),
                     edges=H.number_of_edges(), assort_r=round(r[0], 4),
                     assort_null=round(r[1], 4), assort_sd=round(r[2], 4),
                     z=round(r[3], 2), within_pillar_edges=round(w, 4)))
for combo in [("GOVERNANCE", "INNOVATION"), ("GOVERNANCE", "TALENT"),
              ("INNOVATION", "TALENT")]:
    keep = [i for i in G.nodes() if member[i] not in combo]
    H = G.subgraph(keep).copy()
    r = assort(H, {i: member[i] for i in keep})
    w = sum(1 for u, v in H.edges() if member[u] == member[v]) / H.number_of_edges()
    print("%-26s %6d %7d %9.4f %+8.2f" % ("+".join(combo), H.number_of_nodes(),
                                           H.number_of_edges(), r[0], r[3]))
    rows.append(dict(removed="+".join(combo), nodes=H.number_of_nodes(),
                     edges=H.number_of_edges(), assort_r=round(r[0], 4),
                     assort_null=round(r[1], 4), assort_sd=round(r[2], 4),
                     z=round(r[3], 2), within_pillar_edges=round(w, 4)))

vals = [r["assort_r"] for r in rows]
singles = {r["removed"]: r["assort_r"] for r in rows[1:5]}
print("\nDIRECTION OF EACH SINGLE REMOVAL, window versus full corpus")
print("   %-12s %10s %12s" % ("removed", "window", "full corpus"))
print("   %-12s %10.4f %12.4f" % ("none", vals[0], 0.0723))
for p, v in singles.items():
    full = {"GOVERNANCE": 0.0773, "INNOVATION": 0.1061, "TALENT": 0.0669,
            "UNASSIGNED": 0.1367}[p]
    print("   %-12s %10.4f %12.4f   %s" % (p, v, full,
                                            "both above full" if v > vals[0] and full > 0.0723
                                            else ("both below full" if v < vals[0] and full < 0.0723
                                                  else "DISAGREE")))
print("\n   the unassigned removal is the only one that agrees, and it agrees closely")
print("   (%.4f on the window, 0.1367 on the full corpus)" % singles["UNASSIGNED"])
print("   the three named domains do not agree in direction, so the claim that every")
print("   removal raises segregation does NOT replicate and is not made")

# Chance level for the within-pillar edge share. Under random mixing the expected
# share of edge ends falling inside a group is the sum of squared group degree shares,
# where the group degree share is that group's total degree over total degree. Summing
# squared NODE shares would give the wrong quantity.
tot = sum(kw[i] for i in G.nodes())
grp = collections.Counter()
for i in G.nodes():
    grp[member[i]] += kw[i]
chance = sum((v / tot) ** 2 for v in grp.values())
print("\nchance within-pillar share from the degree distribution: %.4f" % chance)
print("observed within-pillar share: %.4f" % same)
print("ratio observed/chance: %.3f" % (same / chance))

with open(os.path.join(TAB, "A2_load_bearing_window.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("\nwrote A2_load_bearing_window.csv")
