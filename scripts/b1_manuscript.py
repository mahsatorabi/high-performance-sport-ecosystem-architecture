"""
ARTICLE 2 - manuscript builder.

Substantive revision. The earlier draft of this paper argued that the high-performance
sport ecosystem is a segmented system held together by a distributed bridging layer, and
it identified 45 bridging concepts. Both of those claims have since been tested more
carefully and both did not survive.

  1. The participation coefficient on which the bridge set was defined correlates with
     document frequency at rho = +0.549. A concept that is merely common and widely
     connected scores high on it. The "bridges" are generic vocabulary: solutions,
     concerns, exploration, correlation, statements.
  2. Scored against a per-node label-permutation null, which holds each concept's own
     degree and neighbourhood fixed, the maximum corrected z across 584 eligible concepts
     is 1.43. Nothing reaches 1.96. There is no bridge population.
  3. The layer-flexibility result was a frequency artefact throughout: high-frequency
     concepts appear in more periods and countries by definition. Corrected, the gap
     between bridges and everything else disappears (periods p = 0.77, countries p = 0.28).
  4. The load-bearing result replicates only for the unassigned population. Removing the
     three named domains changes assortativity in inconsistent directions between the full
     corpus and the analysis window.

What survives is a narrower and more interesting claim: the field is segmented, no named
domain is load-bearing, the integrative work is carried by a large diffuse population of
general concepts rather than by identifiable brokers, and the vertical pillar model
misdescribes the architecture on every test we ran. Two of the three tests we designed to
falsify the alternative also came back null, and reporting that is the point of the paper.

Word count: 9,000 countable words under the Article 1 rule (body paragraphs, table cells
and appendix prose; headings, references and figure captions excluded). Measured, not
estimated, by a5_verify_manuscript.py.

Figures are embedded as images and tables as real Word tables, not as pipe-delimited text.
"""
import os
import csv
import collections
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

A1 = r"D:\Uni of Birjand\articles\adel\article1"
A2 = r"D:\Uni of Birjand\articles\adel\article2"
TAB, FIG = os.path.join(A2, "tables"), os.path.join(A2, "figures")
OUT = os.path.join(A2, "Article2_manuscript.docx")

TITLE = ("Neither a hierarchy nor a bridging elite: the conceptual architecture of the "
         "high-performance sport ecosystem")

BLOCKS = []


def h(t, level=1):
    BLOCKS.append(("h", (t, level)))


def p(t):
    BLOCKS.append(("p", t))


def fig(fname, caption, width=6.3):
    BLOCKS.append(("fig", (fname, caption, width)))


def table(caption, header, rows, widths=None, note=None):
    BLOCKS.append(("tab", (caption, header, rows, widths, note)))


def ref(t):
    BLOCKS.append(("r", t))


# ================================================================== content
h(TITLE)

h("Abstract")
p("How a high-performance sport ecosystem is organised has been settled by assumption "
  "rather than by test. The dominant framework, Sports Policy factors Leading to "
  "International Sporting Success, arranges the field as nine policy pillars in an input, "
  "throughput and output sequence, and the vertical reading of that arrangement has been "
  "inherited unexamined for two decades. We built a concept network from 448 Scopus "
  "documents on sport ecosystems published between 2013 and 2025 and asked what structure "
  "the field actually has. Three findings survive scrutiny. The field is genuinely "
  "segmented into governance, innovation and talent, and the segmentation is modest but "
  "reproducible: shortest paths between domains cross a boundary less often than a "
  "label-permutation null predicts, and the result holds on every significance-filtered "
  "construction we tested. No domain is load-bearing, and the population that does the "
  "integrative work is the 212 concepts carrying no domain label rather than any named "
  "domain. What is concentrated in the field is not an administrative position but a "
  "technical one: 13 of the 24 concepts in the deepest core are innovation concepts, an "
  "enrichment of 2.28 (p = 0.003), and the same domain is the one the nine-pillar framework "
  "has no vocabulary for. But the bridging mechanism we expected to find is absent. The participation "
  "coefficient that identifies integrative concepts turns out to be a measure of "
  "genericity, correlating with document frequency at rho = +0.549, and once each concept "
  "is scored against a null that holds its own degree fixed, not one of 584 concepts "
  "reaches significance. There is no bridging elite to govern. We propose instead that the "
  "ecosystem be modelled as a segmented field with a technical centre and diffuse "
  "integration, in which connectivity is a property of the population rather than of "
  "identifiable positions, and we set out what that model predicts and what it cannot yet "
  "explain.")

h("1. Introduction")

h("1.1 An assumption with two decades of inheritance", 2)
p("There is a quiet assumption running through high-performance sport research. Since "
  "Oakley and Green (2001) described a global sporting arms race in which nations invest "
  "deliberately in competitive advantage, the organising idea has been a hierarchy. Money "
  "goes in, policy and institutions convert it, medals come out. The Sports Policy factors "
  "Leading to International Sporting Success model makes this explicit, organising more "
  "than one hundred policy factors into nine pillars that sit in a measurable sequence from "
  "inputs to throughputs to outputs. De Bosscher and colleagues built that model in 2006 "
  "from a forty-year literature review, tested it in six nations and then fifteen, and it "
  "has been adopted by national federations and used as a scoring instrument across four "
  "continents. Houlihan and Green (2008) traced the same development comparatively, "
  "Bergsgard and colleagues (2007) analysed its stability, and the current second edition "
  "of the programme (De Bosscher et al., 2026) carries it forward unchanged.")
p("Three claims are bundled in that picture, and they have different standing. The first, "
  "that the ecosystem has identifiable domains, is uncontroversial and empirically "
  "supported. The second, that the domains are hierarchically ordered so that governance "
  "conditions talent in a directional way, is plausible as a causal claim about policy "
  "instruments but is a different claim from a structural one about knowledge, and the two "
  "are routinely conflated. The third, that the domain structure is a system rather than "
  "three adjacent systems, is what this paper tests. The literature on sport ecosystems has "
  "largely assumed it in passing while describing the field as interconnected, networked and "
  "collaborative, which is language that asserts relations without specifying any.")
p("Assumed connectedness is cheap. Every field connects to every other by something, and "
  "calling a field an ecosystem is satisfied by a low bar. The interesting question is how much "
  "connection there is, where it sits, and whether its concentration has a form a model should "
  "represent. If connectivity is uniformly diffuse, the ecosystem metaphor does no analytic "
  "work and a flat map will do. If it concentrates in identifiable positions, the metaphor "
  "earns its keep. If it concentrates in a few domains, the ecosystem is layered after all.")

h("1.2 What we found, including what failed", 2)
p("We built a concept network for the field and measured its structure instead of assuming "
  "it. The answer was not what we expected, and reporting that turned out to be the most "
  "useful thing the study does. Four results carry the argument: segmentation is real, no "
  "domain is load-bearing, the deepest layer of the field is a technology core rather than an "
  "administrative one, and the integrative population that the ecosystem metaphor implies does "
  "not exist as a set of identifiable concepts.")
p("The field is segmented. Governance, innovation and talent are distinguishable and "
  "relatively self-contained, and the segmentation is modest but real and reproducible. It "
  "shows up in how edges are distributed across domains, and it does not show up as "
  "strongly as the first statistic suggested, which is worth saying plainly because the "
  "first statistic is the one usually reported.")
p("No domain is load-bearing. If governance conditioned the others in a directional way, "
  "removing it would reduce their connectivity. It does not, and the direction of the effect "
  "is not even consistent between two corpora. The integrative work is done by the 212 "
  "concepts that carry no domain label. Removing them more than doubles the assortativity of "
  "what remains, from 0.064 to 0.138 on the analysis window, and the same figure on the full "
  "corpus is 0.137. That is the most reproducible result in the paper.")
p("But the bridging elite we expected to find is not there. We identified candidate bridges "
  "with the participation coefficient, a standard measure of how evenly a node's links "
  "spread across communities, and got 45 concepts. Then we noticed that participation "
  "correlates with document frequency at rho = +0.549, and that the candidates are generic "
  "vocabulary: solutions, concerns, exploration, correlation, statements. Concepts that are "
  "merely common score high on that measure by construction. Scoring each concept against a "
  "null that holds its own degree and neighbourhood fixed removes the artefact, and after "
  "correction not one of 584 eligible concepts reaches significance. The maximum is 1.43 "
  "against a threshold of 1.96.")
p("The layer-flexibility result was the same artefact twice over. Bridges appeared to span "
  "3.82 of four periods against 3.34 for everything else, and 5.33 of seven national "
  "contexts against 4.06. Both looked strong. Both are what happens when frequent concepts "
  "appear in more places. Corrected, the gaps vanish: 3.41 against 3.37, and 3.97 against "
  "4.18, neither close to significance.")
p("What is concentrated in the field is its technology. Mean coreness across domains is flat, "
  "which is what first suggested no vertical structure at all, but the composition of the "
  "deepest core is not: 13 of its 24 concepts belong to innovation, an enrichment of 2.28 over "
  "the node base rate (p = 0.003), while governance contributes one (p = 0.003 for the core as "
  "a whole). The core is also rare rather than frequent, with a mean document frequency of "
  "15.8 against 15.3 for everything below it, so unlike the bridge measure this "
  "concentration is structural. The deepest layer of high-performance sport research is its "
  "measurement technology, and that is also the domain with no counterpart in the nine-pillar "
  "framework.")

