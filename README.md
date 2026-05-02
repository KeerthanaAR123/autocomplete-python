# Automatic Query Completion System

A simple Information Retrieval based autocomplete system built using Python, Flask, and SQLite.

## Project Overview

This project demonstrates an autocomplete system that retrieves and ranks suggestions based on user input prefixes.

The backend uses prefix-based search and a relevance scoring mechanism to return the most useful suggestions.

## Files

- app.py — Flask backend and database logic
- database.db — SQLite database (auto-created)
- templates/index.html — UI for autocomplete
- static/script.js — Autocomplete logic
- static/style.css — UI styling

## How It Works

1. User types a query
2. System searches for matching prefixes
3. Results are ranked based on:
   - Exact prefix match
   - Length of match
   - Shorter suggestions preference
4. Top suggestions are displayed instantly

## Run the App

```bash
python app.py