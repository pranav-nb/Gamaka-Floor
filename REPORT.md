# Gamaka Floor — Raga Pitch-Contour Study: Summary Report

*A plain-language summary. For the full technical write-up with every figure,
table, and source citation, see `notebooks/05_report.ipynb`.*

## 1. Problem Statement

In Carnatic (South Indian classical) music, a *raga* is not just a scale — the
same seven or eight notes, sung two different ways, can belong to two
different ragas. The difference often lives in **gamaka**: the slides, bends,
oscillations, and ornaments a singer applies around each note, not the note
itself.

This project asks one question: **if you strip away that fine pitch detail
and keep only the note names, how much of "which raga is this" survives?**

We test this by taking a raga classifier and deliberately blurring its input —
from very fine pitch measurement down to the coarsest possible resolution (12
notes per octave, like a piano). If accuracy holds up even after blurring,
raga identity mostly lives in the note choices. If accuracy collapses, raga
identity lives substantially in the fine pitch movement — the gamaka — which
would mean it can't be captured by note-level analysis alone.

Two smaller questions sit on top of this main one: (a) can two ragas that
share almost the same notes but differ in ornamentation be told apart, and
(b) can a small AI model learn to generate a plausible pitch contour for a
given raga.

## 2. Data Used

- **Dataset:** [Saraga Carnatic Music Dataset 1.5](https://zenodo.org/record/4301737)
  — a public research dataset of Carnatic vocal recordings with hand-verified
  annotations (raga name, artist, song sections, pitch track). Licensed
  **CC BY-NC-SA 4.0** (non-commercial, attribution required, share-alike).
- **Only the text annotations were used, not the audio itself** — for each
  recording, a pre-extracted pitch curve (how the fundamental frequency moves
  over time), the singer's identity, the raga label, and time-stamped section
  boundaries (e.g. which part is unaccompanied improvisation vs. a set
  composition).
- **Scale:** 249 recordings, 184 of them raga-labelled, spanning 96 distinct
  ragas. From this, several working subsets were built depending on what each
  experiment needed:
  - A small **4-raga, unaccompanied-improvisation-only** set, for the
    cleanest possible test.
  - A **12-raga "primary" pool** and a **40-raga "secondary" pool** covering
    all song sections, for the main classification experiment.
  - **2 ragas** (Karaharapriya and Mōhanaṁ) for the generative model, chosen
    because they were the only ones with genuinely balanced singer
    representation (see the confound note below).

**An important catch, handled throughout the project:** many ragas in the
dataset are mostly sung by a *single* artist. If a classifier is trained and
tested on the same singer, it may just be learning to recognise that person's
voice, not the raga. Every experiment below either spreads recordings across
multiple singers in a controlled way (splitting so a singer never appears in
both the training and the testing data) or explicitly says where that wasn't
possible.

## 3. Method

**Step 1 — Corpus build.** Pitch curves were cleaned (removing octave-jump
tracking errors) and converted to a musically standard unit called *cents*,
measured relative to each singer's own home pitch (tonic), so contours from
different singers/keys are directly comparable. Two versions were kept: a
*folded* version (octave collapsed away, good for "which note is this")
and an *unfolded* version (octave preserved, good for reproducing melodic
shape).

**Step 2 — Quantisation study (the core experiment).** The folded pitch was
cut into short windows and turned into a histogram — basically "how much time
was spent near each pitch" — at four levels of coarseness: very fine (10
cents), 20 cents, 50 cents, and a full semitone (100 cents, i.e. a standard
piano note). A raga classifier (logistic regression) was trained and tested
at each coarseness level. If raga identity survived coarsening, accuracy
should stay flat; if it depends on fine pitch movement, accuracy should drop
as the resolution gets coarser.

**Step 3 — Allied-raga search.** Searched the full dataset for a pair of
ragas that share almost the same notes but are considered musically distinct
by ornamentation, *and* that both have balanced multi-singer coverage (to
rule out the "just recognising the voice" problem). No such pair was found —
every musically plausible candidate failed the singer-balance check on at
least one side.

**Step 4 — Small generative model.** A compact AI model (about 57,000
parameters — very small by modern standards) was trained to generate new
pitch contours, conditioned on which of the two balanced ragas it should
sound like. Because the environment used has no GPU, a lightweight
"next-step prediction" model was used instead of a heavier diffusion-style
model, which trains much faster and more reliably in this setting.

**Step 5 — Checking the generated samples.** Three checks: (a) does the
generated pitch distribution statistically resemble the real raga it was
supposed to sound like, (b) does an automatic raga classifier correctly guess
which raga a generated sample belongs to, and (c) is the model just copying
training examples rather than generating something new (checked by measuring
how close each generated sample is to its nearest real example).

## 4. Results

### 4.1 Does raga identity survive coarsening? (the main result)

| Test set | Fine pitch | Coarser | Coarser | Semitone (piano-note) | Random-guess baseline |
|---|---|---|---|---|---|
| 4 ragas, unaccompanied singing | 58.2% | 59.0% | 56.5% | **51.6%** | 25% |
| 12 ragas, all song sections | 38.3% | 39.1% | 40.2% | **30.9%** | 8.3% |
| 40 ragas, all song sections | 13.0% | 13.8% | 14.7% | **11.8%** | 2.5% |

