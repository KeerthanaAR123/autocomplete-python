// Get DOM elements
const searchInput = document.getElementById('searchInput');
const suggestionsContainer = document.getElementById('suggestionsContainer');
const suggestionsList = document.getElementById('suggestionsList');
const searchStats = document.getElementById('searchStats');
const searchButton = document.getElementById('searchButton');
const voiceButton = document.getElementById('voiceButton');

// Debouncing variables
let debounceTimer;
const DEBOUNCE_DELAY = 150; // Faster response like Google

// Current suggestions data
let currentSuggestions = [];
let selectedIndex = -1;

/**
 * Get icon for suggestion type
 * @param {string} type - Suggestion type
 * @returns {string} Material icon name
 */
function getSuggestionIcon(type) {
    const icons = {
        'prefix': 'search',
        'word_match': 'match_word',
        'substring': 'find_in_page',
        'fuzzy': 'blur_on',
        'category': 'category',
        'popular': 'trending_up'
    };
    return icons[type] || 'search';
}

/**
 * Get color class for suggestion type
 * @param {string} type - Suggestion type
 * @returns {string} CSS class name
 */
function getSuggestionClass(type) {
    return `suggestion-icon ${type}`;
}

/**
 * Fetch suggestions from the backend API
 * @param {string} query - Search query string
 */
async function fetchSuggestions(query) {
    // If query is empty, clear suggestions
    if (!query.trim()) {
        clearSuggestions();
        return;
    }

    try {
        // Show loading state
        showLoading();

        // Fetch data from /search endpoint
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Parse JSON response
        const suggestions = await response.json();

        // Store current suggestions
        currentSuggestions = suggestions;

        // Display suggestions
        displaySuggestions(suggestions);

        // Update search stats
        updateSearchStats(suggestions.length, query);

    } catch (error) {
        console.error('Error fetching suggestions:', error);
        clearSuggestions();
        showError();
    }
}

/**
 * Display suggestions in the dropdown list
 * @param {array} suggestions - Array of suggestion objects
 */
function displaySuggestions(suggestions) {
    // Clear previous suggestions
    suggestionsList.innerHTML = '';

    // If no results, show "No results" message
    if (suggestions.length === 0) {
        const div = document.createElement('div');
        div.className = 'suggestion-item no-results';
        div.innerHTML = `
            <div class="suggestion-content">
                <div class="suggestion-text">No results found for "${searchInput.value}"</div>
                <div class="suggestion-category">Try different keywords</div>
            </div>
        `;
        suggestionsList.appendChild(div);
        suggestionsContainer.style.display = 'block';
        return;
    }

    // Create suggestion items
    suggestions.forEach((suggestion, index) => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.dataset.index = index;

        const iconName = getSuggestionIcon(suggestion.type);
        const iconClass = getSuggestionClass(suggestion.type);

        div.innerHTML = `
            <span class="material-icons ${iconClass}">${iconName}</span>
            <div class="suggestion-content">
                <div class="suggestion-text">${highlightMatch(suggestion.text, searchInput.value)}</div>
                <div class="suggestion-category">${suggestion.category}</div>
            </div>
        `;

        // Add click event
        div.addEventListener('click', () => {
            selectSuggestion(suggestion);
        });

        // Add mouseover event for keyboard navigation
        div.addEventListener('mouseover', () => {
            setSelectedIndex(index);
        });

        suggestionsList.appendChild(div);
    });

    // Show suggestions container
    suggestionsContainer.style.display = 'block';

    // Reset selected index
    selectedIndex = -1;
}

/**
 * Highlight matching text in suggestion
 * @param {string} text - Full suggestion text
 * @param {string} query - Search query
 * @returns {string} HTML with highlighted matches
 */
function highlightMatch(text, query) {
    if (!query) return text;

    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
}

/**
 * Select a suggestion
 * @param {object} suggestion - Selected suggestion object
 */
function selectSuggestion(suggestion) {
    searchInput.value = suggestion.text;
    clearSuggestions();

    // Show selected item feedback
    showSearchStats(`Searching for: ${suggestion.text}`, true);

    // Here you could trigger a search or navigate to results
    console.log('Selected:', suggestion);
}

/**
 * Show loading state
 */
function showLoading() {
    suggestionsList.innerHTML = `
        <div class="suggestion-item loading">
            <span class="material-icons suggestion-icon">hourglass_empty</span>
            <div class="suggestion-content">
                <div class="suggestion-text">Searching...</div>
                <div class="suggestion-category">Finding the best matches</div>
            </div>
        </div>
    `;
    suggestionsContainer.style.display = 'block';
}

