# STATUS — Milestone 2: Quantisation Study (THE SPINE)

Ran `notebooks/02_quantisation_study.ipynb` top-to-bottom. All numbers below are
read from `artifacts/numbers.json["m2"]`, `artifacts/m2_perfold_results.csv`, and
`artifacts/m2_raga_degradation_ranking.csv`.

> **CORRECTION (2026-08-29, during M6 verification):** the tables originally
> below were computed against a stale `corpus_allsections/` build. While
> verifying every notebook runs clean for the report, a fresh top-to-bottom
> rerun of `01_corpus_build` → `02_quantisation_study` produced measurably
> different numbers (same shape, same conclusion, different magnitudes and one
> ranking-order change). Re-run twice more independently — byte-identical
> `manifest.csv` and identical `numbers.json["m2"]` both times — confirming the
> pipeline itself is deterministic; the drift was a one-time historical staleness,
> not live nondeterminism. Best-evidenced explanation: `dgm_utils.py`'s mtime
> (Aug 10) postdates the original `corpus_allsections/` build (Aug 9) from this
> same session block, so the corpus was very likely rebuilt with updated
> corpus-building logic after M2's original numbers were computed, and M2 was
> never re-run to pick up that change. **Tables below are now the corrected,
> twice-reproduced numbers** as of the M6 rerun; the original figures are struck
> through, not deleted, so this correction is itself auditable. Lesson for future
> milestones: re-run a downstream milestone's numbers whenever an upstream
> notebook or `dgm_utils.py` changes, don't assume `numbers.json` stays current.

## What was done

**Pipeline.** Folded pitch-class contours windowed at 4s / 4s hop (non-overlapping,
both params). Resolution swept as histogram bin width: 10c (stands in for
"continuous"), 20c, 50c, 100c (semitone). Classifier: `LogisticRegression`,
recording-/artist-/composition-grouped CV via `StratifiedGroupKFold` sized to the
data (`dgm_utils.make_group_cv`).

