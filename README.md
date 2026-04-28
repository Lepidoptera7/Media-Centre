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

2. Create database tables using provided SQL scripts.

## Future

* Expand to organise books
* Add music library support

## Purpose

This project is for learning and experimenting with Python data workflows and relational database design.

---

Constructive criticism appreciated, and movie/TV show recommendations are even better.
