"""
Diagnostic: is the participation coefficient measuring integrative position, or is it
rewarding genericity?

A concept that is merely general, common and linked to everything will score high on the
participation coefficient without being integrative in any substantive sense. If the bridge
set is mostly high-frequency vocabulary, the bridge finding in Article 2 is an artefact of
the measure rather than a property of the field.

Three checks:
  1. correlation between participation and document frequency
  2. the bridge set's document frequency against the eligible set's
  3. a frequency-controlled version of the bridge test: restrict to concepts in a narrow
     document-frequency band, so genericity cannot do the work
"""
import os
import csv
import collections
import numpy as np
from scipy import stats

A2 = r"D:\Uni of Birjand\articles\adel\article2"
TAB = os.path.join(A2, "tables")

rows = list(csv.DictReader(open(os.path.join(TAB, "A2_bridge_scores.csv"),
                                encoding="utf-8-sig")))
print("=" * 74)
print("GENERICITY DIAGNOSTIC")
print("=" * 74)

pc = np.array([float(r["participation"]) for r in rows])
df = np.array([float(r["df_pooled"]) for r in rows])
bt = np.array([float(r["betweenness"]) for r in rows])
isb = np.array([r["is_bridge"] == "1" for r in rows])
pil = np.array([r["pillar"] for r in rows])

print("eligible concepts %d | bridges %d" % (len(rows), isb.sum()))
r1 = stats.spearmanr(pc, df)
r2 = stats.spearmanr(bt, df)
print("\nparticipation vs document frequency : rho = %+.3f  p = %.3g" % (r1.statistic, r1.pvalue))
print("betweenness  vs document frequency : rho = %+.3f  p = %.3g" % (r2.statistic, r2.pvalue))

print("\ndocument frequency, bridges vs the rest")
print("   bridges : mean %.1f  median %.1f  sd %.1f" % (df[isb].mean(), np.median(df[isb]), df[isb].std()))
print("   others  : mean %.1f  median %.1f  sd %.1f" % (df[~isb].mean(), np.median(df[~isb]), df[~isb].std()))
t = stats.ttest_ind(df[isb], df[~isb], equal_var=False)
print("   Welch t = %.2f  p = %.3g" % (t.statistic, t.pvalue))

print("\nbridge pillar distribution inside a narrow frequency band")
lo = int(np.percentile(df, 40))
hi = int(np.percentile(df, 80))
band = (df >= lo) & (df <= hi)
print("   band df %d to %d contains %d concepts" % (lo, hi, band.sum()))
P3 = ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]
obs = collections.Counter(pil[band & isb])
tot_band = collections.Counter(pil[band])
nb = int(sum(obs.values()))
print("   %-12s %8s %8s" % ("pillar", "bridges", "expected"))
o, e = [], []
for p in P3:
    o.append(obs.get(p, 0))
    e.append(tot_band.get(p, 0) * nb / max(sum(tot_band.values()), 1))
    print("   %-12s %8d %8.2f" % (p, obs.get(p, 0), e[-1]))
print("   expected values sum to %.2f and observed to %d" % (sum(e), nb))
if sum(o) > 3 and sum(e) > 0:
    chi = stats.chisquare(o, e)
    print("   chi-square = %.2f  dof = 3  p = %.3f" % (chi.statistic, chi.pvalue))
else:
    print("   too few bridges in band for a chi-square")

print("\nthe 20 most general concepts and their participation")
top = sorted(zip(pc, df, isb, [r["concept"] for r in rows]), key=lambda t: -t[0])[:20]
for p, d, b, nm in top:
    print("   %-24s PC %.3f  df %3d  %s" % (nm[:24], p, d, "BRIDGE" if b else ""))

out = [
    ("participation vs df Spearman rho", round(float(r1.statistic), 3),
     "p %.3g" % r1.pvalue),
    ("betweenness vs df Spearman rho", round(float(r2.statistic), 3),
     "p %.3g" % r2.pvalue),
    ("mean df, bridges", round(float(df[isb].mean()), 1), ""),
    ("mean df, non-bridges", round(float(df[~isb].mean()), 1), ""),
    ("mean df difference, Welch p", float("%.4g" % t.pvalue), "t %.2f" % t.statistic),
    ("frequency band used", "%d to %d" % (lo, hi), "%d concepts" % band.sum()),
    ("band mean df, bridges", round(float(df[band & isb].mean()), 1)
     if (band & isb).sum() else "n/a", ""),
    ("band mean df, all", round(float(df[band].mean()), 1), ""),
]
with open(os.path.join(TAB, "A2_genericity_diagnostic.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["statistic", "value", "note"])
    w.writerows(out)
print("\nwrote A2_genericity_diagnostic.csv")
