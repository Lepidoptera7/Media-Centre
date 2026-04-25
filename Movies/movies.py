from dotenv import load_dotenv
import os
import psycopg2
import tvdb_v4_official

# --- setup ---
load_dotenv()
api_key = os.getenv("TVDB_API_KEY")
mov_dir = os.getenv("MOVIE_DIR")

tvdb = tvdb_v4_official.TVDB(api_key)

conn = psycopg2.connect(
    dbname=os.getenv("SQL_DB"),
    user=os.getenv("SQL_USER"),
    password=os.getenv("SQL_PWD"),
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# --- get IDs to process ---
cur.execute("""
    SELECT input_name, tvdb_id
    FROM movie_lookup
    WHERE tvdb_id IS NOT NULL
""")
rows = cur.fetchall()

lookup = {}
for name, tvdb_id in rows:
    lookup.setdefault(tvdb_id, name)
all_ids = set(lookup.keys())

cur.execute("SELECT id FROM movies")
processed = {row[0] for row in cur.fetchall()}

to_process = all_ids - processed

def clean_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None

# --- process ---
for movie_id in to_process:
    print(f"Processing: {lookup.get(movie_id, movie_id)}")

    try:
        data = tvdb.get_movie_extended(movie_id)

        # --- movie ---
        genres = ", ".join(g["name"] for g in data.get("genres", [])) if data.get("genres") else None
        lists = data.get("lists") or []
        franchise = lists[0]["name"] if len(lists) > 0 else None

        cur.execute("""
            INSERT INTO movies (
                id, name, slug, runtime, year, genres,
                budget, box_office, original_country,
                original_language, franchise, record_type, acquired
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

        # --- cast ---
        for c in data.get("characters", []):
            cur.execute("""
                INSERT INTO movies_cast (
                    id, people_id, movie_id,
                    person_name, role_name, people_type
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                c.get("id"),
                c.get("peopleId"),
                movie_id,
                c.get("personName"),
                c.get("name"),
                c.get("peopleType")
            ))

    except Exception as e:
        print(f"Failed: {lookup[movie_id]} → {e}")

conn.commit()
cur.close()
conn.close()

print("Done")