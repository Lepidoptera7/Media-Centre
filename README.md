# Home Media Centre

## Overview

A personal project to learn Python and PostgreSQL by building a small data pipeline for movies and TV shows. Data is fetched from TheTVDB.com and stored in structured PostgreSQL tables.

## Features

* Python scripts for data ingestion and updates
* PostgreSQL tables for movies, series, episodes, and cast
* Lookup system for resolving titles to TVDB IDs
* Logging for tracking updates and errors

## Tech Stack

* Python
* PostgreSQL
* psycopg2
* rapidfuzz
* dotenv
* datetime
* os
* re
* tvdb_v4_official

## Setup

1. Create a `.env` file:

   ```
   SQL_DB=your_db
   SQL_USER=your_user
   SQL_PWD=your_password
   TVDB_API_KEY=your_api_key
   MOVIE_DIR=path_to_data
   LOG_DIR=path_to_logs
   ```

2. Create database tables using provided SQL schema.

## Updating Databases

Run the main updater from the project root:

```bash
python main.py
```

Choose movies, series, or all when prompted. You can also skip the prompt:

```bash
python main.py movies
python main.py series
python main.py all
```

Each workflow runs a lookup table update first, then pulls data from thetvdb.com and finally updates the acquired status from your storage folders.
Personalise your own list of movies and TV shows via the text files and have fun.

## Future

* Metabase dashboard for data analysis
* Expand to organise books
* Add music library support

## Purpose

This project is for learning and experimenting with Python data workflows and relational database design.

---

Constructive criticism is appreciated, but movie/TV show recommendations are even better.
