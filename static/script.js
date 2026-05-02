const searchInput = document.getElementById('searchInput');
const suggestionsContainer = document.getElementById('suggestionsContainer');
const noResults = document.getElementById('noResults');
let debounceTimer;
const DEBOUNCE_DELAY = 300;

async function fetchSuggestions(query) {
    if (!query.trim()) {
        clearSuggestions();
        return;
    }

    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error('Network error');
        }

        const suggestions = await response.json();
        renderSuggestions(suggestions, query);
    } catch (error) {
        console.error(error);
        clearSuggestions();
    }
}

function renderSuggestions(suggestions, query) {
    suggestionsContainer.innerHTML = '';
    if (suggestions.length === 0) {
        showNoResults();
        return;
    }

    noResults.classList.add('hidden');
    suggestionsContainer.classList.remove('hidden');

    suggestions.forEach((text) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = highlightPrefix(text, query);
        item.addEventListener('click', () => {
            searchInput.value = text;
            clearSuggestions();
        });
        suggestionsContainer.appendChild(item);
    });
}

function highlightPrefix(text, query) {
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`^(${escaped})`, 'i');
    const highlighted = text.replace(regex, '<strong>$1</strong>');
    return `<span class="suggestion-text">${highlighted}</span>`;
}

function clearSuggestions() {
    suggestionsContainer.innerHTML = '';
    suggestionsContainer.classList.add('hidden');
    noResults.classList.add('hidden');
}

function showNoResults() {
    suggestionsContainer.innerHTML = '';
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
