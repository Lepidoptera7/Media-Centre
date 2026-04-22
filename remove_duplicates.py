import pandas as pd
import os

# --- file paths ---
files = {
    "series": r"/mnt/58280C00280BDBBE/db_tvdb/tv_series/series_data.csv",
    "episodes": r"/mnt/58280C00280BDBBE/db_tvdb/tv_series/episodes_data.csv",
    "cast": r"/mnt/58280C00280BDBBE/db_tvdb/tv_series/cast_data.csv"
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