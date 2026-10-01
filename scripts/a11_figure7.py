"""
Figure 7: composition of the coreness hierarchy.

One question, asked three ways. Is the deepest core a cross-section of the field, or is
it made of something in particular?

Panel (a) answers it by composition. For each core from 12 downwards, the share of that
core held by each of the four groups. A field with no core structure gives four flat
lines at the base rate. What is in the data is one sharp departure at the top and flat
profiles everywhere else, which is the honest shape of the result: a concentrated tip on
an otherwise level body. Cores of fewer than 12 concepts are not plotted, because a
share computed on three concepts implies precision that is not there.

Panel (b) answers it by position. Document frequency against degree, log frequency
axis, with the 12-core picked out. The comparison is with the participation measure
examined in section 4.3, which is frequency-driven at rho = +0.549. If the core were
frequency driven it would sit along the general upward trend. It sits in the upper
left, the one region the general trend does not reach: rare and densely connected at
once.

Panel (c) is the one that settles it, and it is a distribution rather than a scatter.
The empirical CDF of document frequency for the 12-core and for the rest of the
network. Two curves that lie on top of each other mean the core is not more frequent
than anything else, which is what makes its core position structural. The relevant
comparison is with section 4.3, where the same kind of check on participation produced
a correlation of +0.549 and an artefactual answer.

Inputs:  article2/tables/A2_hierarchy_roles.csv
Outputs: article2/figures/F7_core_composition.png
"""
import os
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss

A2 = r"D:\Uni of Birjand\articles\adel\article2"
TAB = os.path.join(A2, "tables")
FIG = os.path.join(A2, "figures")
PILLARS = ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]
LABEL = {"GOVERNANCE": "Governance", "INNOVATION": "Innovation",
         "TALENT": "Talent", "UNASSIGNED": "Unassigned"}
COLOR = {"GOVERNANCE": "#4C72B0", "INNOVATION": "#DD8452",
         "TALENT": "#55A868", "UNASSIGNED": "#9A9A9A"}

rows = list(csv.DictReader(
    open(os.path.join(TAB, "A2_hierarchy_roles.csv"), encoding="utf-8-sig")))
for r in rows:
    r["coreness"] = int(r["coreness"])
    r["df"] = int(r["df"])
    r["degree"] = float(r["degree"])

n = len(rows)
base = {p: sum(1 for r in rows if r["pillar"] == p) / n for p in PILLARS}
cores = sorted({r["coreness"] for r in rows}, reverse=True)
plotted = [c for c in cores if sum(1 for r in rows if r["coreness"] == c) >= 12]
c12 = [r for r in rows if r["coreness"] == 12]
rest = [r for r in rows if r["coreness"] < 12]

fig = plt.figure(figsize=(13.2, 4.4))
gs = fig.add_gridspec(1, 3, width_ratios=[1.32, 1.0, 0.92], wspace=0.30)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])

# ---------------------------------------------------------------- panel (a)
w = 0.2
for i, p in enumerate(PILLARS):
    ys = []
    for c in plotted:
        sel = [r for r in rows if r["coreness"] == c]
        ys.append(sum(1 for r in sel if r["pillar"] == p) / len(sel) * 100)
    ax1.bar([x + (i - 1.5) * w for x in plotted], ys, width=w * 0.9,
            color=COLOR[p], label=LABEL[p], zorder=3)

# Base rates as two reference lines, labelled in the right margin where no bars reach.
for p in ("INNOVATION", "GOVERNANCE"):
    ax1.axhline(100 * base[p], color=COLOR[p], ls=":", lw=1.0, zorder=4)
ax1.annotate("innovation\nbase rate 24%", xy=(12.75, 100 * base["INNOVATION"]),
             xytext=(12.95, 27.0), fontsize=6.4, color="#8a4b1f", ha="left",
             va="center")
ax1.annotate("governance\nbase rate 21%", xy=(12.75, 100 * base["GOVERNANCE"]),
             xytext=(12.95, 13.0), fontsize=6.4, color="#2f4a75", ha="left",
             va="center")

ax1.annotate("13 of 24 concepts\n(2.28x base rate)", xy=(12.10, 54), xytext=(10.05, 58.5),
             fontsize=6.9, color="#8a4b1f", ha="left",
             arrowprops=dict(arrowstyle="->", lw=0.8, color="#8a4b1f",
                             shrinkA=0, shrinkB=2))
ax1.annotate("1 of 24 is governance", xy=(11.88, 3.0), xytext=(9.55, 5.2),
             fontsize=6.9, color="#2f4a75", ha="left", va="top",
             arrowprops=dict(arrowstyle="->", lw=0.8, color="#2f4a75",
                             shrinkA=0, shrinkB=2))

ax1.set_xlabel("Coreness level", fontsize=8.5)
ax1.set_ylabel("Share of core (%)", fontsize=8.5)
ax1.set_title("(a) Innovation fills the deepest core; the body is a cross-section",
              fontsize=9, pad=7)
ax1.set_xticks(plotted)
ax1.set_xticklabels([str(c) for c in plotted], fontsize=7.5)
ax1.set_xlim(0.6, 16.2)
ax1.set_ylim(0, 70)
ax1.tick_params(labelsize=7.5)
ax1.grid(axis="y", color="0.9", zorder=0)
ax1.set_axisbelow(True)
for s in ("top", "right"):
    ax1.spines[s].set_visible(False)
ax1.legend(fontsize=7, frameon=False, ncol=4, loc="upper center",
           bbox_to_anchor=(0.46, 1.005), columnspacing=0.9, handlelength=1.1)

