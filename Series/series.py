import pandas as pd
import os
import tvdb_v4_official

series_csv = r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_data.csv"
episodes_csv = r"/mnt/58280C00280BDBBE/Media-Centre/Series/episodes_data.csv"
cast_csv = r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_cast_data.csv"

# --- load API key ---
with open(r"/mnt/58280C00280BDBBE/Media-Centre/tvdb.txt", "r") as f:
    api_key = f.read().strip()

tvdb = tvdb_v4_official.TVDB(api_key)

lookup_path = r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_lookup.csv"

df_lookup = pd.read_csv(lookup_path)

# keep only valid rows
df_lookup = df_lookup.dropna(subset=["tvdb_id"])

input_ids = df_lookup["tvdb_id"].astype(int).tolist()

existing_csv = r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_data.csv"

if os.path.exists(existing_csv):
    df_existing = pd.read_csv(existing_csv)
    processed = set(df_existing["id"].dropna().astype(int).unique())
else:
    processed = set()

to_process_df = df_lookup[~df_lookup["tvdb_id"].isin(processed)]

# --- containers ---
all_series = []
all_episodes = []
all_cast = []

# --- loop through series ---
for _, row in to_process_df.iterrows():
    series_id = row["tvdb_id"]
    series_name = row["input_name"]
    print(f"Processing: {series_name}")

    try:
        # --- fetch data ---
        series = tvdb.get_series_extended(series_id)
        episodes = tvdb.get_series_episodes(series_id)
        cast = series["characters"]

        # --- SERIES ---
        df_series = pd.json_normalize(series)[["id", "name", "slug", "genres", "year", "lists"]]

        df_series["genres"] = df_series["genres"].apply(
            lambda x: ", ".join(g["name"] for g in x) if isinstance(x, list) else None
        )

        df_series = df_series.rename(columns={"lists": "franchise"})
        df_series["franchise"] = df_series["franchise"].apply(
            lambda x: x[0]["name"] if isinstance(x, list) and len(x) > 0 else None
        )
        if "acquired" not in df_series.columns:
            df_series.insert(2, "acquired", False)
        all_series.append(df_series)

        # --- EPISODES ---
        df_episodes = (
            pd.json_normalize(episodes)["episodes"]
            .explode()
            .dropna()
            .pipe(pd.json_normalize)[[
                "id", "seriesId", "name", "aired", "overview",
                "number", "absoluteNumber", "seasonNumber", "year"
            ]]
        )
        all_episodes.append(df_episodes)

        # --- CAST ---
        df_cast = pd.json_normalize(cast)[[
            "id", "peopleId", "seriesId", "personName", "name"
        ]]
        all_cast.append(df_cast)

    except Exception as e:
        print(f"Failed for {series_name}: {e}")

# Combine Everything
# Export
if all_series:
    df_series_all = pd.concat(all_series, ignore_index=True)
    df_series_all.to_csv(series_csv, mode="a", header=not os.path.exists(series_csv), index=False)
else:
    print("Series table is up to date.")

if all_episodes:
    df_episodes_all = pd.concat(all_episodes, ignore_index=True)
    df_episodes_all.to_csv(episodes_csv, mode="a", header=not os.path.exists(episodes_csv), index=False)
else:
    print("Episodes table is up to date.")

if all_cast:
    df_cast_all = pd.concat(all_cast, ignore_index=True)
    df_cast_all.to_csv(cast_csv, mode="a", header=not os.path.exists(cast_csv), index=False)
else:
    print("Cast table is up to date.")


print("Done.")
