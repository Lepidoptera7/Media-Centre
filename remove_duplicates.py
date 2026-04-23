import pandas as pd
import os

# --- file paths ---
files = {
    "series": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_data.csv",
    "episodes": r"/mnt/58280C00280BDBBE/Media-Centre/Series/episodes_data.csv",
    "cast": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_cast_data.csv",
    "look_up": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_lookup.csv",
    "list": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_list.txt"
}

for name, path in files.items():
    if not os.path.exists(path):
        print(f"{name}: file not found")
        continue

    df = pd.read_csv(path)

    before = len(df)

    # --- remove duplicates ---
    df = df.drop_duplicates()

    after = len(df)
    removed = before - after

    # --- overwrite file ---
    df.to_csv(path, index=False, encoding="utf-8-sig")

    print(f"{name}: removed {removed} duplicate rows")

print("Done.")