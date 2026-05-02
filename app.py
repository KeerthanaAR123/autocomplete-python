from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
DATABASE = 'database.db'

# Normalize text for consistent search matching.
def normalize_text(text):
    text = text.lower().strip()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text)
    return text


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS documents')
    cursor.execute('''
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    snippet TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT NOT NULL,
    popularity INTEGER NOT NULL
)
''')

    sample_documents = [
        {
            'title': 'Machine Learning Basics',
            'snippet': 'A concise explanation of supervised and unsupervised learning.',
            'content': 'Machine learning teaches computers to learn from data. This guide covers common algorithms, model evaluation, and how to build predictive systems with Python.',
            'url': 'https://example.com/machine-learning-basics',
            'popularity': 100
        },
        {
            'title': 'Deep Learning Explained',
            'snippet': 'Understand neural networks, backpropagation, and advanced architectures.',
            'content': 'Deep learning uses multiple layers of neurons to extract high-level features from large datasets. It powers image recognition, speech recognition, and natural language models.',
            'url': 'https://example.com/deep-learning-explained',
            'popularity': 95
        },
        {
            'title': 'Python Programming Guide',
            'snippet': 'A practical introduction to Python syntax, functions, and idioms.',
            'content': 'Python is a powerful language for web development, data science, automation, and scripting. Learn how to write clean code, manage packages, and build scripts with this guide.',
            'url': 'https://example.com/python-programming-guide',
            'popularity': 90
        },
        {
            'title': 'Flask Web Development',
            'snippet': 'Build lightweight web applications with Flask and Python.',
            'content': 'Flask is a microframework that makes it easy to create web services, HTML pages, and APIs. This tutorial covers routing, templates, forms, and deployment.',
            'url': 'https://example.com/flask-web-development',
            'popularity': 85
        },
        {
            'title': 'Django Project Quickstart',
            'snippet': 'Create a full-featured web application using Django.',
            'content': 'Django is a batteries-included framework for Python. Learn about models, views, templates, authentication, and deploying Django apps securely.',
            'url': 'https://example.com/django-quickstart',
            'popularity': 80
        },
        {
            'title': 'Natural Language Processing',
            'snippet': 'Learn how machines understand text, sentiment, and language structure.',
            'content': 'Natural language processing helps computers interpret human language. Topics include tokenization, named entity recognition, sentiment analysis, and language modeling.',
            'url': 'https://example.com/nlp-overview',
            'popularity': 78
        },
        {
            'title': 'Artificial Intelligence Overview',
            'snippet': 'What AI is, how it works, and why it matters today.',
            'content': 'Artificial intelligence includes machine learning, reasoning, planning, and perception. Explore the history of AI, applications in business, and ethical considerations.',
            'url': 'https://example.com/ai-overview',
            'popularity': 76
        },
        {
            'title': 'Neural Networks Tutorial',
            'snippet': 'A hands-on guide to building neural networks from scratch.',
            'content': 'Neural networks consist of layers of connected nodes. Learn how to train networks, choose activation functions, and avoid overfitting using Python libraries.',
            'url': 'https://example.com/neural-networks-tutorial',
            'popularity': 75
        },
        {
            'title': 'Search Engine Optimization',
            'snippet': 'Practical tips to improve website visibility in search engines.',
            'content': 'SEO helps sites rank higher in search results. Learn about keywords, on-page optimization, link building, and performance improvements for better organic traffic.',
            'url': 'https://example.com/seo-tips',
            'popularity': 68
        },
        {
            'title': 'Web Scraping with Python',
            'snippet': 'Extract data from websites using requests and Beautiful Soup.',
            'content': 'Web scraping automates data collection from HTML pages. This guide covers selectors, parsing, rate limiting, and legal best practices.',
            'url': 'https://example.com/web-scraping-python',
            'popularity': 66
        }
    ]

    cursor.executemany(
        'INSERT INTO documents (title, snippet, content, url, popularity) VALUES (?, ?, ?, ?, ?)',
        [(doc['title'], doc['snippet'], doc['content'], doc['url'], doc['popularity']) for doc in sample_documents]
    )
    conn.commit()
    conn.close()


def get_all_documents():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT title, snippet, content, url, popularity FROM documents')
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'title': row[0],
            'snippet': row[1],
            'content': row[2],
            'url': row[3],
            'popularity': row[4]
        }
        for row in rows
    ]


class SearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r'(?u)\b\w+\b')
        self.documents = []
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        self.documents = get_all_documents()
        texts = [normalize_text(f"{doc['title']} {doc['snippet']} {doc['content']}") for doc in self.documents]
        if not texts:
            self.tfidf_matrix = None
            return
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def _score_documents(self, normalized_input, query_vector):
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        max_popularity = max((doc['popularity'] for doc in self.documents), default=1)
        scores = []

        for idx, doc in enumerate(self.documents):
            cosine_score = float(similarities[idx])
            popularity_score = doc['popularity'] / max_popularity
            score = (0.6 * cosine_score) + (0.3 * popularity_score)

            title_text = normalize_text(doc['title'])
            if normalized_input in title_text:
                score += 0.15
            if title_text.startswith(normalized_input):
                score += 0.15
            if any(token in title_text for token in normalized_input.split()):
                score += 0.05

            scores.append((idx, score))

        return scores

    def get_suggestions(self, user_input, top_n=5):
        if not user_input or not user_input.strip():
            return []

        normalized_input = normalize_text(user_input)
        if not normalized_input or self.tfidf_matrix is None:
            return []

        query_vector = self.vectorizer.transform([normalized_input])
        scored = self._score_documents(normalized_input, query_vector)
        scored.sort(key=lambda item: item[1], reverse=True)

        suggestions = []
        seen = set()
        for idx, _ in scored:
            title = self.documents[idx]['title']
            if title.lower() not in seen:
                seen.add(title.lower())
                suggestions.append(title)
            if len(suggestions) >= top_n:
                break

        return suggestions

    def get_results(self, user_input, top_n=6):
        if not user_input or not user_input.strip():
            return []

        normalized_input = normalize_text(user_input)
        if not normalized_input or self.tfidf_matrix is None:
            return []

        query_vector = self.vectorizer.transform([normalized_input])
        scored = self._score_documents(normalized_input, query_vector)
        scored.sort(key=lambda item: item[1], reverse=True)

        results = []
        for idx, score in scored[:top_n]:
            doc = self.documents[idx]
            results.append({
                'title': doc['title'],
                'snippet': doc['snippet'],
                'url': doc['url'],
                'score': round(score, 3)
            })

        return results


init_db()
search_engine = SearchEngine()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'suggestions': [], 'results': []})

    return jsonify({
        'suggestions': search_engine.get_suggestions(query, top_n=6),
        'results': search_engine.get_results(query, top_n=6)
    })


if __name__ == '__main__':
    search_engine = SearchEngine()
    app.run(debug=True)
