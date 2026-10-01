"""
ARTICLE 2 - figure generation.

Six figures, all rendered from the CSVs written by a0, a1, a2, a2b and a3, so every
element in every figure is traceable to a file. Publication settings throughout: 300 dpi
PNG, single-column width for two-panel figures and double-column for the network figure,
Helvetica-adjacent sans serif, no chartjunk, greyscale-safe colourblind palette.

Figure numbering matches the captions in a4_manuscript_docx.py.
"""
import os
import json
import csv
import collections
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")
FIG = os.path.join(A2, "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "font.size": 8.5,
    "axes.linewidth": 0.7,
    "axes.titlesize": 9,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "legend.frameon": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})

# Okabe-Ito, colourblind-safe and distinguishable in greyscale by luminance
DOM_COL = {"GOVERNANCE": "#0072B2",   # blue
           "INNOVATION": "#D55E00",    # vermillion
           "TALENT": "#009E73",         # green
           "UNASSIGNED": "#999999"}     # grey
GREY = "#555555"
LIGHT = "#BBBBBB"


def read(name):
    return list(csv.DictReader(open(os.path.join(TAB, name), encoding="utf-8-sig")))


def save(fig, name):
    path = os.path.join(FIG, name)
    fig.savefig(path)
    plt.close(fig)
    print("  wrote %s" % name)
    return path


# ---------------------------------------------------------------- load
lb = read("A2_load_bearing.csv")
bpd = read("A2_bridge_pillar_distribution.csv")
sens = read("A2_segregation_construction_sensitivity.csv")
summ = {r["statistic"]: r["value"] for r in read("A2_bridge_summary_statistics.csv")}
sm = read("A2_bridge_stability_sizematched.csv")
sh = read("A2_bridge_splithalf_reliability.csv")
cv = read("A2_spliss_convergent_validity.csv")
bscores = read("A2_bridge_scores.csv")
hrol = read("A2_hierarchy_roles.csv")

