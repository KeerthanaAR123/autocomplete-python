# IR Autocomplete Demo

A simple Information Retrieval based autocomplete demo built with Python, Flask, and SQLite.

## Project Overview

This project demonstrates an autocomplete system that retrieves and ranks suggestions from a SQLite document collection.
The backend uses prefix-based search and a basic relevance scoring function that prefers exact prefix matches and shorter suggestions.

## Files

- `app.py` — Flask backend and SQLite document initialization
- `database.db` — SQLite database populated automatically on first run
- `templates/index.html` — Minimal autocomplete UI
- `static/script.js` — Fetch-based autocomplete logic with 300ms debounce
- `static/style.css` — Clean dropdown styling and hover effects

## How It Works

1. The backend stores sample queries in a `documents` table.
2. `/search?q=` runs a case-insensitive prefix search using SQL `LIKE 'query%'`.
3. Duplicate suggestions are removed.
4. Suggestions are ranked using a simple scoring function:
   - Exact prefix matches are given priority
   - Longer prefix matches score higher
   - Shorter suggestions are preferred
5. The top 5 ranked suggestions are returned as JSON.

## Run the App

```bash
py -3 app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Information Retrieval Concepts Used

- **Prefix-based retrieval:** The app uses SQL to find documents starting with the query text.
- **Case-insensitive search:** The search ignores capitalization to match user input reliably.
- **Duplicate elimination:** Ensures clean suggestion output.
- **Ranking:** Suggestions are scored and sorted by relevance.
- **Debouncing:** The frontend waits 300ms after typing before requesting suggestions.
