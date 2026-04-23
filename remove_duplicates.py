import pandas as pd
import os

# --- file paths ---
files = {
    #"series": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_data.csv",
    #"episodes": r"/mnt/58280C00280BDBBE/Media-Centre/Series/episodes_data.csv",
    #"series_cast": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_cast_data.csv",
    #"series_look_up": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_lookup.csv",
    #"series_list": r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_list.txt",
    "movie_list": r"/mnt/58280C00280BDBBE/Media-Centre/Movies/movie_list.txt",
    "movie_lookup": r"/mnt/58280C00280BDBBE/Media-Centre/Movies/movie_lookup.csv",
    "movie_cast": r"/mnt/58280C00280BDBBE/Media-Centre/Movies/movies_cast_data.csv",
    "movies": r"/mnt/58280C00280BDBBE/Media-Centre/Movies/movies_data.csv"
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