from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path
import psycopg2
from rapidfuzz import fuzz
import re

load_dotenv()

run_id = datetime.now().strftime("%Y%m%d_%H%M")

mov_dir = os.getenv("MOVIE_DIR")

log_dir = os.getenv("MV_LOG_DIR")
log_path = os.path.join(log_dir + f"/{run_id}_MV_AQ.txt")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# --- PostgreSQL connection ---
conn = psycopg2.connect(
    dbname=os.getenv("SQL_DB"),
    user=os.getenv("SQL_USER"),
    password=os.getenv("SQL_PWD"),
    host="localhost",
    port="5432"
)
cur = conn.cursor()


def get_folder_names(directory_path):
    path = Path(directory_path)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory_path}")

    return [item.name for item in path.iterdir() if item.is_dir()]

directory = os.getenv("MV_STOR")

folders = get_folder_names(directory)


def normalize(s):
    return re.sub(r'[^a-z0-9 ]', '', s.lower())


def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {msg}\n")


def choose_lookup_match(folder_name, lookup_rows, acquired_ids=None):
    acquired_ids = acquired_ids or set()
    folder_n = normalize(folder_name)
    scored = []

    for input_name, matched_name, tvdb_id in lookup_rows:
        score = fuzz.ratio(folder_n, normalize(input_name))
        scored.append((score, input_name, matched_name, tvdb_id))

    scored.sort(reverse=True, key=lambda row: row[0])
    best_score, input_name, matched_name, tvdb_id = scored[0]

    if tvdb_id in acquired_ids:
        return None, None, None

    scored = [row for row in scored if row[3] not in acquired_ids]
    if not scored:
        return None, None, None

    best_score, input_name, matched_name, tvdb_id = scored[0]

    if best_score >= 90:
        print(f"AUTO: {folder_name} -> {input_name} ({best_score:.0f}%)")
        log(f"AUTO: {folder_name} -> {input_name} ({best_score:.0f}%) acquired")
        return input_name, matched_name, tvdb_id

    start = 0

    while True:
        batch = scored[start:start+5]

        if not batch:
            print("No more lookup matches.")
            print()
            log(f"SKIPPED: {folder_name} (no lookup match)")
            return None, None, None

        print(f"\nManual selection for: {folder_name}")
        for i, (score, input_name, matched_name, tvdb_id) in enumerate(batch):
            display_name = matched_name or input_name
            print(f"{i+1}. {input_name} -> {display_name} ({tvdb_id}) [{score:.0f}%]")

        print("\nOptions: 1-5 select | n = next 5 | s = skip")

        choice = input("> ").strip().lower()

        if choice == "s":
            print(f"SKIPPED: {folder_name}")
            print()
            log(f"SKIPPED: {folder_name}")
            return None, None, None

        if choice == "n":
            start += 5
            continue

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(batch):
                _, input_name, matched_name, tvdb_id = batch[idx]
                log(f"MANUAL: {folder_name} -> {input_name}")
                return input_name, matched_name, tvdb_id

        print("Invalid selection")


def resolve_acquired():
    cur.execute("""
        SELECT input_name, matched_name, tvdb_id
        FROM movie_lookup
        WHERE tvdb_id IS NOT NULL
    """)
    lookup_rows = cur.fetchall()

    if not lookup_rows:
        print("No resolved movie_lookup rows found.")
        log("No resolved movie_lookup rows found.")
        return

    cur.execute("""
        SELECT id
        FROM movies
        WHERE acquired = TRUE
    """)
    acquired_ids = {row[0] for row in cur.fetchall()}

    for folder_name in folders:
        try:
            input_name, matched_name, tvdb_id = choose_lookup_match(
                folder_name,
                lookup_rows,
                acquired_ids
            )

            if tvdb_id is None:
                continue

            cur.execute("""
                UPDATE movies
                SET acquired = TRUE
                WHERE id = %s
            """, (tvdb_id,))

            if cur.rowcount == 0:
                print(f"No movie row found for: {folder_name} ({tvdb_id})")
                log(f"NO MOVIE ROW: {folder_name} -> {input_name} ({tvdb_id})")
                continue

            display_name = matched_name or input_name
            print(f"ACQUIRED: {folder_name} -> {display_name} ({tvdb_id})")
            print()
            log(f"ACQUIRED: {folder_name} -> {display_name} ({tvdb_id})")
            acquired_ids.add(tvdb_id)

        except Exception as e:
            conn.rollback()
            print(f"Failed: {folder_name} -> {e}")
            print()
            log(f"FAILED: {folder_name} | ERROR: {e}")


resolve_acquired()

conn.commit()
cur.close()
conn.close()

print("Acquisition up to date!")
