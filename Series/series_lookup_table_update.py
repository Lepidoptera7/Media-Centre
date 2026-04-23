import pandas as pd
import tvdb_v4_official
import os

# --- paths ---
lookup_path = r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_lookup.csv"
series_list_path = r"/mnt/58280C00280BDBBE/Media-Centre/Series/series_list.txt"
api_key_path = r"/mnt/58280C00280BDBBE/Media-Centre/tvdb.txt"

# --- load API key ---
with open(api_key_path, "r") as f:
    api_key = f.read().strip()

tvdb = tvdb_v4_official.TVDB(api_key)

# --- load or create lookup table ---
if os.path.exists(lookup_path):
    df_lookup = pd.read_csv(lookup_path)
else:
    df_lookup = pd.DataFrame(columns=["input_name", "matched_name", "tvdb_id"])

# --- ensure columns exist ---
for col in ["input_name", "matched_name", "tvdb_id"]:
    if col not in df_lookup.columns:
        df_lookup[col] = None

# --- load new names ---
with open(series_list_path, "r", encoding="utf-8") as f:
    new_names = [line.strip() for line in f if line.strip()]

# --- add new names (no duplicates) ---
existing_names = set(df_lookup["input_name"].astype(str))

for name in new_names:
    if name not in existing_names:
        df_lookup.loc[len(df_lookup)] = [name, None, None]

# --- force dtype AFTER all inserts ---
df_lookup["tvdb_id"] = pd.to_numeric(df_lookup["tvdb_id"], errors="coerce").astype("Int64")

# --- resolver ---
def resolve_tvdb_id(tvdb, name):
    results = tvdb.search(name)
    if not results:
        return None, None

    # exact match
    for r in results:
        if r.get("name", "").lower() == name.lower():
            return r["tvdb_id"], r.get("name")

    # fallback
    r = results[0]
    return r["tvdb_id"], r.get("name")

# --- update missing rows only ---
mask = df_lookup["tvdb_id"].isna()

for idx in df_lookup[mask].index:
    name = df_lookup.loc[idx, "input_name"]

    try:
        tvdb_id, matched_name = resolve_tvdb_id(tvdb, name)

        df_lookup.loc[idx, "tvdb_id"] = int(tvdb_id) if tvdb_id else None
        df_lookup.loc[idx, "matched_name"] = matched_name

        print(f"Updated: {name} → {matched_name} ({tvdb_id})")

    except Exception as e:
        print(f"Failed: {name} → {e}")

# --- save ---
df_lookup.to_csv(lookup_path, index=False, encoding="utf-8-sig")

print("Lookup table updated.")
