# STATUS — Milestone 4: Generator v0

Ran `notebooks/04_generator.ipynb` top-to-bottom (CPU, ~6 min). Optional milestone
(spec.md M4); all numbers below are read from `artifacts/numbers.json["m4"]` and the
notebook's own printed output — nothing here is estimated.

## What was done

**Model.** A small conditional GRU language model (`RagaContourGRU`, 56,917 params —
far under the 5–10M cap) over lightly quantised, unfolded, cleaned pitch (cents),
conditioned on raga via an embedding. Trained on the two artist-balanced alapana
ragas only (CLAUDE.md): **Karaharapriya** (KP Nandini + V. Shankaranarayanan) and
**Mōhanaṁ** (Ashwath Narayanan + Sumithra Vasudev).

**Three design decisions made up front, not discovered mid-run:**
1. **AR-over-quantised-pitch chosen directly, not attempted-then-fell-back-from
   diffusion.** This machine is CPU-only (`torch.cuda.is_available() == False`).
   Spec.md explicitly allows picking "whichever trains stably first" without
   requiring the harder option be attempted first when the constraint (no GPU here)
   is known in advance.
2. **Re-extracted contiguous voiced runs from source**, not reused from
   `corpus/*.npy`. The M1 corpus build masks `freq>0` and concatenates survivors —
   correct for M2's order-invariant histogram features, wrong for a sequence model
   (it would splice across dropped unvoiced frames as fake jumps). Re-read
   `pitch-vocal.txt` + `sections-manual-p.txt` directly for just these 4 recordings,
   kept only genuinely time-contiguous voiced runs (single unvoiced frame ends a
   run, no bridging), cleaned octave outliers per-run.
3. **No held-out recording split for training.** Only 2 recordings per raga;
   M5's nearest-neighbour memorisation check is the actual anti-copying safeguard
   for this component, not a train/val split here.

**Data.** 934 windows (2.0 s each, decimated to ~114.8 Hz from the measured ~344.5 Hz
vocal fps) from 712 contiguous voiced runs — 538 Karaharapriya windows (265 KP
Nandini / 273 V. Shankaranarayanan), 396 Mōhanaṁ windows (176 Ashwath Narayanan / 220
Sumithra Vasudev). Quantised to 133-token vocabulary (132 pitch bins @ 25c width over
[-1200, 2100) cents, +1 start token); 0.55% of frames clipped into edge bins.

**Training — divergence check (spec.md's M4 acceptance bar), asserted not eyeballed:**
loss 4.273 → 0.921 over 35 epochs, monotonically decreasing, all finite throughout.
Chance-level loss for a 133-token uniform vocabulary is 4.890 — the trained model
sits well below chance. Loss curve: `artifacts/figures/m4_training_loss.png`.

**Sampling.** 6 raga-conditioned samples per raga generated from scratch (no seed
context — the harder case), 2.0 s each, temperature 0.9. Visual comparison against
real training windows: `artifacts/figures/m4_generated_vs_real.png`. Generated
contours show the same qualitative structure as real ones — held plateaus punctuated
by short gamaka-scale wiggles and occasional level shifts — a plausible PoC result,
not a quantitative match (that's M5's job).

**Data-quality observation (not introduced by M4, worth flagging for the report).**
Some real training windows show single-frame jumps of >1000 cents that
`clean_octave_outliers` doesn't catch — the cleaner targets *isolated* octave
spikes via a local-median filter (CLAUDE.md), not a *sustained* octave-tracking
error that persists long enough to drag the local median with it. One such jump is
visible in the real Karaharapriya panel of `m4_generated_vs_real.png` (~0.25s). The
generator appears to have partially learned this artifact (a similar sharp
excursion appears in a generated Karaharapriya sample) — a real limitation of
training on this corpus, not a generator bug. Belongs in the report's limitations
section alongside the artist confound.

## Numbers (also in `artifacts/numbers.json["m4"]`)

- Model: 1-layer GRU, tok_emb=32, raga_emb=8, hidden=96, 56,917 params, CPU.
- Data: 934 windows (538 Karaharapriya / 396 Mōhanaṁ), 2.0s @ ~114.8 Hz decimated.
- Vocab: 133 tokens (25c bins, [-1200, 2100) cents range).
- Training: 35 epochs, loss 4.273 → 0.921 (chance = 4.890), no divergence.
- Artifacts written: `generator_checkpoint.pt`, `generator_meta.json`,
  `generator_train_windows.npz` (real windows, for M5 reuse), `generator_samples/`
  (12 generated `.npy` files, 6 per raga).

## What's blocked / decision needed from you

None blocking. This is a PoC result only — no quantitative evaluation has run yet.

## What's next

M5 (generator evaluation): pitch-class-histogram distance of generated vs. real
per raga, whether the M2 classifier calls generated samples the right raga, and a
nearest-neighbour memorisation check against `generator_train_windows.npz` (real
windows are already saved specifically so M5 doesn't need to re-extract). If you'd
rather stop here and call the generator a documented PoC without full evaluation,
M0–M4(+M6) is still a complete, submittable project — your call.