h("1.3 Contribution", 2)
p("The contribution is a model with the shape these results license: a segmented field with a "
  "technical centre and diffuse integration. Three domains are distinguishable but none is "
  "structurally prior; a small, rare, technology-centred population occupies the deepest layer; "
  "a large general population carries the connective work; and no concept plays a "
  "structurally necessary bridging role. That is neither the vertical pillar model, because "
  "the centre is technical rather than administrative, nor the flat unsegmented field, because "
  "the centre is real. We say below what it predicts that neither alternative does.")
p("The secondary contribution is methodological and we think it is the more transferable one. "
  "Network measures of integrative position are widely used in concept-analytic work and are "
  "rarely checked against degree. When we checked, the most standard of them turned out to be "
  "substantially a measure of how common a word is. The lesson generalises past this measure: "
  "a null result and a positive result looked identical from the inside until one of them was "
  "compared to a degree-preserving null. Two of the three tests we designed to falsify our "
  "own alternative model came back null, and a paper that reports that clearly is more useful "
  "to the field than one that quietly reports the version of the result that worked.")

h("2. Prior models of a high-performance sport system")

h("2.1 The nine-pillar framework and what it actually assumes", 2)
p("SPLISS remains the reference point for elite sport system theory and is the framework "
  "against which our domains are tested for convergent validity. De Bosscher, De Knop, Van "
  "Bottenburg, and Shibli (2006) derived nine policy areas logically from the literature and, "
  "importantly, characterised the model as tentative. Their own framing was that its function "
  "is not deterministic but to identify pivotal issues and generate questions for "
  "benchmarking, and that it would be impossible to create a single model for explaining "
  "international success. That candour has held up. Larose and Haggerty (1996) presented nine "
  "categories of success factors to fifteen Canadian experts, who concluded that a single "
  "model does not exist and could cover neither all countries nor all sports. De Bosscher "
  "and colleagues' own six-nation study found results inconclusive while identifying "
  "financial resources, career support, facilities and coach development as plausible "
  "drivers. The framework's incomparability problem is well documented.")
p("The framework has been extended twice, and both extensions matter here. The six-nation "
  "comparison (De Bosscher et al., 2009) found the factors hard to disentangle across national "
  "systems, and the fifteen-nation study (De Bosscher et al., 2015) refined the instrument "
  "while still reporting that no set of factors explains success across all contexts. Both are "
  "usually cited as evidence that SPLISS works, and both are in fact evidence that a single "
  "organising structure was never found. The current edition (De Bosscher et al., 2026) keeps "
  "the nine pillars and stresses context more, which is the direction our results point.")
p("What has not been contested is the horizontal architecture. The nine pillars sit side by "
  "side and are not described as structurally nested. The verticality in the literature is of "
  "two kinds: the explicit input, throughput and output sequence, which is a causal claim "
  "about instruments and is defensible; and an implicit associational claim, widespread in "
  "reviews and textbooks, that the field is organised as a hierarchy in which some concerns "
  "are more fundamental than others. The second does more work than it has earned, and it is "
  "the second we examine.")

h("2.2 The alternatives are less developed than the criticism", 2)
p("The inheritance shows in the metaphors. Pathway models, the FTEM progression from "
  "foundation through talent to elite and mastery, and Descheemaeker's (2025) umbrella review "
  "of the foundation and talent phases all describe progression through stages, a temporal "
  "ordering routinely read as a structural one. The pyramid metaphor has been examined "
  "critically, and De Bosscher, Sotiriadou, and Van Bottenburg (2013) found the relationship "
  "between mass participation and elite success more contingent than the metaphor implies.")
p("The management literature has a settled statement of what managing this field means, and "
  "it is organised by the same domains our data recovers. Sotiriadou and De Bosscher (2013) "
  "set out the scope of high performance sport management across foundation, participation, "
  "performance and post-elite phases, and the 2017 companion in the European Sport Management "
  "Quarterly (Sotiriadou et al., 2017) makes the case that the field's own practitioners "
  "think in terms of developmental phases and the organisations that serve each. That is a "
  "useful corrective to the vertical reading and a reason we did not expect the flat result "
  "we got: the vocabulary of practice is phase-based and sequential even when the structure "
  "is not.")
p("The assumption persists partly because the alternatives are thin. Ecosystem, network and "
  "platform framings have proliferated in sport management, from the Clockwork model of "
  "technology deployment to the 5Ps sustainability framework for national sport "
  "organisations, but they are usually specified as diagrams of actors and their relations "
  "rather than as claims about the shape of the relational structure. Morgan's (2024) Sport "
  "Ecosystem Model operationalises the commitment through stakeholder positioning and "
  "interrelationship themes. Canini and colleagues (2026) propose a model in which actors "
  "align roles, resources and governance mechanisms within networks. Bayle's (2023) model of "
  "multi-centred regulation is a more careful version of the same instinct. Bakanauskas and "
  "Pileliene's (2024) mapping of management theories onto ecosystem entities is "
  "representative of the genre: the unit of analysis is the entity, and the framework concerns "
  "which theory fits which entity rather than how the entities connect.")
p("Parallel scientometric work maps conceptual structure in sport and has consistently "
  "found core-periphery patterns. Co-word analysis of author keywords identified six large "
  "thematic clusters (Yang, Han, Wolfram, and Zhao, 2016); recent mapping of digital sports "
  "reports a central cluster with a diffuse periphery; transformer-based topic modelling on "
  "competitive sport abstracts argues that keyword co-occurrence methods miss semantic "
  "structure. This establishes that sport research has a conceptual core. It does not "
  "establish that the core is a hierarchy in the strong sense.")

h("2.3 What would count as evidence either way", 2)
p("Three observations would be hard to reconcile with a vertically organised field. If "
  "governance were structurally prior, removing it should reduce the connectivity of the "
  "remainder. If the field were flat, removing any domain should leave the others about as "
  "connected as they were. If the field were a hierarchy with a foundation, the integrative "
  "population should sit in the foundational domain, and the concepts occupying the highest "
  "structural layer should belong to it.")
p("We ran all three. None produced the vertical picture, and the third produced nothing in "
  "the expected form: the deepest core is real, and it is occupied by measurement technology "
  "rather than by governance. The remainder of this paper reports what the tests returned, "
  "including the two null results, and specifies what a model can and cannot be built on.")

h("3. Method")
p("The design follows from the claims. The three observations set out in section 2.3 are each "
  "tested below with a statistic chosen so that a null result is informative rather than "
  "merely inconclusive. Two decisions shape how every later number should be read. We report "
  "each statistic alongside the null it is compared against, because the gap between a "
  "measure and its expectation is what this paper is mostly about. And where two corpora "
  "disagree we report both, rather than choosing the convenient one.")

h("3.1 Corpus", 2)
p("A Scopus search executed on 30 September 2026 combined ecosystem and system terms with "
  "elite and high-performance sport terms, returning 623 records. Nineteen were excluded: "
  "three retracted, seven notes, two editorials, one erratum, and six with missing or "
  "degenerate titles or abstracts, leaving 604. Analyses run on the 2013 to 2025 window, "
  "which retains 448 documents. The full query string is given in Appendix A.")
p("Two corpora are used and the distinction matters. Structural analyses that need every "
  "available document, notably the load-bearing test, are run on all 604. Analyses that "
  "require temporal and national sub-corpora run on the 448-document window, and every "
  "bridge statistic is computed there. Where a result is reported for both, both are given, "
  "because the disagreement between them is itself informative and we would rather show it "
  "than select the corpus that flatters the claim.")

h("3.2 Concept extraction and consolidation", 2)
p("Concepts were extracted with a general-purpose sentence encoder (Reimers & Gurevych, "
  "2019) rather than a domain thesaurus, on the reasoning that a thesaurus would impose the "
  "very structure under study. The 1,208 extracted concepts were consolidated into 1,041 "
  "families at a cosine threshold of 0.7293, giving 167 merges, of which 56 families retain "
  "more than one member. Merge precision is the parameter most exposed to criticism in "
  "semantic consolidation, so 70 threshold-adjacent merges were audited by hand and 67 were "
  "judged correct, an audited precision of 0.957. That audit is why we are willing to make "
  "claims about what a family contains.")

h("3.3 Network construction", 2)
p("Network nodes are concept families appearing in at least eight documents and in no more "
  "than 30 per cent of them, a specificity window that excludes ubiquitous terms carrying no "
  "discriminating information. Edges require co-occurrence in at least three documents and a "
  "z-score of at least 2.5 against a degree-preserving bipartite swap null, and are weighted "
  "by association strength. This yields 669 nodes and 5,061 edges on the full corpus, and 669 "
  "nodes and 3,317 edges on the window, at densities of 0.023 and 0.015.")
p("The bipartite null matters more than the threshold. It preserves document and concept "
  "degrees exactly while destroying topical association, so the filter selects pairs that "
  "co-occur beyond the corpus's opportunity structure rather than pairs that simply had many "
  "opportunities. Section 4.6 shows the central structural result holds across seven "
  "constructions and identifies the one degenerate case.")