pillar = {int(k): v for k, v in
          json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
blob = json.load(open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8"))
fam_label = blob["fam_label"]

print("=" * 70)
print("ARTICLE 2 - FIGURES")
print("=" * 70)

# ================================================================ FIGURE 1
# Network architecture, before and after the bridging population is removed.
# The point of the pair is that the second panel looks MORE separated, not less.
edges = [(r["source"], r["target"], float(r["weight"])) for r in
         csv.DictReader(open(os.path.join(A1, "data", "network_edges.csv"),
                             encoding="utf-8-sig"))]
lab2i = {}
for r in hrol:
    lab2i[r["label"]] = None
G = nx.Graph()
for r in hrol:
    G.add_node(r["label"], pillar=r["pillar"], df=float(r["df"]),
               coreness=int(r["coreness"]))
for a, b, w in edges:
    if a in G and b in G:
        G.add_edge(a, b, weight=w)

# FIGURE 1 is a domain-by-domain mixing matrix rather than a node-link drawing.
# A spring embedding of 669 nodes and 5,061 edges is a hairball, and the segregation
# it is supposed to show is genuinely weak (0.310 of edges are within-domain against
# 0.257 by chance), so a picture that appears to show separated clusters would
# overstate the result. The matrix reports the quantity directly and the caption says
# what the diagonal means.
DOMS = ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]
bridge = [r["concept"] for r in bscores if r["is_bridge"] == "1"]
bs = set(bridge)
r_all = float([r["assort_r"] for r in lb if r["removed"].startswith("none")][0])
r_no = float([r["assort_r"] for r in lb if r["removed"] == "UNASSIGNED"][0])


def domain_matrix(drop_pillar=None, drop_nodes=None):
    """Share of all edge weight falling between each ordered pair of domains."""
    di = {p: i for i, p in enumerate(DOMS)}
    M = np.zeros((4, 4))
    for u, v, d in G.edges(data=True):
        if drop_nodes is not None and (u in drop_nodes or v in drop_nodes):
            continue
        pu, pv = G.nodes[u]["pillar"], G.nodes[v]["pillar"]
        if drop_pillar is not None and (pu == drop_pillar or pv == drop_pillar):
            continue
        w = d.get("weight", 1.0)
        M[di[pu], di[pv]] += w
        if pu != pv:
            M[di[pv], di[pu]] += w
    return M / M.sum()


# Panel (b) removes the UNASSIGNED population, not the 45 bridges. The two operations
# are different and the quoted assortativity must match the operation shown. Removing
# only the 45 bridges barely moves the aggregate matrix (they carry a small share of
# edge weight) while removing the 212 unassigned concepts changes the picture and
# raises assortativity from 0.072 to 0.137.
M1 = domain_matrix()
M2 = domain_matrix(drop_pillar="UNASSIGNED")

# Read the two panels off the numbers before titling them. The named-domain diagonals
# and the named-domain off-diagonals are close in panel (a), and the unassigned block
# is the most connected of the four.
named = [0, 1, 2]
dg_a = np.mean([M1[i, i] for i in named])
off_a = np.mean([M1[i, j] for i in named for j in named if i != j])
dg_b = np.mean([M2[i, i] for i in named])
off_b = np.mean([M2[i, j] for i in named for j in named if i != j])
print("   named-domain diagonal %.4f vs off-diagonal %.4f (full)" % (dg_a, off_a))
print("   named-domain diagonal %.4f vs off-diagonal %.4f (unassigned removed)"
      % (dg_b, off_b))

# IMPORTANT AND UNEXPECTED. By raw edge weight the named domains are NOT internally
# clustered: the diagonal/off-diagonal ratio is below 1 in both panels, while the
# degree-weighted assortativity is +0.072 (z = 8.88) and within-domain edges are
# 0.310 of all edges against 0.257 by chance. Both are true. Assortativity weights
# edge ENDS, so a modest set of high-degree within-domain links produces positive
# assortativity even when the bulk of edges run between domains. The unassigned block
# is the least internally connected of the four (diagonal 0.063 against 0.075-0.084
# to the named domains), which is exactly why removing it raises assortativity.
# This is written to a CSV so the manuscript can report it rather than omit it.
mix_rows = []
for i, pi in enumerate(DOMS):
    for j, pj in enumerate(DOMS):
        mix_rows.append(dict(sending_domain=pi, receiving_domain=pj,
                             share_all_edges=round(float(M1[i, j]), 5),
                             share_unassigned_removed=round(float(M2[i, j]), 5)))
with open(os.path.join(TAB, "A2_domain_mixing_matrix.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sending_domain", "receiving_domain",
                                      "share_all_edges", "share_unassigned_removed"])
    w.writeheader()
    w.writerows(mix_rows)
with open(os.path.join(TAB, "A2_mixing_summary.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statistic", "value", "note"])
    w.writerow(["named-domain diagonal share, full network", round(float(dg_a), 4),
                "mean of the three within-domain cells"])
    w.writerow(["named-domain off-diagonal share, full network", round(float(off_a), 4),
                "mean of the six between-domain cells"])
    w.writerow(["named-domain diagonal / off-diagonal, full network",
                round(float(dg_a / off_a), 3), "below 1: not internally clustered "
                "by edge weight"])
    w.writerow(["named-domain diagonal / off-diagonal, unassigned removed",
                round(float(dg_b / off_b), 3), "unchanged by the removal"])
    w.writerow(["unassigned diagonal share, full network", round(float(M1[3, 3]), 4),
                "below its own off-diagonals; the least internally connected block"])
    w.writerow(["within-domain share of edges, all blocks", 0.310, "from "
                "A2_load_bearing.csv, against 0.257 by chance"])
    w.writerow(["assortativity for domain, full network", round(r_all, 4),
                "degree-weighted; positive because it weights edge ends"])
print("   wrote A2_domain_mixing_matrix.csv and A2_mixing_summary.csv")

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15),
                         gridspec_kw={"width_ratios": [1, 1.12]})
