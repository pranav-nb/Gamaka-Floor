import json, glob, os, re
import numpy as np

ROOT = r"D:\sg\saraga1.5_carnatic"
OUT  = r"D:\DGM\corpus"
RAGAS = {"Karaharapriya", "Mōhanaṁ", "Ṣanmukhapriya", "Bhairavi"}

os.makedirs(OUT, exist_ok=True)

def safe(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")

def read_tonic(folder):
    tf = glob.glob(os.path.join(folder, "*.ctonic.txt"))
    if not tf:
        return None
    return float(open(tf[0], encoding="utf-8").read().split()[0])

def read_sections(folder):
    sf = glob.glob(os.path.join(folder, "*.sections-manual*.txt"))
    if not sf:
        return []
    out = []
    for line in open(sf[0], encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4:
            continue
        try:
            start, dur = float(parts[0]), float(parts[2])
        except ValueError:
            continue
        out.append((start, dur, parts[3].strip()))
    return out

def clean_octave_outliers(cents, win=51, thresh=900):
    """Drop frames that sit more than `thresh` cents from a local median."""
    if len(cents) < win:
        med = np.median(cents)
        return cents[np.abs(cents - med) < thresh]
    # rolling median via cumulative trick would be overkill; use simple pass
    from numpy.lib.stride_tricks import sliding_window_view
    pad = win // 2
    padded = np.pad(cents, pad, mode="edge")
    local_med = np.median(sliding_window_view(padded, win), axis=1)
    keep = np.abs(cents - local_med) < thresh
    return cents[keep]

manifest = []
for meta in glob.glob(os.path.join(ROOT, "**", "*.json"), recursive=True):
    folder = os.path.dirname(meta)
    try:
        m = json.load(open(meta, encoding="utf-8"))
    except Exception:
        continue

    raga = (m.get("raaga") or [{}])[0].get("name")
    if raga not in RAGAS:
        continue

    artist = (m.get("album_artists") or m.get("artists") or [{}])[0].get("name") or "unknown"

    tonic = read_tonic(folder)
    if tonic is None:
        print("no tonic:", folder); continue

    pf = glob.glob(os.path.join(folder, "*.pitch.txt"))
    if not pf:
        print("no pitch:", folder); continue
    data = np.loadtxt(pf[0])
    t, f = data[:, 0], data[:, 1]

    for (start, dur, lab) in read_sections(folder):
        if "ālāp" not in lab.lower() or "violin" in lab.lower():
            continue
        end = start + dur
        seg = (t >= start) & (t < end)
        fseg = f[seg]
        voiced = fseg > 0
        if voiced.sum() < 100:
            continue
        cents = 1200 * np.log2(fseg[voiced] / tonic)
        cents = clean_octave_outliers(cents)
        if len(cents) < 100:
            continue

        name = f"{safe(raga)}__{safe(artist)}__{safe(os.path.basename(folder))[:40]}__{int(start)}.npy"
        np.save(os.path.join(OUT, name), cents.astype(np.float32))
        manifest.append({"raga": raga, "artist": artist,
                         "minutes": len(cents) / 225 / 60, "file": name})

# summary
import pandas as pd
mf = pd.DataFrame(manifest)
mf.to_csv(os.path.join(OUT, "manifest.csv"), index=False)
print(f"\nsaved {len(mf)} alapana segments to {OUT}\n")
print(mf.groupby("raga").agg(mins=("minutes","sum"),
                             artists=("artist","nunique"),
                             segs=("file","count")))
print("\nper-artist minutes (watch for single-artist dominance):")
print(mf.groupby(["raga","artist"]).minutes.sum().round(1))