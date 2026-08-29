# CLAUDE.md — Gamaka Floor: A Raga Pitch-Contour Study

**Project name: Gamaka Floor** (chosen 2026-08-29). The working directory
stays `D:\DGM\` on disk purely as a filesystem path — only the project's
displayed name/title changed, not the folder path or any of the hardcoded
`D:\DGM\` references throughout this file and the notebooks.

Standing context for this repo. Read alongside `spec.md`, which holds the full
milestone plan and acceptance checks. This file is the durable "what and why";
`spec.md` is the "how and in what order". If they ever conflict, `spec.md` wins on
process, this file wins on facts and decisions.

---

## What this project is

A **deep generative models study**, deliberately light in scope, novelty
optional. Adjacent to the owner's MRI thesis but evaluated as its own thing.

Core idea: in Carnatic music, raga identity lives substantially in the **continuous
pitch contour** (gamaka / ornamentation), not just the discrete note set. The
**spine** is a **quantisation study** — how far can pitch resolution be coarsened
(continuous cents → 12 semitones) before a raga classifier collapses? That curve
quantifies how much raga identity sits below the note level. Two smaller pieces sit
on top: an **allied-raga contrast** and an **optional proof-of-concept generator** of
pitch contours.

**Priority order:** quantisation study (must ship) > report honesty > allied pair >
generator (optional, must never block submission). The spine plus report = a complete
project on its own.

---

## Owner & working preferences

- Software engineer (MRI, Siemens Healthineers); M.Tech (Online) at IISc. Strong on
  ML; **no Carnatic/Sanskrit music background** (corrected 2026-08-29 — this file
  previously and wrongly assumed deep music-theory expertise and treated him as
  the musical-judgement authority; he said directly he doesn't have that
  background). Explanations should assume ML fluency but not raga/gamaka
  familiarity.
- Writing style for any prose: **no em dashes** (use commas, colons, periods);
  Sanskrit/Kannada terms in **plain English spelling, no IAST diacritics** in prose
  (data labels keep their original diacritics — see below).
- **Musical interpretation is sourced from documented Carnatic theory (academic
  papers, reference sites), not personal ear-training** — this replaces the
  original plan of the owner writing the musical argument himself. Cite sources,
  hedge honestly where documentation is thin or contradicts the data (e.g. M6's
  Sāvēri counterexample — see `notebooks/05_report.ipynb` §2), and never invent a
  gamaka characterization that isn't in a found source. Notebooks still generate
  figures/tables/numbers; interpretation prose is now researched-and-drafted by
  Claude and reviewed by the owner, not ghost-written from nothing.
- Timeline: **48 hours**, worked in intermittent blocks, with a **status report every
  6–8 hours**. Each milestone ends by writing `status/STATUS_Mn.md`.

---

## Hard constraints

1. **Free tier only** (Kaggle/Colab, single T4/P100, ~12 h session cap, ephemeral
   disk). Small models, frequent checkpoints, a single `DATA_ROOT` switch for
   local-vs-Kaggle paths.
2. **Artist confound is first-class.** Every raga-level result is reported with its
   artist composition. Never claim "distinguishes raga X from Y" where singer identity
   could equally explain it. (See rejected/known-bad below.)
2b. **Composition (kriti) confound is equally first-class**, for metered sections only.
   Two recordings of the same composition in the same raga let a classifier learn the
   song, not the raga. Report per-raga composition diversity (via `work[0].mbid`)
   alongside artist diversity, and use composition-disjoint folds where feasible in
   addition to recording-grouped and artist-grouped splits. **Alapana is exempt**
   (unmetered, no fixed melody, no composition identity) — this is a second reason,
   beyond cleanliness, to keep the alapana-only corpus as its own thing.
   **Concrete instance found (M1):** all 6 "Saurāṣtraṁ" recordings in the corpus are
   the same mangalam ("Pavamana Suthudu") sung by 6 different artists — passes the
   artist-balance bar cleanly, fails composition diversity completely (1 distinct
   composition). Jōnpuri similarly thin (2 compositions / 3 recordings). Both flagged
   `comp_degenerate=True` in `artifacts/coverage_allsections.csv` and excluded from
   the primary M2 pool below. This is why the guard exists as its own axis, not a
   derivative of the artist check.
3. **Split by recording, never by window.** Windows from one recording must not
   straddle a train/test split. Prefer artist-disjoint splits where feasible.
4. **Two representations, never conflated:** folded pitch-class (`cents % 1200`) for
   histograms/classification; unfolded cleaned contour for the generator.
5. **No fabricated numbers.** If it can't be computed, the status report says so.

---

## Verified data facts (trust these over priors; re-verify against disk if surprised)

Dataset: **Saraga Carnatic 1.5**, CC BY-NC-SA 4.0, Zenodo 4301737. Audio (14.4 GB) is
NOT needed; only text annotations are used.

Paths (local Windows):
- Extracted annotations: `D:\sg\saraga1.5_carnatic\`
- Alapana corpus (built): `D:\DGM\corpus\` — per-segment unfolded-cents `.npy` +
  `manifest.csv`. 4 ragas, 8 segments.
- All-vocal-sections corpus (built, M1): `D:\DGM\corpus_allsections\` — per-segment
  unfolded-cents `.npy` + `manifest.csv`. 96 ragas (Rāgamālika excluded), 526
  segments, 111 sectioned + 65 whole-track-fallback recordings. This is the spine's
  corpus (M2).
- Prototypes (superseded by `dgm_utils.py`, kept for record): `D:\DGM\prototypes\`.
- Working dir: `D:\DGM\`; notebooks in `notebooks\`, outputs in `artifacts\`,
  status in `status\`.

File formats (verified):
- `*.pitch.txt`: 2 cols `time, freq(Hz)`; **frame rate ≈ 225 Hz**; unvoiced = freq 0;
  voiced fraction ~0.7.
- `*.pitch-vocal.txt`: cleaner, isolated-vocal, but only ~56 recordings have it.
  **Different hop size: ≈344.5 Hz, NOT 225 Hz** (verified M1 across 8 sampled files
  each, both rates exactly consistent within their file type). `dgm_utils.read_pitch()`
  measures fps per file rather than assuming a constant — a shared constant would
  have silently inflated every duration/minute figure for vocal-sourced recordings
  by ~53%.
- `*.ctonic.txt`: single float tonic (Hz). `cents = 1200*log2(freq/tonic)`.
- `*.sections-manual-p.txt` (119) and `*.sections-manual.txt` (73): **4 tab cols**
  `start, 1, DURATION, label`. Column 3 is duration, not end. `end = start+duration`.
  **Resolved in M0: use `-p` only** — plain is a strict subset, merging adds nothing.
- Metadata `.json`: raga = `raaga[0].name`; artist = `album_artists[0].name` (or
  `artists`). Verify keys on a real file.
- Section labels carry diacritics. **Alapana = `Vocal ālāp`** (also `Violin ālāp` —
  exclude). Match substring `ālāp`, exclude `violin`.

Pitch cleaning (verified necessary):
- Octave errors: isolated ±~1200-cent frames → rolling-local-median filter, drop
  frames > ~900 cents from local median over ~50 frames.
- Fold `cents % 1200` for pitch-class work; keep unfolded cleaned contour for the
  generator. A correct folded histogram shows sharp peaks with a strong one near 0 (Sa).

---

## Raga set & the artist confound (the decision that shapes every claim)

Only 4 ragas cleared "≥15 min alapana, ≥2 artists", and two are effectively
single-voice:

| Raga          | ~min | artist balance                             | status            |
|---------------|------|--------------------------------------------|-------------------|
| Karaharapriya | 20   | KP Nandini 10.4 / Shankaranarayanan 9.8    | balanced — usable |
| Mōhanaṁ       | 16   | Ashwath Narayanan 8.0 / Sumithra Vasudev 7.9| balanced — usable |
| Bhairavi      | 13   | Vignesh Ishwar 12.3 / Sanjay 0.3           | single-artist     |
| Ṣanmukhapriya | 12   | Sanjay 12.0 / Akkarai Sisters 0.5          | single-artist     |

Implications:
- **Generator** trains cleanly only on Karaharapriya + Mōhanaṁ.
- **Allied pair**: Bhairavi vs Karaharapriya is confounded (Bhairavi = one voice).
  Milestone 0 searches the full collection for an allied AND balanced pair; if none,
  the allied framing is dropped and the point is made via the quantisation curve.
- **Quantisation study** uses ALL raga-labelled recordings (~185, many artists), which
  dilutes the confound — this is why it is the spine, not the alapana-only pieces.

**Milestone 0 result (2026-08-09):** searched 5 musically-plausible allied candidates
(Suraṭi/Kēdāragauḷa, Kāṁbhōji/Harikāmbhōji, Ābhōgi/Śrīranjani, Bēgaḍa/Śankarābharaṇaṁ,
Kalyāṇi/Hamīr kaḷyaṇi) against per-artist vocal-section minutes across all 96 ragas in
the collection. **No pair has ≥2 well-represented artists (≥4 vocal-min) on both
sides** — every candidate fails on one side or the other, or has the same lead artist
dominating both ragas. Regardless of that outcome, **M2 produced a per-raga
accuracy-drop ranking** (continuous → semitone, every raga in the quantisation pool):
this generalises the allied-pair claim without needing a balance constraint (ragas
whose identity lives in gamaka should degrade hard; note-set-only ragas should barely
move).

**Milestone 3 result (2026-08-29): allied pair CONFIRMED DROPPED.** Owner reviewed
the 18-raga balanced-vocal-minutes list and did not volunteer a named pair; M3 closed
as the documented drop per `spec.md`'s fallback acceptance. The M2 degradation
ranking (`artifacts/m2_raga_degradation_ranking.csv`, re-presented in
`notebooks/03_allied_pair.ipynb`) stands as the sole allied-pair-adjacent evidence in
this project. **No leave-one-artist-out check was ever run** — spec §5's ideal M3
acceptance criterion required an actual pair to run it on, and none qualified. State
this explicitly in the report's limitations section rather than presenting the
degradation ranking as an equivalent, artist-controlled result. See
`status/STATUS_M3.md`.

Section-file merge question resolved: every `sections-manual.txt` (plain, 73
files) recording also has a `sections-manual-p.txt`, and merging adds zero alapana
minutes (252.6 either way) — **use `-p` only**, drop the plain variant from the
pipeline entirely.

**Rāgamālika excluded from all classification work.** It is a medley that moves
through several ragas by construction, not a single raga — including it would poison
any classifier's raga classes. It never appears as a training label in M2 (or
downstream). (8 recordings / 7 artists under that label, per `coverage_quantisation.csv`.)

**Mislabelled-section filtering (M1).** Within a track, some metered-section labels
name a *different* raga than the track's own label (e.g. `Caraṇam sahānā`,
`Anupallavi kāpi`, `Caraṇam hamsānandi` inside a track whose main raga is something
else) — these mark a passage rendered in another raga and are contaminated training
data for the track's nominal raga. `dgm_utils.py` detects and drops them (any
`Caraṇam/Anupallavi/Pallavi <suffix>` label whose suffix doesn't normalize-match the
track's own raga name), logging the count/duration removed per raga. Alapana is
unaffected (single-raga by construction, no sub-labels of this kind).

---

## Rejected / known-bad approaches (do not revisit without a strong reason)

- **MRI-based DGM ideas** (learned motion-corruption model, k-space diffusion prior,
  disentanglement of acquisition from anatomy): considered first, set aside. The
  k-space prior specifically is infeasible on free tier.
- **Sanskrit chant / Vagdhenu prosody conditioning**: the Vagdhenu system is F5-TTS
  (flow-matching DiT); its own tech report shows **text-side prosody conditioning is
  architecturally inert** (multiple negatives, E41/E59/E65/E68/E78 — never re-attempt).
  Also, no public aligned Sanskrit corpus is available to us. Abandoned in favour of
  the Carnatic-analysis project, which has public data (Saraga) today.
- **Kannada shatpadi generation** and **terrain diffusion** and **raga-conditioned
  broad generator (20 ragas)**: viable but not chosen; shatpadi remains the fallback
  if Saraga data ever proves unworkable (its data is text the owner already owns).
- **Bhairavi-vs-Karaharapriya allied pair**: rejected due to the artist confound above.
- **Allied-pair framing generally**: M0 searched 5 candidate pairs across the full
  collection (not just the alapana-only 4-raga set) and found none with balanced
  artist coverage on both sides — see M0 result above. Pending owner confirmation,
  the allied-pair experiment is dropped; M3 documents this instead of running it.
- **Merging `sections-manual.txt` (plain) with `sections-manual-p.txt`**: tested in M0;
  plain is a strict subset of `-p` (every plain-file recording also has `-p`, and `-p`
  already covers all of plain's alapana). Merging adds zero coverage. Use `-p` only.
- **FID for evaluation**: meaningless here (ImageNet features on hillshades/contours).
  Use pitch-class-histogram distance and classifier-called-raga instead.
- **Blind `split("\t")` giving 3 cols / `end-start` math**: wrong — sections are 4-col
  and col 3 is duration. (Historical bug, fixed; noted so it isn't reintroduced.)
- **A single `FRAME_RATE_HZ` constant for both pitch file types**: wrong — `pitch.txt`
  is ≈225 Hz, `pitch-vocal.txt` is ≈344.5 Hz (verified M1, consistent across samples).
  Caught before it reached the corpus. `dgm_utils.read_pitch()` measures fps per file;
  never hardcode it.
- **Trusting `numbers.json`/status-report numbers without re-running after an
  upstream change**: caught during M6's verification pass. `dgm_utils.py` was
  edited (Aug 10) after `corpus_allsections/` was built (Aug 9) in the same
  session block, but M2 was never re-run afterward — its headline table and
  per-raga degradation ranking sat stale in `numbers.json`/`STATUS_M2.md` for
  the rest of the project, including being reused verbatim by M3. Caught only
  because M6 re-executed every notebook fresh as its own acceptance check, then
  re-ran M2 twice more back-to-back to confirm the new numbers were reproducible
  (byte-identical `manifest.csv`, identical `numbers.json["m2"]`) rather than
  live nondeterminism. **Lesson: re-run a downstream milestone whenever an
  upstream notebook or `dgm_utils.py` changes — don't assume a prior milestone's
  `numbers.json` entry is still current just because it exists.** See
  `status/STATUS_M2.md`'s correction note for the corrected tables.
- **Unweighted `LogisticRegression` on the per-window pitch-class histograms (M2)**:
  window counts per raga range ~170–1700 (allsections corpus); unweighted multinomial
  LR collapses under this — several ragas get 0% recall at every resolution, balanced
  accuracy sits near chance, and the resolution sweep looks like non-monotonic noise.
  Not a hypothesis failure, a starved-classifier artifact. Fixed with
  `class_weight="balanced"` (verified: zero-recall classes → 0, accuracy roughly
  doubles). `C=10` (less L2 reg. than sklearn's default `C=1`) gave a cleaner, higher
  curve in validation. This exact config (`class_weight="balanced", C=10`) is the
  standard classifier for every M2 experiment — don't revert to defaults.

---

## Deliverables

Notebooks (see `spec.md` §4 for details): `00_data_audit`, `01_corpus_build`,
`02_quantisation_study` (spine), `03_allied_pair` (or documented drop), `04_generator`
(optional), `05_report`. Shared pipeline in `dgm_utils.py`. Headline metrics collected
in `artifacts/numbers.json`; figures in `artifacts/figures/`.

"Done" = notebooks run clean top-to-bottom on a fresh kernel + the
accuracy-vs-resolution curve exists + an honest limitations section (artist confound,
mix-vs-vocal pitch, tiny corpus, single dataset, CC BY-NC-SA licence).

---
### Maintenance: 

Keep this file true as decisions land. When Milestone 0 resolves the section-merge and allied-pair questions, or the raga set changes, update the raga table and the rejected-approaches list in the same commit, and note the change in that milestone's status report.