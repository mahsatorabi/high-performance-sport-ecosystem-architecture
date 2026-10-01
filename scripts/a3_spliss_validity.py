"""
ARTICLE 2 - Stage D: convergent validity against the SPLISS nine-pillar model.

The three derived pillars (GOVERNANCE, INNOVATION, TALENT) were discovered from the corpus.
If the derived structure is real and not an artefact of embedding and clustering, it should
overlap with an independently constructed taxonomy of the same domain. SPLISS (De Bosscher
et al., 2006) supplies exactly that: nine policy pillars with roughly 100 critical success
factors, built from a literature review and national benchmarking over more than two decades,
entirely independently of any text-mining of Scopus abstracts.

Method: a lexicon maps SPLISS pillar terminology to concept families. Each concept is
assigned to the SPLISS pillar with the strongest evidence. Because the nine pillars are not
mutually exclusive by construction (SPLISS itself models policy areas, and a single policy
concern can sit in two), a concept can receive more than one assignment. Overlap between a
derived pillar and a SPLISS pillar is then measured with a two-sided Fisher exact test on the
contingency table, with the derived-pillar and SPLISS-pillar marginals held fixed.

The honest expectation is partial convergence, not identity. SPLISS is a taxonomy of POLICY
LEVERS; the derived pillars are clusters of KNOWLEDGE. Where a derived pillar concentrates on
SPLISS concepts, the two are describing the same object. Where it does not, the derived
structure captures something SPLISS has no vocabulary for, which is itself informative.
"""
import os, json, csv, collections
import numpy as np
from scipy import stats

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DATA, TAB = os.path.join(A2, "data"), os.path.join(A2, "tables")

