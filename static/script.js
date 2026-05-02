// Get DOM elements
const searchInput = document.getElementById('searchInput');
const suggestionsList = document.getElementById('suggestionsList');
const selectedItem = document.getElementById('selectedItem');

// Debouncing variable
let debounceTimer;
const DEBOUNCE_DELAY = 300; // 300ms delay

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
        // Fetch data from /search endpoint
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Parse JSON response
        const suggestions = await response.json();

        // Display suggestions
        displaySuggestions(suggestions);
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        clearSuggestions();
    }
}

/**
 * Display suggestions in the dropdown list
 * @param {array} suggestions - Array of suggestion strings
 */
function displaySuggestions(suggestions) {
    // Clear previous suggestions
    suggestionsList.innerHTML = '';

    // If no results, show "No results" message
    if (suggestions.length === 0) {
        const li = document.createElement('li');
        li.className = 'no-results';
        li.textContent = 'No results found';
        suggestionsList.appendChild(li);
        suggestionsList.style.display = 'block';
        return;
    }

    // Create list items for each suggestion
    suggestions.forEach((suggestion) => {
        const li = document.createElement('li');
        li.className = 'suggestion-item';
        li.textContent = suggestion;

        // Add click event to fill input with suggestion
        li.addEventListener('click', () => {
            searchInput.value = suggestion;
            selectedItem.textContent = `Selected: ${suggestion}`;
            clearSuggestions();
        });

        suggestionsList.appendChild(li);
    });

    // Show suggestions list
    suggestionsList.style.display = 'block';
}

/**
 * Clear all suggestions from the dropdown
 */
function clearSuggestions() {
    suggestionsList.innerHTML = '';
    suggestionsList.style.display = 'none';
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

// Add event listener to search input
searchInput.addEventListener('input', debouncedSearch);

// Close suggestions when clicking outside
document.addEventListener('click', (event) => {
    // If click is not on input or suggestions list, close suggestions
    if (!event.target.closest('.input-wrapper')) {
        clearSuggestions();
    }
});
