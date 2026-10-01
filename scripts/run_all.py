"""
Pipeline driver for Article 2.

Article 2 is a second-order analysis: it reads the concept families, the network and
the domain labels that Article 1's pipeline produces, and asks what structure those
carry. Its dependency on Article 1 is therefore explicit rather than hidden, and this
driver states it: Article 1's run_all.py must be run first.

Ordering matters here for one non-obvious reason. a9_load_bearing_window.py recomputes
the load-bearing test on the analysis window, and it overwrites nothing, but its
result is what qualifies the full-corpus result in Table 3. Running it after
a1_hierarchy.py and before the manuscript is required for the manuscript's two-corpus
reporting to be coherent. The figure scripts come last so that every table they read
already exists.

Stages 0-9 run in roughly four minutes once Article 1's artefacts exist. Stages 10-11
are the document build and its verification, which is what makes the reproducibility
claim checkable rather than asserted: a5_verify_manuscript.py fails loudly on an
unresolvable citation, a free-floating statistic, or a word count that disagrees with
the builder.

Usage
-----
    python scripts/run_all.py            run everything
    python scripts/run_all.py --stage 8  run one stage by number or name

What must be present before any of this will run
-------------------------------------------------
    ../article1/data/corpus.json          Article 1 corpus (withheld: Scopus licence)
    ../article1/data/network_edges.csv    Article 1 edge list (withheld, same reason)

Paths are resolved relative to this file, so the repository can be cloned anywhere
alongside a copy of Article 1's outputs.
"""
import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.normpath(os.path.join(HERE, "..", "..", "article1"))
A2 = os.path.normpath(os.path.join(HERE, ".."))

# (number, script, one-line purpose)
STAGES = [
    (0, "a0_matrices.py",
     "windowed document-by-concept matrix; period and national blocks; segregation by scope"),
    (0.5, "a0b_sensitivity.py",
     "segregation re-tested across seven network constructions"),
    (1, "a1_hierarchy.py",
     "coreness decomposition, role decomposition, full-corpus load-bearing test"),
    (2, "a2_bridges.py",
     "participation coefficient on the window; raw bridge candidates; period blocks"),
    (2.5, "a2b_stability.py",
     "size-matched block analysis, split-half reliability, power diagnostic"),
    (3, "a3_spliss_validity.py",
     "convergent validity against the nine-pillar framework, BH-corrected"),
    (4, "a8_bridges_corrected.py",
     "null-centred bridge measure, 1,000 label permutations (the decisive analysis)"),
    (5, "a9_load_bearing_window.py",
     "load-bearing recomputed on the analysis window (the two-corpus comparison)"),
    (6, "a7_genericity_diagnostic.py",
     "participation-vs-frequency confound and the frequency-band control"),
    (7, "a10_core_composition.py",
     "domain composition of each core; core frequency profile; assignment audit"),
    (8, "a6_figures.py",
     "Figures 1-6 and the domain-mixing matrix"),
    (8.5, "a11_figure7.py", "Figure 7, core composition"),
    (9, "b1_manuscript.py", "builds the manuscript (.docx) with embedded figures"),
    (10, "a5_verify_manuscript.py",
     "verifies citations, statistic traceability, word count and structure"),
]

REQUIRED_INPUTS = [
    ("Article 1 corpus", os.path.join(A1, "data", "corpus.json")),
    ("Article 1 edge list", os.path.join(A1, "data", "network_edges.csv")),
]


def preflight():
    missing = [(label, p) for label, p in REQUIRED_INPUTS if not os.path.exists(p)]
    if missing:
        print("PREFLIGHT FAILED")
        for label, p in missing:
            print("   missing %-22s %s" % (label, p))
        print()
        print("Article 2 is a second-order analysis and needs Article 1's outputs.")
        print("Run article1/scripts/run_all.py first. Note that corpus.json and")
        print("network_edges.csv are deliberately absent from the public repository:")
        print("Scopus licensing forbids redistributing them. Users with institutional")
        print("Scopus access can rebuild them from the query in docs/scopus_query.md.")
        return False
    print("preflight: Article 1 inputs present")
    return True


def run(script):
    p = os.path.join(HERE, script)
    r = subprocess.run([sys.executable, p], cwd=HERE)
    return r.returncode == 0


def main():
    sel = None
    if "--stage" in sys.argv:
        i = sys.argv.index("--stage") + 1
        if i >= len(sys.argv):
            print("--stage needs a value")
            return 2
        sel = sys.argv[i]

    if sel is None and not preflight():
        return 1

    ran = failed = 0
    for num, script, purpose in STAGES:
        if sel is not None:
            s = str(num)
            if sel not in (s, script, script[:-3]):
                continue
        print("\n" + "=" * 72)
        print("STAGE %s  %s" % (num, script))
        print("%s" % purpose)
        print("=" * 72)
        if not run(script):
            print("\nSTAGE %s FAILED (%s)" % (num, script))
            failed += 1
            if sel is None:
                return 1
        else:
            ran += 1

    print("\n" + "=" * 72)
    if failed:
        print("FINISHED WITH %d FAILING STAGE(S), %d succeeded" % (failed, ran))
    else:
        print("ALL %d STAGES COMPLETE" % ran)
    print("Tables  -> article2/tables")
    print("Figures -> article2/figures")
    print("Paper   -> article2/Article2_manuscript.docx")
    print("=" * 72)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())