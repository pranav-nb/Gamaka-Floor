# STATUS — Milestone 3: Allied Pair (documented drop)

Ran `notebooks/03_allied_pair.ipynb` top-to-bottom. Confirms and closes out the
allied-pair question that M0 flagged as "on hold, not dropped" pending the owner's
review of the 18-raga balanced list. **Owner confirmed: proceed as the documented
drop** (no named pair volunteered). All numbers below are reused from
`artifacts/numbers.json["m0"]`/`["m2"]` and `artifacts/coverage_quantisation.csv` —
no new modelling ran in this milestone.

## What was done

**Recapped M0's search with numbers, in-notebook.** Five musically-plausible allied
candidates (Suraṭi/Kēdāragauḷa, Kāṃbhōji/Harikāṃbhōji, Ābhōgi/Śrīranjani,
Bēgaḍa/Śankarābharaṇaṃ, Kalyāṇi/Hamīr kaḷyaṇi) all fail the artist-balance bar on at
least one side — either one side is single-artist, or the same lead voice dominates
both sides (Kāṃbhōji/Harikāṃbhōji: Sanjay Subrahmanyan on both). Widening to every
raga with ≥2 artists each contributing ≥4 vocal-minutes gives 18 well-balanced ragas
collection-wide; none of those 18 form a musically allied pair with each other by
ear/theory. The well-balanced set and the allied set simply don't intersect in this
corpus.

**Decision recorded: allied-pair experiment dropped.** Per `spec.md` M3's fallback
acceptance ("a crisp written justification for dropping it"). Reasoning: any
allied-pair contrast run on this collection would be indistinguishable from a
singer-identity effect, which CLAUDE.md constraint 2 explicitly rules out as a claim
this project makes.

**Substitute presented: M2's per-raga degradation ranking**, reused (not
recomputed) from `artifacts/m2_raga_degradation_ranking.csv`. This generalises the
allied-pair claim — ragas whose identity lives in gamaka should lose more recall
under coarsening than note-set-only ragas — across the whole 12-raga quantisation
pool, without needing artist balance (it's a within-raga, continuous-vs-semitone
comparison, not a between-raga one). New figure:
`artifacts/figures/m3_degradation_ranking_reuse.png` (same data as M2's figure,
re-plotted here so this notebook is self-contained).

9/12 ragas show a positive drop; Suraṭi (0.170), Sindhubhairavi (0.147), Mōhanaṁ
(0.139), Kamās (0.124), Rītigauḷa (0.095) show the largest. Sāvēri is the clear
outlier, improving at semitone resolution (-0.098) — still flagged for the owner's
musical read, unresolved since M2. **(Correction, 2026-08-29: these numbers were
updated during M6's verification pass — the original M2 ranking this notebook first
reused was computed against a stale corpus build; see `status/STATUS_M2.md`'s
correction note. The decision to drop the allied-pair experiment and the figure
`m3_degradation_ranking_reuse.png` were regenerated fresh against the corrected data
and are unaffected in substance — only the specific numbers cited in this prose
changed.)**

## Numbers (also in `artifacts/numbers.json["m3"]`)

- `decision`: "dropped"
- `candidates_checked`: the 5 pairs above, all failed
- `n_balanced_ragas_no_ally`: 18 (≥2 artists × ≥4 vocal-min each, none allied to each other)
- `substitute`: `m2_raga_degradation_ranking` (reused)
- `leave_one_artist_out_check_run`: **False** — spec §5's ideal M3 acceptance
  criterion (a leave-one-artist-out check on an actual pair) was never run, because no
  pair qualified to run it on. Stated explicitly here and belongs in the report's
  limitations section, not glossed over.

## What's blocked / decision needed from you

None blocking M3 itself — it's closed. Still open from M2, unrelated to this
milestone: Sāvēri's reversed degradation pattern (real signal or small-sample
artifact, comps=3).

## What's next

Per `spec.md`'s fallback ordering, M0+M1+M2+M3(+M6 report) is now a complete,
submittable project with the allied-pair question honestly closed rather than left
open. Remaining: M4/M5 (generator, optional, must not block submission) and M6
(report assembly). Your call on whether to attempt the generator next or go straight
to the report.