for ax, M, title, rv, ratio in (
        (axes[0], M1, "(a)  all 669 concepts, 5,061 edges\nassortativity r = %.3f" % r_all,
         r_all, dg_a / off_a),
        (axes[1], M2, "(b)  212 unassigned concepts removed\nassortativity r = %.3f" % r_no,
         r_no, dg_b / off_b)):
    im = ax.imshow(M, cmap="BuPu", vmin=0, vmax=0.09)
    for i in range(4):
        for j in range(4):
            if M[i, j] > 0.0005:
                ax.text(j, i, "%.3f" % M[i, j], ha="center", va="center",
                        fontsize=7.2, color="white" if M[i, j] > 0.058 else "black")
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(["gov", "innov", "talent", "unassigned"], fontsize=7.2)
    ax.set_yticklabels(["gov", "innov", "talent", "unassigned"], fontsize=7.2)
    ax.set_xlabel("receiving end", fontsize=7.8)
    if ax is axes[0]:
        ax.set_ylabel("sending end", fontsize=7.8)
    ax.set_title(title, pad=6, fontsize=8.5)
    ax.text(0.5, -0.42, "named-domain diagonal / off-diagonal = %.2f" % ratio,
            transform=ax.transAxes, ha="center", fontsize=7.2, color="#333333")

cb = fig.colorbar(im, ax=axes, fraction=0.030, pad=0.02)
cb.ax.tick_params(labelsize=6.8)
cb.set_label("share of total edge weight", fontsize=7.2)
fig.suptitle("Figure 1. Domain-level mixing, and the named domains once the unassigned "
             "population is removed", y=1.02, fontsize=9.5)
save(fig, "F1_network_architecture.png")

# ================================================================ FIGURE 2
# Load-bearing test. Every removal raises assortativity.
order = ["none (full network)", "GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED",
         "GOVERNANCE+INNOVATION", "GOVERNANCE+TALENT", "INNOVATION+TALENT"]
rows = {r["removed"]: r for r in lb}
lbw = {r["removed"]: r for r in read("A2_load_bearing_window.csv") if r.get("assort_r")}
vals_full = [float(rows[o]["assort_r"]) for o in order]
vals_win = [float(lbw[o]["assort_r"]) if o in lbw else np.nan for o in order]
cols = [GREY] + [DOM_COL[p] for p in
                 ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]] + [LIGHT] * 3

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.3),
                              gridspec_kw={"width_ratios": [2.1, 1]})
x = np.arange(len(order))
ax.bar(x - 0.19, vals_full, width=0.36, color=cols, edgecolor="white", linewidth=0.4,
       label="full corpus, 604 docs")
ax.bar(x + 0.19, vals_win, width=0.36, color=cols, edgecolor="white", linewidth=0.4,
       alpha=0.45, hatch="///", label="analysis window, 448 docs")
ax.axhline(vals_full[0], color="#333333", lw=0.8, ls="--", zorder=5)
ax.axhline(vals_win[0], color="#777777", lw=0.8, ls=":", zorder=5)
ax.set_xticks(x)
ax.set_xticklabels(["full", "no\ngov", "no\ninnov", "no\ntalent", "no\nunass.",
                    "no gov\n+ innov", "no gov\n+ talent", "no innov\n+ talent"],
                   fontsize=7)
ax.set_ylabel("assortativity for the domain attribute")
ax.set_ylim(-0.02, 0.175)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", fontsize=7)
ax.set_title("(a)  the named domains disagree between corpora; unassigned does not", pad=6)

# within-pillar edge share against chance
wit = [float(rows[o]["within_pillar_edges"]) for o in order]
ax2.barh(x[::-1], wit, color=cols, height=0.66, edgecolor="white", linewidth=0.5)
ax2.set_yticks(x[::-1])
ax2.set_yticklabels(["full", "gov", "innov", "talent", "unassigned", "g+i", "g+t", "i+t"],
                    fontsize=7)
