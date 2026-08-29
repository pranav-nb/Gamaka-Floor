# STATUS — Milestone 0: Data Audit & Scope Lock

Ran `notebooks/00_data_audit.ipynb` top-to-bottom on the full local
`D:\sg\saraga1.5_carnatic` tree (249 recordings). All numbers below come from that run;
raw outputs are in `artifacts/coverage_alapana.csv`, `artifacts/coverage_quantisation.csv`,
`artifacts/numbers.json`.

## What was done

**JSON key verification.** `raaga` is a list that can be **empty** — 184/249 recordings
are raga-labelled, 65 are not. `album_artists[0]["name"]` is reliable. `artists` is
nested differently (`artists[0]["artist"]["name"]`) — don't use it as a flat fallback,
it silently returns the wrong shape.

**File inventory.** 197 have `pitch.txt` + `ctonic.txt`; 56 have the cleaner
`pitch-vocal.txt`; 119 have `sections-manual-p.txt`; 73 have `sections-manual.txt`; 117
have `mphrases-manual.txt`.

**Section-file merge question — resolved.** Every recording with a plain
`sections-manual.txt` also has a `-p` file (`has_both == has_plain`, 73 == 73). Alapana
minutes: `-p` alone = 252.6 min across 42 recordings; merged with plain = 252.6 min,
identical; zero recordings gain coverage from the merge. **Decision: use `-p` only,
drop the plain-file merge entirely.** This simplifies M1 (`dgm_utils.py` needs one
section-file rule, not two).

**Alapana coverage (unchanged from CLAUDE.md's table, now verified against disk):**

| Raga | alap min | artists | recs |
|---|---|---|---|
| Karaharapriya | 24.7 | 2 | 2 |
| Mōhanaṁ | 18.9 | 2 | 2 |
| Ṣanmukhapriya | 17.7 | 2 | 2 |
| Bhairavi | 15.0 | 2 | 2 |

Only these four clear ≥15 min AND ≥2 artists. Per-artist breakdown confirms the known
confound: Karaharapriya (KP Nandini 11.8 / V. Shankaranarayanan 12.9) and Mōhanaṁ
(Ashwath Narayanan 9.9 / Sumithra Vasudev 9.0) are genuinely balanced. Bhairavi (Vignesh
Ishwar 14.5 / Sanjay Subrahmanyan 0.6) and Ṣanmukhapriya (Sanjay Subrahmanyan 16.8 /
Akkarai Sisters 0.9) are effectively single-artist. No new candidate raga crossed the
15-min bar — the four-raga alapana set is final.

**Allied-pair search.** Widened the vocal-minutes lens beyond alapana-only (used all
non-violin, non-tani sections per artist) and checked five musically-plausible allied
candidates against the full 96-raga, 184-recording collection:

| Pair | Balance | Verdict |
|---|---|---|
| Suraṭi / Kēdāragauḷa | Suraṭi: 1 artist w/ ≥4min (Ashwath Narayanan 7.1); Kēdāragauḷa: 2 artists (25.4/9.9), no overlap | fails — Suraṭi single-artist |
| Kāṁbhōji / Harikāmbhōji | Kāṁbhōji: 1 artist w/ ≥4min (58.7); Harikāmbhōji: 2 (38.5/11.7); Sanjay dominates both | fails — same lead voice on both sides |
| Ābhōgi / Śrīranjani | both only 1 artist w/ ≥4min | fails — thin on both sides |
| Bēgaḍa / Śankarābharaṇaṁ | Bēgaḍa: 2 (17.0/8.8); Śankarābharaṇaṁ: 1 (15.0) | fails — Śankarābharaṇaṁ single-artist |
| Kalyāṇi / Hamīr kaḷyaṇi | Kalyāṇi: 1 (15.2); Hamīr kaḷyaṇi: 1 (4.5) | fails — both single-artist |

**No candidate pair has ≥2 well-represented artists on both sides.** I widened the
scan to every raga with ≥2 artists each contributing ≥4 min of vocal material (18
ragas qualify: Bhairavi, Ṣanmukhapriya, Karaharapriya, Mōhanaṁ, Kamās, Harikāmbhōji,
Tōḍi, Rītigauḷa, Rāgamālika, Kēdāragauḷa, Kumudakriyā, Bēgaḍa, Behāg, Sindhubhairavi,
Pāḍi, Kānaḍa, Sahānā, Kuntalavarāḷi — full list in `coverage_quantisation.csv`), then
checked musical adjacency among them by ear/theory. None of the well-balanced ragas in
that list are close allied pairs (shared note-set, differing gamaka) with each other —
the strongest theory-adjacent pairs I could construct (above) all lose to the balance
constraint. **Recommendation: drop the allied-pair framing per spec §3/M0, make the
point through the quantisation curve alone.** M3 becomes the short documented-drop
notebook per spec.

**Quantisation inventory.** 184 raga-labelled recordings with usable pitch+tonic, 96
distinct ragas, 42 ragas clear ≥2 recordings from ≥2 artists — plenty for the spine
(spec says run over every raga with ≥2 recordings from ≥2 artists). Top of that list:
Rāgamālika (8 recs/7 artists), Tōḍi (7/7), Saurāṣtraṁ (7/5), Kamās (7/4), Behāg (5/4),
Bhairavi (5/4), Mōhanaṁ (4/4), Ṣanmukhapriya (4/3), Karaharapriya (2/2).

## Numbers (also in `artifacts/numbers.json`)

- 249 recordings total, 184 raga-labelled, 197 with pitch+tonic.
- Section-merge: **no gain**, use `-p` only.
- 4 alapana ragas at ≥15min/≥2artists (Karaharapriya, Mōhanaṁ, Bhairavi, Ṣanmukhapriya);
  only Karaharapriya + Mōhanaṁ are artist-balanced.
- 42 ragas usable for quantisation (≥2 recs, ≥2 artists).
- Allied-pair search: **no balanced pair found** — recommend dropping.

## What's blocked / decision needed from you

1. **Allied-pair: drop it?** My read is yes — no candidate survives the balance
   constraint, per the search above. If you know a specific pair from your own
   listening that I should check with a different criterion (e.g. accepting 1 strong +
   1 weaker artist, or lowering the minute bar), tell me which one and I'll re-run the
   check before M3 instead of writing it up as dropped.
2. **Corpus rebuild scope for M1.** Existing `corpus/` (from your `extractpitch.py`
   prototype) only has the 4 alapana ragas, alapana-only, `-p` sections. For the
   quantisation spine I'll need a second, much larger corpus covering all 42
   usable ragas across **all non-violin vocal sections** (not just alapana) — confirm
   that's the right scope, since it changes what "recording" and "artist balance" mean
   per raga (the table above is vocal-section minutes, not alapana minutes).
3. **`ext.py` / `extractpitch.py`**: these were early prototypes (pre-`dgm_utils.py`).
   I'll fold their logic into `dgm_utils.py` in M1 rather than keep them standalone —
   flag if you want them kept as-is for any reason.

## What's next

On your go-ahead on (1)-(3) above: start M1 — `dgm_utils.py` (loaders, cents
conversion, octave-outlier cleaner, fold, recording-grouped splitter, windower) and
rebuild both corpora (alapana-only for the generator; all-vocal-sections for the
quantisation spine) with per-raga/per-artist minute tables and sanity histograms.