# ---------------------------------------------------------------- panel (b)
ax2.set_xscale("log")
ax2.scatter([r["df"] for r in rest], [r["degree"] for r in rest], s=10,
            c="0.80", edgecolors="none", zorder=2, label="cores 1-11 (n = 645)")
ax2.scatter([r["df"] for r in c12], [r["degree"] for r in c12], s=36,
            c="#C44E52", edgecolors="0.3", linewidths=0.4, zorder=4,
            label="12-core (n = 24)")

# The general trend, so that "the core does not follow it" is visible rather than
# asserted. Fitted on the non-core nodes only.
xs = np.array([r["df"] for r in rest], float)
ys = np.array([r["degree"] for r in rest], float)
b, a = np.polyfit(np.log(xs), ys, 1)
grid = np.linspace(xs.min(), xs.max(), 100)
ax2.plot(grid, a + b * np.log(grid), color="0.45", ls="--", lw=0.9, zorder=3,
         label="trend, cores 1-11")

# Annotate a few core members only. Labelling all twelve collides; the point is the
# cluster, not any one concept, so a representative handful plus the note is enough.
SHOW = {"wearable": (5.2, 6.4, "left"), "artificial intelligence": (3.8, 5.35, "left"),
        "ai": (3.9, 4.55, "right"), "algorithm": (11.5, 2.9, "left"),
        "smart": (3.4, 3.35, "left"), "monitoring": (8.2, 4.25, "left"),
        "innovation": (21.0, 2.25, "left")}
for lab, (tx, ty, ha) in SHOW.items():
    for r in c12:
        if r["label"] == lab:
            ax2.annotate(lab, xy=(r["df"], r["degree"]), xytext=(tx, ty),
                         fontsize=6.2, color="#7a2f33", ha=ha,
                         arrowprops=dict(arrowstyle="-", lw=0.5, color="#c9a0a2",
                                         shrinkA=1, shrinkB=2))

rho_all, _ = ss.spearmanr([r["df"] for r in rows], [r["degree"] for r in rows])
rho_12, p_12 = ss.spearmanr([r["df"] for r in c12], [r["degree"] for r in c12])
ax2.text(0.985, 0.985, "df vs degree, whole network:  rho = %.2f" % rho_all,
         transform=ax2.transAxes, ha="right", va="top", fontsize=6.8)
ax2.text(0.985, 0.075, "within 12-core:  rho = %.2f (p = %.2f)"
         % (rho_12, p_12), transform=ax2.transAxes, ha="right", va="bottom", fontsize=6.8)
ax2.text(0.03, 0.30, "the core sits above the\ntrend at low frequency",
         transform=ax2.transAxes, ha="left", va="bottom", fontsize=6.8, style="italic",
         color="0.35")

ax2.set_xlabel("Documents containing the concept (log scale)", fontsize=8.5)
ax2.set_ylabel("Weighted degree", fontsize=8.5)
ax2.set_ylim(-0.5, 8.2)
ax2.set_title("(b) The core is rare and densely linked at once", fontsize=9, pad=7)
ax2.tick_params(labelsize=7.5)
ax2.grid(color="0.93", zorder=0)
ax2.set_axisbelow(True)
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)
ax2.legend(fontsize=6.6, frameon=False, loc="upper right", handlelength=1.3,
           bbox_to_anchor=(1.0, 0.885))

# ---------------------------------------------------------------- panel (c)
for pop, lab, col, ls in [(rest, "cores 1-11", "0.45", "--"),
                          (c12, "12-core", "#C44E52", "-")]:
    d = np.sort([r["df"] for r in pop])
    y = np.arange(1, len(d) + 1) / len(d)
    ax3.step(d, y, where="post", color=col, ls=ls, lw=1.4, label=lab, zorder=3)
    ax3.plot([d.mean()], [0.5], marker="|", ms=11, mew=1.5, color=col, zorder=5)

t, tp = ss.ttest_ind([r["df"] for r in c12], [r["df"] for r in rest], equal_var=False)
ax3.set_xscale("log")
ax3.set_xlabel("Documents containing the concept (log scale)", fontsize=8.5)
ax3.set_ylabel("Cumulative share of group", fontsize=8.5)
ax3.set_title("(c) ... and no more frequent than the rest", fontsize=9, pad=7)
ax3.tick_params(labelsize=7.5)
ax3.grid(color="0.93", zorder=0)
ax3.set_axisbelow(True)
for s in ("top", "right"):
    ax3.spines[s].set_visible(False)
ax3.legend(fontsize=7, frameon=False, loc="upper left")
ax3.text(0.97, 0.10,
         "mean df %.1f vs %.1f, Welch p = %.2f\nticks mark each group's mean"
         % (np.mean([r["df"] for r in c12]), np.mean([r["df"] for r in rest]), tp),
         transform=ax3.transAxes, ha="right", va="bottom", fontsize=6.6)

fig.savefig(os.path.join(FIG, "F7_core_composition.png"), dpi=300,
            bbox_inches="tight", facecolor="white")
print("wrote F7_core_composition.png")
print("cores plotted %s | skipped (n<12): %s"
      % (plotted, [c for c in cores if c not in plotted]))
print("df-degree rho all %.3f | within 12-core %.3f (p %.3f)" % (rho_all, rho_12, p_12))
print("mean df 12-core %.1f vs rest %.1f, Welch p %.3f"
      % (np.mean([r["df"] for r in c12]), np.mean([r["df"] for r in rest]), tp))
