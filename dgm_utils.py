"""Shared pipeline for the raga pitch-contour study: loaders, cents conversion,
cleaning, section-label handling, and CV-split helpers. Notebooks orchestrate;
this module does the mechanical work so it isn't copy-pasted per notebook.

Verified facts this module encodes (see CLAUDE.md for the decisions behind them):
- frame rate ~225 Hz; unvoiced = freq 0.
- sections-manual-p.txt only (plain adds zero coverage, M0).
- sections are 4 tab cols: start, const, DURATION, label. end = start + duration.
- raaga can be an empty list; use album_artists, not the differently-shaped artists.
"""
import glob
import json
import os
import re
import unicodedata

import numpy as np

FRAME_RATE_MIX_HZ = 225.0        # verified: *.pitch.txt
FRAME_RATE_VOCAL_HZ = 344.531    # verified: *.pitch-vocal.txt -- DIFFERENT hop size,
                                  # NOT 225 Hz. Always measure per-file (see read_pitch);
                                  # these two constants are documentation, not used directly.
OCTAVE_CLEAN_WINDOW = 51
OCTAVE_CLEAN_THRESH = 900.0


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def load_meta(json_path):
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def raga_of(meta):
    lst = meta.get("raaga") or []
    return lst[0].get("name") if lst else None


def artist_of(meta):
    lst = meta.get("album_artists") or []
    return lst[0].get("name") if lst else None


def composition_id_of(meta):
    """Stable composition identity: MusicBrainz work id, else work title, else track title.
    Two recordings sharing this id are the same kriti -> composition-confound risk."""
    works = meta.get("work") or []
    if works:
        return works[0].get("mbid") or works[0].get("title")
    return meta.get("title")


def composition_title_of(meta):
    works = meta.get("work") or []
    return works[0].get("title") if works else meta.get("title")


# ---------------------------------------------------------------------------
# Pitch / tonic
# ---------------------------------------------------------------------------

def read_tonic(folder):
    tf = glob.glob(os.path.join(folder, "*.ctonic.txt"))
    if not tf:
        return None
    return float(open(tf[0], encoding="utf-8").read().split()[0])


def read_pitch(folder, prefer_vocal=True):
    """Returns (t, f, source, frame_rate_hz) where source is 'vocal' or 'mix'.
    frame_rate_hz is MEASURED from the time column, not assumed -- pitch-vocal.txt
    runs at ~344.5 Hz, pitch.txt at ~225 Hz; a shared constant would silently corrupt
    duration/minute math for whichever source it doesn't match.
    Returns (None, None, None, None) if neither file exists."""
    if prefer_vocal:
        pf = glob.glob(os.path.join(folder, "*.pitch-vocal.txt"))
        if pf:
            data = np.loadtxt(pf[0])
            t = data[:, 0]
            return t, data[:, 1], "vocal", 1.0 / np.median(np.diff(t))
    pf = glob.glob(os.path.join(folder, "*.pitch.txt"))
    if not pf:
        return None, None, None, None
    data = np.loadtxt(pf[0])
    t = data[:, 0]
    return t, data[:, 1], "mix", 1.0 / np.median(np.diff(t))


def hz_to_cents(freq, tonic):
    return 1200.0 * np.log2(freq / tonic)


def fold_cents(cents):
    return np.mod(cents, 1200.0)


def clean_octave_outliers(cents, win=OCTAVE_CLEAN_WINDOW, thresh=OCTAVE_CLEAN_THRESH):
    """Drop frames whose cents value sits > thresh from the local median over `win` frames."""
    if len(cents) == 0:
        return cents
    if len(cents) < win:
        med = np.median(cents)
        return cents[np.abs(cents - med) < thresh]
    from numpy.lib.stride_tricks import sliding_window_view
    pad = win // 2
    padded = np.pad(cents, pad, mode="edge")
    local_med = np.median(sliding_window_view(padded, win), axis=1)
    keep = np.abs(cents - local_med) < thresh
    return cents[keep]


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def section_file(folder):
    """-p only (M0: plain sections-manual.txt is a strict subset, merging adds nothing)."""
    g = glob.glob(os.path.join(folder, "*.sections-manual-p.txt"))
    return g[0] if g else None


