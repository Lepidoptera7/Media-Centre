from dotenv import load_dotenv
import os
import pandas as pd

# --- directory ---
load_dotenv()
mov_dir = os.getenv("MOVIE_DIR")
ser_dir = os.getenv("SERIES_DIR")

# --- file paths ---
files = {
    #"series": ser_dir + "/series_data.csv",
    #"episodes": ser_dir + "/episodes_data.csv",
    #"series_cast": ser_dir + "/series_cast_data.csv",
    #"series_look_up": ser_dir + "/series_lookup.csv",
    #"series_list": ser_dir + "/series_list.txt",
    "movie_list": mov_dir + "/movie_list.txt",
    "movie_lookup": mov_dir + "/movie_lookup.csv",
    "movie_cast": mov_dir + "/movies_cast_data.csv",
    "movies": mov_dir + "/movies_data.csv"
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