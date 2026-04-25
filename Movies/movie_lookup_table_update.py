from dotenv import load_dotenv
import os
import psycopg2
import tvdb_v4_official

# --- base variables ---
load_dotenv()

mov_dir = os.getenv("MOVIE_DIR")
movie_list_path = mov_dir + "/movie_list.txt"

api_key = os.getenv("TVDB_API_KEY")
assert api_key is not None, "Missing API key"

tvdb = tvdb_v4_official.TVDB(api_key)

# --- PostgreSQL connection ---
conn = psycopg2.connect(
    dbname = os.getenv("SQL_DB"),
    user = os.getenv("SQL_USER"),
    password = os.getenv("SQL_PWD"),
    host = "localhost",
    port = "5432"
)

cur = conn.cursor()

# --- load new names ---
with open(movie_list_path, "r", encoding="utf-8") as f:
    new_names = [line.strip() for line in f if line.strip()]

# --- Insert new names, ignore duplicates ---
for name in new_names:
    cur.execute("""
        INSERT INTO movie_lookup (input_name, matched_name, tvdb_id)
        VALUES (%s, NULL, NULL)
        ON CONFLICT (input_name) DO NOTHING
    """, (name,))

conn.commit()

# --- TVDB resolver ---
def resolve_tvdb_id(tvdb, name):
    try:
        results = tvdb.search(name)
    except Exception:
        return None, None

    if not results:
        return None, None

    # exact match (case-insensitive)
    for r in results:
        if r.get("name", "").lower() == name.lower():
            return r.get("tvdb_id"), r.get("name")

    # fallback to first result
    r = results[0]
    return r.get("tvdb_id"), r.get("name")

# --- update missing rows only ---
cur.execute("""
    SELECT input_name
    FROM movie_lookup
    WHERE tvdb_id IS NULL
""")
missing_rows = cur.fetchall()

for (name,) in missing_rows:
    try:
        tvdb_id, matched_name = resolve_tvdb_id(tvdb, name)

        cur.execute("""
            UPDATE movie_lookup
            SET tvdb_id = %s,
                matched_name = %s
            WHERE input_name = %s
        """, (tvdb_id, matched_name, name))

        print(f"Updated: {name} → {matched_name} ({tvdb_id})")

    except Exception as e:
        print(f"Failed: {name} → {e}")

# --- save & close ---
conn.commit()

cur.close()
conn.close()

print("Lookup table updated.")


