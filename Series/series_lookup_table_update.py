from datetime import datetime
from dotenv import load_dotenv
import os
import psycopg2
from rapidfuzz import fuzz
import re
import tvdb_v4_official

# --- setup ---
load_dotenv()

run_id = datetime.now().strftime("%Y%m%d_%H%M")


ser_dir = os.getenv("SERIES_DIR")
series_list_path = os.path.join(ser_dir + "/series_list.txt")

log_dir = os.getenv("SR_LOG_DIR")
log_path = os.path.join(log_dir + f"/{run_id}_LU.txt")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

api_key = os.getenv("TVDB_API_KEY")
assert api_key is not None, "Missing API Key"

tvdb = tvdb_v4_official.TVDB(api_key)

# --- PostgreSQL connection ---
conn = psycopg2.connect(
    dbname = os.getenv("SQL_DB"),
    user = os.getenv("SQL_USER"),
    password = os.getenv("SQL_PWD"),
    host = "localhost",
    port = "5432",
)

cur = conn.cursor()

def clean_text(s):
    return s.replace("\ufeff", "").strip() if s else s

def normalize(s):
    return re.sub(r'[^a-z0-9 ]', '', s.lower())

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime("%Y-%m-%d %H:%M")}] {msg}\n\n")

# --- load new names ---
with open(series_list_path, "r", encoding="utf-8") as f:
    new_names = []
    for line in f:
        name = clean_text(line)
        if name:
            new_names.append(name)

# --- Insert new names, ignore duplicates ---
for name in new_names:
    cur.execute("""
        INSERT INTO series_lookup (input_name, matched_name, tvdb_id)
        VALUES (TRIM(%s), NULL, NULL)
        ON CONFLICT (input_name) DO NOTHING
    """, (name,))

conn.commit()

def resolve_tvdb_id(tvdb, name):
    results = tvdb.search(name)
    if not results:
        print(f"No results for: {name}")
        log(f"NO MATCH: {name} (no match)")
        return None, None

    name_n = normalize(name)

    # 1. auto-accept high confidence match
    best = None
    best_score = 0

    for r in results:
        candidate = r.get("name", "")
        score = fuzz.ratio(name_n, normalize(candidate))

        if score > best_score:
            best_score = score
            best = r

    if best_score >= 95:
        print(f"AUTO: {name}")
        log(f"AUTO: {name}")
        return best["tvdb_id"], best["name"]

    # 2. manual review (top 5)
    start = 0

    while True:
        batch = results[start:start+5]

        if not batch:
            print("No more results.")
            print()
            log(f"SKIPPED: {name} (no match)")
            return None, None

        print(f"\nManual selection for: {name}")
        for i, r in enumerate(batch):
            print(f"{i+1}. {r.get('name')} ({r.get('tvdb_id')})")

        print("\nOptions: 1-5 select | n = next 5 | s = skip")

        choice = input("> ").strip().lower()

        if choice == "s":
            print(f"SKIPPED: {name}")
            print()
            log(f"SKIPPED: {name} (no match)")
            return None, None

        if choice == "n":
            start += 5
            continue

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(batch):
                r = batch[idx]
                log(f"MANUAL UPDATED: {name}")
                return r["tvdb_id"], r.get("name")
            else:
                print("Invalid selection")
                continue

# --- update missing rows only ---
cur.execute("""
    SELECT input_name
    FROM series_lookup
    WHERE tvdb_id IS NULL
""")

missing_rows = cur.fetchall()

for (name,) in missing_rows:
    try:
        tvdb_id, matched_name = resolve_tvdb_id(tvdb, name)

        if tvdb_id is None:
            print(f"Failed to resolve tvdb_id: {name}")
            print()
            log(f"SKIPPED: {name}")
            continue

        cur.execute("""
            UPDATE series_lookup
            SET tvdb_id = %s,
                matched_name = %s
            WHERE input_name = %s
        """, (tvdb_id, matched_name, name))

        print(f"Updated: {name} → {matched_name} ({tvdb_id})")
        print()
        log(f"UPDATED: {name} → {matched_name} ({tvdb_id})\n")

    except Exception as e:
        conn.rollback()
        print(f"Failed: {name} → {e}")
        print()
        log(f"FAILED: {name} | ERROR: {e}\n")


# --- save & close ---
conn.commit()

cur.close()
conn.close()

print("Series lookup table up to date.")
