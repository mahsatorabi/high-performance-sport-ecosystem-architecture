"""
Assemble the public replication repository for Article 2.

Article 1's build_repo.py is the model. The controlling constraint is the same:
Scopus licensing forbids redistributing bibliographic records, so this script
copies code, derived tables, figures and the manuscript, and refuses to copy
anything derived from record text. The final sweep walks the assembled tree and
exits non-zero if a forbidden file survived, which is the check that matters,
because a stale copy in the staging directory would otherwise be committed.

What is withheld, and why
--------------------------
  data.csv, corpus.json      raw and consolidated Scopus exports (licence)
  *.npy                      document-concept matrices, embeddings, degree and
                             adjacency arrays: numeric transforms of record text
  data/blocks.json, etc.     block definitions and per-document country labels,
                             which are a projection of the record set
  country_window.json        one country string per document: a per-record field

What is released, and why
-------------------------
  tables/*.csv               aggregate network and concept statistics. These are
                             outputs of the analysis, not bibliographic records.
                             Two of them carry concept labels, which is the same
                             class of derived artefact Article 1 released and
                             which does not reproduce any record's text.
  figures/*.png              300 dpi renders
  manuscript/*.docx          the submission document
  scripts/*.py               the pipeline
  docs/                      query record, method and results notes
"""
import os
import shutil
import glob
import sys

SRC = r"D:\Uni of Birjand\articles\adel"
A1 = os.path.join(SRC, "article1")
A2 = os.path.join(SRC, "article2")
DST = os.path.join(SRC, "repo_build2")

# Scopus records and record-derived binaries: never committed.
FORBIDDEN_NAMES = {
    # raw and consolidated exports
    "data.csv", "corpus.json", "corpus_meta.csv",
    # Article 1 artefacts that Article 2 reads
    "network_edges.csv", "concept_family_map.csv", "families.csv", "concepts.csv",
    "pillar_of.json",
    # per-document projections of the record set
    "country_window.json", "blocks.json",
}
FORBIDDEN_EXT = {".npy", ".npz"}

copied, skipped = [], []


def copy_file(src, dst, force=False):
    base = os.path.basename(src)
    ext = os.path.splitext(base)[1].lower()
    if base in FORBIDDEN_NAMES or ext in FORBIDDEN_EXT:
        skipped.append(base)
        return
    if not force and os.path.exists(dst):
        # Stale files in the staging tree would silently ship. Overwrite rather than
        # skip, so that a rerun after a rename removes nothing by accident.
        shutil.copy2(src, dst)
        copied.append(os.path.relpath(dst, DST))
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    copied.append(os.path.relpath(dst, DST))


def wipe():
    """Clear the staging tree but keep .git, .gitignore and docs/, so this can be rerun
    before a push. README.md, CITATION.cff, LICENSE and requirements.txt are also kept:
    they are hand-written prose with no upstream source, and regenerating a repository
    should not silently delete them."""
    if not os.path.isdir(DST):
        os.makedirs(DST)
        return
    keep = {".git", ".gitignore", "README.md", "CITATION.cff", "LICENSE",
            "requirements.txt", "docs"}
    for name in os.listdir(DST):
        if name in keep:
            continue
        p = os.path.join(DST, name)
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)


wipe()

# 1. analysis pipeline. a4_manuscript_docx.py and a3_structure_docx.py are the
# superseded draft builder and the outline generator for a structure that no longer
# exists; shipping them would let a reader regenerate the old manuscript and its
# abandoned claims, so they are left behind explicitly rather than by accident.
SUPERSEDED = {"a4_manuscript_docx.py", "a3_structure_docx.py"}
for f in sorted(glob.glob(os.path.join(A2, "scripts", "*.py"))):
    b = os.path.basename(f)
    if b in SUPERSEDED:
        skipped.append(b + " (superseded)")
        continue
    copy_file(f, os.path.join(DST, "scripts", b))