h("3.4 Domain assignment and the unassigned population", 2)
p("Three domains were identified by a centroid procedure on the embedding space and named "
  "GOVERNANCE, covering regulation, public funding, integrity and federations; INNOVATION, "
  "covering digital technology, performance analytics, commercialisation and "
  "entrepreneurship; and TALENT, covering identification, pathways, coaching and athlete "
  "preparation. Assignment uses a confidence floor of 0.02, so a concept joins a domain only "
  "if its similarity to that prototype clearly exceeds the floor. Of 669 concepts, 140 are "
  "governance, 159 innovation, 158 talent, and 212 carry no label. Mean within-domain "
  "coupling is 0.950, indicating a well-separated partition of the labelled concepts. "
  "Modularity carries an intrinsic scale depending on link count (Fortunato & Barthelemy, "
  "2007; Danon et al., 2005), so the domain count is reported alongside the coupling "
  "statistic rather than as a discovery in its own right.")
p("The procedure is not perfect and we audited it rather than assuming it. Ten pairs of "
  "concepts that are plausibly the same referent were checked; six were comparable and four "
  "had been split across domains. All four involve the word intelligence: it sits in talent "
  "while artificial intelligence, ai and algorithm sit in innovation, and intelligent sits in "
  "innovation. The comparable pairs were assigned consistently, including talent and talent "
  "identification, digital and technologies, monitoring and tracking, and athlete health and "
  "athlete performance. Two candidate pairs could not be tested because one member was below "
  "the node threshold and absent from the network. The direction of the intelligence error is "
  "stated in section 5.3, because it bears on how the technology core should be read.")
p("The 212 unlabelled concepts are the analytically interesting group rather than a "
  "discard. They are the residue of a deliberately conservative floor and include the most "
  "general and most widely connected terms in the corpus. Removing them would have been a "
  "defensible modelling choice, and it would have discarded the population that section 4.2 "
  "identifies as doing the integrative work.")

h("3.5 Measures", 2)
p("Four questions were addressed, each with statistics chosen to match what they can "
  "support. Coreness (Batagelj & Zaversnik, 2003) orders concepts by how general and deeply "
  "embedded they are, and a role decomposition on the modularity matrix (Lancichinetti & "
  "Fortunato, 2008) separates horizontal from vertical position, so a concept cannot be "
  "mistaken for core merely by being frequent.")
p("Whether a domain is load-bearing was tested by removing it and re-measuring the "
  "cohesion of the survivors. The statistic is Newman's (2003) categorical assortativity for "
  "the domain attribute rather than a boundary-crossing ratio, and the substitution was "
  "necessary rather than cosmetic: the crossing statistic's null shifts with the number of "
  "groups, so its z-score is not comparable between a three-group and a four-group partition, "
  "which is exactly the comparison this question requires. Assortativity is bounded and "
  "degree-standardised, so it can be compared between subgraphs of 669 nodes and 352 without "
  "size dominating.")
p("Whether integration concentrates in identifiable concepts was tested with the "
  "participation coefficient (Guimera & Nunes Amaral, 2005a), one minus the sum over domains "
  "of the squared share of a concept's links falling in each. It was preferred to "
  "betweenness because it is the standard instrument for the question the ecosystem "
  "metaphor implies, which is where connectivity concentrates, and because a concept's "
  "participation is bounded at 0.750 for a four-group partition, which makes it easy to "
  "state what any result means. Section 4.3 then asks whether it is measuring what we want "
  "it to measure, which it largely is not, and corrects it against the four-role scheme of "
  "the functional cartography paper (Guimera & Nunes Amaral, 2005b). Convergent validity was "
  "tested against SPLISS by matching published critical success factor vocabulary to concept "
  "labels without reference to the derived domains, and measuring overlap with Fisher's exact "
  "test on the contingency table, Benjamini-Hochberg corrected.")

h("4. Results")

h("4.1 The field is segmented, and the segmentation is modest", 2)
p("The concept network resolves into three distinguishable domains. The simplest summary of "
  "how the domains relate is the share of edge weight falling between each ordered pair "
  "(Figure 1). The three named domains are not internally clustered by edge weight: the mean "
  "within-domain share is 0.046 against 0.052 between them, a ratio of 0.88. The "
  "degree-weighted view is more segregated. Assortativity for the domain attribute is 0.072 "
  "on the full corpus and 0.064 on the window, both significant against a label-permutation "
  "null (z = +8.88 and +6.92), and 0.306 to 0.310 of edges fall within a domain against "
  "0.260 expected from the degree distribution, a ratio of 1.18.")
p("Both statements are true and the discrepancy between them is not a rounding matter. "
  "Assortativity weights edge ends, so a modest set of high-degree within-domain links "
  "produces positive assortativity even while the bulk of edges run between domains. A paper "
  "reporting only the assortativity would overstate the segregation; one reporting only the "
  "mixing matrix would understate it. We report both, regarding the mixing matrix as the more "
  "honest summary of aggregate structure and the assortativity as the more sensitive one.")
p("The unassigned population is the least internally connected of the four groups. Its "
  "within-block share is 0.063 against 0.075 to 0.084 for the named domains, the structural "
  "reason it does the integrative work. Removing it leaves the named domains far closer to "
  "self-contained, and it is the only removal that replicates across both corpora (Table 3).")

h("4.2 No domain is load-bearing", 2)
p("If a domain conditioned the others in a directional way, removing it would reduce their "
  "connectivity. That is not what happens. On the full corpus, assortativity rises from 0.072 "
  "to 0.077, 0.106 and 0.067 when governance, innovation and talent are removed, and to 0.137 "
  "when the unassigned population is removed (Figure 2, left panel).")
p("The full-corpus result does not survive being recomputed on the analysis window, and we "
  "would rather say so than present the cleaner of the two. On the window, removing governance "
  "gives 0.057 and removing talent gives 0.047, both below the full-network value of 0.064, "
  "while removing innovation gives 0.103 and removing the unassigned population gives 0.138. "
  "The three named domains therefore do not agree in direction between corpora, and the claim "
  "that every removal raises segregation is not made. What does agree, closely, is the "
  "unassigned removal: 0.138 on the window, 0.137 on the full corpus.")
p("That is the paper's most reproducible structural result and it is a negative one for the "
  "vertical model. No named domain is structurally necessary to the others, and the general "
  "population is what holds the field together. Pairwise removals reveal no interaction: on "
  "the window, removing governance with talent gives -0.000, effectively no segregation, while "
  "removing governance with innovation gives 0.124.")
p("The 212 unassigned concepts are worth naming, since they carry the connective work and "
  "are otherwise easy to dismiss as residual noise. The most connected of them are athlete "
  "performance, mental, mental health, historical, integration, gender, accuracy, structural, "
  "committee and collaboration, followed by sectional, strategies, participation, athletic and "
  "olympic. They are general in the way the field itself is general: terms that belong to more "
  "than one domain at once, and terms about the field's subject matter and setting rather than "
  "about its mechanisms. Their mean coreness is the lowest of the four groups at 8.33, which "
  "is what a bridging population should look like if the idea were true, and their mean "
  "corrected participation is no higher than the named domains' at Cohen's d = 0.068. They "
  "hold the field together in aggregate without any of them being individually distinctive, "
  "which is the pattern section 5 describes.")

h("4.3 The participation coefficient measures genericity, and no concept is a bridge", 2)
p("This section reports a null result and the diagnostic that produced it, kept separate from "
  "the previous section because those findings are strong and folding them together would "
  "let them carry a result that is not here.")
p("We identified candidate integrative concepts by taking the top decile of the participation "
  "coefficient. It behaved as expected in one sense: it correlated with weighted betweenness "
  "at rho = 0.478, and because the two share no machinery, one neighbourhood-based and one "
  "path-based, that agreement looked like corroboration. The bridge set also looked "
  "sensible. It matched the eligible population's domain distribution (chi-square = 4.60 on 3 "
  "degrees of freedom, p = .20) and its members spanned more periods and more national "
  "contexts than the concepts they connected.")
p("Then we looked at what the members actually were. They are solutions, concerns, "
  "exploration, correlation, statements, reactions, landscape, beliefs. Participation "
  "correlates with document frequency at rho = +0.549 (p = 2 x 10^-47). The candidate bridges "
  "average 29.1 documents against 15.8 for the eligible set. These are common words that "
  "connect to many things, which is what the measure rewards, and it is not the same thing as "
  "integrating domains.")
p("The correction is already implied by the null we had been computing. If domain labels are "
  "permuted while the graph is held fixed, each concept keeps its own degree and "
  "neighbourhood but loses its real domain affiliation, so the mean participation under "
  "permutation is what a concept of that degree scores by chance. Observed participation "
  "averages 0.589 against a null mean of 0.623. Scoring the difference in standard deviations "
  "removes most of the frequency dependence: the correlation with document frequency falls "
  "from +0.549 to -0.046 (Figure 3).")
p("With 1,000 permutations, 54 concepts exceed z = 1.00 and none exceeds 1.64. The maximum is "
  "1.43, against a two-sided 5 per cent threshold of 1.96. There is no bridge population. The "
  "top decile of the corrected score overlaps the raw participation decile by only 25 of 59, "
  "and the two rankings correlate at 0.64, so the correction is not a re-ranking but a "
  "different and largely empty set.")
p("The distributional result survives the correction. Corrected bridges match the eligible "
  "population's domain distribution (chi-square = 0.60, p = .90) and, inside a narrow "
  "frequency band of 260 concepts, still match (chi-square = 1.28, p = .73). Bridging, such as "
  "it is, is spread across the four groups rather than concentrated in one. The layer "
  "flexibility result does not survive: corrected bridges touch 3.41 of four periods against "
  "3.37 for the rest (p = 0.77) and 3.97 of seven contexts against 4.18 (p = 0.28). Those "
  "earlier gaps were frequency, not structure. The unassigned population as a whole is "
  "marginally more integrative than the named domains, mean corrected score -0.457 against "
  "-0.552, but negligible at Cohen's d = 0.068.")

