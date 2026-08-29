# STATUS — Milestone 1: Corpus + Utils Solid

Ran `notebooks/01_corpus_build.ipynb` top-to-bottom. All numbers below are read from
`artifacts/numbers.json`, `artifacts/coverage_allsections.csv`,
`artifacts/coverage_alapana.csv`, and the two figures in `artifacts/figures/`. (Note:
outputs weren't saved back into the `.ipynb` on this run — the artifacts are all
correct, but re-save after "Run All" next time so the notebook itself carries its
outputs, per spec's "runs clean" bar.)

## What was done

**`dgm_utils.py` built and unit-checked.** Loaders (json/pitch/tonic/sections), cents
conversion, octave-outlier cleaner, fold, section-label classifier, composition-id
extraction, windower, grouped-split helpers.

**Caught a real bug before it reached the corpus.** `pitch-vocal.txt` measures
~344.5 Hz, not the 225 Hz verified for `pitch.txt` — confirmed consistent across 8
sampled files each, two genuinely different hop sizes. `dgm_utils.read_pitch()` now
measures frame rate per file instead of assuming a constant. Had this shipped
uncaught, every duration/minute figure for the ~56 recordings with a vocal-pitch
track would have been ~53% too high.

**Guard #2 (mislabelled sections) validated, not just implemented.** Checked the
section-label classifier against every label actually observed in the collection
(527 sections total): 12 sections are labelled with a raga name different from their
track's main raga (e.g. `Caraṇam sahānā`, `Anupallavi kāpi`, `Caraṇam hamsānandi`) —
and **all 12 belong to Rāgamālika tracks**, which are already excluded wholesale.
Once Rāgamālika is dropped, the mislabelled-section filter removes **zero** sections
from any other raga (`mislabelled_sections_outside_ragamalika: 0`). One genuinely
unrecognized label surfaced (`Viruttam`, a recitation form, not a raga name) and was
added to the canonical section-type set rather than silently dropped.

**Two corpora built:**

| | segments | ragas | notes |
|---|---|---|---|
| `corpus/` (alapana-only) | 8 | 4 (Karaharapriya, Mōhanaṁ, Bhairavi, Ṣanmukhapriya) | unchanged from M0 numbers, rebuilt clean |
| `corpus_allsections/` (spine) | 526 | 96 (Rāgamālika excluded) | 111 recordings sectioned, 65 whole-track fallback |

**Guard #4 (composition tracking) caught a concrete confound.** All 6 "Saurāṣtraṁ"
recordings in the corpus are the *same* composition — `Pavamana Suthudu`, a mangalam
(closing benediction, same fixed tune) — sung by 6 different artists (KP Nandini,
Akkarai Sisters, Sanjay Subrahmanyan ×3, Mahati, V. Shankaranarayanan). Saurāṣtraṁ
passes the artist-balance bar (5 distinct artists) but is composition-degenerate:
any classifier accuracy on it would mostly reflect recognizing one song's tune, not
the raga. Jōnpuri similarly fails (2 compositions across 3 recordings). Both are
flagged `comp_degenerate=True` in `coverage_allsections.csv` and excluded from the
primary pool below.

**Primary vs secondary M2 pool, three-way guarded** (recs≥3, artists≥3,
**comps≥3**) — landed at 12 ragas, in your expected 10-15 range:

| Raga | minutes | artists | recs | comps |
|---|---|---|---|---|
| Tōḍi | 115.9 | 7 | 6 | 6 |
| Ṣanmukhapriya | 108.6 | 3 | 4 | 4 |
| Bhairavi | 107.8 | 4 | 5 | 4 |
| Kamās | 49.9 | 4 | 7 | 7 |
| Rītigauḷa | 47.3 | 4 | 4 | 4 |
| Mōhanaṁ | 58.5 | 4 | 4 | 4 |
| Harikāmbhōji | 43.3 | 3 | 3 | 3 |
| Kalyāṇi | 33.2 | 3 | 4 | 4 |
| Sāvēri | 33.5 | 3 | 3 | 3 |
| Behāg | 16.2 | 4 | 5 | 4 |
| Sindhubhairavi | 11.8 | 3 | 3 | 3 |
| Suraṭi | 12.7 | 4 | 4 | 4 |

Secondary/full robustness pool (recs≥2, artists≥2, no composition guard): 40 ragas —
run M2 on both, per your instruction, and report whether the accuracy-vs-resolution
curve replicates.

**Sanity check passed.** Folded pitch-class histograms for all 4 alapana ragas show
a sharp, dominant peak at/near Sa (0/1200 cents) with sensible secondary peaks
matching each raga's swara positions (`artifacts/figures/m1_alapana_folded_histograms.png`).
One observation, not a red flag: Ṣanmukhapriya's histogram is visibly smeared /
broad-peaked rather than sharply multi-modal compared to the other three — could be
this raga's characteristically heavy gamaka usage (you're the authority on whether
that's musically expected) or a slightly off tonic on the dominant recording (Sanjay
Subrahmanyan, 16.8 of its 17.7 alapana-min). Flagging for your read, not treating as
a bug.

## Numbers (also in `artifacts/numbers.json`)

- Alapana corpus: 8 segments / 4 ragas. All-sections corpus: 526 segments / 96 ragas
  (111 sectioned recordings, 65 whole-track fallback).
- Mislabelled sections dropped: 0 (outside Rāgamālika, which is excluded entirely).
- Primary M2 pool: 12 ragas. Secondary: 40 ragas.
- Composition-degenerate (flagged, excluded from primary): Saurāṣtraṁ, Jōnpuri.
- `pitch-vocal.txt` fps = 344.531 (measured); `pitch.txt` fps = 225.0 (measured).

## What's blocked / decision needed from you

None blocking M2. Two things worth your read when convenient:

1. **Ṣanmukhapriya's smeared histogram** above — musical judgement call, not a data
   bug as far as I can tell.
2. **Allied pair** — still on hold per your last message, no action needed from me
   until you come back with a pair or a confirmed drop.

## What's next

M2 — the quantisation spine. Windowing (3-5s, param), baseline classifier
(histogram-feature + small 1-D CNN), recording-grouped CV (and composition-grouped
where `comps>=3`), the accuracy-vs-resolution sweep on **both** corpora (alapana-only
and all-vocal-sections) and **both** raga pools (primary 12, secondary 40), reported
with balanced accuracy / macro F1 given class sizes range 1-8. Plus the new
per-raga degradation ranking (continuous → semitone accuracy drop) you asked for,
which generalises the allied-pair claim independent of your pending decision.
