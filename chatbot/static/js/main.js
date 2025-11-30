document.addEventListener('DOMContentLoaded', function() {
    // Generate a unique session ID
    const sessionId = generateSessionId();
    // Store it in window object so it can be accessed from chat.js
    window.sessionId = sessionId;
    
    // Initialize language
    updateLanguageDirection();
    
    // Load suggestions
    loadSuggestions();
    
    // Event listener for language selection
    document.getElementById('language-select').addEventListener('change', function() {
        updateLanguageDirection();
        loadSuggestions();
    });
});

// Generate a random session ID
function generateSessionId() {
    return 'session_' + Math.random().toString(36).substring(2, 15);
}

// Update language direction based on selected language
function updateLanguageDirection() {
    const languageSelect = document.getElementById('language-select');
    const lang = languageSelect.value;
    
    // Set language direction (RTL for Arabic)
    if (lang === 'ar') {
        document.documentElement.setAttribute('dir', 'rtl');
        document.documentElement.setAttribute('lang', 'ar');
    } else {
        document.documentElement.setAttribute('dir', 'ltr');
        document.documentElement.setAttribute('lang', lang);
    }
    
    // Update placeholder text based on language
    const questionInput = document.getElementById('question-input');
    if (lang === 'en') {
        questionInput.placeholder = 'Ask a question about the Moroccan Constitution...';
    } else if (lang === 'fr') {
        questionInput.placeholder = 'Posez une question sur la Constitution marocaine...';
    } else if (lang === 'ar') {
        questionInput.placeholder = 'اطرح سؤالاً حول الدستور المغربي...';
    }
}

// Load suggested questions from API
function loadSuggestions() {
    const language = document.getElementById('language-select').value;

    fetch(`/api/suggestions?language=${language}`)
        .then(response => response.json())
        .then(data => {
            displaySuggestions(data.suggestions);
        })
        .catch(error => {
            console.error('Error loading suggestions:', error);
            // Fallback suggestions (English)
            const fallbackSuggestions = [
                "What are the fundamental principles of the Moroccan Constitution?",
                "What rights are guaranteed to Moroccan citizens?",
                "How is the government structured in Morocco?"
            ];
            displaySuggestions(fallbackSuggestions);
        });
}

// Display suggestions in the UI
function displaySuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('suggestions');
    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const suggestionElement = document.createElement('div');
        suggestionElement.classList.add('suggestion');
        suggestionElement.textContent = suggestion;
        
        // Add click event to use the suggestion
        suggestionElement.addEventListener('click', function() {
            document.getElementById('question-input').value = suggestion;
            document.getElementById('question-form').dispatchEvent(new Event('submit'));
        });
        
        suggestionsContainer.appendChild(suggestionElement);
    });
}