ax2.set_xlabel("share of edges within a domain")
ax2.set_xlim(0, 0.70)
ax2.axvline(0.260, color="#333333", lw=0.8, ls="--")
ax2.text(0.268, 0.4, "0.260\nchance", fontsize=6, color="#333333")
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_title("(b)  raw mixing share, full corpus", pad=6)
fig.suptitle("Figure 2. Load-bearing test: removing the unassigned population raises "
             "segregation in both corpora; the named domains do not", y=1.03, fontsize=9.5)
save(fig, "F2_load_bearing.png")

# ================================================================ FIGURE 3
# The bridge analysis and its correction. Panel (a): raw participation is a measure of
# genericity. Panel (b): once each concept is compared with a concept of its own degree
# under a label-permutation null, no concept is an outlier.
elig = [r for r in bscores]
pc = np.array([float(r["participation"]) for r in elig])
dfa = np.array([float(r["df_pooled"]) for r in elig])
pil = np.array([r["pillar"] for r in elig])
isb = np.array([r["is_bridge"] == "1" for r in elig])
rho = stats.spearmanr(pc, dfa)

# A2_bridge_scores.csv keys on concept_id; A2_bridges_corrected.csv keys on family_id.
# They are the same identifier for the same concept, so join on it.
corr = {int(r["family_id"]): r for r in read("A2_bridges_corrected.csv")}
cz = np.array([float(corr[int(r["concept_id"])]["corrected_z"]) for r in elig])

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.1),
                              gridspec_kw={"width_ratios": [1.25, 1]})
for p in ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]:
    m = (pil == p) & ~isb
    ax.scatter(dfa[m], pc[m], s=9, color=DOM_COL[p], alpha=0.55, linewidths=0)
ax.scatter(dfa[isb], pc[isb], s=32, facecolor="none", edgecolor="#111111",
           linewidths=0.8, zorder=6, label="top-decile on raw score")
