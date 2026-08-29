# STATUS — Milestone 5: Generator Evaluation

Appended the M5 evaluation sections directly onto `notebooks/04_generator.ipynb`
(per spec.md, M4 and M5 share the same notebook file) and re-ran the whole
notebook top-to-bottom on a fresh kernel (~7 min CPU: M4 retrains, then M5 runs
against exactly that run's generated samples — no reuse of stale artifacts). All
numbers below are read from `artifacts/numbers.json["m5"]` and the notebook's own
output. Optional milestone (spec.md M5); framed throughout as PoC-only.

## What was done

Three checks, all against the 2 artist-balanced alapana ragas from M4
(Karaharapriya, Mōhanaṁ): 6 generated samples/raga vs. 934 real windows from 2
recordings/raga.

**1. Folded pitch-class-histogram distance** (Jensen-Shannon, generated vs. real,
own-raga vs. other-raga, swept at M2's 4 resolutions). **Mixed result, split by
raga:** Karaharapriya generated samples show a real, consistent discriminative gap
(closer to real Karaharapriya than to real Mōhanaṁ) at 20/50/100c — 0.054, 0.050,
0.045 respectively — that collapses at 10c (too fine for only 1,380 generated
frames to estimate). **Mōhanaṁ generated samples show almost no gap at any
resolution** (0.003–0.019) — its pitch-class distribution doesn't clearly read as
closer to real Mōhanaṁ than to real Karaharapriya. Figure:
`artifacts/figures/m5_histogram_distance.png` (20c shown).

**2. Classifier-called-raga.** Judge: fresh `LogisticRegression(class_weight=
"balanced", C=10)` (M2's standing config) on real 2.0s-window folded histograms —
M2's own fitted models weren't persisted, so this is a new fit scoped to the
generator's window length, not a reused artifact. **Critical context, not a
caveat to skip past:** the judge's own artist-grouped CV accuracy on *real* data
is only 0.576–0.601 across resolutions (chance = 0.5) — this 2-raga, 2-artist
problem is hard even on real data under a fair (leave-one-artist-out-style) test.
Read the generated-sample numbers against that ceiling, not against 100%:

| bin_width | Karaharapriya call acc | Mōhanaṁ call acc | real CV sanity (chance=0.5) |
|---|---|---|---|
| 10c | 0.167 (1/6) | 1.000 (6/6) | 0.601 |
| 20c | 0.833 (5/6) | 0.667 (4/6) | 0.591 |
| 50c | 0.833 (5/6) | 0.500 (3/6) | 0.578 |
| 100c | 0.833 (5/6) | 0.500 (3/6) | 0.576 |

Karaharapriya generations are called correctly well above the judge's own real-data
ceiling at every resolution except 10c (where n=6 generated samples makes single
misclassifications swing the rate by 16.7 points). Mōhanaṁ is inconsistent — perfect
at 10c, chance at 50c/100c — consistent with check 1's finding that Mōhanaṁ
generation is the weaker of the two.

**3. Memorisation check.** Nearest-neighbour RMS distance (cents) from each
generated sample to the full real-window pool, against a real-to-real leave-one-out
baseline (n=200 sampled). **No evidence of copying:** generated-to-real median
distance (149.3c) sits in the same range as the real-to-real baseline median
(161.9c) — generation is not collapsing onto training examples. The single closest
generated sample (13.9c, a Mōhanaṁ sample) sits near the low tail of the real
baseline (min 7.1c, p5 11.4c cents) — close enough to flag by name, but real windows
themselves get that close to each other too (almost certainly adjacent/overlapping
windows from the same sustained phrase), so this isn't distinguishable from normal
corpus self-similarity. Worth noting: that closest sample's real nearest-neighbour is
a *Karaharapriya* window (KP Nandini), not a Mōhanaṁ one — a third, independent
data point for the same asymmetry as checks 1 and 2. Figure:
`artifacts/figures/m5_memorisation_check.png`.

## Honest synthesis (stated plainly, not left for the reader to infer)

**Karaharapriya generation shows real raga-conditioning signal** across all three
checks (discriminative histogram gap, above-ceiling judge accuracy, no
memorisation). **Mōhanaṁ generation does not clearly show the same** — weak
histogram gap, judge accuracy that swings between perfect and chance depending on
resolution, and its single closest real match is from the other raga. This is a
consistent pattern across three independent methods, not noise in one of them, so
it's worth taking seriously rather than averaging away. Two plausible explanations,
not adjudicated here: Mōhanaṁ has fewer training windows (396 vs. 538) and one
Mōhanaṁ artist has visibly shorter/choppier alapana runs (see M4's run-length
stats), or Mōhanaṁ's own note-set (a pentatonic raga) may simply be less
distinguishable in a coarse pitch-class histogram than Karaharapriya's — the
report's musical-judgement call, not a modelling one.

Every number here is over 6 generated samples and 2 real recordings per raga. This
is a proof-of-concept, not a benchmark result, and should be presented as such.

## Numbers (also in `artifacts/numbers.json["m5"]`)

Full per-resolution histogram-distance table, judge-classifier table, and
memorisation-check numbers are all in `numbers.json["m5"]`; headline figures above.

## What's blocked / decision needed from you

None blocking. The Karaharapriya/Mōhanaṁ asymmetry above is a musical-judgement
question (why would Mōhanaṁ generate less distinctively?) that belongs to you per
CLAUDE.md, not something to resolve in code.

## What's next

M4+M5 are both closed. Per spec's fallback ordering, the project is now
M0–M5(+M6): everything except the final report assembly. **M6** (`05_report.ipynb`)
is what remains — collect every figure/table/number produced so far into the
submission narrative with the limitations section (artist confound, mix-vs-vocal
pitch, tiny corpus, single dataset, CC BY-NC-SA licence, plus the two new honest
flags from M4/M5: the sustained-octave-tracking-error data-quality issue and the
Karaharapriya/Mōhanaṁ generation asymmetry above).
