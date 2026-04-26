from datetime import datetime
from dotenv import load_dotenv
import os
import psycopg2
from rapidfuzz import fuzz
import re
import tvdb_v4_official


# --- setup ---
load_dotenv()

run_id = datetime.now().strftime("%Y%m%d_H%M")

ser_dir = os.getenv("SERIES_DIR")
series_list_path = ser_dir + "/series_list.txt"

log_dir = os.getenv("SR_LOG_DIR")
log_path = os.path.join(log_dir + f"/{run_id}_SR.txt")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

api_key = os.getenv("TVDB_API_KEY")
assert api_key is not None, "Missing API Key"

tvdb = tvdb_v4_official.TVDB(api_key)

# --- PostgreSQL Connection ---
conn = psycopg2.connect(
    dbname = os.getenv("SQL_DB"),
    user = os.getenv("SQL_USER"),
    password = os.getenv("SQL_PWD"),
    host = "localhost",
    port = "5432"
)

cur = conn.cursor()

def clean_text(s):
    return s.replace("\ufeff", "").strip() if s else s

def normalize(s):
    return re.sub(r'[^a-z0-9 ]', '', s.lower())

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime("%Y-%m-%d %H:%M")}] {msg}\n")

# --- get IDs to process ---
cur.execute("""
    SELECT input_name, tvdb_id
    FROM series_lookup
    WHERE tvdb_id IS NOT NULL
""")
rows = cur.fetchall()

lookup = {}
for name, tvdb_id in rows:
    lookup.setdefault(tvdb_id, name)
all_ids = set(lookup.keys())

cur.execute("SELECT id FROM series")
processed = {row[0] for row in cur.fetchall()}

to_process = all_ids - processed

# --- update DB ---
for series_id in to_process:
    print(f"Processing: {lookup.get(series_id, series_id)}")

    try:
        data = tvdb.get_series_extended(series_id)

        # --- series ---
        genres = ", ".join(g["name"] for g in data.get("genres", [])) if data.get("genres") else None
        lists = data.get("lists") or []
        franchise = lists[0]["name"] if len(lists) > 0 else None

        cur.execute("""
            INSERT INTO movies (
                id, name, slug, genres, year, franchise,
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            data.get("id"),
            data.get("name"),
            data.get("slug"),
            data.get("runtime"),
            data.get("year"),
            genres,
            clean_int(data.get("budget")),
            clean_int(data.get("boxOffice")),
            data.get("originalCountry"),
            data.get("originalLanguage"),
            franchise,
            data.get("status", {}).get("recordType"),
            False
        ))
        print("Updated: ", lookup[movie_id])
        print()
        log(f"UPDATED: {lookup[movie_id]} (no match)")











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
