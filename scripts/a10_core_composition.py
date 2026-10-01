"""
Composition of the coreness hierarchy, by domain.

Section 4.4 reports the coreness profile of the field as flat: mean coreness spans
0.42 across the four groups on a 1-12 scale, and no domain occupies the top cores. That
statement is about averages and it is true, but it conceals what is actually in the
deepest core, which is a concentration rather than a flat spread.

This script produces three things the manuscript needs.

  1. The domain composition of each core, from 12 downwards. The 12-core is 24
     concepts and it is not a cross-section of the field.

  2. The frequency profile of the deepest core. The concepts in it are rare. They
     appear in five or six documents and carry a degree of five to seven, which is a
     different kind of generality from the frequency-driven generality that section 4.3
     identifies in the participation measure.

  3. The highest-degree concepts in each domain, which is what the domains are
     actually made of, since domain names were assigned from a prototype and not from
     the concepts the domain contains.

A fourth output is a check on the assignment procedure rather than on the field: pairs
of concepts that are plainly the same referent and that received different domain
labels. These are reported as an assignment limitation and not as a finding.

Inputs:  article2/tables/A2_hierarchy_roles.csv
Outputs: A2_core_composition.csv
         A2_core12_profile.csv
         A2_domain_top_degree.csv
         A2_core12_list.csv
         A2_assignment_conflicts.csv
"""
import os
import csv
import collections
import scipy.stats as ss

A2 = r"D:\Uni of Birjand\articles\adel\article2"
TAB = os.path.join(A2, "tables")
PILLARS = ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]

rows = list(csv.DictReader(
    open(os.path.join(TAB, "A2_hierarchy_roles.csv"), encoding="utf-8-sig")))
for r in rows:
    r["coreness"] = int(r["coreness"])
    r["df"] = int(r["df"])
    r["degree"] = float(r["degree"])
    r["betweenness"] = float(r["betweenness"])

# ---------------------------------------------------------------- 1. by core
out = []
for core in sorted({r["coreness"] for r in rows}, reverse=True):
    sel = [r for r in rows if r["coreness"] == core]
    n = len(sel)
    rec = {"coreness": core, "n_concepts": n}
    for p in PILLARS:
        k = sum(1 for r in sel if r["pillar"] == p)
        rec[p] = k
        rec[p + "_share"] = round(k / n, 4)
    out.append(rec)