ax.set_xlabel("documents containing the concept")
ax.set_ylabel("participation coefficient")
ax.set_title("(a)  participation tracks frequency, $\\rho$ = %.2f" % rho.statistic, pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower right", fontsize=7)

ax2.axhline(1.96, color="#333333", lw=0.8, ls="--")
ax2.scatter(dfa, cz, s=9, color=DOM_COL["INNOVATION"], alpha=0.5, linewidths=0)
top40 = np.argsort(-cz)[:40]
ax2.scatter(dfa[top40], cz[top40], s=20, facecolor="none", edgecolor="#111111",
            linewidths=0.6, zorder=6)
ax2.text(0.97, 0.07, "dashed line: 1.96", transform=ax2.transAxes,
         ha="right", fontsize=6.6, color="#333333")
ax2.set_xlabel("documents containing the concept")
ax2.set_ylabel("participation, null-centred (z)")
ax2.set_ylim(-0.7, 2.4)
ax2.set_title("(b)  corrected: max z = %.2f, none significant" % cz.max(), pad=6)
ax2.spines[["top", "right"]].set_visible(False)
fig.suptitle("Figure 3. Participation measures genericity, and no concept is a "
             "significant bridge once degree is controlled", y=1.03, fontsize=9.5)
save(fig, "F3_bridges.png")

# ================================================================ FIGURE 4
# Stability, and the demonstration that it is a power artefact.
q = [r for r in sm if r["block"].startswith("Q") and r.get("rho")]
nat = [r for r in sm if r["block"] in ("Australia", "Canada") and r.get("rho")]
rhoq = np.array([float(r["rho"]) for r in q])
eq = np.array([float(r["edges"]) for r in q])
allb = q + nat
rhoa = np.array([float(r["rho"]) for r in allb])
ega = np.array([float(r["edges"]) for r in allb])
lga = np.log(ega)
half = [r for r in sh if r["analysed"] == "1" and r.get("rho_half")]
rh = [float(r["rho_half"]) for r in half]
pr = stats.pearsonr(lga, rhoa)
fit = np.polyfit(lga, rhoa, 1)
r2 = 1 - np.var(rhoa - np.polyval(fit, lga)) / np.var(rhoa)

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
ax = axes[0]
for r, m in ((q, "o"), (nat, "s")):
    ax.scatter(np.log([float(x["edges"]) for x in r]), [float(x["rho"]) for x in r],
               s=34, marker=m, color=DOM_COL["INNOVATION"], alpha=0.85,
               edgecolor="white", linewidths=0.5,
               label="chronological quartile" if m == "o" else "national context")
xs = np.linspace(lga.min() - 0.25, lga.max() + 0.25, 60)
ax.plot(xs, np.polyval(fit, xs), color="#333333", lw=1.0)
ax.axhline(float(np.median(rh)), color="#D55E00", lw=1.0, ls="--")
ax.text(lga.min() - 0.2, float(np.median(rh)) + 0.02,
        "split-half reliability %.2f" % np.median(rh), fontsize=7, color="#D55E00")
ax.set_xlabel("log edges in block")
ax.set_ylabel("correlation with pooled participation")
ax.set_title("(a)  r = %.3f, $R^2$ = %.3f: block size explains rho" % (pr.statistic, r2),
             pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left")

ax = axes[1]
labels = [r["block"].replace(" ", "\n", 1) for r in allb]
cols3 = [DOM_COL["INNOVATION"]] * len(q) + [DOM_COL["TALENT"]] * len(nat)
ax.bar(np.arange(len(allb)), rhoa, color=cols3, width=0.68, edgecolor="white",
       linewidth=0.5)
ax.set_xticks(np.arange(len(allb)))
ax.set_xticklabels(labels, fontsize=6.4)
ax.set_ylabel("correlation with pooled participation")
ax.set_title("(b)  correlations by block, against the reliability floor", pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.axhline(float(np.median(rh)), color="#D55E00", lw=0.8, ls="--")
fig.suptitle("Figure 4. Bridge stability is a power limit, not a finding about the field",
             y=1.03, fontsize=9.5)
save(fig, "F4_stability_power.png")

# ================================================================ FIGURE 5
# Convergent validity against SPLISS.
order_p = ["TALENT", "GOVERNANCE", "INNOVATION"]
# Match on the pillar code (P1..P9) rather than on the full label, because the CSV
# labels are written out in full and do not line up word-for-word with these labels.
P9 = {"P1": "P1 financial", "P2": "P2 policy", "P3": "P3 participation",
      "P4": "P4 talent ID", "P5": "P5 career", "P6": "P6 facilities",
      "P7": "P7 coaching", "P8": "P8 competition"}
p9keys = list(P9)
pairs = [r for r in cv if float(r["p_bh"]) < 0.05]
lab5 = ["%s %s" % (r["spliss_pillar"][:2], r["spliss_pillar"].split()[1])
        for r in pairs]
val5 = [-np.log10(max(float(r["p_bh"]), 1e-12)) for r in pairs]
pil5 = [r["derived_pillar"] for r in pairs]
M = np.zeros((3, 8))
for r in pairs:
    i = order_p.index(r["derived_pillar"])
    j = p9keys.index(r["spliss_pillar"][:2])
    M[i, j] = float(r["odds_ratio"])

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9),
                              gridspec_kw={"width_ratios": [1.5, 1]})
im = ax.imshow(M, cmap="BuPu", aspect="auto", vmin=0, vmax=25)
ax.set_xticks(range(8))
ax.set_xticklabels([P9[k].split()[0] for k in p9keys], fontsize=7)
ax.set_yticks(range(3))
ax.set_yticklabels(order_p, fontsize=8)
ax.set_xlabel("SPLISS pillar")
for i in range(3):
    for j in range(8):
        if M[i, j] > 0:
            ax.text(j, i, "%.1f" % M[i, j], ha="center", va="center",
                    fontsize=6.6, color="white" if M[i, j] > 12 else "black")
        elif order_p[i] == "INNOVATION":
            ax.text(j, i, "0.0", ha="center", va="center", fontsize=6.6, color="#888888")
ax.set_title("(a)  odds ratio, seven associations surviving BH at .05", pad=6)
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.ax.tick_params(labelsize=6.5)
cb.set_label("odds ratio", fontsize=7)

y = np.arange(len(lab5))[::-1]
ax2.barh(y, val5, color=[DOM_COL[p] for p in pil5], height=0.68, edgecolor="white",
         linewidth=0.4)
ax2.set_yticks(y)
ax2.set_yticklabels(lab5, fontsize=6.6)
ax2.set_xlabel("$-\\log_{10}$(BH-corrected p)")
ax2.axvline(-np.log10(0.05), color="#333333", lw=0.8, ls="--")
ax2.spines[["top", "right"]].set_visible(False)
ax2.set_title("(b)  innovation is depleted, not enriched", pad=6)
fig.suptitle("Figure 5. Convergent validity against the nine-pillar framework is partial "
             "and asymmetric", y=1.03, fontsize=9.5)
save(fig, "F5_spliss_validity.png")

# ================================================================ FIGURE 6
# Construction sensitivity.
lab6 = []
short = []
for r in sens:
    c = r["construction"]
    if c.startswith("Unfiltered"):
        short.append("unfiltered\n(all pairs)")
    elif c == "Count >= 3 only":
        short.append("count >= 3\nonly")
    elif "null z >= 1.0" in c:
        short.append("count >= 3\nz >= 1.0")
    elif "null z >= 2.0" in c:
        short.append("count >= 3\nz >= 2.0")
    elif "2.5 (Article 1)" in c:
        short.append("count >= 3\nz >= 2.5\n(main)")
    elif "null z >= 3.0" in c:
        short.append("count >= 3\nz >= 3.0")
    else:
        short.append("count >= 5\nz >= 2.5")
    lab6.append(c)
z6 = [float(r["z"]) for r in sens]
e6 = [float(r["edges"]) for r in sens]
md6 = [float(r["mean_degree"]) for r in sens]
col6 = ["#D55E00" if zz > -1.96 else DOM_COL["TALENT"] for zz in z6]

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9),
                              gridspec_kw={"width_ratios": [1.55, 1]})