h("4.4 The field has a technical centre and no administrative spine", 2)
p("Coreness ranges from 1 to 12 across 13 cores. The average profile across domains is flat: "
  "mean coreness is 8.48 for governance, 8.38 for innovation, 8.75 for talent and 8.33 for "
  "the unassigned concepts, a spread of 0.42 on a 1 to 12 scale. If the vertical axis "
  "organised the field, one domain would occupy the high cores throughout, and it does not; "
  "governance, the nominally most foundational domain, has the second-lowest mean of the three "
  "named domains. The structure is also shallow, with 24 concepts in the 12-core and 233 at "
  "coreness 11, more than nine times as many. Neither observation is the complete picture, and "
  "the composition of the top core is the informative part of this result rather than an "
  "aside.")
p("Averages conceal more than they show here, and the composition of the core turns out to "
  "matter (Table 7, Figure 7). The 12-core is 24 concepts and it is not a cross-section of "
  "the field. "
  "Thirteen of the 24 are innovation concepts, 54 per cent of the core against 24 per cent of "
  "all nodes, an enrichment of 2.28. Governance contributes one, enrichment 0.20. The "
  "composition of the deepest core differs significantly from what the node counts predict, "
  "at chi-square = 14.03 on 3 degrees of freedom, p = 0.003, where the 11-core immediately "
  "below shows nothing of the kind (chi-square = 4.81, p = 0.19). Reading down the table makes "
  "the shape plain: innovation enrichment runs 2.28, 0.85, 0.93, 0.81, 1.22, 0.88 and 1.46 "
  "from core 12 to core 6, scatter around the base rate rather than a gradient, so the "
  "concentration is confined to the top. The one provisional entry is core 6, with 26 concepts "
  "and an enrichment of 1.46; nine innovation concepts in a cell of 26 make it the level most "
  "likely to move under a different decomposition.")
p("What sits in that core is worth stating plainly, because it is a specific and slightly "
  "uncomfortable result. The 12-core contains wearable, artificial intelligence, ai, "
  "algorithm, smart, digital, devices, monitoring, analytics, technologies, prediction and "
  "innovation: twelve of its 24 members are technology vocabulary, and they are joined by "
  "injury, physiological, learning, intelligence, making, athlete performance, integration, "
  "strategies, accuracy and implementation. The deepest structural layer of this field is "
  "occupied by the measurement technology, not by governance and not by athlete development. "
  "Read against section 4.5, the same domain is the one the nine-pillar framework has no "
  "vocabulary for. The part of high-performance sport that the literature treats as most "
  "central to its own structure is the part the dominant policy taxonomy does not describe.")
p("The highest-degree concepts in each domain make the same point without the hierarchy. "
  "Governance's are governance, implementation, institutional, global, funding, countries, "
  "olympic committee and sport policy. Talent's are intelligence, injury, youth, youth sport, "
  "psychological, athlete development, talent and talent identification. Innovation's are "
  "wearable, artificial intelligence, ai, technologies, ecosystem, monitoring, smart and "
  "digital. The three are cleanly distinct in vocabulary, which is what one wants of a domain "
  "assignment, and the two that look foundational in policy discourse, governance and talent, "
  "both reach their ceiling on administrative or biological vocabulary rather than on anything "
  "connecting the field to the rest of it.")
p("This also sharpens the contrast with the previous section, and it is why we do not simply "
  "report the flat profile. The 12-core is rare rather than frequent (Figure 7). Its mean "
  "document frequency is 15.8, indistinguishable from the 15.3 of everything below it (Welch "
  "t = 0.12, p = 0.90), with a median of 11. Within the core, document frequency is unrelated "
  "to degree (rho = 0.17, p = 0.43) though across the network the two are strongly related "
  "(rho = 0.59). The concepts in the deepest layer appear in a handful of papers and are "
  "densely connected in those papers. Coreness is therefore doing something different here "
  "from what participation was doing: it is not reading frequency, and what it finds is a "
  "technology core rather than a brokerage elite.")
p("That combination, a concentrated top and a flat body, is a specific architecture. It is not "
  "the pyramid, because the concentrated top is not the domain the vertical model makes "
  "foundational. It is not the flat field either, because the top is significantly "
  "non-random. It is a field with a technical centre and no administrative spine.")
p("The role decomposition assigns 547 concepts to the hub role and 122 to the peripheral role, "
  "with none in the central or least-connected roles. This is the expected outcome for a "
  "single-layer network and carries no substantive weight on its own. Its value is negative "
  "evidence: the method that would detect a differentiated vertical ordering cannot apply "
  "here because the network does not present the layered structure the method assumes. Read "
  "alongside Gallagher, Young, and Foucault Welles's (2021) argument that core-periphery "
  "algorithms extract fundamentally different structures and that a network must be situated "
  "within a typology before interpretation, this network should not be described as "
  "core-periphery in the layered sense.")

h("4.5 Convergent validity against the nine-pillar framework is partial and asymmetric", 2)
p("The three derived domains come from embeddings of abstracts; SPLISS comes from a "
  "forty-year literature review and national benchmarking. They are independent, which is "
  "what makes the comparison a test. Matching published critical success factor vocabulary "
  "against concept labels assigned 117 of 669 concepts, 17.5 per cent, to at least one "
  "pillar, with coverage concentrated where the SPLISS vocabulary is most operational: 30 "
  "concepts in talent identification, 25 in career support, 18 in policy development, 13 in "
  "competition, 12 each in participation and scientific support, 7 in coaching, and 5 each in "
  "finance and facilities.")
p("Convergence is partial and asymmetric. Of 27 domain-by-pillar associations tested, 7 "
  "survive correction at .05 and they are not scattered. Talent concentrates on the pillars "
  "it would be expected to: talent identification at an odds ratio of 9.38 (corrected p = "
  "1.3 x 10^-7), career support at 5.11, and coaching at 24.11. Governance concentrates on "
  "policy development at 7.12 (corrected p = 0.0008), which is an independent confirmation "
  "that the derived governance domain is the governance domain.")
p("Innovation is the informative failure. It is depleted from every SPLISS pillar it could "
  "plausibly have matched, significantly so for talent identification, policy development and "
  "career support, and only 13 of its 159 concepts, 8.2 per cent, match any SPLISS vocabulary "
  "against 33.7 per cent for talent and 13.6 per cent for governance. The derived innovation "
  "domain has no counterpart in the nine-pillar framework (Figure 5). This is not a defect in "
  "either method. SPLISS was built as a taxonomy of levers a government can pull, and digital "
  "technology, performance analytics, wearable monitoring, e-sports and sport "
  "entrepreneurship sit largely outside that space. The gap suggests that policy instruments "
  "for technology and commercialisation in high-performance sport are being formulated "
  "without reference to the field's own understanding of those topics.")

h("4.6 Construction sensitivity, and the one degenerate case", 2)
p("The structural results are re-tested on seven constructions (Figure 6, Table 6). "
  "Segregation replicates on every significance-filtered graph: z = -3.54 at a threshold of "
  "1.0, -4.06 at 2.0, -4.12 at 2.5, -5.84 at 3.0, and -3.97 at a co-occurrence threshold of "
  "5. The count-only construction gives -1.82.")
p("The single null is the unfiltered graph of all co-occurring pairs, at z = 0.02 with a mean "
  "degree of 232, and it is degenerate rather than contradictory. On a near-complete graph "
  "almost every concept connects to almost every other, so observed and null shortest paths "
  "cross boundaries constantly and the statistic has no room to discriminate. It also "
  "disagrees with the count-based sub-corpus results in section 4.3. Segregation is a property "
  "of the significant structure, which is the structure carrying topical meaning.")

h("4.7 Bridge identity is not measurable, for a different reason than expected", 2)
p("Before the correction in section 4.3 we tested whether bridge identity is stable across "
  "periods and national contexts, on the reasonable expectation that a real integrative "
  "population would be detectable. It was not detectable, and the diagnostic for that failure "
  "turned out to matter more than the result.")
p("The first design used four natural year-bounded periods and seven national contexts and "
  "gave a mean correlation of 0.186. That figure is uninterpretable: the periods were wildly "
  "unequal, with 229 of 448 documents in 2022 to 2025, so the pooled network is largely one "
  "block and its correlation was partly circular. Re-specifying the periods as chronological "
  "quartiles of exactly 112 documents each, so no block dominates, raised the mean to 0.356 "
  "with a range of 0.299 to 0.411. The circularity was real and removing it roughly doubled "
  "the correlation.")
p("The decisive test compares nothing across blocks. Splitting each block's documents in "
  "half, building an independent network from each half and correlating the two participation "
  "vectors asks how well the measure replicates when nothing changes at all. The median is "
  "0.100. A cross-block correlation of 0.356 is not far above what the measure achieves on a "
  "single context, so the stability question could not have been answered with this design. "
  "Across the six analysable blocks, the correlation between rho and the logarithm of block "
  "edge count is 0.956 (p = 0.003) and block size explains 91 per cent of the variance "
  "(Figure 4). Every stability number is largely a statement about how many edges a block has.")
