# STATUS — Milestone 6: Report Assembly & Polish

`notebooks/05_report.ipynb` written and executed clean (7s, all pulled live from
`artifacts/numbers.json` and existing figures/CSVs — no recomputation). This is
the final milestone; the project is submission-ready.

## What was done

**Report notebook.** Assembles every headline figure/table/number from M0–M5
into one narrative: motivation → data & artist confound → quantisation spine
(§2) → allied-pair drop (§3) → generator PoC (§4) → limitations (§5) → licence
(§6) → reproduction instructions (§7). Per CLAUDE.md's standing instruction, the
notebook presents **what was measured, not what it means** — every major result
section ends with an explicit `> **Your read:**` callout marking where your own
musical interpretation goes, rather than the notebook ghost-writing that
argument.

**A real correction surfaced during verification, not swept under the rug.**
Per spec's acceptance bar ("every notebook runs clean"), I re-ran `00`→`01`→`02`→
`03` fresh on a clean kernel as an actual check, not an assumption — and this
caught a genuine problem: **M2's headline accuracy table and per-raga degradation
ranking had gone stale.** `dgm_utils.py` was edited (Aug 10) after
`corpus_allsections/` was originally built (Aug 9), but M2 was never re-run
afterward — its numbers sat unrefreshed in `numbers.json`/`STATUS_M2.md` for the
rest of the project, and M3 reused them verbatim. Verified this wasn't live
nondeterminism by re-running `01`→`02` twice more, back-to-back: byte-identical
`manifest.csv`, identical `numbers.json["m2"]` both times. **`STATUS_M2.md` and
`STATUS_M3.md` are now corrected** (old numbers struck through and kept for the
audit trail, not deleted; corrected tables added; CLAUDE.md carries the lesson
for future sessions). The conclusion doesn't change (accuracy still holds flat
through 50c then drops at semitone; allied-pair still correctly dropped) but
several per-raga numbers do — most notably **Rītigauḷa moved from "essentially
flat" to the 5th-largest degradation**, which changes what you can say about it
musically. Read the correction notes in both status files before using those
numbers anywhere else.

**All 6 notebooks verified running clean on a fresh kernel this session:**
`00_data_audit` (13.6s), `01_corpus_build` (~107-115s), `02_quantisation_study`
(~99-101s, ran 3 times total for the determinism check), `03_allied_pair` (8.4s),
`04_generator` (~7 min, includes M4+M5), `05_report` (7s). Zero errors across
every run.

**`requirements.txt` written**, pinning the exact versions this project was
verified against: numpy 2.4.6, pandas 2.3.3, scikit-learn 1.9.0, scipy 1.18.0,
matplotlib 3.11.0, torch 2.12.1, nbformat 5.11.0, nbclient 0.11.0, ipykernel 7.3.0.

**Limitations section** (in the report notebook, §5) covers: artist confound,
composition confound, the never-run leave-one-artist-out allied-pair check, mix-
vs-vocal pitch source difference, residual sustained octave-tracking errors
(found during M4), tiny corpus / single dataset, generator quantisation blockiness,
and the CC BY-NC-SA 4.0 licence.

## Numbers (also in `artifacts/numbers.json["m6"]`)

- `status`: "report assembled"
- `milestones_present`: [m0, m1, m2, m3, m4, m5]
- `requirements_pinned`: true

## Update (2026-08-29): interpretation sections written, CLAUDE.md corrected

The owner told me directly he does not have Carnatic music background —
CLAUDE.md had wrongly assumed the opposite ("strong on Carnatic/Sanskrit music
theory... he is the musical-judgement authority"), which is why the report
originally left `> **Your read:**` placeholders for him to fill in. Corrected
CLAUDE.md's owner-background section and its "notebooks don't ghost-write
interpretation" rule to reflect reality: **musical interpretation is now
researched from documented Carnatic theory (academic sources, cited inline)
rather than personal ear-training.**

A research pass (prioritising CompMusic-affiliated academic sources — the same
research group that built the Saraga dataset) found per-raga theory
characterizations for the ragas in the M2 degradation ranking and the M4/M5
generator pair, and this has now been written into `notebooks/05_report.ipynb`
(re-executed clean, 7.9s):

- **§2** cites Krishna & Ishwar (2012, CompMusic workshop) as the theoretical
  grounding for the core hypothesis, then checks the degradation ranking
  against documented per-raga gamaka characterizations: a partial match
  (Mōhanaṁ, Sindhubhairavi, Harikāmbhōji line up with theory) with one clear,
  stated-not-hidden counterexample (**Sāvēri** is documented as equally
  gamaka-dependent as Mōhanaṁ, yet empirically improves at coarse resolution —
  no source explains this) and one honest gap (Kamās has no gamaka-specific
  documentation found).
- **§3** notes the allied-pair drop didn't need musical expertise in the first
  place — it was an exhaustive, objective balance-criterion search, not a
  theory judgement call.
- **§4/5** proposes a hedged hypothesis for the Karaharapriya/Mōhanaṁ
  generation asymmetry: Karaharapriya's gamaka vocabulary spans 7 scale
  degrees vs. Mōhanaṁ's 5, which may give a folded pitch-class histogram less
  structural room to separate Mōhanaṁ from a 7-note raga — explicitly labelled
  a hypothesis, not a verified finding.

Every claim above is sourced (URLs inline in the notebook) and hedged where
documentation was thin, missing, or contradicted the data — no invented
gamaka characterizations.

## What's blocked / decision needed from you

None blocking submission. Sāvēri's reversed degradation pattern remains an
open, unexplained disagreement between documented theory and this result
(stated as such in §2, not resolved) — worth a look if you want to dig further,
but not required for submission.

## What's next

**Done.** M0–M6 complete: notebooks run clean, the accuracy-vs-resolution
quantisation curve is the headline result, the allied-pair question is honestly
closed, the generator PoC is evaluated with disclosed caveats, the
interpretation sections are written and sourced, and the limitations section is
honest rather than glossed over. This is a submittable project. Remaining work
is a read-through of `05_report.ipynb` and the corrected `STATUS_M2.md`/
`STATUS_M3.md` numbers before submission — nothing left for me to generate.
