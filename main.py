import argparse
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

WORKFLOWS = {
    "movies": [
        ("Update movie lookup table", BASE_DIR / "Movies" / "movie_lookup_table_update.py"),
        ("Update movies database", BASE_DIR / "Movies" / "movies.py"),
        ("Update acquired movies", BASE_DIR / "Movies" / "movies_acquired.py"),
    ],
    "series": [
        ("Update series lookup table", BASE_DIR / "Series" / "series_lookup_table_update.py"),
        ("Update series database", BASE_DIR / "Series" / "series.py"),
        ("Update acquired series", BASE_DIR / "Series" / "series_acquired.py"),
    ],
}


def run_script(label, script_path):
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    print(f"\n=== {label} ===")
    result = subprocess.run([sys.executable, str(script_path)], cwd=BASE_DIR)

    if result.returncode != 0:
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")


def run_workflow(media_type):
    for label, script_path in WORKFLOWS[media_type]:
        run_script(label, script_path)


def prompt_media_type():
    choices = {
        "1": "movies",
        "2": "series",
        "3": "all",
        "m": "movies",
        "s": "series",
        "a": "all",
    }

    print("Choose update type:")
    print("1. Movies")
    print("2. Series")
    print("3. All")

    while True:
        choice = input("> ").strip().lower()
        media_type = choices.get(choice)

        if media_type:
            return media_type

        print("Invalid choice. Enter 1, 2, 3, m, s, or a.")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the Media Centre database update workflow."
    )
    parser.add_argument(
        "media_type",
        nargs="?",
        choices=["movies", "series", "all"],
        help="Which database workflow to run.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    media_type = args.media_type or prompt_media_type()

    try:
        if media_type == "all":
            run_workflow("movies")
            run_workflow("series")
        else:
            run_workflow(media_type)
    except Exception as exc:
        print(f"\nUpdate stopped: {exc}")
        return 1

    print("\nAll requested updates complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
