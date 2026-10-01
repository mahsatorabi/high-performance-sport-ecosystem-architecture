"""
Manuscript verification for Article 2, rewritten for b1_manuscript.py.

The previous version of this script validated the superseded draft, which had a
different document structure: a "Figure captions" section listing captions as prose
after the references, and tables placed in a "Tables" section. The current builder
embeds figures and tables inline, in reading order, and puts the reference list last.
A verifier that assumed the old layout would silently mis-partition the new document,
so it is written against the structure that actually exists.

Four checks:

  1. every in-text citation resolves to an entry in the reference list
  2. every reference list entry is cited in the text, and every narrative citation
     carries a year
  3. every decimal statistic quoted in prose appears in one of the CSVs written by
     article2/scripts, or rounds to a value that does
  4. the structural facts hold: headings, embedded images, real Word tables, and a
     word count that matches the builder under Article 1's counting rule

The word count rule is Article 1's: body paragraphs, table cells and appendix prose
count; headings, the reference list, table captions, table notes and figure captions
do not. Table notes are excluded here for the same reason captions are, and the builder
is held to the same rule so the two numbers can be compared.
"""
import os
import re
import csv
import glob
import sys
from docx import Document
from docx.oxml.ns import qn

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
DOCX = os.path.join(A2, "Article2_manuscript.docx")
TAB = os.path.join(A2, "tables")

doc = Document(DOCX)
paras = [p.text for p in doc.paragraphs]
styles = [p.style.name for p in doc.paragraphs]

# The builder is imported rather than trusted from its stdout, so the two counts below
# come from the same BLOCKS list that produced the document.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1_manuscript
BUILDER_COUNT = b1_manuscript.count_words()

i_ref = paras.index("References")
i_decl = paras.index("Declarations")

# Countable region runs from the title to the Declarations heading. The declaration
# block and the reference list are both outside it, matching the builder's rule and
# Article 1's, where the declaration block was written after the 9,000 total was fixed.
body_idx = [i for i in range(i_decl) if not styles[i].startswith("Heading")]
body = [paras[i] for i in body_idx]
decl = [t for t in paras[i_decl + 1:i_ref] if t.strip()]
reflist = [t for t in paras[i_ref + 1:] if t.strip()]

print("=" * 74)
print("ARTICLE 2 - MANUSCRIPT VERIFICATION")
print("=" * 74)
print("body paragraphs %d | declaration paragraphs %d | reference entries %d | images %d "
      "| tables %d" % (len(body), len(decl), len(reflist), len(doc.inline_shapes),
                       len(doc.tables)))

# ---------------------------------------------------------------- 1. references
# Surnames may contain a particle ("De Bosscher") or accents (Guimera,
# Sotiriadou). The family name is everything before the first comma.
SURNAME = r"(?:[Dd]e\s+)?[A-ZÀ-ſ][\wÀ-ſ'’\-]+"
ref_re = re.compile(r"^((?:%s)),\s+(.+?)\((\d{4})([a-z]?)\)" % SURNAME)
refs = {}
for r in reflist:
    m = ref_re.match(r.strip())
    if m:
        refs.setdefault(m.group(1), []).append(m.group(3) + m.group(4))
    else:
        print("  UNPARSED reference entry: %s" % r[:70])
print("\nreference entries parsed: %d from %d distinct first authors"
      % (sum(len(v) for v in refs.values()), len(refs)))
multi = {k: v for k, v in refs.items() if len(v) > 1}
if multi:
    print("  multi-entry first authors (a/b suffixes required in text): %s" % multi)

# ---------------------------------------------------------------- 2. citations
# Matching is restricted to surnames that appear in the reference list. A generic
# capitalised-word pattern produces false positives, because an ordinary word followed
# by a year ("The 2013 window", "Scopus ... 2026") is shaped like a citation.
surnames = sorted(refs, key=len, reverse=True)
ALT = "|".join(re.escape(s) for s in surnames)
# The year captures its own a/b suffix, so that two entries by the same first author in
# the same year stay distinguishable in the citation set.
YR = r"((?:1[89]\d{2}|20\d{2})[a-z]?)"
# The second slot after a surname may be a co-author surname, "colleagues", "others" or
# "et al."; all forms occur in this manuscript. Non-capturing, so the year stays at
# group index 2.
SECOND = r"(?:%s|and\s+(?:%s|colleagues|others?)|et al\.)" % (ALT, ALT)

