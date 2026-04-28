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
                id, name, slug, genres, year, franchise, original_country, original_language, acquired
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            data.get("id"),
            data.get("name"),
            data.get("slug"),
            genres,
            data.get("year"),
            franchise,
            data.get("originalCountry"),
            data.get("originalLanguage"),
            data.get("status", {}).get("recordType"),
            False
        ))
        print("Updated: ", lookup[series_id])
        print()
        log(f"UPDATED: {lookup[series_id]} (no match)")


        # --- cast ---
        for c in data.get("characters", []):
            cur.execute("""
                INSERT INTO series_cast (
                    id, people_id, series_id,
                    person_name, role_name, people_type
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                c.get("id"),
                c.get("peopleId"),
                series_id,
                c.get("personName"),
                c.get("name"),
                c.get("peopleType")
            ))

        # --- episodes ---
        for e in data.get("episodes", []):
            cur.execute("""
                INSERT INTO series_episodes (
                    id, series_id, name, aired, overview
                    number, absolute_number, season_number, year
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                c.get("id"),
                series_id,
                c.get("name"),
                c.get("aired"),
                c.get("overview"),
                c.get("number"),
                c.get("absoluteNumber"),
                c.get("seasonNumber"),
                c.get("year")
            ))

    except Exception as e:
        print(f"Failed: {lookup[movie_id]} → {e}")
        print()
        log(f"FAILED UPDATE: {lookup[movie_id]} (no match)")
conn.commit()
cur.close()
conn.close()

print("Done")