# 2. result tables
for f in sorted(glob.glob(os.path.join(A2, "tables", "*.csv"))):
    copy_file(f, os.path.join(DST, "tables", os.path.basename(f)))

# 3. figures
for f in sorted(glob.glob(os.path.join(A2, "figures", "*.png"))):
    copy_file(f, os.path.join(DST, "figures", os.path.basename(f)))

# 4. manuscript. The structure outline describes the pre-revision document, so only
# the current manuscript is shipped.
for f in ["Article2_manuscript.docx"]:
    p = os.path.join(A2, f)
    if os.path.exists(p):
        copy_file(p, os.path.join(DST, "manuscript", f))

# 5. verification output, and the hand-written docs. The verifier's report is committed
# as a static file so the manuscript's validation claims can be checked without running
# the pipeline. The docs are maintained alongside the code, so they are preserved across
# the wipe at the top rather than being rewritten each run.
VER = os.path.join(DST, "verification")
for f in ["verification_report.txt"]:
    p = os.path.join(A2, f)
    if os.path.exists(p):
        copy_file(p, os.path.join(VER, f))

print("=" * 72)
print("REPOSITORY ASSEMBLY - ARTICLE 2")
print("=" * 72)
print("staged at %s" % DST)
print("copied %d files" % len(copied))
for c in sorted(set(copied)):
    print("   %s" % c)
print()
print("EXCLUDED %d" % len(skipped))
for s in sorted(set(skipped)):
    print("   %s" % s)

# Final safety sweep over everything actually on disk, not just what this run copied.
leaked = []
for root, dirs, files in os.walk(DST):
    dirs[:] = [d for d in dirs if d != ".git"]
    for f in files:
        if f in FORBIDDEN_NAMES or os.path.splitext(f)[1].lower() in FORBIDDEN_EXT:
            leaked.append(os.path.join(root, f))
if leaked:
    print("\n*** LEAK CHECK FAILED ***")
    for l in leaked:
        print("   %s" % l)
    sys.exit(1)

# A second check: no file may contain a Scopus record field. The tables and
# verification report are the realistic carriers. build_repo.py is excluded from the
# scan because it necessarily names the fields it is looking for, which is the one
# place in the repository where they appear at all.
NEEDLES = ["prism.doi", "eid", "dc:identifier", "@affiliation", "au-affil",
           "cited-by-count", "Author full name"]
SELF = "build_repo.py"
hits = []
for root, dirs, files in os.walk(DST):
    dirs[:] = [d for d in dirs if d != ".git"]
    for f in files:
        if f == SELF:
            continue
        if not f.lower().endswith((".csv", ".md", ".txt", ".cff")):
            continue
        p = os.path.join(root, f)
        blob = open(p, encoding="utf-8", errors="ignore").read()
        for nd in NEEDLES:
            if nd.lower() in blob.lower():
                hits.append("%s :: %s" % (os.path.relpath(p, DST), nd))
if hits:
    print("\n*** RECORD-FIELD CHECK FAILED ***")
    for h in hits:
        print("   %s" % h)
    sys.exit(1)

print("\nleak check: clean")
print("record-field check: clean (no Scopus export fields in any text artefact)")
# docs/ is hand-written and preserved across the wipe, so its contents are reported
# rather than asserted. An empty docs/ after a run means the prose was lost.
n_docs = len(glob.glob(os.path.join(DST, "docs", "*.md")))
print("staged %d scripts, %d tables, %d figures, %d manuscript, %d verification, "
      "%d docs"
      % (len(glob.glob(os.path.join(DST, "scripts", "*.py"))),
         len(glob.glob(os.path.join(DST, "tables", "*.csv"))),
         len(glob.glob(os.path.join(DST, "figures", "*.png"))),
         len(glob.glob(os.path.join(DST, "manuscript", "*.docx"))),
         len(glob.glob(os.path.join(VER, "*"))),
         n_docs))
if n_docs == 0:
    print("\n*** WARNING: docs/ is empty. README, licence and query record are missing. ***")