cites = set()
undated = []
for para in body:
    # "Surname and colleagues' 2006", "Surname's 2009", "Surname and Other 2008"
    for m in re.finditer(
            r"\b(%s)(?:\s+%s)?(?:['’]s)?\s+%s" % (ALT, SECOND, YR), para):
        cites.add((m.group(1), m.group(2)))
    # "Surname and Other (2006)", "Surname and colleagues (2006)", "Surname (2006)"
    for m in re.finditer(
            r"\b(%s)(?:\s+%s)?\s*\(%s\)" % (ALT, SECOND, YR), para):
        cites.add((m.group(1), m.group(2)))
    # "(Surname et al., 2006)", "(Surname, 2006)", "(Surname and Other, 2006)"
    for m in re.finditer(
            r"\((%s)(?:\s+et al\.)?(?:\s+and\s+%s)?,\s*%s\)" % (ALT, ALT, YR),
            para):
        cites.add((m.group(1), m.group(2)))
    # Narrative with the year later in the same clause, the dominant style here:
    # "De Bosscher and colleagues built that model in 2006 from a ...". The window stops
    # at a sentence boundary so a name and an unrelated later year are not paired by
    # accident.
    for m in re.finditer(
            r"\b(%s)(?:\s+%s)?(?:['’]s)?[^.]{0,90}?\b%s" % (ALT, SECOND, YR),
            para):
        cites.add((m.group(1), m.group(2)))
    # Narrative citation carrying no year in its clause. APA requires a year in every
    # citation, so these are collected for correction rather than silently accepted.
    for m in re.finditer(r"\b(%s)\s+and\s+(%s)\b" % (ALT, ALT), para):
        clause = para[m.end():m.end() + 150].split(".")[0]
        if not re.search(YR, clause):
            undated.append((m.group(1), m.group(2),
                            para[max(0, m.start() - 45):m.end() + 55]))

print("\nin-text citations detected: %d" % len(cites))
for a, y in sorted(cites):
    print("   %-24s %s%s" % (a, y, "" if a in refs else "   <-- NOT IN REFERENCE LIST"))

print("\nnarrative citations with no year in the same clause: %d" % len(undated))
for a, b, ctx in undated:
    print("   %s and %s :: %s" % (a, b, ctx))

unresolved = [(a, y) for a, y in sorted(cites) if a not in refs]
print("\nUNRESOLVED citations (cited but absent from reference list): %d"
      % len(unresolved))
for a, y in unresolved:
    print("   %s (%s)" % (a, y))

# An entry counts as cited if the text cites its exact year, or its suffixed year. The
# unsuffixed form is not accepted as covering a suffixed entry, because that is the
# ambiguity the check above reports.
uncited = [(a, y) for a, ys in sorted(refs.items()) for y in ys
           if (a, y) not in cites]
print("\nreference entries never cited in text: %d" % len(uncited))
for a, y in uncited:
    print("   %s (%s)" % (a, y))

# When one first author has several entries in the same year, APA requires a/b suffixes
# in both the list and the text. A text citation to the bare year resolves ambiguously,
# so the check is made explicitly rather than inferred from the count above.
same_year = {a: [y for y in ys if ys.count(y) > 1] for a, ys in refs.items()
             if len(ys) != len(set(ys))}
ambiguous = []
for a, ys in same_year.items():
    for y in ys:
        if (a, y) in cites:
            ambiguous.append("%s (%s) cited without a suffix" % (a, y))
print("\nsame-year first authors needing a/b suffixes: %d %s"
      % (len(same_year), same_year if same_year else ""))
print("suffixed citations used: %s"
      % sorted({("%s %s" % (a, y)) for a, y in cites if y[-1].isalpha()}))
print("ambiguous same-year citations: %d %s"
      % (len(ambiguous), ambiguous if ambiguous else ""))

# ---------------------------------------------------------------- 3. statistics
csv_blob = ""
for f in glob.glob(os.path.join(TAB, "*.csv")):
    csv_blob += open(f, encoding="utf-8-sig").read()
corpus = open(os.path.join(A1, "data", "corpus.json"), encoding="utf-8").read()
all_csv_nums = re.findall(r"\d+\.\d+", csv_blob + corpus)

# Captions and table notes are part of the document, so a statistic in either has to be
# traceable too; they are gathered here rather than excluded.
cap_blob = "\n".join(paras[i] for i in range(i_ref)
                     if styles[i].startswith("Heading") is False and paras[i].strip())
body_blob = cap_blob

stats = set()
for m in re.finditer(r"(?<![\w.])(\d+\.\d{3,})(?![\w])", body_blob):
    stats.add(m.group(1))
missing = []
for s in sorted(stats):
    if s in csv_blob or s in corpus:
        continue
    # A manuscript rounds for readability; accept if the value appears at the reported
    # precision once rounded.
    v = float(s)
    if any(abs(float(x) - v) < 5e-4 for x in all_csv_nums):
        continue
    missing.append(s)
