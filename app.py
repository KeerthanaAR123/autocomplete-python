from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import re
from collections import Counter

app = Flask(__name__)

# Database configuration
DATABASE = 'database.db'

def init_db():
    """Initialize database with comprehensive sample data and migrate if needed."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create products table with columns for category and popularity if needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            popularity INTEGER DEFAULT 50
        )
    ''')

    # Ensure a unique index for product names to avoid duplicates
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_products_name ON products(name)')

    # Check schema columns and add missing ones for old databases
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'General'")
    if 'popularity' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN popularity INTEGER DEFAULT 50")

    # Create search history table if missing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            count INTEGER DEFAULT 1
        )
    ''')

    # Update existing rows that may have null category values
    cursor.execute("UPDATE products SET category='General' WHERE category IS NULL OR category = ''")

    # Load a broader set of common user search queries
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]

    sample_data = [
        # Most common quick search terms
        ('weather today', 'General', 98),
        ('news headlines', 'General', 96),
        ('youtube', 'General', 95),
        ('facebook login', 'General', 94),
        ('google translate', 'General', 91),
        ('gmail login', 'General', 92),
        ('amazon', 'Shopping', 97),
        ('flipkart', 'Shopping', 90),
        ('instagram', 'General', 93),
        ('whatsapp web', 'General', 89),
        ('netflix', 'Entertainment', 94),
        ('spotify', 'Entertainment', 90),
        ('zomato', 'Food', 88),
        ('ola taxi', 'Travel', 87),
        ('google maps', 'Travel', 92),
        ('covid vaccine', 'Health', 90),
        ('weather tomorrow', 'General', 88),
        ('how to lose weight', 'Health', 86),
        ('best restaurants near me', 'Food', 89),
        ('stock market live', 'Business', 91),
        ('flight tickets', 'Travel', 90),
        ('hotels near me', 'Travel', 88),
        ('online courses', 'Education', 89),
        ('python tutorial', 'Technology', 97),
        ('java tutorial', 'Technology', 94),
        ('react js tutorial', 'Technology', 93),
        ('node js tutorial', 'Technology', 91),
        ('flask tutorial', 'Technology', 88),
        ('django tutorial', 'Technology', 87),
        ('machine learning', 'Technology', 95),
        ('data science', 'Technology', 94),
        ('cloud computing', 'Technology', 92),
        ('aws certification', 'Technology', 90),
        ('azure certification', 'Technology', 89),
        ('google cloud', 'Technology', 88),
        ('android development', 'Technology', 87),
        ('ios development', 'Technology', 86),
        ('web development', 'Technology', 96),
        ('css flexbox', 'Technology', 82),
        ('sql query', 'Technology', 84),
        ('shopping deals', 'Shopping', 91),
        ('best smartphones 2026', 'Shopping', 88),
        ('laptop deals', 'Shopping', 90),
        ('camera deals', 'Shopping', 86),
        ('home decor ideas', 'Lifestyle', 85),
        ('garden ideas', 'Lifestyle', 82),
        ('fitness tips', 'Health', 88),
        ('mental health tips', 'Health', 86),
        ('movie reviews', 'Entertainment', 87),
        ('music streaming', 'Entertainment', 89),
        ('how to learn python', 'Technology', 96),
        ('best python libraries', 'Technology', 93),
        ('react vs angular', 'Technology', 90),
        ('how to deploy flask app', 'Technology', 92),
        ('best online courses for data science', 'Education', 94),
        ('how to build a website', 'Technology', 95),
        ('programming interview questions', 'Education', 91),
        ('top machine learning algorithms', 'Technology', 92),
        ('css grid tutorial', 'Technology', 87),
        ('best android phones 2026', 'Shopping', 88),
        ('latest tech news', 'Technology', 93),
        ('stock market today', 'Business', 90),
        ('best coding bootcamp', 'Education', 89),
        ('data science projects', 'Technology', 90),
        ('learn sql online', 'Education', 88)
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO products (name, category, popularity) VALUES (?, ?, ?)',
        sample_data
    )

    conn.commit()
    conn.close()

def get_db():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/search')
def search():
    """
    Advanced search with multiple matching strategies like Google
    Returns JSON list of suggestions with categories and ranking
    """
    query = request.args.get('q', '').strip().lower()

    # Validate query - must not be empty and at least 1 character
    if not query or len(query) < 1:
        return jsonify([])

    # Connect to database
    conn = get_db()
    cursor = conn.cursor()

    # Get all products for advanced matching
    cursor.execute('SELECT name, category, popularity FROM products')
    all_products = cursor.fetchall()

    suggestions = []
    seen = set()  # Track unique suggestions

    # Strategy 1: Exact prefix match (highest priority)
    prefix_matches = [p for p in all_products if p['name'].lower().startswith(query)]
    for product in sorted(prefix_matches, key=lambda x: x['popularity'], reverse=True)[:3]:
        if product['name'] not in seen:
            suggestions.append({
                'text': product['name'],
                'category': product['category'],
                'type': 'prefix'
            })
            seen.add(product['name'])

    # Strategy 2: Word boundary matches (like "web dev" matching "Web Development")
    word_boundary_matches = []
    query_words = query.split()
    for product in all_products:
        product_lower = product['name'].lower()
        if all(word in product_lower for word in query_words):
            # Check if it's a word boundary match
            if any(re.search(r'\b' + re.escape(word), product_lower) for word in query_words):
                word_boundary_matches.append(product)

    for product in sorted(word_boundary_matches, key=lambda x: x['popularity'], reverse=True)[:2]:
        if product['name'] not in seen:
            suggestions.append({
                'text': product['name'],
                'category': product['category'],
                'type': 'word_match'
            })
            seen.add(product['name'])

    # Strategy 3: Substring matches (contains query anywhere)
    substring_matches = [p for p in all_products if query in p['name'].lower() and p['name'] not in seen]
    for product in sorted(substring_matches, key=lambda x: x['popularity'], reverse=True)[:2]:
        if product['name'] not in seen:
            suggestions.append({
                'text': product['name'],
                'category': product['category'],
                'type': 'substring'
            })
            seen.add(product['name'])

    # Strategy 4: Fuzzy matches (similar words)
    fuzzy_matches = []
    for product in all_products:
        product_lower = product['name'].lower()
        # Simple fuzzy matching - check if most characters match in order
        if len(query) >= 3:
            query_chars = set(query)
            product_chars = set(product_lower)
            similarity = len(query_chars.intersection(product_chars)) / len(query_chars.union(product_chars))
            if similarity > 0.6 and product['name'] not in seen:
                fuzzy_matches.append((product, similarity))

    for product, similarity in sorted(fuzzy_matches, key=lambda x: (x[1], x[0]['popularity']), reverse=True)[:1]:
        suggestions.append({
            'text': product['name'],
            'category': product['category'],
            'type': 'fuzzy'
        })
        seen.add(product['name'])

    # Strategy 5: Category-based suggestions (if we have few results)
    if len(suggestions) < 3:
        # Find categories that match the query
        category_matches = []
        for product in all_products:
            if product['category'].lower().startswith(query) and product['name'] not in seen:
                category_matches.append(product)

        for product in sorted(category_matches, key=lambda x: x['popularity'], reverse=True)[:2]:
            if product['name'] not in seen:
                suggestions.append({
                    'text': product['name'],
                    'category': product['category'],
                    'type': 'category'
                })
                seen.add(product['name'])

    # Strategy 6: Popular items in similar categories (if still few results)
    if len(suggestions) < 5:
        # Get popular items from categories that appeared in results
        existing_categories = {s['category'] for s in suggestions}
        popular_from_categories = []
        for product in all_products:
            if product['category'] in existing_categories and product['name'] not in seen and product['popularity'] > 75:
                popular_from_categories.append(product)

        for product in sorted(popular_from_categories, key=lambda x: x['popularity'], reverse=True)[:3]:
            if product['name'] not in seen:
                suggestions.append({
                    'text': product['name'],
                    'category': product['category'],
                    'type': 'popular'
                })
                seen.add(product['name'])

    # Limit to top 8 suggestions
    suggestions = suggestions[:8]

    # Record search in history
    try:
        cursor.execute('INSERT OR REPLACE INTO search_history (query, count) VALUES (?, COALESCE((SELECT count FROM search_history WHERE query = ?), 0) + 1)', (query, query))
        conn.commit()
    except:
        pass  # Ignore history errors

    conn.close()

    return jsonify(suggestions)

@app.route('/results')
def results():
    """
    Return full search results for the query.
    """
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name, category, popularity FROM products')
    all_products = cursor.fetchall()

    query_words = query.split()
    scored_results = []

    for product in all_products:
        name = product['name']
        name_lower = name.lower()
        score = 0
        match_type = 'none'

        if name_lower == query:
            score += 150
            match_type = 'exact'
        if name_lower.startswith(query):
            score += 100
            match_type = 'prefix'
        if any(name_lower.startswith(word) for word in query_words):
            score += 60
            if match_type == 'none':
                match_type = 'word_match'
        if all(word in name_lower for word in query_words):
            score += 50
            if match_type == 'none':
                match_type = 'word_match'
        if query in name_lower and match_type == 'none':
            score += 35
            match_type = 'substring'

        # Phrase match for multi-word input
        if len(query_words) > 1 and ' '.join(query_words) in name_lower:
            score += 80
            match_type = 'phrase'

        # Fuzzy similarity for complex queries
        if len(query) >= 3:
            query_chars = set(query)
            name_chars = set(name_lower)
            similarity = len(query_chars.intersection(name_chars)) / len(query_chars.union(name_chars))
            if similarity > 0.55 and match_type == 'none':
                score += int(similarity * 30)
                match_type = 'fuzzy'

        if score > 0:
            score += product['popularity'] / 2
            description = f"Category: {product['category']} · Popularity {product['popularity']}"
            scored_results.append({
                'text': name,
                'category': product['category'],
                'match_type': match_type,
                'description': description,
                'score': score
            })

    scored_results.sort(key=lambda item: item['score'], reverse=True)
    conn.close()

    # return top 20 results
    return jsonify(scored_results[:20])

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run Flask app with debug mode enabled
    app.run(debug=True)