blob = json.load(open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8"))
fam_label = blob["fam_label"]
pillar = {int(k): v for k, v in
          json.load(open(os.path.join(DATA, "pillar_of.json"))).items()}
nodes = sorted(pillar)
NN = len(nodes)

print("=" * 78)
print("ARTICLE 2 - STAGE D  convergent validity against SPLISS")
print("=" * 78)
print("concepts %d" % NN)

# SPLISS pillar terminology. Terms are the critical-success-factor vocabulary published for
# each pillar (De Bosscher et al., 2006, 2015); matching is on the concept label only, with
# no knowledge of the derived assignment, so the test is not circular.
SPLISS = {
    "P1 financial support": [
        "funding", "financial", "finance", "investment", "invest", "resource",
        "resources", "budget", "expenditure", "sponsor", "sponsorship", "subsid",
        "economic", "economies", "cost", "grant", "public spending", "afford",
    ],
    "P2 policy development": [
        "policy", "policies", "policymaking", "regulation", "regulatory", "governance",
        "legislation", "law", "legal", "government", "strategy", "strategic", "planning",
        "coordination", "framework", "accountability", "legitimacy", "ministry",
        "politics", "political", "reform", "compliance", "enforcement",
    ],
    "P3 sport participation": [
        "participation", "participate", "participating", "involvement", "access",
        "inclusion", "inclusivity", "grassroots", "community", "recreation", "active",
        "population", "retention", "dropout", "engagement",
    ],
    "P4 talent identification and development": [
        "talent", "talents", "talented", "pathway", "pathways", "academy", "academies",
        "youth", "junior", "juvenile", "development", "developing", "selection",
        "identifying", "identification", "identify", "pipeline", "transition", "elite",
        "athlete", "athletes", "players", "sporters", "prospect", "graduate",
    ],
    "P5 athlete career support": [
        "career", "support", "welfare", "wellbeing", "mental", "health", "psychosocial",
        "education", "dual", "scholarship", "financial support", "transition",
        "post-retirement", "retirement", "lifelong", "balance", "stress", "burnout",
    ],
    "P6 training facilities": [
        "facility", "facilities", "infrastructure", "equipment", "training centre",
        "training center", "centre", "center", "gym", "venue", "laboratory", "lab",
        "fitness", "gymnasium", "building", "maintenance",
    ],
    "P7 coaching": [
        "coach", "coaching", "coaches", "mentor", "mentoring", "mentorship", "tutor",
        "instruction", "instructional", "pedagog", "qualification", "certification",
        "expertise", "staff", "educator",
    ],
    "P8 competition": [
        "competition", "competitions", "competitive", "contest", "championship",
        "championships", "tournament", "event", "events", "meet", "league", "fixture",
        "international", "hosting", "calendar",
    ],
    "P9 scientific and medical support": [
        "science", "sciences", "scientific", "research", "medicine", "medical", "physiolog",
        "biomechanic", "nutrition", "psycholog", "testing", "monitoring", "analytics",
        "physiotherapy", "physiotherapist", "injury", "rehabilitation", "rehab",
        "diagnos", "screening", "biomarker", "data", "evidence",
    ],
}

# unigram match on the label; labels are single lemmas or short noun phrases
def match_spliss(label):
    hits = set()
    toks = [t for t in "".join(c.lower() if (c.isalnum() or c == " ") else " "
                              for c in label).split() if len(t) > 2]
    for p, terms in SPLISS.items():
        for t in terms:
            head = t.split()[0][:6]
            if any(head == tk[:6] for tk in toks):
                hits.add(p)
                break
    return hits


rows = []
assign = {}
for i in nodes:
    assign[i] = match_spliss(fam_label[i])

cov = sum(1 for v in assign.values() if v)
print("concepts matched to at least one SPLISS pillar: %d of %d (%.1f%%)"
      % (cov, NN, 100 * cov / NN))
for p in SPLISS:
    n = sum(1 for v in assign.values() if p in v)
    print("   %-34s %4d concepts" % (p, n))

DERIVED = ["GOVERNANCE", "INNOVATION", "TALENT", "UNASSIGNED"]
print("\ncontingency table (derived pillar x SPLISS pillar presence)")
tab = np.zeros((len(DERIVED), len(SPLISS) + 1), dtype=int)
for i in nodes:
    d = pillar[i]
    di = DERIVED.index(d)
    if not assign[i]:
        tab[di, -1] += 1
    else:
        for p in assign[i]:
            tab[di, list(SPLISS).index(p)] += 1

hdr = [p.split()[0] for p in SPLISS] + ["noSPLISS"]
print("   %-12s %s" % ("", " ".join("%7s" % h for h in hdr)))
for r, d in enumerate(DERIVED):
    print("   %-12s %s" % (d, " ".join("%7d" % v for v in tab[r])))

# strongest pairwise association: for each derived pillar, which SPLISS pillar is over-represented
print("\nper-derived-pillar enrichment (Fisher exact, two-sided, BH-corrected within row)")
allp = []
for r, d in enumerate(DERIVED[:3]):
    res = []
    for c in range(len(SPLISS)):
        a = tab[r, c]
        b = tab[r, -1]
        c2 = tab[:, c].sum() - a
        d2 = tab[:, -1].sum() - b
        odds, p = stats.fisher_exact([[a, b], [c2, d2]])
        res.append((p, odds, list(SPLISS)[c], a, c2))
    res.sort()
    m = len(res)
    for rank, (p, odds, name, a, exp) in enumerate(res):
        adj = min(1.0, p * m / (rank + 1))          # Benjamini-Hochberg
        allp.append((d, name, p, adj, odds, a, exp))
    for p, odds, name, a, exp in res[:3]:
        print("   %-11s %-34s in=%3d (col total %3d)  OR=%.2f  p=%.3g  BH=%.3g"
              % (d, name, a, exp, odds, p, min(1.0, p * m / 1)))

sig = [(d, n, ad) for d, n, p, ad, o, a, e in allp if ad < .05]
print("\n   pairs surviving BH at .05: %d of %d tested" % (len(sig), len(allp)))
for d, n, ad in sorted(sig, key=lambda t: t[2]):
    print("     %-11s x %-34s BH p = %.3g" % (d, n, ad))

# direction of agreement: does the DERIVED label predict the SPLISS label at all?
print("\naggregate: derived pillar vs SPLISS pillar, marginal association")
for r, d in enumerate(DERIVED[:3]):
    v = [x for x in tab[r, :len(SPLISS)]]
    print("   %-11s has any SPLISS match: %3d of %3d (%.1f%%)"
          % (d, sum(v), sum(v) + tab[r, -1], 100 * sum(v) / (sum(v) + tab[r, -1])))

with open(os.path.join(TAB, "A2_spliss_convergent_validity.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["derived_pillar", "spliss_pillar", "n_in", "n_column_total",
                "odds_ratio", "p_fisher", "p_bh"])
    for d, n, p, ad, o, a, e in allp:
        w.writerow([d, n, a, e, round(float(o), 4), float("%.4g" % p), float("%.4g" % ad)])

with open(os.path.join(TAB, "A2_contingency_derived_spliss.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["derived_pillar"] + [p for p in SPLISS] + ["no_spliss_match"])
    for r, d in enumerate(DERIVED):
        w.writerow([d] + list(tab[r]))

print("\nWrote A2_spliss_convergent_validity.csv, A2_contingency_derived_spliss.csv")