def read_sections(path):
    """4-col tab file: start, const, DURATION, label. Returns [(start, dur, label), ...]."""
    out = []
    for line in open(path, encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4:
            continue
        try:
            start, dur = float(parts[0]), float(parts[2])
        except ValueError:
            continue
        out.append((start, dur, parts[3].strip()))
    return out


def is_alap(label):
    l = label.lower()
    return ("ālāp" in l or "alap" in l) and "violin" not in l


def is_vocal_section(label):
    l = label.lower()
    return ("violin" not in l) and ("tani" not in l) and ("tāni" not in l)


def _strip_diacritics(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalize_label(s):
    """Lowercase, diacritics stripped, non-alnum removed. Used to compare labels/raga
    names across the diacritic-inconsistent annotation vocabulary."""
    return re.sub(r"[^a-z0-9]", "", _strip_diacritics(s).lower())


_CANONICAL_SECTION_TYPES = {
    "pallavi", "anupallavi", "caranam", "vocalalap", "violinalap", "kalpanasvara",
    "nereval", "taniavartana", "muktayisvara", "cittasvara", "tanam", "jatisvara",
    "sloka", "verse", "melkalam", "tisram", "ragamalikasvara", "viruttam", "",
}
_RAGA_SUFFIX_PREFIXES = ("caranam", "anupallavi", "pallavi")


def classify_section_label(label, track_raga):
    """Classify a section label against the track's own raga.
    Returns (kind, detail) where kind in {"canonical", "named_other_raga", "unrecognized"}.
    "named_other_raga": label is "<Caranam/Anupallavi/Pallavi> <raga-name>" and the
    raga-name suffix does NOT match the track's own raga -> the section is rendered in
    a different raga and is contaminated training data for the track's nominal label.
    """
    norm = normalize_label(label)
    if norm in _CANONICAL_SECTION_TYPES:
        return "canonical", None
    track_norm = normalize_label(track_raga or "")
    for prefix in _RAGA_SUFFIX_PREFIXES:
        if norm.startswith(prefix) and norm != prefix:
            suffix = norm[len(prefix):]
            if suffix == track_norm:
                return "canonical", None  # verbose but matches the track's own raga
            return "named_other_raga", suffix
    return "unrecognized", norm


# ---------------------------------------------------------------------------
# Windowing
# ---------------------------------------------------------------------------

def make_windows(arr, win_frames, hop_frames):
    """Non-overlapping (or hop<win for overlap) fixed-length windows over a 1-D array.
    Drops a trailing partial window. Returns a list of 1-D arrays, each length win_frames."""
    n = len(arr)
    out = []
    start = 0
    while start + win_frames <= n:
        out.append(arr[start:start + win_frames])
        start += hop_frames
    return out


# ---------------------------------------------------------------------------
# Grouped splitting
# ---------------------------------------------------------------------------

def group_diversity(manifest_df, group_col):
    """Per-raga count of distinct values of group_col (e.g. 'artist' or 'composition_id')."""
    return manifest_df.groupby("raga")[group_col].nunique()


def composition_grouped_feasible(manifest_df, raga, min_groups=3):
    sub = manifest_df[manifest_df.raga == raga]
    return sub.composition_id.nunique() >= min_groups


def safe_filename(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


# ---------------------------------------------------------------------------
# M2: quantisation-resolution features + grouped CV
# ---------------------------------------------------------------------------

RESOLUTIONS_CENTS = [10, 20, 50, 100]  # 10c stands in for "continuous"; 100c = semitone
RESOLUTION_LABELS = {10: "continuous (10c)", 20: "20c", 50: "50c", 100: "semitone (100c)"}


def recover_fps(n_frames, minutes):
    """fps used when a segment's .npy was written, recovered exactly from the stored
    frame count and duration (minutes = n_frames/fps/60 at write time) -- avoids
    needing to reopen the original recording or add a schema column retroactively."""
    return n_frames / (minutes * 60.0)


def histogram_feature(folded_cents, bin_width):
    """Normalized pitch-class histogram over [0,1200) at the given bin width (cents).
    This IS the quantisation step: bin_width sweeps continuous (fine bins) -> semitone
    (100c bins). Returns a probability vector (sums to 1); zero vector if input empty."""
    edges = np.arange(0, 1200 + bin_width, bin_width)
    hist, _ = np.histogram(folded_cents, bins=edges)
    total = hist.sum()
    return hist / total if total > 0 else hist.astype(float)


def make_group_cv(labels, groups, max_splits=5):
    """StratifiedGroupKFold sized to the data: n_splits = min(max_splits, the smallest
    per-class group count), so no fold is starved of a class's only group. Returns
    (splitter, n_splits)."""
    from sklearn.model_selection import StratifiedGroupKFold
    import pandas as pd
    df = pd.DataFrame({"label": labels, "group": groups})
    min_groups_per_class = df.groupby("label")["group"].nunique().min()
    n_splits = max(2, min(max_splits, int(min_groups_per_class)))
    return StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=0), n_splits