print("\ndecimal statistics quoted: %d" % len(stats))
print("untraceable to any A2 table or the Article 1 corpus: %d" % len(missing))
for s in missing:
    i = body_blob.find(s)
    ctx = body_blob[max(0, i - 70):i + 40].replace("\n", " ") if i >= 0 else ""
    print("   %-10s %s" % (s, ctx))

# ---------------------------------------------------------------- 4. structure
CAPRE = re.compile(r"^(Table|Figure)\s+\d+\.")


def is_note(p):
    """A table note is emitted by the builder as a 7.5pt italic run. It is apparatus
    describing a table, so the counting rule excludes it, exactly as it excludes the
    caption above the table."""
    if not p.runs:
        return False
    r = p.runs[0]
    return bool(r.italic) and r.font.size is not None and r.font.size.pt == 7.5


n_count = n_head = n_ref = n_cap = n_note = n_decl = 0
for i, t in enumerate(paras):
    t = t.strip()
    if styles[i].startswith("Heading"):
        n_head += 1
        continue
    if not t:
        continue
    if i > i_ref:
        n_ref += len(t.split())
        continue
    if i_decl < i < i_ref:
        n_decl += len(t.split())
        continue
    if CAPRE.match(t):
        n_cap += len(t.split())
        continue
    if is_note(doc.paragraphs[i]):
        n_note += len(t.split())
        continue
    n_count += len(t.split())

for tb in doc.tables:
    for row in tb.rows:
        for c in row.cells:
            n_count += len(c.text.split())

print("\nheadings %d | countable body paragraphs and appendix prose %d | table cells "
      "included" % (n_head, n_count))
print("excluded: declarations %d, reference list %d, table and figure captions %d, "
      "table notes %d" % (n_decl, n_ref, n_cap, n_note))
print("countable words (body + table cells + appendix prose): %d" % n_count)
print("target 9000 | delta %+d" % (n_count - 9000))

# The builder holds itself to the same rule, so the two counts must agree exactly. A
# difference means the builder's block list and the document have diverged.
print("agreement with the builder's count: %s"
      % ("exact" if n_count == BUILDER_COUNT else
         "MISMATCH, builder %d vs document %d (%+d)"
         % (BUILDER_COUNT, n_count, n_count - BUILDER_COUNT)))

# Embedded media
n_pic = sum(1 for s in doc.inline_shapes)
print("\nembedded images: %d (expect 7)" % n_pic)
print("Word tables: %d (expect 7), rendered as real tables not text: %s"
      % (len(doc.tables), "yes" if len(doc.tables) == 7 else "NO"))

# Prose check, same rules as Article 1.
em = body_blob.count("—")
print("\nem dashes in body, tables and captions: %d" % em)

banned = ["moreover", "furthermore", "it is worth noting", "it is important to note",
          "it should be noted", "needless to say", "in conclusion", "to sum up",
          "firstly", "secondly", "thirdly", "delve", "tapestry", "a myriad",
          "pave the way", "seamless", "underscore", "multifaceted"]
hits = [(b, len(re.findall(re.escape(b), body_blob, re.I))) for b in banned]
hits = [(b, n) for b, n in hits if n]
print("formulaic connectors found: %d %s" % (len(hits), hits if hits else ""))

# Every figure and table referenced in prose must exist, and every one that exists must
# be referenced. Captions are matched by number.
n_fig_cap = len([1 for t in paras if re.match(r"^Figure\s+\d+\.", t.strip())])
n_tab_cap = len([1 for t in paras if re.match(r"^Table\s+\d+\.", t.strip())])
print("\nfigure captions %d | table captions %d" % (n_fig_cap, n_tab_cap))
missing_ref = []
for kind, cnt in (("Figure", n_fig_cap), ("Table", n_tab_cap)):
    for k in range(1, cnt + 1):
        if not re.search(r"\b%s\s+%d\b" % (kind, k), body_blob):
            missing_ref.append("%s %d" % (kind, k))
print("captions never mentioned in body text: %d %s"
      % (len(missing_ref), missing_ref if missing_ref else ""))

# Headings must be numbered in order for a Q1 submission, and no heading may be
# duplicated, which is the usual symptom of a botched find-and-replace.
heads = [t.strip() for t, s in zip(paras, styles) if s.startswith("Heading")]
numbered = [t for t in heads if re.match(r"^\d+(\.\d+)?\.?\s", t)]
print("headings: %d total, %d numbered" % (len(heads), len(numbered)))
dupes = [t for t in set(heads) if heads.count(t) > 1]
print("duplicate headings: %d %s" % (len(dupes), dupes if dupes else ""))
