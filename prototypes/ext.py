import json, glob, os, re
import pandas as pd

root = r"D:\sg\saraga1.5_carnatic"
rows = []
for meta in glob.glob(os.path.join(root, "**", "*.json"), recursive=True):
    d = os.path.dirname(meta)
    secs = glob.glob(os.path.join(d, "*.sections-manual*.txt"))
    if not secs:
        continue
    try:
        m = json.load(open(meta, encoding="utf-8"))
    except Exception:
        continue
    raga = (m.get("raaga") or [{}])[0].get("name")
    artist = (m.get("album_artists") or m.get("artists") or [{}])[0].get("name")
    for line in open(secs[0], encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 4:
            continue
        start, _, dur, lab = parts[0], parts[1], parts[2], parts[3]
        rows.append({"raga": raga, "artist": artist,
                     "section": lab.strip(), "minutes": float(dur) / 60})

df = pd.DataFrame(rows)
print(len(df), "sections,", df.raga.nunique(), "ragas")
print(df.section.value_counts().head(20))

alap = df[df.section.str.contains("ālāp", case=False, na=False) &
          ~df.section.str.contains("Violin", case=False, na=False)]

tbl = (alap.groupby("raga")
          .agg(mins=("minutes","sum"), artists=("artist","nunique"), tracks=("section","count"))
          .sort_values("mins", ascending=False))
print(tbl.head(15))
print("\nragas with >=2 alapana tracks:", (tbl.tracks >= 2).sum())
print("clearing 15 min AND 2 artists:", tbl.query("mins>=15 and artists>=2").shape[0])