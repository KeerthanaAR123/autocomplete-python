from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
DATABASE = 'database.db'

# Preprocess text: lowercase, remove punctuation, and normalize whitespace.
def normalize_text(text):
    text = text.lower().strip()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text)
    return text


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY,
            query TEXT NOT NULL,
            frequency INTEGER NOT NULL
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM queries')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_queries = [
            ('machine learning', 100),
            ('deep learning', 95),
            ('data mining', 90),
            ('data science', 85),
            ('python programming', 80),
            ('flask tutorial', 75),
            ('django tutorial', 70),
            ('natural language processing', 65),
            ('artificial intelligence', 60),
            ('neural networks', 55),
            ('computer vision', 50),
            ('reinforcement learning', 45),
            ('support vector machine', 40),
            ('random forest', 35),
            ('gradient boosting', 30),
            ('convolutional neural network', 25),
            ('recurrent neural network', 22),
            ('transfer learning', 20),
            ('generative adversarial network', 18),
            ('word embedding', 16),
            ('tf-idf vectorization', 15),
            ('cosine similarity', 14),
            ('text classification', 13),
            ('sentiment analysis', 12),
            ('information retrieval', 11),
            ('search engine optimization', 10),
            ('web scraping', 9),
            ('pandas python', 8),
            ('numpy python', 7),
            ('matplotlib visualization', 6),
            ('scikit-learn tutorial', 5),
            ('tensorflow keras', 4),
            ('pytorch deep learning', 3),
            ('jupyter notebook', 2),
            ('git version control', 2),
            ('docker container', 2),
            ('kubernetes deployment', 2),
            ('aws cloud services', 2),
            ('azure machine learning', 2),
            ('database normalization', 2),
            ('sql query optimization', 2),
            ('react javascript', 2),
            ('angular framework', 2),
            ('vue js tutorial', 2),
            ('html css javascript', 2),
            ('rest api development', 2),
            ('microservices architecture', 2),
            ('blockchain technology', 2),
            ('cybersecurity fundamentals', 2)
        ]
        cursor.executemany(
            'INSERT INTO queries (query, frequency) VALUES (?, ?)',
            sample_queries
        )
        conn.commit()
    conn.close()


def get_all_queries():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT query, frequency FROM queries')
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], row[1]) for row in rows]


class QuerySuggestionSystem:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r'(?u)\b\w+\b')
        self.queries = []
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        self.queries = get_all_queries()
        query_texts = [normalize_text(q[0]) for q in self.queries]
        if not query_texts:
            self.tfidf_matrix = None
            return
        self.tfidf_matrix = self.vectorizer.fit_transform(query_texts)

    def get_suggestions(self, user_input, top_n=5):
        if not user_input or not user_input.strip():
            return []

        normalized_input = normalize_text(user_input)
        if not normalized_input:
            return []

        if self.tfidf_matrix is None:
            return []

        try:
            input_vector = self.vectorizer.transform([normalized_input])
        except ValueError:
            return []

        similarities = cosine_similarity(input_vector, self.tfidf_matrix)[0]
        max_freq = max((freq for _, freq in self.queries), default=1)

        scored = []
        for idx, (query_text, freq) in enumerate(self.queries):
            cosine_score = similarities[idx]
            if cosine_score <= 0:
                continue

            normalized_freq = freq / max_freq
            combined_score = (0.7 * cosine_score) + (0.3 * normalized_freq)

            if normalize_text(query_text).startswith(normalized_input):
                combined_score += 0.2

            scored.append((query_text, combined_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        seen = set()
        suggestions = []
        for query_text, _ in scored:
            if query_text.lower() not in seen:
                seen.add(query_text.lower())
                suggestions.append(query_text)
            if len(suggestions) >= top_n:
                break

        return suggestions


init_db()
query_system = QuerySuggestionSystem()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    suggestions = query_system.get_suggestions(query, top_n=5)
    return jsonify(suggestions)


if __name__ == '__main__':
    query_system = QuerySuggestionSystem()
    app.run(debug=True)