with open(os.path.join(TAB, "A2_core_composition.csv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)

print("=" * 74)
print("DOMAIN COMPOSITION BY CORE")
print("=" * 74)
print("%4s %6s %s" % ("core", "n", "  ".join("%-22s" % p for p in PILLARS)))
for rec in out[:6]:
    print("%4d %6d %s" % (rec["coreness"], rec["n_concepts"],
                          "  ".join("%-22s" % ("%d (%.0f%%)"
                                               % (rec[p], 100 * rec[p + "_share"]))
                                   for p in PILLARS)))
tot = {p: sum(1 for r in rows if r["pillar"] == p) for p in PILLARS}
print("%4s %6d %s" % ("all", len(rows),
                      "  ".join("%-22s" % ("%d (%.0f%%)" % (tot[p],
                                                             100 * tot[p] / len(rows)))
                                for p in PILLARS)))

# The 12-core against the field it sits in. This is the comparison that matters: a
# concentration is only interesting relative to the base rate.
c12 = [r for r in rows if r["coreness"] == 12]
print("\n12-core enrichment against the node base rate")
print("%-12s %6s %9s %9s %8s" % ("domain", "n_12", "share_12", "share_all", "ratio"))
for p in PILLARS:
    a = sum(1 for r in c12 if r["pillar"] == p)
    b = tot[p]
    print("%-12s %6d %8.0f%% %8.0f%% %8.2f"
          % (p, a, 100 * a / len(c12), 100 * b / len(rows), (a / len(c12)) / (b / len(rows))))

# Is the core-12 composition distinguishable from what the node counts predict? A
# chi-square on a 4x2 contingency, degrees of freedom 3. If this is not significant the
# core is a cross-section of the field and the flatness claim stands unchanged.
chi2, pv, dof, exp = ss.chi2_contingency(
    [[sum(1 for r in c12 if r["pillar"] == p) for p in PILLARS],
     [tot[p] - sum(1 for r in c12 if r["pillar"] == p) for p in PILLARS]])
print("\ncore-12 composition vs node base rate: chi-square = %.2f, df = %d, p = %.3f"
      % (chi2, dof, pv))
print("  expected under independence: %s"
      % ", ".join("%s %.1f" % (p, e) for p, e in zip(PILLARS, exp[0])))

# The same test for the 11-core, which is 233 concepts and therefore much better
# populated. If both are null the field has no core composition worth describing and
# the manuscript should not claim one.
c11 = [r for r in rows if r["coreness"] == 11]
chi2b, pvb, dofb, _ = ss.chi2_contingency(
    [[sum(1 for r in c11 if r["pillar"] == p) for p in PILLARS],
     [tot[p] - sum(1 for r in c11 if r["pillar"] == p) for p in PILLARS]])
print("core-11 composition vs node base rate: chi-square = %.2f, df = %d, p = %.3f"
      % (chi2b, dofb, pvb))

# ---------------------------------------------------------------- 2. profile
print("\n" + "=" * 74)
print("FREQUENCY PROFILE OF THE 12-CORE")
print("=" * 74)
d12 = [r["df"] for r in c12]
d_rest = [r["df"] for r in rows if r["coreness"] < 12]
print("12-core n = %d | mean df %.1f (median %.0f, range %d to %d)"
      % (len(c12), sum(d12) / len(d12), sorted(d12)[len(d12) // 2],
         min(d12), max(d12)))
print("rest     n = %d | mean df %.1f (median %.0f)"
      % (len(d_rest), sum(d_rest) / len(d_rest),
         sorted(d_rest)[len(d_rest) // 2]))
t, tp = ss.ttest_ind(d12, d_rest, equal_var=False)
print("Welch t = %.2f, p = %.2e" % (t, tp))

# Within the 12-core, degree against frequency. The claim is that these are rare but
# densely linked, which is a different signature from "common and therefore central".
rho, rp = ss.spearmanr([r["df"] for r in c12], [r["degree"] for r in c12])
print("within 12-core, df vs degree: rho = %.3f (p = %.3f)" % (rho, rp))
rho2, rp2 = ss.spearmanr([r["df"] for r in c12], [r["betweenness"] for r in c12])
print("within 12-core, df vs betweenness: rho = %.3f (p = %.3f)" % (rho2, rp2))

# Across the whole network, for contrast.
rho3, rp3 = ss.spearmanr([r["df"] for r in rows], [r["degree"] for r in rows])
print("across network, df vs degree: rho = %.3f (p = %.2e)" % (rho3, rp3))

with open(os.path.join(TAB, "A2_core12_profile.csv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["statistic", "value"])
    for k, v in [
            ("12-core n", len(c12)),
            ("12-core mean df", round(sum(d12) / len(d12), 2)),
            ("12-core median df", sorted(d12)[len(d12) // 2]),
            ("12-core min df", min(d12)),
            ("12-core max df", max(d12)),
            ("core below 12 mean df", round(sum(d_rest) / len(d_rest), 2)),
            ("12-core vs rest Welch t", round(float(t), 3)),
            ("12-core vs rest p", "%.3e" % tp),
            ("within 12-core df-degree rho", round(float(rho), 4)),
            ("within 12-core df-degree p", round(float(rp), 4)),
            ("within 12-core df-betweenness rho", round(float(rho2), 4)),
            ("across network df-degree rho", round(float(rho3), 4)),
            ("core-12 composition chi2", round(float(chi2), 3)),
            ("core-12 composition df", int(dof)),
            ("core-12 composition p", round(float(pv), 4)),
            ("core-11 composition chi2", round(float(chi2b), 3)),
            ("core-11 composition p", round(float(pvb), 4)),
    ]:
        w.writerow([k, v])

with open(os.path.join(TAB, "A2_core12_list.csv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["label", "pillar", "df", "degree", "betweenness", "coreness"])
    for r in sorted(c12, key=lambda r: -r["degree"]):
        w.writerow([r["label"], r["pillar"], r["df"],
                    round(r["degree"], 4), r["betweenness"], r["coreness"]])

# ---------------------------------------------------------------- 3. domains
with open(os.path.join(TAB, "A2_domain_top_degree.csv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pillar", "rank", "label", "df", "degree", "coreness", "betweenness"])
    for p in PILLARS:
        s = sorted([r for r in rows if r["pillar"] == p],
                   key=lambda r: -r["degree"])[:15]
        for i, r in enumerate(s, 1):
            w.writerow([p, i, r["label"], r["df"], round(r["degree"], 4),
                        r["coreness"], r["betweenness"]])

print("\n" + "=" * 74)
print("WHAT THE DEEPEST CORE CONTAINS")
print("=" * 74)
for r in sorted(c12, key=lambda r: -r["degree"]):
    print("  %-24s %-11s df=%-4d deg=%5.2f" %
          (r["label"], r["pillar"], r["df"], r["degree"]))

# ---------------------------------------------------------------- 4. conflicts
# Same-referent pairs that received different labels. These are a property of the
# assignment procedure and are reported as a limitation, not as a field finding.
PAIRS = [("intelligence", "ai"), ("intelligence", "artificial intelligence"),
         ("intelligence", "algorithm"), ("talent", "talent identification"),
         ("pathways", "pathway"), ("sport policy", "policy"),
         ("digital", "technologies"), ("monitoring", "tracking"),
         ("intelligent", "intelligence"), ("athlete health", "athlete performance")]
by = {r["label"]: r for r in rows}
print("\n" + "=" * 74)
print("ASSIGNMENT CONFLICTS: same referent, different domain")
print("=" * 74)
conf = []
for a, b in PAIRS:
    if a in by and b in by and by[a]["pillar"] != by[b]["pillar"]:
        rec = {"concept_a": a, "pillar_a": by[a]["pillar"],
               "concept_b": b, "pillar_b": by[b]["pillar"],
               "df_a": by[a]["df"], "df_b": by[b]["df"]}
        conf.append(rec)
        print("  %-22s %-11s vs %-22s %-11s"
              % (a, rec["pillar_a"], b, rec["pillar_b"]))
if not conf:
    print("  none")
with open(os.path.join(TAB, "A2_assignment_conflicts.csv"), "w", newline="",
          encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["concept_a", "pillar_a", "concept_b",
                                      "pillar_b", "df_a", "df_b"])
    w.writeheader()
    w.writerows(conf)
print("\nconflicts found: %d" % len(conf))