p("This matters less now, because section 4.3 shows there is no bridge population to be stable "
  "in the first place. It remains worth reporting for a narrower reason: concept-level network "
  "measures on corpora of this size are not reproducible at the individual-concept level, "
  "which constrains what any future study of this kind should attempt. The national dimension "
  "is in any case largely absent: 55 lead countries appear and only 2 are analysable, so no "
  "national claim is made.")

h("5. A segmented field with a technical centre and diffuse integration")

h("5.1 What the results license", 2)
p("The architecture the data support has four components. Three are segmented domains of "
  "domain-specific knowledge. The fourth is a large general population carrying no domain "
  "label, which is the least internally connected group in the network and the one that holds "
  "the field together. Above the domains sits a fifth element, small and structurally distinct: "
  "a 24-concept core in which measurement technology is over-represented 2.28-fold and "
  "governance is under-represented 5-fold.")
p("The relations follow from the results. Within-domain density is high (coupling 0.950) "
  "and is each domain's primary relation to itself. Between-domain connectivity is real but "
  "not concentrated: aggregate mixing shows the named domains slightly more connected to each "
  "other than to themselves, and the degree-weighted view shows modest but reliable "
  "segregation. Most importantly, there is no relation with a single node through which "
  "connectivity must pass, because no concept plays a distinguishable integrative role.")
p("The centre is technical and the integration is diffuse, and the two findings have to be "
  "held together to be read correctly. Neither alone would be the architecture. A technical "
  "core with concentrated integration would be a hierarchy with technology at the top, and "
  "that is not what the network shows: the technology core is 24 concepts out of 669, it sits "
  "at the shallowest tier of a 13-level hierarchy rather than above a deep one, and the "
  "concepts in it are rare, appearing in a median of 11 documents. It is a centre in the sense "
  "that a few concepts sit structurally deeper than the rest, not in the sense that the field "
  "is organised around them.")
p("The model is specified over three named domains because those are what the corpus "
  "separates, not because three is privileged. The centre is also shallow, at the top of a "
  "13-level hierarchy whose next level holds 233 concepts, and narrow, 24 of 669 nodes. A "
  "centre both shallow and narrow cannot be the axis along which the rest of the field is "
  "arranged, which is what a hierarchy needs.")

h("5.2 What the model predicts", 2)
p("Five predictions follow, each falsifiable.")
p("First, no single domain will be a useful target for intervention aimed at the others. "
  "Improving governance should not be expected to improve talent or innovation through a "
  "structural route, because governance carries no integrative load. Interventions aimed at "
  "shared terminology across domains are more likely to move connectivity than interventions "
  "aimed at a domain.")
p("Second, the general population should be identifiable prospectively. Its members share "
  "measurable properties: no domain label, mid-range coreness, and links spread across "
  "domains. A concept with these properties at the time of network construction should be "
  "more likely to sit between domains subsequently. Section 4.3 makes this a weaker claim "
  "than it would otherwise be, because no individual member is an outlier; the testable form "
  "is at the level of the population, not the individual concept.")
p("Third, the technology core should be where new cross-domain work comes from. The deepest "
  "layer of the field is measurement technology, not administration, and the same domain is "
  "the one the nine-pillar framework cannot describe. If a researcher wants work that "
  "connects domains, the structure says the path is through analytics, wearables and "
  "prediction applied to a substantive question, not through better coordination between "
  "governance and talent. The two findings converge: the domain that is structurally central "
  "is the one the dominant taxonomy leaves out, which is the clearest available evidence "
  "that the taxonomy is not tracking the field.")
p("Fourth, innovation-domain interventions in national sport policy are being designed against "
  "a framework with no vocabulary for them. That is a finding about a gap between policy "
  "instruments and the field's own conceptual vocabulary, and it is directly testable by "
  "asking whether sport-governments' technology and commercialisation strategies use the "
  "terminology the literature uses.")
p("Fifth, and against expectation, the model's most robust feature is its least useful for "
  "practitioners. What travels across periods and countries is the general population as a "
  "whole; which specific concepts connect domains is not measurable at this corpus size and, "
  "on the evidence here, may not be a meaningful question. A field whose integrative "
  "structure is diffuse across a population is harder to act on through any specific concept "
  "than one with identifiable brokers, and that is a real cost of the architecture.")

h("5.3 Limits", 2)
p("Five things this study cannot establish, in the order they should temper the conclusions.")
p("The bridge result is a null, and a null is not a demonstration of absence. We can say that "
  "no concept in this corpus is an integrative outlier on a degree-controlled measure, with a "
  "maximum z of 1.43 over 584 concepts. We cannot say that no integrative concepts exist, only "
  "that if they do they are not distinguishable from generic vocabulary at this sample size "
  "and with this vocabulary.")
p("The national dimension is essentially absent, 55 lead countries and 2 analysable. This is "
  "a property of the corpus rather than the method: sport research is internationally "
  "distributed but not internationally co-indexed under this query.")
p("The load-bearing result is corpus-dependent for the named domains. The unassigned removal "
  "replicates closely; the three named domains do not agree in direction between the two "
  "corpora. Any claim about named domains rests on a single corpus and should be treated as "
  "provisional.")
p("The technology core is a 24-concept result, and small cells cut both ways. It is "
  "statistically distinguishable from the node base rate, but a single reassignment of a "
  "borderline concept moves a domain's share by four points. The audit in section 3.4 found "
  "the word intelligence assigned to talent while artificial intelligence and ai were assigned "
  "to innovation. That error cuts against the finding rather than for it, since correcting it "
  "would move one more concept into the technology core, not out of it. It is a reason to "
  "treat the enrichment ratio as an order of magnitude rather than a precise figure, and a "
  "reason for future work to assign domains from a hand-checked vocabulary.")
p("Finally, this is a model of concepts, not of institutions. Nothing here establishes that "
  "the knowledge structure corresponds to the organisational structure. A distributed "
  "conceptual structure could coexist with a highly centralised institutional one, in which a "
  "single national agency coordinates all three domains. Establishing whether the epistemic and "
  "organisational structures correspond needs different data, and the claim that they are the "
  "same thing should be resisted. This is the limit that should govern how the model is used: "
  "it describes how the field's concepts relate, and is silent on who holds which position.")

h("6. Conclusion")
p("We began with a framework twenty years in use and asked whether its central structural "
  "assumption holds. It does not, in the strong form. The assumption was not that the "
  "ecosystem has parts, which it plainly does, but that some are foundational for others. "
  "Every test for that relation came back against it, and two came back with nothing at all. "
  "What the field has instead can be stated in one line: a small, rare technical centre, a "
  "large general population, and no administrative spine.")
p("The high-performance sport ecosystem is usually modelled as a vertical hierarchy, and the "
  "model has been inherited rather than tested. Tested against a concept network of 448 "
  "documents, it does not survive. The field's three substantive domains are genuinely "
  "segregated, though the segregation is modest and shows up in degree-weighted mixing more "
  "than in aggregate edge weight. No domain is load-bearing; removing any of them changes the "
  "connectivity of the survivors in inconsistent directions between corpora. The integrative "
  "work is done by the concepts that carry no domain label, and removing them more than "
  "doubles the assortativity of what remains, reproducibly across two corpora.")
p("One thing in the field is genuinely concentrated, and it is not where the vertical model "
  "predicts. Thirteen of the 24 concepts in the deepest core are measurement-technology "
  "concepts, and governance contributes one. The core is rare rather than frequent, so unlike "
  "the integrative measure examined below it is not reading word commonness. High-performance "
  "sport research is deepest where it measures, and the nine-pillar framework, which is built "
  "around what a government can do, has no vocabulary for the thing the field is deepest in.")
p("The bridging elite we expected is not there. The standard measure of integrative position "
  "turned out to be substantially a measure of how common a word is, and once degree is "
  "controlled no concept qualifies. What remains is a field in which connectivity is a "
  "property of the population rather than of identifiable positions, which is a different "
  "object from what the ecosystem metaphor usually implies.")
p("The most transferable result here may be the negative one. A widely used concept-analytic "
  "measure produced a confident, well-behaved, entirely artefactual answer, and nothing about "
  "its internal behaviour distinguished it from a real finding. Checking such measures "
  "against degree is not a refinement. It is the minimum required before a claim about "
  "integrative position is worth making.")

h("Figures")
fig("F1_network_architecture.png",
    "Figure 1. Domain-level mixing. Panel (a) shows the share of total edge weight falling "
    "between each ordered pair of domains in the full network. Panel (b) shows the same "
    "quantities with the 212 unassigned concepts removed. The named-domain diagonal sits "
    "slightly below the named-domain off-diagonal in both panels (ratio 0.88), so the domains "
    "are not internally clustered by edge weight; segregation appears in the degree-weighted "
    "assortativity quoted beneath each panel, not in this matrix. Removing the unassigned "
    "population raises assortativity from 0.072 to 0.137 and leaves the diagonal ratio "
    "unchanged.", 6.3)
fig("F7_core_composition.png",
    "Figure 7. Composition of the coreness hierarchy. Panel (a) gives the share of each core "
    "held by each of the four groups, with cores of fewer than 12 concepts omitted. The 12-core "
    "sits far above the innovation base rate and far below the governance one; from core 11 "
    "downward every profile collapses onto its base rate. Panel (b) plots document frequency "
    "against weighted degree on a log frequency axis, with the general trend fitted on the "
    "non-core nodes. The 12-core occupies the one region the trend does not reach: low "
    "frequency, high degree. Panel (c) plots the cumulative distribution of document frequency "
    "for the core and for the rest; the two curves lie on top of each other, with means of "
    "15.8 and 15.3 documents (Welch p = 0.90). Frequency within the core is unrelated to "
    "degree (rho = 0.17) although across the network the two are strongly related "
    "(rho = 0.59).", 6.4)
