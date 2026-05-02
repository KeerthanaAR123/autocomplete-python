from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database configuration
DATABASE = 'database.db'

def init_db():
    """Initialize database with sample data if empty"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    # Check if table is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
    # Insert sample data if table is empty
    if count == 0:
        sample_data = [
            'apple',
            'application',
            'appetite',
            'banana',
            'bat',
            'ball',
            'cat',
            'car',
            'carbon'
        ]
        cursor.executemany('INSERT INTO products (name) VALUES (?)', [(item,) for item in sample_data])
    
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
    Search for products based on query parameter
    Returns JSON list of matching products
    """
    query = request.args.get('q', '').strip()
    
    # Validate query - must not be empty
    if not query:
        return jsonify([])
    
    # Connect to database and perform search
    conn = get_db()
    cursor = conn.cursor()
    
    # SQL query with LIKE operator - search for products starting with query
    cursor.execute('SELECT name FROM products WHERE name LIKE ? LIMIT 5', (query + '%',))
    results = cursor.fetchall()
    conn.close()
    
    # Convert results to list of product names
    suggestions = [row['name'] for row in results]
    
    return jsonify(suggestions)

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run Flask app with debug mode enabled
    app.run(debug=True)