*(Accuracy shown is "balanced accuracy" — corrected for how often each raga
appears — averaged across repeated train/test splits.)*

**The pattern is consistent across every version of this test:** accuracy
stays roughly flat, or even ticks up slightly, as pitch is coarsened from
very fine down to a moderately coarse level — and then drops clearly at the
final step, when pitch is forced onto the same 12 notes a piano uses. In
other words, most of what a classifier needs is already present well before
full precision, but that **last stretch of precision — the difference
between "which of 12 notes" and true continuous pitch — matters measurably**.

Looking at individual ragas, most (9 of 12 in the main pool) lose classifier
recall when coarsened to piano-note resolution — some quite sharply (the
largest single-raga drop was about 17 percentage points). A few ragas barely
change, and one raga (Sāvēri) unexpectedly got *easier* to classify at coarse
resolution — flagged as an open, unexplained result rather than glossed over.

### 4.2 Allied-raga pair

No usable pair was found — dropped as planned, with the reasoning documented.
The per-raga breakdown above (4.1) stands in as a broader version of the same
idea, run across many ragas instead of one hand-picked pair.

### 4.3 Generative model

- The model trained successfully (its prediction error dropped steadily and
  never became unstable), and it could generate new pitch contours on
  request for either raga.
- **Mixed but honest result:** generated samples for one raga
  (**Karaharapriya**) reliably came out sounding statistically like that
  raga, by three independent measures. Samples for the other raga
  (**Mōhanaṁ**) did not show the same clear signal — a plausible reason is
  discussed in §5 below.
- **No evidence of the model simply copying its training data** — generated
  samples were about as "far" from the nearest real example as real examples
  are from each other.

## 5. Inference — What This Means

*(Interpretation grounded in documented Carnatic music theory, since this
project was carried out without a Carnatic music background — every claim
below is sourced, not personal musical judgement; see `05_report.ipynb` for
full citations.)*

- **The core hypothesis holds, with a specific shape.** Raga identity does
  not need extremely fine pitch measurement to be classified — moderate
  resolution works almost as well as very fine resolution. But identity
  clearly does **not** reduce to "which 12 notes were used": forcing pitch
  onto a semitone grid measurably hurts classification, meaning a real part
  of what makes a raga recognisable lives in pitch movement finer than a
  single note.
- **Some of the per-raga pattern matches documented theory, some doesn't.**
  Ragas described in Carnatic music scholarship as heavily
  ornamentation-dependent (e.g. Mōhanaṁ, Sindhubhairavi) tend to show larger
  accuracy drops when coarsened, matching the theory. One raga
  (Harikāmbhōji), documented as a comparatively "plain" reference scale,
  shows almost no drop — also consistent. But **Sāvēri is a documented
  counterexample**: theory places it in the same "every note needs gamaka"
  category as Mōhanaṁ, yet it empirically got *easier* to classify at coarse
  resolution. No source found explains this, and it's presented here as an
  open disagreement, not resolved.
- **The allied-pair question turned out to be a data-availability problem,
  not a musical one.** Every musically plausible candidate pair failed
  because one side or the other wasn't sung by enough different singers in
  this dataset — not because the ragas aren't distinguishable.
- **Why did the generator work for one raga and not the other?** A plausible,
  documented-theory-based hypothesis: Karaharapriya uses all 7 notes of its
  scale, each allowing ornamentation, so there's more room for its overall
  pitch pattern to look statistically different from the other raga.
  Mōhanaṁ, despite also being heavily ornamented, uses only 5 notes — fewer
  categories for the same statistical comparison to spread across, which may
  make it inherently harder to tell apart this way, regardless of how good
  the generator itself is. **This is a reasonable hypothesis, not a proven
  explanation** — it hasn't been directly tested.

## 6. Honest Limitations (worth stating plainly)

- Results depend on which singers happen to be in the dataset for each raga;
  most experiments control for this, but the smallest ones (4-raga set,
  generator) rely on only 2 singers per raga — a hard confound to fully rule
  out at this scale.
- The dataset mixes two different pitch-extraction sources (full-mix audio
  vs. isolated-vocal audio) with different quality and time resolution.
- This is a small dataset (one public collection, tens of minutes per raga in
  the smallest experiments) — treat every number here as suggestive of a real
  pattern, not as a precise, bulletproof measurement.
- The generative model is a small proof-of-concept, evaluated on only 6
  generated samples per raga — informative, not a benchmark result.
- Dataset licence (CC BY-NC-SA 4.0) restricts this work and its outputs to
  non-commercial, attributed, share-alike use.

---
*Generated from `artifacts/numbers.json` and the analysis in
`notebooks/00_data_audit.ipynb` through `notebooks/05_report.ipynb`. See
`status/STATUS_M0.md` through `STATUS_M6.md` for the full milestone-by-milestone
record, including a correction made during final verification
(`status/STATUS_M2.md`'s correction note) — the numbers in this report are the
corrected, twice-reproduced ones.*