fig("F2_load_bearing.png",
    "Figure 2. Load-bearing test. Panel (a) shows assortativity for the domain attribute "
    "after each single and pairwise domain removal, on the full corpus (604 documents, solid "
    "bars) and the analysis window (448 documents, hatched). The three named domains disagree "
    "between corpora in direction; the unassigned population does not, giving 0.137 and 0.138 "
    "respectively. Panel (b) shows the share of edges falling within a domain against the "
    "0.260 expected from the degree distribution.", 6.3)
fig("F3_bridges.png",
    "Figure 3. The bridge analysis and its correction. Panel (a) plots participation against "
    "document frequency: the two are strongly related (rho = 0.55), and the concepts selected "
    "as bridges on the raw score sit at the participation ceiling across the frequency range. "
    "Panel (b) plots the null-centred score against the same frequency axis. The frequency "
    "dependence has gone, and no concept reaches the 1.96 threshold; the maximum is 1.43.", 6.3)
fig("F4_stability_power.png",
    "Figure 4. Bridge stability and its power confound. Panel (a) plots block-level "
    "correlation with pooled participation against the logarithm of block edge count, with "
    "the fitted line (r = 0.956, R-squared = 0.913) and the split-half reliability of the "
    "measure (0.100) marked. Panel (b) shows the same correlations by block against that "
    "reliability floor. Correlation is a function of block size rather than of context.", 6.3)
fig("F5_spliss_validity.png",
    "Figure 5. Convergent validity against the nine-pillar framework. Panel (a) gives the "
    "odds ratio for each derived-domain by SPLISS-pillar pair that survives "
    "Benjamini-Hochberg correction at .05; the innovation row is empty because innovation is "
    "depleted from every pillar rather than enriched in one. Panel (b) shows the same "
    "associations as negative log corrected p.", 6.3)
fig("F6_construction_sensitivity.png",
    "Figure 6. Construction sensitivity. Panel (a) shows the boundary-crossing z across seven "
    "network constructions; orange bars are not significant. Panel (b) plots the same z "
    "against mean degree on a log scale, showing that the single null is the near-complete "
    "graph at mean degree 232, where the statistic cannot discriminate.", 6.3)

h("Tables")

table("Table 1. Corpus and network construction.",
      ["Parameter", "Value"],
      [["Scopus query date", "30 September 2026"],
       ["Raw records", "623"],
       ["Excluded: retracted / note / editorial / erratum", "3 / 7 / 2 / 1"],
       ["Excluded: missing or degenerate title or abstract", "6"],
       ["Analytic corpus", "604"],
       ["Analysis window", "2013 to 2025, 448 documents"],
       ["Extracted concepts before consolidation", "1,208"],
       ["Concept families after consolidation", "1,041"],
       ["Semantic consolidation threshold (cosine)", "0.7293"],
       ["Merges at threshold", "167"],
       ["Hand-audited merges / judged correct", "70 / 67"],
       ["Audited merge precision", "0.957"],
       ["Node frequency window", "at least 8 documents, at most 30% of corpus"],
       ["Edge rule", "co-occurrence at least 3 and bipartite-null z at least 2.5"],
       ["Network nodes", "669"],
       ["Network edges, full corpus / window", "5,061 / 3,317"],
       ["Graph density, full corpus / window", "0.023 / 0.015"],
       ["Domain assignment confidence floor", "0.02"],
       ["Mean within-domain coupling", "0.950"]],
      [3.4, 3.0],
      "Corpus and construction parameters. Every value is written by a script in "
      "article2/scripts and listed in Appendix A.")

table("Table 2. Domain composition and hierarchy measures.",
      ["Quantity", "Governance", "Innovation", "Talent", "Unassigned"],
      [["Concepts", "140", "159", "158", "212"],
       ["Share of network nodes", "20.9%", "23.8%", "23.6%", "31.7%"],
       ["Mean coreness", "8.48", "8.38", "8.75", "8.33"],
       ["Assortativity of domain attribute", "0.072 (z = 8.88)"],
       ["Assortativity, full corpus", "0.0723"],
       ["Assortativity, analysis window", "0.0640"],
       ["Mean within-domain edge share, full corpus", "0.310"],
       ["Mean within-domain edge share, window", "0.306"],
       ["Expected within-domain share from degree", "0.260"],
       ["Named-domain diagonal / off-diagonal, edge weight", "0.88"],
       ["Unassigned within-block share", "0.063"],
       ["Unassigned share to each named domain", "0.075 to 0.084"],
       ["Coreness range across network", "1 to 12, 13 cores"],
       ["Concepts in 12-core / 11-core", "24 / 233"],
       ["Concepts in hub / peripheral role", "547 / 122"],
       ["Concepts in central / least-connected role", "0 / 0"]],
      [3.0, 1.2, 1.2, 1.2, 1.2],
      "Domain composition, hierarchy depth and mixing. The last three rows are network-level "
      "and are not domain-specific.")

table("Table 3. Load-bearing test on both corpora.",
      ["Removed", "Nodes", "Edges", "Full corpus r", "Window r", "Window z"],
      [["None (full network)", "669", "5,061", "0.0723", "0.0640", "+6.92"],
       ["Governance", "529", "2,057", "0.0773", "0.0574", "+3.74"],
       ["Innovation", "510", "2,155", "0.1061", "0.1031", "+6.88"],
       ["Talent", "511", "1,904", "0.0669", "0.0472", "+2.96"],
       ["Unassigned", "457", "1,534", "0.1367", "0.1380", "+7.99"],
       ["Governance and innovation", "370", "1,150", "0.1261", "0.1244", "+4.59"],
       ["Governance and talent", "371", "936", "0.0619", "-0.0003", "+0.25"],
       ["Innovation and talent", "352", "1,068", "0.1000", "0.0829", "+3.06"]],
      [2.0, 0.9, 0.9, 1.3, 1.1, 1.0],
      "Assortativity for the domain attribute after each removal. The named domains "
      "disagree in direction between corpora; the unassigned population agrees closely, which "
      "is why the claim that every removal raises segregation is not made.")

table("Table 4. Bridge identification before and after the degree correction.",
      ["Statistic", "Raw participation", "Null-centred score"],
      [["Concepts eligible", "584", "584"],
       ["Correlation with document frequency (rho)", "+0.549", "-0.046"],
       ["Mean score", "0.589", "-0.531"],
       ["Mean score under label-permutation null", "not computed", "0.623"],
       ["Concepts exceeding z = 1.00", "not applicable", "54"],
       ["Concepts exceeding z = 1.64", "not applicable", "0"],
       ["Concepts exceeding z = 1.96", "not applicable", "0"],
       ["Maximum score", "0.750 (ceiling)", "1.43"],
       ["Concepts in selected set", "45", "59"],
       ["Mean document frequency of set", "29.1", "14.2"],
       ["Mean document frequency of remainder", "15.8", "17.1"],
       ["Domain distribution chi-square (df 3)", "4.60, p = 0.20", "0.60, p = 0.90"],
       ["Domain distribution inside frequency band", "not computed", "1.28, p = 0.73"],
       ["Mean periods touched, set vs remainder", "3.82 vs 3.34, p < 0.001",
        "3.41 vs 3.37, p = 0.77"],
       ["Mean contexts touched, set vs remainder", "5.33 vs 4.06, p < 0.001",
        "3.97 vs 4.18, p = 0.28"],
       ["Overlap of the two selected sets", "25 of 59 (42%)"],
       ["Spearman correlation of the two scores", "0.64"],
       ["Unassigned minus named, Cohen's d", "0.068"]],
      [2.6, 2.0, 1.9],
      "The raw measure and the degree-controlled measure. The frequency dependence and the "
      "layer-flexibility gap appear only in the raw column.")

table("Table 5. Convergent validity against the SPLISS nine-pillar framework.",
      ["Association", "Observed", "Expected", "Odds ratio", "Corrected p"],
      [["Talent x talent identification", "21", "9.0", "9.38", "1.3e-07"],
       ["Talent x career support", "14", "11.0", "5.11", "0.00053"],
       ["Governance x policy development", "12", "6.0", "7.12", "0.00077"],
       ["Talent x coaching", "6", "1.0", "24.11", "0.0013"],
       ["Innovation x talent identification (depleted)", "1", "29.0", "0.10", "0.019"],
       ["Innovation x policy development (depleted)", "0", "18.0", "0.00", "0.026"],
       ["Innovation x career support (depleted)", "1", "24.0", "0.12", "0.026"]],
      [2.9, 1.0, 1.1, 1.0, 1.2],
      "Seven of 27 tested associations survive Benjamini-Hochberg correction at .05. Match "
      "rates are 33.7% for talent, 13.6% for governance and 8.2% for innovation, from 117 of "
      "669 concepts matched overall.")