**Class-imbalance catch, confirmed in the real run.** Window counts per raga range
~170–1700 (allsections corpus). An unweighted classifier gave near-chance,
non-monotonic garbage with several ragas at 0% recall at every resolution —
not a hypothesis failure, a starved-classifier artifact. `class_weight="balanced",
C=10` fixed it outright (demonstrated in the notebook's section 2 before/after). This
is now CLAUDE.md's standing classifier config for the project.

**Two bugs found and fixed during this run** (both now patched on disk):
1. `ax.barh(RANK.raga, RANK.drop)` — `RANK.drop` resolved to the DataFrame's `.drop()`
   *method* (pandas attribute access loses to method names on collision), not the
   column named "drop". Fixed to `RANK["drop"]`. This one took three attempts because
   VS Code kept re-saving a stale in-memory copy of the cell over my on-disk fix —
   worth remembering if a "fixed" bug reappears identically: check whether the editor
   tab was actually reloaded from disk, not just re-run.
2. The accuracy-vs-resolution figure called `ax.invert_xaxis()` on all three panels,
   which flipped the x-axis to show semitone (100c) on the left — the opposite of
   what the figure's own title claims ("finer bins → left; semitone=100c → right").
   Removed; axis direction now matches the title.

**Five experiment configs run**, all on `class_weight="balanced", C=10`:

~~| Corpus | Pool | Grouping | continuous(10c) | 20c | 50c | semitone(100c) | chance |~~
~~|---|---|---|---|---|---|---|---|~~
~~| alapana | 4 ragas | recording | 0.474 ± .056 | 0.489 ± .086 | 0.451 ± .054 | 0.454 ± .077 | 0.25 |~~
~~| allsections | primary-12 | recording | 0.343 ± .072 | 0.348 ± .075 | 0.352 ± .065 | 0.279 ± .060 | 0.083 |~~
~~| allsections | primary-12 | artist | 0.431 ± .016 | 0.430 ± .004 | 0.443 ± .028 | 0.338 ± .028 | 0.083 |~~
~~| allsections | primary-12 | composition | 0.355 ± .011 | 0.362 ± .017 | 0.385 ± .017 | 0.299 ± .020 | 0.083 |~~
~~| allsections | secondary-40 | recording | 0.106 ± .009 | 0.110 ± .009 | 0.115 ± .009 | 0.086 ± .011 | 0.025 |~~
*(struck through — superseded, see correction note at top)*

**Corrected (2026-08-29, twice-reproduced):**

| Corpus | Pool | Grouping | continuous(10c) | 20c | 50c | semitone(100c) | chance |
|---|---|---|---|---|---|---|---|
| alapana | 4 ragas | recording | 0.582 ± .129 | 0.590 ± .141 | 0.565 ± .137 | 0.516 ± .111 | 0.25 |
| allsections | primary-12 | recording | 0.383 ± .009 | 0.391 ± .011 | 0.402 ± .019 | 0.309 ± .010 | 0.083 |
| allsections | primary-12 | artist | 0.398 ± .044 | 0.408 ± .040 | 0.419 ± .065 | 0.326 ± .005 | 0.083 |
| allsections | primary-12 | composition | 0.382 ± .036 | 0.391 ± .032 | 0.397 ± .031 | 0.316 ± .041 | 0.083 |
| allsections | secondary-40 | recording | 0.130 ± .006 | 0.138 ± .007 | 0.147 ± .002 | 0.118 ± .014 | 0.025 |

(mean balanced accuracy ± std over folds; n_splits = 2 for alapana and secondary-40,
3 for primary-12 — sized to the smallest per-class group count, per
`dgm_utils.make_group_cv` — **this sizing is unchanged from before the
correction**; the drift is in the underlying window data, not the CV structure.)

**Pattern, stated factually:** all five configs show the same shape — roughly
flat, or mildly rising, from continuous through 50c, then a real drop at semitone.
The drop is most confident (small std relative to the gap) in the artist-grouped
and composition-grouped primary-12 runs and in the secondary-40 pool; the
alapana-only corpus shows the same direction but with only 2 CV folds the error
bars are wide enough that continuous vs. semitone isn't clearly distinguishable
there specifically. The effect is concentrated at the last, coarsest step (50c →
semitone) rather than a smooth decline from the very start — continuous does not
clearly outperform 20c or 50c in any config.

**Per-raga degradation ranking** (primary-12 pool, recording-grouped, out-of-fold
recall at continuous vs. semitone). ~~Original table superseded — see correction
note at top; Suraṭi/Kamās/Sindhubhairavi/Mōhanaṁ/Tōḍi/Kalyāṇi/Harikāmbhōji/
Bhairavi/Ṣanmukhapriya/Behāg/Rītigauḷa/Sāvēri = 0.186/0.140/0.135/0.118/0.103/
0.099/0.050/0.045/0.023/-0.009/-0.020/-0.154 is the old, stale ranking, kept
here only for the audit trail.~~ **Corrected:**

| Raga | recall (continuous) | recall (semitone) | drop |
|---|---|---|---|
| Suraṭi | 0.441 | 0.271 | **0.170** |
| Sindhubhairavi | 0.465 | 0.318 | 0.147 |
| Mōhanaṁ | 0.433 | 0.295 | 0.139 |
| Kamās | 0.497 | 0.374 | 0.124 |
| Rītigauḷa | 0.198 | 0.103 | 0.095 |
| Bhairavi | 0.450 | 0.384 | 0.065 |
| Tōḍi | 0.433 | 0.369 | 0.063 |
| Kalyāṇi | 0.132 | 0.085 | 0.047 |
| Behāg | 0.377 | 0.339 | 0.038 |
| Ṣanmukhapriya | 0.432 | 0.408 | 0.025 |
| Harikāmbhōji | 0.188 | 0.190 | -0.002 |
| Sāvēri | 0.649 | 0.747 | **-0.098** |

9 of 12 ragas still show a positive drop, but the ranking order changed
materially — **Rītigauḷa moved from "essentially flat" (-0.020) to the 5th-largest
drop (0.095)**, and Harikāmbhōji moved the other way, from a real drop (0.050) to
essentially flat (-0.002). Behāg is now mildly positive rather than flat. **Sāvēri
is still the clear outlier in the reverse direction** (recall improves at semitone
resolution), though the magnitude shrank from -0.154 to -0.098. Flagging for your
musical read, not interpreting further (per CLAUDE.md, that call is yours) — note
that any earlier reading of "Behāg and Rītigauḷa are flat, so gamaka-dependence
doesn't apply to them" no longer holds for Rītigauḷa.

## Numbers (also in `artifacts/numbers.json["m2"]`)

- Window: 4s / 4s hop. Resolutions: 10/20/50/100 cents.
- Classifier: `LogisticRegression(class_weight="balanced", C=10)`.
- Primary pool: 12 ragas. Secondary pool: 40 ragas.
- Headline accuracy table and full per-raga ranking: see tables above.
- Per-fold numbers: `artifacts/m2_perfold_results.csv` (48 rows: 5 configs × 4
  resolutions × 2-3 folds each).

## What's blocked / decision needed from you

None blocking. Two things for your read when convenient:

1. **Sāvēri's reversed pattern** in the degradation ranking — real signal or an
   artifact of its small sample (comps=3, right at the primary-pool floor)? Your
   call.
2. **Allied pair** — still on hold per your earlier message. The per-raga
   degradation ranking above is the generalised substitute you asked M2 to produce
   regardless of that decision; it's already done. Whenever you come back with a
   named pair (or a confirmed drop), M3 can either test that pair directly or fold
   into a short write-up pointing at this ranking.

## What's next

Per the fallback ordering in `spec.md`, M0+M1+M2 (+M6 report) is already a complete,
submittable project. From here: M3 (allied pair or its documented drop, depends on
your review) and M4/M5 (generator, optional, must not block submission) are
enhancements. Your call on which to do next.
