from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

# Initialize the SQLite database and the documents table.
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL
        )
    ''')

    sample_documents = [
        'python tutorial',
        'machine learning introduction',
        'data science basics',
        'deep learning models',
        'flask web development',
        'sqlite database example',
        'information retrieval systems',
        'search engine autocomplete',
        'natural language processing',
        'artificial intelligence overview',
        'web scraping with python',
        'javascript array methods',
        'react component lifecycle',
        'css flexbox layout',
        'html semantic tags',
        'linux command line',
        'git version control',
        'docker container basics',
        'cloud computing services',
        'cyber security fundamentals',
        'mobile app development',
        'data visualization tools',
        'network protocols',
        'database normalization',
        'probability and statistics'
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO documents (content) VALUES (?)',
        [(item,) for item in sample_documents]
    )
    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT content FROM documents WHERE lower(content) LIKE ? ORDER BY content LIMIT 50",
        (query + '%',)
    )
    rows = cursor.fetchall()
    conn.close()

    suggestions = []
    seen = set()

    for row in rows:
        content = row['content']
        lower_content = content.lower()
        if lower_content in seen:
            continue
        seen.add(lower_content)

        prefix_length = len(query)
        length_score = max(0, 100 - len(content))
        exact_prefix = 1 if lower_content.startswith(query) else 0
        score = exact_prefix * 100 + prefix_length * 5 + length_score

        suggestions.append({
            'text': content,
            'score': score
        })

    suggestions.sort(key=lambda item: item['score'], reverse=True)
    return jsonify([item['text'] for item in suggestions[:5]])


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