table("Table 6. Construction sensitivity of the segregation result.",
      ["Construction", "Edges", "Mean degree", "Observed", "Null", "z"],
      [["Unfiltered, all co-occurring pairs", "77,555", "231.9", "0.8703", "0.8700",
        "+0.02"],
       ["Count at least 3 only", "12,179", "36.4", "0.9181", "0.9353", "-1.82"],
       ["Count at least 3, null z at least 1.0", "7,972", "23.8", "0.9281", "0.9464",
        "-3.54"],
       ["Count at least 3, null z at least 2.0", "4,518", "13.5", "0.9500", "0.9642",
        "-4.06"],
       ["Count at least 3, null z at least 2.5 (main)", "3,219", "9.6", "0.9623", "0.9736",
        "-4.12"],
       ["Count at least 3, null z at least 3.0", "2,222", "6.6", "0.9697", "0.9828",
        "-5.84"],
       ["Count at least 5, null z at least 2.5", "1,049", "3.1", "0.9692", "0.9823",
        "-3.97"]],
      [2.7, 1.0, 1.1, 1.0, 1.0, 0.8],
      "Segregation replicates on all five significance-filtered constructions. The unfiltered "
      "graph is degenerate at mean degree 232.")

table("Table 7. Composition of the coreness hierarchy, by domain.",
      ["Core", "n", "Governance", "Innovation", "Talent", "Unassigned",
       "Innovation enrichment"],
      [["12", "24", "1 (4%)", "13 (54%)", "5 (21%)", "5 (21%)", "2.28"],
       ["11", "233", "47 (20%)", "47 (20%)", "65 (28%)", "74 (32%)", "0.85"],
       ["10", "95", "23 (24%)", "21 (22%)", "21 (22%)", "30 (32%)", "0.93"],
       ["9", "62", "15 (24%)", "12 (19%)", "15 (24%)", "20 (32%)", "0.81"],
       ["8", "45", "9 (20%)", "13 (29%)", "9 (20%)", "14 (31%)", "1.22"],
       ["7", "43", "12 (28%)", "9 (21%)", "10 (23%)", "12 (28%)", "0.88"],
       ["6", "26", "6 (23%)", "9 (35%)", "5 (19%)", "6 (23%)", "1.46"],
       ["5", "42", "10 (24%)", "10 (24%)", "6 (14%)", "16 (38%)", "1.00"],
       ["4", "30", "6 (20%)", "9 (30%)", "4 (13%)", "11 (37%)", "1.26"],
       ["3", "35", "6 (17%)", "7 (20%)", "10 (29%)", "12 (34%)", "0.84"],
       ["All nodes", "669", "140 (21%)", "159 (24%)", "158 (24%)", "212 (32%)", "1.00"]],
      [0.8, 0.6, 1.05, 1.05, 0.95, 1.1, 1.15],
      "Enrichment is the core's share of a domain divided by that domain's share of all nodes, "
      "so 1.00 is the base rate. The 12-core is the only level whose departure from the base "
      "rate is statistically distinguishable (chi-square = 14.03, df = 3, p = 0.003); core 11 "
      "shows none (chi-square = 4.81, p = 0.19), and the single-concept cores below are not "
      "tested. Governance enrichment in the 12-core is 0.20.")

h("Appendix A. Analysis scripts, reproducibility and the Scopus query")
p("Every statistic in this paper is produced by a script, run in order by run_all.py. "
  "a0_matrices.py builds the windowed matrix and the period and national blocks. "
  "a0b_sensitivity.py re-tests segregation across seven constructions. a1_hierarchy.py "
  "produces the coreness hierarchy and the role decomposition. a2_bridges.py produces the raw "
  "participation analysis. a2b_stability.py produces the size-matched block analysis, the "
  "split-half reliability and the power diagnostic. a3_spliss_validity.py produces the "
  "convergent validity analysis. a8_bridges_corrected.py computes the null-centred bridge "
  "measure with 1,000 permutations. a9_load_bearing_window.py recomputes the load-bearing test "
  "on the analysis window. a7_genericity_diagnostic.py tests the frequency confound. "
  "a10_core_composition.py tests whether the deepest core is a cross-section of the field, "
  "profiles its frequency distribution, and audits the domain assignment for same-referent "
  "conflicts. a6_figures.py and a11_figure7.py render the seven figures. Each writes a named "
  "CSV, and every table in this manuscript is a direct rendering of one of those files.")
p("The analysis code, all seven result tables, all seven figures and this manuscript are "
  "available at https://github.com/mahsatorabi/high-performance-sport-ecosystem-architecture, "
  "together with a verifier that checks every statistic quoted in the prose against the "
  "released tables, resolves every citation, and confirms that the word count agrees with the "
  "builder under a single stated rule. This is a second-order analysis and reads three inputs "
  "from a companion paper mapping the same corpus, "
  "https://github.com/mahsatorabi/high-performance-sport-concept-network, withheld here for "
  "the same licence reason as the matrices derived from them.")
p("The Scopus query was (\"sport ecosystem\" OR \"sport system\" OR \"sport network\" OR "
  "\"sport value chain\" OR \"innovation ecosystem\" OR \"entrepreneurial ecosystem\") AND "
  "(\"elite sport\" OR \"high performance sport\" OR \"professional sport\" OR \"athlete*\"), "
  "executed on 30 September 2026, returning 623 records. Scopus licensing does not permit "
  "redistribution of the source records, so the derived matrices and graphs are not released; "
  "the scripts that produce them are.")

h("Appendix B. Method choices that a reader might query")
p("Four. The load-bearing metric is assortativity rather than a boundary-crossing ratio, "
  "because the crossing null shifts with the number of groups and its z is not comparable "
  "across the three-group and four-group partitions this test requires. Sub-corpora analyses "
  "use a co-occurrence threshold without the bipartite significance filter, because a 40-draw "
  "null cannot place a per-edge threshold on 28 to 229 documents; under the filter the "
  "early-period blocks collapse to mean degree 0.5, too sparse for a participation coefficient "
  "to rank. Stability blocks are chronological quartiles of 112 documents rather than natural "
  "year-bounded periods, because the natural periods were unequal in size and the pooled "
  "network was largely one of them. And the participation coefficient is reported both raw and "
  "null-centred, because the two disagree about whether any bridge population exists and the "
  "disagreement is the substantive result.")

h("Appendix C. Known limitations of the measures")
p("Four. Domain labels come from embedding-space prototypes, and an audit of ten same-referent "
  "pairs found four split across domains, all involving the word intelligence, which is in "
  "talent while artificial intelligence and ai are in innovation. This limits the "
  "technology-core result and is reported rather than fixed, because correcting it would "
  "require rebuilding the whole assignment and the direction of the error is known: it dilutes "
  "the innovation core rather than creating it. The role decomposition populates only two of "
  "four roles in a single-layer network, so it gives no evidence about vertical role ordering "
  "and is reported as a negative result about method applicability. A weight-based "
  "assortativity variant was attempted and abandoned: for a scalar-weighted undirected graph "
  "the mixing matrix is symmetric, so permuting labels permutes only its rows and columns and "
  "the null collapses to a point, giving a null z of nan. The unweighted mixing matrix is "
  "asymmetric because each edge is counted once, which is what makes it sensitive to the label "
  "assignment. Finally, the participation coefficient saturates at 0.750 for a four-group "
  "partition and its top decile clusters between 0.735 and 0.750, so ranking within the decile "
  "is partly ranking noise, a further reason to prefer the null-centred score.")

h("Appendix D. Reproducibility notes a reviewer is likely to raise")
p("Three. Seeds are fixed but the permutation tests still carry Monte Carlo error: with 1,000 "
  "draws the reported null mean of 0.623 and observed mean of 0.589 should be read to two "
  "decimal places and no further. The maximum z of 1.43 is a maximum over 584 concepts and is "
  "biased upward by selection, which is the conservative direction for a null result: any "
  "correction for that selection would lower it further. Since core 11 holds 233 concepts, a "
  "re-run under a different core implementation could move the 12-core boundary by a concept "
  "or two; the enrichment finding survives that, because the nearest technology concepts sit "
  "at coreness 11 carrying the same domain labels.")

h("Declarations")
p("Funding")
p("The authors declare that no funds, grants, or other support were received during the "
  "preparation of this manuscript.")
p("Conflict of interest")
p("The authors declare no potential conflicts of interest.")
p("Ethics approval")
p("This study analysed bibliographic metadata only. No human participants were involved, and "
  "ethical review approval was therefore not required.")
p("Data availability")
p("All analysis code, derived data, figures and this manuscript are openly available at "
  "https://github.com/mahsatorabi/high-performance-sport-ecosystem-architecture. The "
  "repository contains the analysis pipeline (run_all.py), the frozen Python environment "
  "(requirements.txt), all seven result tables, all seven figures, the tables underlying "
  "every statistic quoted in the text, and the manuscript verifier, which checks that no "
  "cited statistic is free-floating and that the word count and citation graph are internally "
  "consistent.")
p("The bibliographic records themselves are not redistributed. They were retrieved from "
  "Scopus under the single structured query recorded in Appendix A on 30 September 2026, which "
  "returned 623 records; Scopus licensing does not permit redistribution of the raw export. "
  "The query and retrieval date are sufficient to reproduce the corpus for users with "
  "institutional Scopus access. No record text (titles, abstracts, author keywords or "
  "affiliations) appears in the repository, and the document-by-concept matrices and concept "
  "embeddings derived from that text are withheld for the same reason. The scripts that "
  "produce them are included.")
p("Author contributions (CRediT)")
p("All authors contributed equally to this work and are accountable for the content of the "
  "article. All authors jointly conceived the study, designed the analytical framework, "
  "conducted the analysis, and drafted and revised the manuscript. No single author held "
  "exclusive responsibility for any section or any stage of the research.")
