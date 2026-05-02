from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import re
from collections import Counter

app = Flask(__name__)

# Database configuration
DATABASE = 'database.db'

def init_db():
    """Initialize database with comprehensive sample data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create products table with additional columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            popularity INTEGER DEFAULT 0
        )
    ''')

    # Create search history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            count INTEGER DEFAULT 1
        )
    ''')

    # Check if products table is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]

    # Insert comprehensive sample data if table is empty
    if count == 0:
        sample_data = [
            # Technology & Software
            ('Python Programming', 'Technology', 95),
            ('JavaScript Tutorial', 'Technology', 90),
            ('React Framework', 'Technology', 88),
            ('Node.js Development', 'Technology', 85),
            ('Machine Learning', 'Technology', 92),
            ('Data Science', 'Technology', 87),
            ('Web Development', 'Technology', 93),
            ('Mobile App Development', 'Technology', 84),
            ('Cloud Computing', 'Technology', 89),
            ('Artificial Intelligence', 'Technology', 91),

            # Food & Restaurants
            ('Pizza Delivery', 'Food', 78),
            ('Italian Restaurant', 'Food', 75),
            ('Coffee Shop', 'Food', 82),
            ('Fast Food', 'Food', 80),
            ('Healthy Eating', 'Food', 76),
            ('Vegan Recipes', 'Food', 74),
            ('Dessert Recipes', 'Food', 79),
            ('Breakfast Ideas', 'Food', 77),

            # Shopping & Products
            ('Wireless Headphones', 'Shopping', 83),
            ('Smartphone Cases', 'Shopping', 70),
            ('Laptop Accessories', 'Shopping', 72),
            ('Home Decor', 'Shopping', 69),
            ('Fashion Trends', 'Shopping', 81),
            ('Beauty Products', 'Shopping', 73),
            ('Sports Equipment', 'Shopping', 71),
            ('Books Online', 'Shopping', 68),

            # Services
            ('Online Banking', 'Services', 86),
            ('Travel Booking', 'Services', 85),
            ('Hotel Reservations', 'Services', 83),
            ('Car Rental', 'Services', 75),
            ('Health Insurance', 'Services', 79),
            ('Legal Services', 'Services', 67),
            ('Home Cleaning', 'Services', 70),
            ('Tutoring Services', 'Services', 69),

            # Entertainment
            ('Movie Reviews', 'Entertainment', 88),
            ('Music Streaming', 'Entertainment', 90),
            ('Video Games', 'Entertainment', 87),
            ('Streaming Services', 'Entertainment', 89),
            ('Sports News', 'Entertainment', 84),
            ('Concert Tickets', 'Entertainment', 76),
            ('TV Shows', 'Entertainment', 85),

            # Health & Fitness
            ('Gym Workouts', 'Health', 82),
            ('Yoga Classes', 'Health', 78),
            ('Mental Health', 'Health', 80),
            ('Nutrition Tips', 'Health', 77),
            ('Weight Loss', 'Health', 81),
            ('Meditation Apps', 'Health', 74),

            # Education
            ('Online Courses', 'Education', 86),
            ('Language Learning', 'Education', 83),
            ('Math Tutoring', 'Education', 75),
            ('Science Experiments', 'Education', 72),
            ('Art Classes', 'Education', 70),

            # Travel
            ('Flight Tickets', 'Travel', 87),
            ('Vacation Planning', 'Travel', 84),
            ('Beach Resorts', 'Travel', 79),
            ('Adventure Travel', 'Travel', 76),
            ('City Guides', 'Travel', 78),

            # Business
            ('Business News', 'Business', 85),
            ('Stock Market', 'Business', 83),
            ('Freelance Jobs', 'Business', 80),
            ('Marketing Tips', 'Business', 77),
            ('Entrepreneurship', 'Business', 81),

            # Lifestyle
            ('Home Improvement', 'Lifestyle', 79),
            ('Gardening Tips', 'Lifestyle', 73),
            ('Pet Care', 'Lifestyle', 78),
            ('Cooking Classes', 'Lifestyle', 76),
            ('Photography', 'Lifestyle', 74),
            ('DIY Projects', 'Lifestyle', 75)
        ]
        cursor.executemany('INSERT INTO products (name, category, popularity) VALUES (?, ?, ?)', sample_data)

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

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run Flask app with debug mode enabled
    app.run(debug=True)
