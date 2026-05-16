              Table "public.movie_lookup"
    Column    |  Type  | Collation | Nullable | Default 
--------------+--------+-----------+----------+---------
 input_name   | text   |           | not null | 
 matched_name | text   |           |          | 
 tvdb_id      | bigint |           |          | 
Indexes:
    "movie_lookup_pkey" PRIMARY KEY, btree (input_name)
    "unique_tvdb_id" UNIQUE, btree (tvdb_id) WHERE tvdb_id IS NOT NULL


                    Table "public.movies"
      Column       |  Type   | Collation | Nullable | Default 
-------------------+---------+-----------+----------+---------
 id                | bigint  |           | not null | 
 name              | text    |           |          | 
 slug              | text    |           |          | 
 runtime           | integer |           |          | 
 year              | integer |           |          | 
 genres            | text    |           |          | 
 budget            | bigint  |           |          | 
 box_office        | bigint  |           |          | 
 original_country  | text    |           |          | 
 original_language | text    |           |          | 
 franchise         | text    |           |          | 
 record_type       | text    |           |          | 
 acquired          | boolean |           |          | false
Indexes:
    "movies_pkey" PRIMARY KEY, btree (id)


              Table "public.movies_cast"
   Column    |  Type  | Collation | Nullable | Default 
-------------+--------+-----------+----------+---------
 id          | bigint |           |          | 
 people_id   | bigint |           |          | 
 movie_id    | bigint |           |          | 
 person_name | text   |           |          | 
 role_name   | text   |           |          | 
 people_type | text   |           |          | 
Indexes:
    "idx_cast_unique" UNIQUE, btree (id)


                    Table "public.series"
      Column       |  Type   | Collation | Nullable | Default 
-------------------+---------+-----------+----------+---------
 id                | bigint  |           | not null | 
 name              | text    |           | not null | 
 slug              | text    |           |          | 
 genres            | text    |           |          | 
 year              | integer |           |          | 
 franchise         | text    |           |          | 
 original_country  | text    |           |          | 
 original_language | text    |           |          | 
 acquired          | boolean |           |          | false
Indexes:
    "series_pkey" PRIMARY KEY, btree (id)
    "idx_series_name" btree (name)
Referenced by:
    TABLE "series_cast" CONSTRAINT "series_cast_series_id_fkey" FOREIGN KEY (series_id) REFERENCES series(id)
    TABLE "series_eps" CONSTRAINT "series_eps_seriesid_fkey" FOREIGN KEY (seriesid) REFERENCES series(id)


              Table "public.series_cast"
   Column    |  Type  | Collation | Nullable | Default 
-------------+--------+-----------+----------+---------
 id          | bigint |           | not null | 
 people_id   | bigint |           |          | 
 series_id   | bigint |           |          | 
 person_name | text   |           | not null | 
 role_name   | text   |           |          | 
 people_type | text   |           |          | 
Indexes:
    "series_cast_pkey" PRIMARY KEY, btree (id)
    "idx_series_cast_person_name" btree (person_name)
Foreign-key constraints:
    "series_cast_series_id_fkey" FOREIGN KEY (series_id) REFERENCES series(id)


                 Table "public.series_eps"
     Column     |  Type   | Collation | Nullable | Default 
----------------+---------+-----------+----------+---------
 id             | bigint  |           | not null | 
 seriesid       | bigint  |           |          | 
 name           | text    |           | not null | 
 aired          | date    |           |          | 
 overview       | text    |           |          | 
 number         | integer |           |          | 
 absolutenumber | integer |           |          | 
 seasonnumber   | integer |           |          | 
 year           | integer |           |          | 
Indexes:
    "series_eps_pkey" PRIMARY KEY, btree (id)
    "idx_series_eps_name" btree (name)
Foreign-key constraints:
    "series_eps_seriesid_fkey" FOREIGN KEY (seriesid) REFERENCES series(id)


             Table "public.series_lookup"
    Column    |  Type  | Collation | Nullable | Default 
--------------+--------+-----------+----------+---------
 input_name   | text   |           | not null | 
 matched_name | text   |           |          | 
 tvdb_id      | bigint |           |          | 
Indexes:
    "series_lookup_pkey" PRIMARY KEY, btree (input_name)
    "series_lookup_tvdb_id_idx" UNIQUE, btree (tvdb_id) WHERE tvdb_id IS NOT NULL

