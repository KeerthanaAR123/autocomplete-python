# QuerySense Auto-Complete Demo

A polished Information Retrieval autocomplete demo built with Python, Flask, and SQLite.

## Project Overview

QuerySense is an IR-style autocomplete demo that retrieves and ranks query suggestions from a small SQLite corpus.
The backend uses TF-IDF vectorization and cosine similarity to score relevance, while the frontend shows a modern centered search card with live suggestions.

## Files

- `app.py` — Flask backend, SQLite corpus initialization, and IR ranking logic
- `database.db` — SQLite database populated automatically when the app starts
- `templates/index.html` — Modern autocomplete UI
- `static/script.js` — Fetch-based autocomplete logic with 300ms debounce and suggestion highlighting
- `static/style.css` — Responsive card styling and dropdown UI

## How It Works

1. On startup, `app.py` initializes the SQLite `queries` table and inserts sample query text with frequency counts.
2. The backend builds a TF-IDF index from all stored query texts.
3. When `/search?q=` is called, the user query is normalized and transformed with the same TF-IDF model.
4. The backend ranks suggestions by cosine similarity plus a normalized frequency bonus.
5. The top 5 unique suggestions are returned as JSON.

## Run the App

```bash
py -3 app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Information Retrieval Concepts Used

- **TF-IDF vectorization:** Converts queries into weighted term vectors.
- **Cosine similarity:** Measures relevance between the input query and stored queries.
- **Query frequency:** Adds a popularity signal to help rank more common queries higher.
- **Normalization:** Lowercases text, removes punctuation, and collapses whitespace.
- **Debouncing:** The frontend waits 300ms before sending requests to reduce noise.
- **Modern UI:** Presents a centered search card with result highlighting and responsive styling.