/**
 * Show error state
 */
function showError() {
    suggestionsList.innerHTML = `
        <div class="suggestion-item no-results">
            <span class="material-icons suggestion-icon">error</span>
            <div class="suggestion-content">
                <div class="suggestion-text">Search temporarily unavailable</div>
                <div class="suggestion-category">Please try again later</div>
            </div>
        </div>
    `;
    suggestionsContainer.style.display = 'block';
}

/**
 * Update search statistics
 * @param {number} count - Number of suggestions
 * @param {string} query - Search query
 */
function updateSearchStats(count, query) {
    if (count > 0) {
        searchStats.textContent = `About ${count} suggestion${count !== 1 ? 's' : ''} for "${query}"`;
        searchStats.classList.add('visible');
    } else {
        searchStats.classList.remove('visible');
    }
}

/**
 * Show search stats with custom message
 * @param {string} message - Message to display
 * @param {boolean} temporary - Whether to hide after delay
 */
function showSearchStats(message, temporary = false) {
    searchStats.textContent = message;
    searchStats.classList.add('visible');

    if (temporary) {
        setTimeout(() => {
            searchStats.classList.remove('visible');
        }, 3000);
    }
}

/**
 * Clear all suggestions
 */
function clearSuggestions() {
    suggestionsList.innerHTML = '';
    suggestionsContainer.style.display = 'none';
    searchStats.classList.remove('visible');
    currentSuggestions = [];
    selectedIndex = -1;
}

/**
 * Set selected suggestion index for keyboard navigation
 * @param {number} index - Index of selected suggestion
 */
function setSelectedIndex(index) {
    // Remove previous selection
    const previousSelected = suggestionsList.querySelector('.selected');
    if (previousSelected) {
        previousSelected.classList.remove('selected');
    }

    // Add new selection
    if (index >= 0 && index < currentSuggestions.length) {
        const selectedItem = suggestionsList.children[index];
        if (selectedItem) {
            selectedItem.classList.add('selected');
            selectedIndex = index;
        }
    } else {
        selectedIndex = -1;
    }
}

/**
 * Debounced search - delays API call until user stops typing
 */
function debouncedSearch() {
    // Clear previous timer
    clearTimeout(debounceTimer);

    // Set new timer to call fetchSuggestions after DEBOUNCE_DELAY
    debounceTimer = setTimeout(() => {
        const query = searchInput.value.trim();
        fetchSuggestions(query);
    }, DEBOUNCE_DELAY);
}

// Event Listeners

// Input event for search
searchInput.addEventListener('input', debouncedSearch);

// Focus event to show suggestions if there's a value
searchInput.addEventListener('focus', () => {
    const query = searchInput.value.trim();
    if (query) {
        fetchSuggestions(query);
    }
});

// Keyboard navigation
searchInput.addEventListener('keydown', (event) => {
    if (currentSuggestions.length === 0) return;

    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            setSelectedIndex(selectedIndex + 1);
            break;
        case 'ArrowUp':
            event.preventDefault();
            setSelectedIndex(selectedIndex - 1);
            break;
        case 'Enter':
            event.preventDefault();
            if (selectedIndex >= 0 && selectedIndex < currentSuggestions.length) {
                selectSuggestion(currentSuggestions[selectedIndex]);
            } else {
                // Perform search with current input
                const query = searchInput.value.trim();
                if (query) {
                    showSearchStats(`Searching for: ${query}`, true);
                    clearSuggestions();
                }
            }
            break;
        case 'Escape':
            clearSuggestions();
            searchInput.blur();
            break;
    }
});

// Search button click
searchButton.addEventListener('click', () => {
    const query = searchInput.value.trim();
    if (query) {
        showSearchStats(`Searching for: ${query}`, true);
        clearSuggestions();
    }
});

// Voice button click (placeholder)
voiceButton.addEventListener('click', () => {
    // In a real implementation, this would trigger voice recognition
    alert('Voice search coming soon!');
});

// Close suggestions when clicking outside
document.addEventListener('click', (event) => {
    if (!event.target.closest('.search-box-container')) {
        clearSuggestions();
    }
});

// Handle window resize for responsive behavior
window.addEventListener('resize', () => {
    // Close suggestions on mobile when resizing
    if (window.innerWidth < 768) {
        clearSuggestions();
    }
});

// Initialize - focus on search input
document.addEventListener('DOMContentLoaded', () => {
    searchInput.focus();
});