p("Acknowledgements")
p("The authors gratefully acknowledge the assistance of Grammarly and OpenAI GPT-5, used "
  "for language editing and to improve grammatical clarity and comprehension of the "
  "manuscript. The study design, data analysis, interpretation of results, and the substantive "
  "claims are the work of the authors, who take full responsibility for the content of the "
  "article.")

h("References")

for r in [
    "Bakanauskas, P., & Pileliene, L. (2024). Applying management theories to the entities "
    "of sports ecosystem. Management of Organizations: Systematic Research, 92(1), 17-32.",
    "Batagelj, V., & Zaversnik, M. (2003). An O(m) algorithm for cores decomposition of "
    "networks. arXiv:cs/0310049.",
    "Bayle, E. (2023). A model for the multi-centered regulation of world sport. "
    "International Journal of Sport Policy and Politics, 15(2), 309-327.",
    "Bergsgard, N. A., Houlihan, B., Mangset, P., Nodland, S. I., & Rommetveldt, H. (2007). "
    "Sport policy: A comparative analysis of stability and change. Elsevier.",
    "Canini, D., Tjonndal, A., & Vicentini, F. (2026). Open innovation ecosystems: A scoping "
    "review and conceptual model for sport management. Managing Sport and Leisure.",
    "Danon, L., Diez-Guillera, A., Duch, J., & Arenas, A. (2005). Comparing community "
    "structure identification methods. Journal of Statistical Mechanics, 2005(09), P09008.",
    "De Bosscher, V., De Knop, P., Van Bottenburg, M., & Shibli, S. (2006). A conceptual "
    "framework for analysing Sports Policy Factors Leading to International Sporting "
    "Success. European Sport Management Quarterly, 6(2), 185-215.",
    "De Bosscher, V., De Knop, P., van Bottenburg, M., Shibli, S., & Bingham, J. (2009). "
    "Explaining international sporting success: An international comparison of elite sport "
    "systems and policies in six countries. Sport Management Review, 12(3), 113-136.",
    "De Bosscher, V., Shibli, S., Westerbeek, H., & van Bottenburg, M. (2015). Successful "
    "elite sport policies: An international comparison of the Sports Policy factors Leading "
    "to International Sporting Success (SPLISS 2.0) in 15 nations. Meyer & Meyer.",
    "De Bosscher, V., Shibli, S., & van Bottenburg, M. (2026). Evaluating successful elite "
    "sport policies: The SPLISS model. In P. Sotiriadou & V. De Bosscher (Eds.), Managing "
    "high performance sport (2nd ed., pp. 38-71). Routledge.",
    "De Bosscher, V., Sotiriadou, P., & van Bottenburg, M. (2013). Scrutinizing the sport "
    "pyramid metaphor: An examination of the relationship between elite success and mass "
    "participation in Flanders. International Journal of Sport Policy and Politics, 5(3), "
    "319-339.",
    "Descheemaeker, K., Shibli, S., Weissensteiner, J. R., & De Bosscher, V. (2025). Youth "
    "sport and talent development policies: An umbrella review of the foundation and talent "
    "phases for future high performance. Journal of Sports Sciences.",
    "Fortunato, S., & Barthelemy, M. (2007). Resolution limit in community detection. "
    "Proceedings of the National Academy of Sciences, 104(1), 36-41.",
    "Gallagher, R. J., Young, J.-G., & Foucault Welles, B. (2021). A clarified typology of "
    "core-periphery structure in networks. Science Advances, 7(12), eabc9800.",
    "Guimera, R., & Nunes Amaral, L. A. (2005a). Cartography of complex networks: Modules and "
    "universal roles. Journal of Statistical Mechanics: Theory and Experiment, 2005(02), "
    "P02001.",
    "Guimera, R., & Nunes Amaral, L. A. (2005b). Functional cartography of complex metabolic "
    "networks. Nature, 433(7027), 895-900.",
    "Houlihan, B., & Green, B. C. (2008). Comparative elite sport development: Systems, "
    "structures and public policy. Elsevier.",
    "Lancichinetti, A., & Fortunato, S. (2008). Benchmark graphs for testing community "
    "detection algorithms. Physical Review E, 78(4), 046110.",
    "Larose, J., & Haggerty, R. (1996). A future for elite Canadian sport. Journal of "
    "Physical Education, Recreation and Dance, 67(3), 16-21.",
    "Morgan, S. (2024). The hitchhiker's guide to the sport ecosystem: Development of a new "
    "theoretical framework and organisational model. Doctoral thesis, Loughborough "
    "University.",
    "Newman, M. E. J. (2003). Mixing patterns in networks. Physical Review E, 67(2), "
    "026126.",
    "Oakley, B., & Green, B. C. (2001). The global sporting arms race. Sport in Society, "
    "4(3), 318-343.",
    "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using siamese "
    "BERT-networks. Proceedings of EMNLP-IJCNLP (pp. 3982-3992).",
    "Sotiriadou, K. P., & De Bosscher, V. (2013). Managing high performance sport. Routledge.",
    "Sotiriadou, P., Brouwers, J., & De Bosscher, V. (2017). Managing high-performance sport: "
    "Introduction to past, present and future considerations. European Sport Management "
    "Quarterly, 27(1), 1-20.",
    "Yang, Y., Han, R., Wolfram, D., & Zhao, Y. (2016). Visualizing the intellectual "
    "structure of information science (2006-2015): Introducing author keyword coupling "
    "analysis. Journal of Informetrics, 10(1), 150-160.",
]:
    ref(r)


# ================================================================== build
def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def add_table(doc, caption, header, rows, widths, note):
    cap = doc.add_paragraph()
    r = cap.add_run(caption)
    r.bold = True
    r.font.size = Pt(9)
    cap.paragraph_format.space_before = Pt(12)
    cap.paragraph_format.space_after = Pt(3)

    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, txt in enumerate(header):
        hdr[i].text = ""
        para = hdr[i].paragraphs[0]
        run = para.add_run(txt)
        run.bold = True
        run.font.size = Pt(8)
        para.paragraph_format.space_after = Pt(1)
        shade(hdr[i], "DCE6F1")
    for row in rows:
        cells = t.add_row().cells
        for i, txt in enumerate(row):
            cells[i].text = ""
            para = cells[i].paragraphs[0]
            run = para.add_run(str(txt))
            run.font.size = Pt(8)
            para.paragraph_format.space_after = Pt(1)
    if widths:
        for r_ in t.rows:
            for i, w in enumerate(widths):
                if i < len(r_.cells):
                    r_.cells[i].width = Inches(w)
    if note:
        np_ = doc.add_paragraph()
        nr = np_.add_run(note)
        nr.font.size = Pt(7.5)
        nr.italic = True
        nr.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        np_.paragraph_format.space_before = Pt(3)
    return t


def build():
    doc = Document()
    n = doc.styles["Normal"]
    n.font.name = "Calibri"
    n.font.size = Pt(10.5)
    n.paragraph_format.space_after = Pt(7)
    n.paragraph_format.line_spacing = 1.12
    for s in doc.sections:
        s.left_margin = s.right_margin = Inches(1.0)
        s.top_margin = s.bottom_margin = Inches(1.0)

    for kind, payload in BLOCKS:
        if kind == "h":
            title, level = payload
            doc.add_heading(title, level=level)
        elif kind == "p":
            doc.add_paragraph(payload)
        elif kind == "r":
            para = doc.add_paragraph()
            run = para.add_run(payload)
            run.font.size = Pt(9)
            para.paragraph_format.left_indent = Inches(0.3)
            para.paragraph_format.space_after = Pt(1)
        elif kind == "fig":
            fname, caption, width = payload
            path = os.path.join(FIG, fname)
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.space_before = Pt(12)
            para.add_run().add_picture(path, width=Inches(width))
            cpara = doc.add_paragraph()
            crun = cpara.add_run(caption)
            crun.font.size = Pt(8.5)
            crun.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            cpara.paragraph_format.space_before = Pt(3)
            cpara.paragraph_format.space_after = Pt(10)
        elif kind == "tab":
            add_table(doc, *payload)
    doc.save(OUT)
    return doc


def count_words():
    """Article 1's rule, which this builder holds itself to.

    Countable: body paragraphs, table header and body cells, appendix prose.
    Excluded: headings, the title, the reference list, declarations, figure captions,
    table captions and table notes. Declarations sit outside the count on the same
    ground as the reference list: they are submission furniture, not argument, and
    Article 1 counted its declaration block after the 9,000 total was fixed. Captions
    and notes are apparatus describing a table rather than content of the paper.
    Article 1's split was "main 8,185 + tables 818 = 9,000", where 818 was cell text
    alone.
    """
    n = 0
    in_declarations = False
    for kind, payload in BLOCKS:
        if kind == "h":
            if payload[0] == "Declarations":
                in_declarations = True
            elif payload[0] == "References":
                in_declarations = False
            continue
        if in_declarations:
            continue
        if kind == "p":
            n += len(payload.split())
        elif kind == "tab":
            _, header, rows, _, _ = payload
            for c in header:
                n += len(str(c).split())
            for row in rows:
                for c in row:
                    n += len(str(c).split())
    return n


if __name__ == "__main__":
    d = build()
    w = count_words()
    print("wrote %s" % OUT)
    print("paragraphs %d | tables %d | images %d"
          % (len(d.paragraphs), len(d.tables),
             len(d.inline_shapes)))
    print("countable words: %d | target 9000 | delta %+d" % (w, w - 9000))
