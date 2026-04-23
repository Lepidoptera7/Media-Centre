import os
import pandas as pd
import tvdb_v4_official

movies_csv = r"C:\Not_Work\notworknotgames\cyber sec\home server\movies\movies_data.csv"
cast_csv = r"C:\Not_Work\notworknotgames\cyber sec\home server\movies\cast_data.csv"

with open(r"C:\Not_Work\notworknotgames\cyber sec\home server\TVDB.txt", "r") as f:
    api_key = f.read().strip()

tvdb = tvdb_v4_official.TVDB(api_key)

lookup_path = r"C:\Not_Work\notworknotgames\cyber sec\home server\movies\movie_lookup.csv"
df_lookup = pd.read_csv(lookup_path).dropna(subset=["tvdb_id"])
#df_lookup = df_lookup.dropna(subset=["tvdb_id"])

# Existing data
input_ids = df_lookup["tvdb_id"].astype(int).tolist()
existing_csv = r"C:\Not_Work\notworknotgames\cyber sec\home server\movies\movies_data.csv"

if os.path.exists(existing_csv):
    df_existing = pd.read_csv(existing_csv)
    processed = set(df_existing["id"].dropna().astype(int).unique())
else:
    processed = set()

to_process_df = df_lookup[~df_lookup["tvdb_id"].isin(processed)]

all_movies = []
all_cast = []

for _, row in to_process_df.iterrows():
    movie_id = row["tvdb_id"]
    movie_name = row["input_name"]
    print(f"Processing: {movie_name}")

    try:
        # --- fetch data ---
        movies = tvdb.get_movie_extended(movie_id)
        cast = movies["characters"]

        #print(movies.keys())
        #print()
        #print(cast)

        df_movies = pd.json_normalize(movies)[["id",
                                              "name",
                                              "slug",
                                              "runtime",
                                              "year",
                                              "genres",
                                              "budget",
                                              "boxOffice",
                                              "originalCountry",
                                              "originalLanguage",
                                              "lists",
                                              "status.recordType"
                                             ]]

        df_movies["genres"] = df_movies["genres"].apply(
                                                        lambda x: ", ".join(g["name"] for g in x) if isinstance(x, list) else None
                                                        )
        
        df_movies = df_movies.rename(columns={"lists": "franchise"})
        df_movies["franchise"] = df_movies["franchise"].apply(
                                                              lambda x: x[0]["name"] if isinstance(x, list) and len(x) > 0 else None
                                                              )
        if "acquired" not in df_movies.columns:
            df_movies.insert(2, "acquired", False)
        all_movies.append(df_movies)


        # --- CAST & CREW ---
        df_cast = pd.json_normalize(cast)[[
            "id", "peopleId", "movieId", "personName", "name", "peopleType"
        ]]
        all_cast.append(df_cast)

    except Exception as e:
        print(f"Failed for {movie_name}: {e}")

if all_movies:
    df_movies_all = pd.concat(all_movies, ignore_index=True)
    df_movies_all.to_csv(movies_csv, mode="a", header=not os.path.exists(movies_csv), index=False)
else:
    print("Movies table is up to date.")

if all_cast:
    df_cast_all = pd.concat(all_cast, ignore_index=True)
    df_cast_all.to_csv(cast_csv, mode="a", header=not os.path.exists(cast_csv), index=False)
else:
    print("Cast table is up to date.")

print("Done")