x = np.arange(len(sens))
ax.bar(x, z6, color=col6, width=0.7, edgecolor="white", linewidth=0.5)
ax.axhline(-1.96, color="#333333", lw=0.8, ls="--")
ax.axhline(0, color="#888888", lw=0.6)
ax.set_xticks(x)
ax.set_xticklabels(short, fontsize=6.2)
ax.set_ylabel("boundary-crossing z")
ax.set_ylim(-7, 2.2)
ax.set_title("(a)  segregation replicates on every filtered graph", pad=6)
ax.spines[["top", "right"]].set_visible(False)
ax.text(0.02, 0.05, "orange = not significant", transform=ax.transAxes, fontsize=7,
        color="#D55E00")

ax2.scatter(md6, z6, s=36, color=col6, edgecolor="white", linewidths=0.5, zorder=4)
ax2.set_xscale("log")
ax2.axhline(-1.96, color="#333333", lw=0.8, ls="--")
ax2.set_xlabel("mean degree (log scale)")
ax2.set_ylabel("boundary-crossing z")
ax2.set_title("(b)  the exception is the near-complete graph", pad=6)
ax2.spines[["top", "right"]].set_visible(False)
ax2.annotate("mean degree 232\ndegenerate test", xy=(231.9, 0.02), xytext=(14, -4.6),
             fontsize=6.6, color="#D55E00",
             arrowprops=dict(arrowstyle="->", color="#D55E00", lw=0.7))
fig.suptitle("Figure 6. Construction sensitivity of the segregation finding", y=1.03,
             fontsize=9.5)
save(fig, "F6_construction_sensitivity.png")

print("\n6 figures written to %s" % FIG)
