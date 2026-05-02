const searchInput = document.getElementById('searchInput');
const suggestionsContainer = document.getElementById('suggestionsContainer');
const stats = document.getElementById('stats');
const noResults = document.getElementById('noResults');
const resultsContainer = document.getElementById('resultsContainer');
let debounceTimer;
const DEBOUNCE_DELAY = 300;

async function fetchSuggestions(query) {
    if (!query.trim()) {
        clearSuggestions();
        clearResults();
        return;
    }

    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Network error');
        }

        const data = await response.json();
        renderSuggestions(data.suggestions, query);
        renderResults(data.results);
    } catch (error) {
        console.error(error);
        clearSuggestions();
        clearResults();
    }
}

function renderSuggestions(suggestions, query) {
    suggestionsContainer.innerHTML = '';
    if (suggestions.length === 0) {
        suggestionsContainer.classList.add('hidden');
        return;
    }

    noResults.classList.add('hidden');
    suggestionsContainer.classList.remove('hidden');
    updateStats(suggestions.length, 'suggestion');

    suggestions.forEach((text) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = highlightPrefix(text, query);
        item.addEventListener('click', () => {
            searchInput.value = text;
            fetchSuggestions(text);
        });
        suggestionsContainer.appendChild(item);
    });
}

function renderResults(results) {
    resultsContainer.innerHTML = '';
    if (!results || results.length === 0) {
        showNoResults();
        clearResults();
        return;
    }

    noResults.classList.add('hidden');
    resultsContainer.classList.remove('hidden');
    updateStats(results.length, 'result');

    results.forEach((result) => {
        const card = document.createElement('div');
        card.className = 'result-card';

        const titleLink = document.createElement('a');
        titleLink.href = result.url;
        titleLink.target = '_blank';
        titleLink.rel = 'noopener noreferrer';
        titleLink.className = 'result-title';
        titleLink.textContent = result.title;

        const urlText = document.createElement('div');
        urlText.className = 'result-url';
        urlText.textContent = result.url;

        const snippet = document.createElement('p');
        snippet.className = 'result-snippet';
        snippet.textContent = result.snippet;

        card.appendChild(titleLink);
        card.appendChild(urlText);
        card.appendChild(snippet);
        resultsContainer.appendChild(card);
    });
}

function updateStats(count, type) {
    if (count > 0) {
        stats.textContent = `Showing ${count} ${type}${count > 1 ? 's' : ''}`;
        stats.classList.remove('hidden');
    } else {
        stats.classList.add('hidden');
    }
}

function highlightPrefix(text, query) {
    const escaped = query.replace(/[.*+?^${}()|[\\]\\]/g, '\\$&');
    const regex = new RegExp(`^(${escaped})`, 'i');
    const highlighted = text.replace(regex, '<strong>$1</strong>');
    return `<span class="suggestion-text">${highlighted}</span>`;
}

function clearSuggestions() {
    suggestionsContainer.innerHTML = '';
    suggestionsContainer.classList.add('hidden');
}

function clearResults() {
    resultsContainer.innerHTML = '';
    resultsContainer.classList.add('hidden');
    stats.classList.add('hidden');
}

function showNoResults() {
    suggestionsContainer.classList.add('hidden');
    noResults.classList.remove('hidden');
}

function handleInput() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchSuggestions(searchInput.value);
    }, DEBOUNCE_DELAY);
}

searchInput.addEventListener('input', handleInput);
searchInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        fetchSuggestions(searchInput.value);
        clearSuggestions();
    }
});
searchInput.addEventListener('focus', () => {
    if (searchInput.value.trim()) {
        fetchSuggestions(searchInput.value);
    }
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('.autocomplete-wrapper')) {
        clearSuggestions();
    }
});
